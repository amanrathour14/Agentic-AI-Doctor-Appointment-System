"""
MCP (Model Context Protocol) Server Implementation
Follows the MCP standard for tool discovery and execution
"""
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime, date, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class MCPMessageType(str, Enum):
    """MCP message types"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"

class MCPToolType(str, Enum):
    """MCP tool types"""
    FUNCTION = "function"
    TEXT = "text"
    IMAGE = "image"
    EMBEDDING = "embedding"

@dataclass
class MCPTool:
    """MCP tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]
    handler: Callable
    type: MCPToolType = MCPToolType.FUNCTION

class MCPRequest(BaseModel):
    """MCP request model"""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: str
    params: Optional[Dict[str, Any]] = None

class MCPResponse(BaseModel):
    """MCP response model"""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

class MCPError(BaseModel):
    """MCP error model"""
    code: int
    message: str
    data: Optional[Any] = None

class MCPServer:
    """MCP Server implementation"""
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.connections: List[WebSocket] = []
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default MCP tools"""
        # Tool discovery
        self.register_tool(
            name="tools/list",
            description="List all available tools",
            inputSchema={"type": "object", "properties": {}},
            handler=self._list_tools,
            type=MCPToolType.FUNCTION
        )
        
        # Tool schema
        self.register_tool(
            name="tools/get",
            description="Get tool schema by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Tool name"}
                },
                "required": ["name"]
            },
            handler=self._get_tool_schema,
            type=MCPToolType.FUNCTION
        )
        
        # Appointment tools
        self.register_tool(
            name="appointments/schedule",
            description="Schedule a new appointment",
            inputSchema={
                "type": "object",
                "properties": {
                    "doctor_name": {"type": "string", "description": "Doctor's name"},
                    "patient_name": {"type": "string", "description": "Patient's name"},
                    "patient_email": {"type": "string", "description": "Patient's email"},
                    "appointment_date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "appointment_time": {"type": "string", "description": "Time in HH:MM format"},
                    "symptoms": {"type": "string", "description": "Patient symptoms"}
                },
                "required": ["doctor_name", "patient_name", "patient_email", "appointment_date", "appointment_time"]
            },
            handler=self._schedule_appointment,
            type=MCPToolType.FUNCTION
        )
        
        self.register_tool(
            name="appointments/check_availability",
            description="Check doctor availability for a specific date and time",
            inputSchema={
                "type": "object",
                "properties": {
                    "doctor_name": {"type": "string", "description": "Doctor's name"},
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "time_preference": {"type": "string", "description": "Time preference: morning, afternoon, evening, or specific time"}
                },
                "required": ["doctor_name", "date"]
            },
            handler=self._check_availability,
            type=MCPToolType.FUNCTION
        )
        
        self.register_tool(
            name="appointments/list",
            description="List appointments for a doctor or patient",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_type": {"type": "string", "enum": ["doctor", "patient"], "description": "Type of entity"},
                    "entity_name": {"type": "string", "description": "Name of doctor or patient"},
                    "date_from": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                    "date_to": {"type": "string", "description": "End date in YYYY-MM-DD format"}
                },
                "required": ["entity_type", "entity_name"]
            },
            handler=self._list_appointments,
            type=MCPToolType.FUNCTION
        )
        
        # Doctor tools
        self.register_tool(
            name="doctors/list",
            description="List all available doctors",
            inputSchema={
                "type": "object",
                "properties": {
                    "specialty": {"type": "string", "description": "Filter by medical specialty"},
                    "available_date": {"type": "string", "description": "Filter by available date"}
                }
            },
            handler=self._list_doctors,
            type=MCPToolType.FUNCTION
        )
        
        self.register_tool(
            name="doctors/get_schedule",
            description="Get doctor's schedule for a specific date",
            inputSchema={
                "type": "object",
                "properties": {
                    "doctor_name": {"type": "string", "description": "Doctor's name"},
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format"}
                },
                "required": ["doctor_name", "date"]
            },
            handler=self._get_doctor_schedule,
            type=MCPToolType.FUNCTION
        )
        
        # Analytics tools
        self.register_tool(
            name="analytics/appointment_stats",
            description="Get appointment statistics for a doctor",
            inputSchema={
                "type": "object",
                "properties": {
                    "doctor_name": {"type": "string", "description": "Doctor's name"},
                    "period": {"type": "string", "enum": ["day", "week", "month", "year"], "description": "Time period"},
                    "date": {"type": "string", "description": "Reference date in YYYY-MM-DD format"}
                },
                "required": ["doctor_name", "period"]
            },
            handler=self._get_appointment_stats,
            type=MCPToolType.FUNCTION
        )
        
        # Search tools
        self.register_tool(
            name="search/patients_by_symptoms",
            description="Search patients by symptoms",
            inputSchema={
                "type": "object",
                "properties": {
                    "symptoms": {"type": "string", "description": "Symptoms to search for"},
                    "date_from": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                    "date_to": {"type": "string", "description": "End date in YYYY-MM-DD format"}
                },
                "required": ["symptoms"]
            },
            handler=self._search_patients_by_symptoms,
            type=MCPToolType.FUNCTION
        )
    
    def register_tool(self, name: str, description: str, inputSchema: Dict[str, Any], 
                     handler: Callable, type: MCPToolType = MCPToolType.FUNCTION):
        """Register a new MCP tool"""
        tool = MCPTool(
            name=name,
            description=description,
            inputSchema=inputSchema,
            handler=handler,
            type=type
        )
        self.tools[name] = tool
        logger.info(f"Registered MCP tool: {name}")
    
    async def _list_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all available tools"""
        tools_list = []
        for name, tool in self.tools.items():
            tools_list.append({
                "name": name,
                "description": tool.description,
                "inputSchema": tool.inputSchema,
                "type": tool.type.value
            })
        
        return {
            "tools": tools_list,
            "count": len(tools_list)
        }
    
    async def _get_tool_schema(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get tool schema by name"""
        tool_name = params.get("name")
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        tool = self.tools[tool_name]
        return {
            "name": tool.name,
            "description": tool.description,
            "inputSchema": tool.inputSchema,
            "type": tool.type.value
        }
    
    async def _schedule_appointment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a new appointment"""
        # This would integrate with the actual appointment service
        appointment_id = str(uuid.uuid4())
        
        return {
            "appointment_id": appointment_id,
            "status": "scheduled",
            "details": params,
            "message": "Appointment scheduled successfully"
        }
    
    async def _check_availability(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check doctor availability"""
        doctor_name = params.get("doctor_name")
        date_str = params.get("date")
        time_preference = params.get("time_preference", "any")
        
        # Mock availability data - in real implementation, this would query the database
        available_slots = [
            "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
            "14:00", "14:30", "15:00", "15:30", "16:00", "16:30"
        ]
        
        return {
            "doctor_name": doctor_name,
            "date": date_str,
            "available_slots": available_slots,
            "message": f"Found {len(available_slots)} available slots for {doctor_name} on {date_str}"
        }
    
    async def _list_appointments(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List appointments"""
        entity_type = params.get("entity_type")
        entity_name = params.get("entity_name")
        
        # Mock appointments - in real implementation, this would query the database
        appointments = [
            {
                "id": "apt_001",
                "doctor": "Dr. Smith",
                "patient": "John Doe",
                "date": "2024-01-15",
                "time": "10:00",
                "status": "confirmed"
            }
        ]
        
        return {
            "entity_type": entity_type,
            "entity_name": entity_name,
            "appointments": appointments,
            "count": len(appointments)
        }
    
    async def _list_doctors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available doctors"""
        specialty = params.get("specialty")
        
        # Mock doctors data - in real implementation, this would query the database
        doctors = [
            {"name": "Dr. Smith", "specialty": "Cardiology", "available": True},
            {"name": "Dr. Johnson", "specialty": "Dermatology", "available": True},
            {"name": "Dr. Williams", "specialty": "Pediatrics", "available": False}
        ]
        
        if specialty:
            doctors = [d for d in doctors if d["specialty"].lower() == specialty.lower()]
        
        return {
            "doctors": doctors,
            "count": len(doctors),
            "specialty_filter": specialty
        }
    
    async def _get_doctor_schedule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get doctor's schedule"""
        doctor_name = params.get("doctor_name")
        date_str = params.get("date")
        
        # Mock schedule - in real implementation, this would query the database
        schedule = {
            "doctor_name": doctor_name,
            "date": date_str,
            "slots": [
                {"time": "09:00", "status": "available"},
                {"time": "09:30", "status": "booked"},
                {"time": "10:00", "status": "available"}
            ]
        }
        
        return schedule
    
    async def _get_appointment_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get appointment statistics"""
        doctor_name = params.get("doctor_name")
        period = params.get("period")
        
        # Mock stats - in real implementation, this would query the database
        stats = {
            "doctor_name": doctor_name,
            "period": period,
            "total_appointments": 45,
            "completed": 42,
            "cancelled": 2,
            "no_show": 1,
            "completion_rate": 93.3
        }
        
        return stats
    
    async def _search_patients_by_symptoms(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search patients by symptoms"""
        symptoms = params.get("symptoms")
        
        # Mock search results - in real implementation, this would query the database
        patients = [
            {
                "name": "Jane Doe",
                "symptoms": "fever, cough",
                "last_visit": "2024-01-10",
                "doctor": "Dr. Smith"
            }
        ]
        
        return {
            "symptoms": symptoms,
            "patients": patients,
            "count": len(patients)
        }
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP message"""
        try:
            if message.get("method") == "tools/list":
                result = await self._list_tools(message.get("params", {}))
                return {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": result
                }
            
            elif message.get("method") == "tools/get":
                result = await self._get_tool_schema(message.get("params", {}))
                return {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": result
                }
            
            elif message.get("method") in self.tools:
                tool = self.tools[message.get("method")]
                params = message.get("params", {})
                
                # Execute the tool
                if asyncio.iscoroutinefunction(tool.handler):
                    result = await tool.handler(params)
                else:
                    result = tool.handler(params)
                
                return {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": result
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Method '{message.get('method')}' not found"
                    }
                }
        
        except Exception as e:
            logger.error(f"Error handling MCP message: {e}")
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def connect(self, websocket: WebSocket):
        """Handle new WebSocket connection"""
        await websocket.accept()
        self.connections.append(websocket)
        logger.info(f"New MCP connection established. Total connections: {len(self.connections)}")
        
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle the message
                response = await self.handle_message(message)
                
                # Send response back
                await websocket.send_text(json.dumps(response))
        
        except WebSocketDisconnect:
            self.connections.remove(websocket)
            logger.info(f"MCP connection closed. Total connections: {len(self.connections)}")
        
        except Exception as e:
            logger.error(f"Error in MCP connection: {e}")
            if websocket in self.connections:
                self.connections.remove(websocket)

# Global MCP server instance
mcp_server = MCPServer()