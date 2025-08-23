"""
MCP (Model Context Protocol) Server Implementation
Provides tool discovery and execution following MCP standard
"""
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from tool_registry import tool_registry, ToolType
from gmail_service import gmail_service
from google_calendar_service import calendar_service

logger = logging.getLogger(__name__)

# MCP Protocol Models
class MCPRequest(BaseModel):
    """MCP request model"""
    jsonrpc: str = "2.0"
    id: str
    method: str
    params: Optional[Dict[str, Any]] = None

class MCPResponse(BaseModel):
    """MCP response model"""
    jsonrpc: str = "2.0"
    id: str
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

class MCPTool(BaseModel):
    """MCP tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]

class MCPToolCall(BaseModel):
    """MCP tool call request"""
    name: str
    arguments: Dict[str, Any]

class MCPToolResult(BaseModel):
    """MCP tool call result"""
    content: List[Dict[str, Any]]
    isError: bool = False

class MCPServer:
    """MCP Server implementation following MCP standard"""
    
    def __init__(self):
        self.app = FastAPI(title="MedAI MCP Server", version="1.0.0")
        self.active_connections: List[WebSocket] = []
        self.tools: Dict[str, Callable] = {}
        self._register_tools()
        self._setup_routes()
    
    def _register_tools(self):
        """Register all available tools"""
        # Appointment Tools
        self.tools["schedule_appointment"] = self._schedule_appointment
        self.tools["check_doctor_availability"] = self._check_doctor_availability
        self.tools["list_doctors"] = self._list_doctors
        
        # Calendar Tools
        self.tools["create_calendar_event"] = self._create_calendar_event
        self.tools["update_calendar_event"] = self._update_calendar_event
        self.tools["cancel_calendar_event"] = self._cancel_calendar_event
        
        # Email Tools
        self.tools["send_appointment_confirmation"] = self._send_appointment_confirmation
        self.tools["send_appointment_reminder"] = self._send_appointment_reminder
        self.tools["send_cancellation_notification"] = self._send_cancellation_notification
        
        # Analytics Tools
        self.tools["get_appointment_statistics"] = self._get_appointment_statistics
        self.tools["search_patients_by_symptoms"] = self._search_patients_by_symptoms
        
        logger.info(f"Registered {len(self.tools)} MCP tools")
    
    def _setup_routes(self):
        """Setup FastAPI routes for MCP endpoints"""
        
        @self.app.get("/mcp")
        async def mcp_info():
            """MCP server information"""
            return {
                "name": "MedAI MCP Server",
                "version": "1.0.0",
                "description": "MCP server for MedAI doctor appointment system",
                "capabilities": {
                    "tools": True,
                    "resources": False,
                    "prompts": False
                }
            }
        
        @self.app.get("/mcp/tools")
        async def list_tools():
            """List all available MCP tools"""
            tools = []
            for name, func in self.tools.items():
                tool_def = tool_registry.get_tool(name)
                if tool_def:
                    tools.append({
                        "name": name,
                        "description": tool_def.definition.description,
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                param.name: {
                                    "type": param.type,
                                    "description": param.description,
                                    "required": param.required
                                }
                                for param in tool_def.definition.parameters
                            },
                            "required": [
                                param.name for param in tool_def.definition.parameters 
                                if param.required
                            ]
                        }
                    })
            return {"tools": tools}
        
        @self.app.post("/mcp/tools/call")
        async def call_tool(tool_call: MCPToolCall):
            """Execute an MCP tool call"""
            try:
                if tool_call.name not in self.tools:
                    raise HTTPException(status_code=404, detail=f"Tool '{tool_call.name}' not found")
                
                # Execute the tool
                result = await self.tools[tool_call.name](**tool_call.arguments)
                
                return MCPToolResult(
                    content=[{
                        "type": "text",
                        "text": str(result)
                    }],
                    isError=False
                )
                
            except Exception as e:
                logger.error(f"Error executing tool {tool_call.name}: {e}")
                return MCPToolResult(
                    content=[{
                        "type": "text",
                        "text": f"Error executing tool: {str(e)}"
                    }],
                    isError=True
                )
        
        @self.app.websocket("/mcp/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for MCP communication"""
            await websocket.accept()
            self.active_connections.append(websocket)
            
            try:
                while True:
                    # Receive MCP request
                    data = await websocket.receive_text()
                    request = json.loads(data)
                    
                    # Process MCP request
                    response = await self._process_mcp_request(request)
                    
                    # Send response
                    await websocket.send_text(json.dumps(response.dict()))
                    
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                if websocket in self.active_connections:
                    self.active_connections.remove(websocket)
    
    async def _process_mcp_request(self, request: Dict[str, Any]) -> MCPResponse:
        """Process MCP request and return response"""
        try:
            mcp_request = MCPRequest(**request)
            
            if mcp_request.method == "tools/list":
                return await self._handle_tools_list(mcp_request)
            elif mcp_request.method == "tools/call":
                return await self._handle_tools_call(mcp_request)
            elif mcp_request.method == "tools/get":
                return await self._handle_tools_get(mcp_request)
            else:
                return MCPResponse(
                    id=mcp_request.id,
                    error={
                        "code": -32601,
                        "message": f"Method '{mcp_request.method}' not found"
                    }
                )
                
        except Exception as e:
            logger.error(f"Error processing MCP request: {e}")
            return MCPResponse(
                id=request.get("id", "unknown"),
                error={
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            )
    
    async def _handle_tools_list(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/list MCP method"""
        tools = []
        for name, func in self.tools.items():
            tool_def = tool_registry.get_tool(name)
            if tool_def:
                tools.append({
                    "name": name,
                    "description": tool_def.definition.description,
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            param.name: {
                                "type": param.type,
                                "description": param.description,
                                "required": param.required
                            }
                            for param in tool_def.definition.parameters
                        },
                        "required": [
                            param.name for param in tool_def.definition.parameters 
                            if param.required
                        ]
                    }
                })
        
        return MCPResponse(
            id=request.id,
            result={"tools": tools}
        )
    
    async def _handle_tools_call(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/call MCP method"""
        try:
            params = request.params or {}
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if not tool_name:
                return MCPResponse(
                    id=request.id,
                    error={
                        "code": -32602,
                        "message": "Missing tool name"
                    }
                )
            
            if tool_name not in self.tools:
                return MCPResponse(
                    id=request.id,
                    error={
                        "code": -32601,
                        "message": f"Tool '{tool_name}' not found"
                    }
                )
            
            # Execute the tool
            result = await self.tools[tool_name](**arguments)
            
            return MCPResponse(
                id=request.id,
                result={
                    "content": [{
                        "type": "text",
                        "text": str(result)
                    }],
                    "isError": False
                }
            )
            
        except Exception as e:
            logger.error(f"Error in tools/call: {e}")
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32603,
                    "message": f"Tool execution error: {str(e)}"
                }
            )
    
    async def _handle_tools_get(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/get MCP method"""
        try:
            params = request.params or {}
            tool_name = params.get("name")
            
            if not tool_name:
                return MCPResponse(
                    id=request.id,
                    error={
                        "code": -32602,
                        "message": "Missing tool name"
                    }
                )
            
            tool_def = tool_registry.get_tool(tool_name)
            if not tool_def:
                return MCPResponse(
                    id=request.id,
                    error={
                        "code": -32601,
                        "message": f"Tool '{tool_name}' not found"
                    }
                )
            
            return MCPResponse(
                id=request.id,
                result={
                    "name": tool_name,
                    "description": tool_def.definition.description,
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            param.name: {
                                "type": param.type,
                                "description": param.description,
                                "required": param.required
                            }
                            for param in tool_def.definition.parameters
                        },
                        "required": [
                            param.name for param in tool_def.definition.parameters 
                            if param.required
                        ]
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Error in tools/get: {e}")
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32603,
                    "message": f"Tool get error: {str(e)}"
                }
            )
    
    # Tool implementations
    async def _schedule_appointment(self, doctor_name: str, patient_name: str, 
                                  patient_email: str, appointment_date: str, 
                                  appointment_time: str, symptoms: str = None, 
                                  duration: int = 30) -> Dict[str, Any]:
        """Schedule appointment with real calendar and email integration"""
        try:
            # Create calendar event
            calendar_data = {
                'doctor_name': doctor_name,
                'patient_name': patient_name,
                'patient_email': patient_email,
                'appointment_date': appointment_date,
                'appointment_time': appointment_time,
                'duration': duration,
                'symptoms': symptoms or 'General consultation'
            }
            
            calendar_result = await calendar_service.create_appointment_event(calendar_data)
            
            if calendar_result.get('error'):
                return {
                    "success": False,
                    "error": f"Calendar integration failed: {calendar_result['error']}"
                }
            
            # Send confirmation email
            email_data = {
                'to_email': patient_email,
                'patient_name': patient_name,
                'doctor_name': doctor_name,
                'appointment_date': appointment_date,
                'appointment_time': appointment_time,
                'appointment_id': calendar_result.get('event_id', 'unknown')
            }
            
            email_result = await gmail_service.send_appointment_confirmation(email_data)
            
            return {
                "success": True,
                "appointment_id": calendar_result.get('event_id'),
                "calendar_event_created": not calendar_result.get('error'),
                "email_sent": not email_result.get('error'),
                "message": "Appointment scheduled successfully"
            }
            
        except Exception as e:
            logger.error(f"Error scheduling appointment: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _check_doctor_availability(self, doctor_name: str, date: str, 
                                       time_preference: str = "any") -> Dict[str, Any]:
        """Check doctor availability using real calendar data"""
        try:
            availability = await calendar_service.check_doctor_availability(
                doctor_name, date, time_preference
            )
            
            if availability.get('error'):
                return {
                    "success": False,
                    "error": availability['error']
                }
            
            return {
                "success": True,
                "doctor_name": doctor_name,
                "date": date,
                "available_slots": availability.get('available_slots', []),
                "total_available": availability.get('total_available', 0)
            }
            
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _list_doctors(self, specialty: str = None, location: str = None) -> Dict[str, Any]:
        """List available doctors"""
        try:
            # Mock data - in real implementation would query database
            doctors = [
                {"name": "Dr. Smith", "specialty": "Cardiology", "location": "Main Office"},
                {"name": "Dr. Johnson", "specialty": "Dermatology", "location": "Main Office"},
                {"name": "Dr. Williams", "specialty": "Pediatrics", "location": "Downtown Office"}
            ]
            
            # Apply filters
            if specialty:
                doctors = [d for d in doctors if d["specialty"].lower() == specialty.lower()]
            if location:
                doctors = [d for d in doctors if d["location"].lower() == location.lower()]
            
            return {
                "success": True,
                "doctors": doctors,
                "count": len(doctors)
            }
            
        except Exception as e:
            logger.error(f"Error listing doctors: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_calendar_event(self, summary: str, start_time: str, end_time: str,
                                   description: str = None, attendees: List[str] = None) -> Dict[str, Any]:
        """Create Google Calendar event"""
        try:
            event_data = {
                'summary': summary,
                'start_time': start_time,
                'end_time': end_time,
                'description': description,
                'attendees': attendees or []
            }
            
            result = await calendar_service.create_appointment_event(event_data)
            
            if result.get('error'):
                return {
                    "success": False,
                    "error": result['error']
                }
            
            return {
                "success": True,
                "event_id": result.get('event_id'),
                "calendar_link": result.get('html_link')
            }
            
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _update_calendar_event(self, event_id: str, **updates) -> Dict[str, Any]:
        """Update Google Calendar event"""
        try:
            result = await calendar_service.update_appointment_event(event_id, updates)
            
            if result.get('error'):
                return {
                    "success": False,
                    "error": result['error']
                }
            
            return {
                "success": True,
                "event_id": event_id,
                "updated": True
            }
            
        except Exception as e:
            logger.error(f"Error updating calendar event: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _cancel_calendar_event(self, event_id: str, reason: str = "Cancelled") -> Dict[str, Any]:
        """Cancel Google Calendar event"""
        try:
            result = await calendar_service.cancel_appointment_event(event_id, reason)
            
            if result.get('error'):
                return {
                    "success": False,
                    "error": result['error']
                }
            
            return {
                "success": True,
                "event_id": event_id,
                "cancelled": True
            }
            
        except Exception as e:
            logger.error(f"Error cancelling calendar event: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _send_appointment_confirmation(self, to_email: str, patient_name: str,
                                           doctor_name: str, appointment_date: str,
                                           appointment_time: str, appointment_id: str) -> Dict[str, Any]:
        """Send appointment confirmation via Gmail API"""
        try:
            email_data = {
                'to_email': to_email,
                'patient_name': patient_name,
                'doctor_name': doctor_name,
                'appointment_date': appointment_date,
                'appointment_time': appointment_time,
                'appointment_id': appointment_id
            }
            
            result = await gmail_service.send_appointment_confirmation(email_data)
            
            if result.get('error'):
                return {
                    "success": False,
                    "error": result['error']
                }
            
            return {
                "success": True,
                "email_sent": True,
                "message_id": result.get('message_id')
            }
            
        except Exception as e:
            logger.error(f"Error sending confirmation email: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _send_appointment_reminder(self, to_email: str, patient_name: str,
                                        doctor_name: str, appointment_date: str,
                                        appointment_time: str) -> Dict[str, Any]:
        """Send appointment reminder via Gmail API"""
        try:
            email_data = {
                'to_email': to_email,
                'patient_name': patient_name,
                'doctor_name': doctor_name,
                'appointment_date': appointment_date,
                'appointment_time': appointment_time,
                'appointment_id': 'reminder'
            }
            
            result = await gmail_service.send_appointment_reminder(email_data)
            
            if result.get('error'):
                return {
                    "success": False,
                    "error": result['error']
                }
            
            return {
                "success": True,
                "reminder_sent": True,
                "message_id": result.get('message_id')
            }
            
        except Exception as e:
            logger.error(f"Error sending reminder email: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _send_cancellation_notification(self, to_email: str, patient_name: str,
                                             doctor_name: str, appointment_date: str,
                                             appointment_time: str, reason: str = "Cancelled") -> Dict[str, Any]:
        """Send cancellation notification via Gmail API"""
        try:
            email_data = {
                'to_email': to_email,
                'patient_name': patient_name,
                'doctor_name': doctor_name,
                'appointment_date': appointment_date,
                'appointment_time': appointment_time,
                'appointment_id': 'cancelled'
            }
            
            result = await gmail_service.send_cancellation_notification(email_data)
            
            if result.get('error'):
                return {
                    "success": False,
                    "error": result['error']
                }
            
            return {
                "success": True,
                "cancellation_notification_sent": True,
                "message_id": result.get('message_id')
            }
            
        except Exception as e:
            logger.error(f"Error sending cancellation notification: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_appointment_statistics(self, doctor_name: str, period: str,
                                         start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get appointment statistics from calendar data"""
        try:
            result = await calendar_service.get_appointment_events(
                start_date or "2024-01-01", 
                end_date or "2024-12-31", 
                doctor_name
            )
            
            return {
                "success": True,
                "doctor_name": doctor_name,
                "period": period,
                "total_appointments": len(result),
                "appointments": result
            }
            
        except Exception as e:
            logger.error(f"Error getting appointment statistics: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _search_patients_by_symptoms(self, symptoms: str, date_from: str = None,
                                          date_to: str = None, doctor_name: str = None) -> Dict[str, Any]:
        """Search patients by symptoms using calendar data"""
        try:
            events = await calendar_service.get_appointment_events(
                date_from or "2024-01-01",
                date_to or "2024-12-31",
                doctor_name
            )
            
            # Filter by symptoms (simplified search)
            matching_patients = []
            for event in events:
                if symptoms.lower() in event.get('description', '').lower():
                    matching_patients.append(event)
            
            return {
                "success": True,
                "symptoms": symptoms,
                "patients_found": len(matching_patients),
                "patients": matching_patients
            }
            
        except Exception as e:
            logger.error(f"Error searching patients: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Create MCP server instance
mcp_server = MCPServer()
app = mcp_server.app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)