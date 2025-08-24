"""
FastAPI MCP Server Implementation
Integrates with existing backend services and provides MCP-compliant tool discovery
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union
import json
import logging
import asyncio
from datetime import datetime, date

# Import existing services
from config import settings
from mcp_server import MCPServer, MCPTool, MCPToolType
from llm_agent import DoctorAppointmentAgent
from google_calendar_service import calendar_service
from email_service import email_service
from notification_service import notification_manager

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="MedAI MCP Server",
    version="1.0.0",
    description="Model Context Protocol server for MedAI doctor appointment system"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
mcp_server = MCPServer()
llm_agent = DoctorAppointmentAgent()

# Pydantic models for MCP requests
class MCPToolCall(BaseModel):
    """MCP tool call request"""
    tool_name: str = Field(..., description="Name of the tool to call")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")

class MCPToolDiscoveryRequest(BaseModel):
    """MCP tool discovery request"""
    include_schemas: bool = Field(default=False, description="Include tool schemas in response")

class MCPToolExecutionRequest(BaseModel):
    """MCP tool execution request"""
    tool_calls: List[MCPToolCall] = Field(..., description="List of tools to execute")
    session_id: Optional[str] = Field(None, description="Session ID for context")

class MCPToolExecutionResponse(BaseModel):
    """MCP tool execution response"""
    results: List[Dict[str, Any]] = Field(..., description="Results from tool executions")
    session_id: Optional[str] = Field(None, description="Session ID")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")

# MCP Tool Discovery Endpoint
@app.get("/mcp/tools", response_model=Dict[str, Any])
async def discover_tools(include_schemas: bool = False):
    """
    Discover all available MCP tools
    
    This endpoint provides tool discovery following the MCP standard.
    Returns a list of all available tools with their descriptions and schemas.
    """
    try:
        tools_list = []
        for name, tool in mcp_server.tools.items():
            tool_info = {
                "name": name,
                "description": tool.description,
                "type": tool.type.value
            }
            
            if include_schemas:
                tool_info["inputSchema"] = tool.inputSchema
            
            tools_list.append(tool_info)
        
        return {
            "tools": tools_list,
            "count": len(tools_list),
            "server_info": {
                "name": "MedAI MCP Server",
                "version": "1.0.0",
                "description": "MCP server for doctor appointment management"
            }
        }
    
    except Exception as e:
        logger.error(f"Error in tool discovery: {e}")
        raise HTTPException(status_code=500, detail=f"Tool discovery failed: {str(e)}")

# MCP Tool Schema Endpoint
@app.get("/mcp/tools/{tool_name}/schema", response_model=Dict[str, Any])
async def get_tool_schema(tool_name: str):
    """
    Get detailed schema for a specific MCP tool
    
    Returns the complete input schema and metadata for the specified tool.
    """
    try:
        if tool_name not in mcp_server.tools:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        tool = mcp_server.tools[tool_name]
        return {
            "name": tool.name,
            "description": tool.description,
            "inputSchema": tool.inputSchema,
            "type": tool.type.value,
            "examples": _get_tool_examples(tool_name)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tool schema: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tool schema: {str(e)}")

# MCP Tool Execution Endpoint
@app.post("/mcp/tools/execute", response_model=MCPToolExecutionResponse)
async def execute_tools(request: MCPToolExecutionRequest):
    """
    Execute multiple MCP tools in sequence
    
    This endpoint allows batch execution of multiple tools and maintains
    conversation context through session management.
    """
    try:
        results = []
        errors = []
        
        for tool_call in request.tool_calls:
            try:
                if tool_call.tool_name in mcp_server.tools:
                    tool = mcp_server.tools[tool_call.tool_name]
                    
                    # Execute the tool
                    if asyncio.iscoroutinefunction(tool.handler):
                        result = await tool.handler(tool_call.parameters)
                    else:
                        result = tool.handler(tool_call.parameters)
                    
                    results.append({
                        "tool_name": tool_call.tool_name,
                        "success": True,
                        "result": result,
                        "execution_time": datetime.now().isoformat()
                    })
                
                else:
                    errors.append(f"Tool '{tool_call.tool_name}' not found")
                    results.append({
                        "tool_name": tool_call.tool_name,
                        "success": False,
                        "error": f"Tool '{tool_call.tool_name}' not found"
                    })
            
            except Exception as e:
                error_msg = f"Error executing tool '{tool_call.tool_name}': {str(e)}"
                errors.append(error_msg)
                results.append({
                    "tool_name": tool_call.tool_name,
                    "success": False,
                    "error": error_msg
                })
        
        return MCPToolExecutionResponse(
            results=results,
            session_id=request.session_id,
            errors=errors
        )
    
    except Exception as e:
        logger.error(f"Error in tool execution: {e}")
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

# MCP WebSocket Endpoint for Real-time Communication
@app.websocket("/mcp/ws")
async def mcp_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time MCP communication
    
    Provides persistent connection for tool discovery and execution
    with real-time updates and notifications.
    """
    await mcp_server.connect(websocket)

# Enhanced Tool Registration with Real Services
def _register_enhanced_tools():
    """Register enhanced tools that integrate with real backend services"""
    
    # Enhanced appointment scheduling with Google Calendar integration
    async def enhanced_schedule_appointment(params: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule appointment with Google Calendar integration"""
        try:
            # Extract parameters
            doctor_name = params.get("doctor_name")
            patient_name = params.get("patient_name")
            patient_email = params.get("patient_email")
            appointment_date = params.get("appointment_date")
            appointment_time = params.get("appointment_time")
            symptoms = params.get("symptoms", "")
            
            # Create appointment in the system
            appointment_data = {
                "doctor_name": doctor_name,
                "patient_name": patient_name,
                "patient_email": patient_email,
                "appointment_date": appointment_date,
                "appointment_time": appointment_time,
                "symptoms": symptoms
            }
            
            # TODO: Integrate with actual database
            appointment_id = f"apt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create Google Calendar event
            try:
                event_details = {
                    "summary": f"Appointment: {patient_name} with {doctor_name}",
                    "description": f"Patient: {patient_name}\nSymptoms: {symptoms}\nEmail: {patient_email}",
                    "start_time": f"{appointment_date}T{appointment_time}:00",
                    "end_time": f"{appointment_date}T{appointment_time}:00",
                    "attendees": [patient_email]
                }
                
                # Create actual Google Calendar event
                if calendar_service.is_available():
                    calendar_event = await calendar_service.create_appointment_event(
                        doctor_name=doctor_name,
                        patient_name=patient_name,
                        patient_email=patient_email,
                        appointment_date=appointment_date,
                        appointment_time=appointment_time,
                        symptoms=symptoms
                    )
                else:
                    calendar_event = {"id": "mock_event_id", "status": "calendar_unavailable"}
                
            except Exception as e:
                logger.warning(f"Google Calendar integration failed: {e}")
                calendar_event = {"error": "Calendar integration unavailable"}
            
            # Send confirmation email
            try:
                email_content = {
                    "to": patient_email,
                    "subject": "Appointment Confirmation",
                    "template": "appointment_confirmation",
                    "data": {
                        "patient_name": patient_name,
                        "doctor_name": doctor_name,
                        "date": appointment_date,
                        "time": appointment_time,
                        "appointment_id": appointment_id
                    }
                }
                
                # Send actual confirmation email
                if email_service.is_available():
                    email_result = await email_service.send_appointment_confirmation(
                        patient_email=patient_email,
                        patient_name=patient_name,
                        doctor_name=doctor_name,
                        appointment_date=appointment_date,
                        appointment_time=appointment_time,
                        symptoms=symptoms
                    )
                else:
                    email_result = {"status": "email_unavailable", "message": "Email service not configured"}
                
            except Exception as e:
                logger.warning(f"Email service failed: {e}")
                email_result = {"error": "Email service unavailable"}
            
            # Send notification
            try:
                await notification_manager.send_appointment_notification(
                    doctor_name=doctor_name,
                    patient_name=patient_name,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time
                )
            except Exception as e:
                logger.warning(f"Notification service failed: {e}")
            
            return {
                "appointment_id": appointment_id,
                "status": "scheduled",
                "calendar_event": calendar_event,
                "email_sent": email_result,
                "message": "Appointment scheduled successfully with all integrations"
            }
        
        except Exception as e:
            logger.error(f"Error in enhanced appointment scheduling: {e}")
            return {
                "error": f"Appointment scheduling failed: {str(e)}",
                "status": "failed"
            }
    
    # Register the enhanced tool
    mcp_server.register_tool(
        name="appointments/schedule_enhanced",
        description="Schedule appointment with full integration (Google Calendar, Email, Notifications)",
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
        handler=enhanced_schedule_appointment,
        type=MCPToolType.FUNCTION
    )

# Initialize enhanced tools
_register_enhanced_tools()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "mcp_server": "running",
            "llm_agent": "running",
            "tools_count": len(mcp_server.tools)
        }
    }

# MCP Server Info Endpoint
@app.get("/mcp/info")
async def get_mcp_info():
    """Get MCP server information and capabilities"""
    return {
        "server": {
            "name": "MedAI MCP Server",
            "version": "1.0.0",
            "description": "Model Context Protocol server for doctor appointment management"
        },
        "capabilities": {
            "tool_discovery": True,
            "tool_execution": True,
            "websocket_support": True,
            "batch_execution": True
        },
        "tools": {
            "total": len(mcp_server.tools),
            "categories": {
                "appointments": len([t for t in mcp_server.tools.keys() if t.startswith("appointments/")]),
                "doctors": len([t for t in mcp_server.tools.keys() if t.startswith("doctors/")]),
                "analytics": len([t for t in mcp_server.tools.keys() if t.startswith("analytics/")]),
                "search": len([t for t in mcp_server.tools.keys() if t.startswith("search/")])
            }
        },
        "endpoints": {
            "tool_discovery": "/mcp/tools",
            "tool_schema": "/mcp/tools/{tool_name}/schema",
            "tool_execution": "/mcp/tools/execute",
            "websocket": "/mcp/ws",
            "health": "/health"
        }
    }

def _get_tool_examples(tool_name: str) -> List[Dict[str, Any]]:
    """Get example usage for a specific tool"""
    examples = {
        "appointments/schedule": [
            {
                "description": "Schedule a morning appointment",
                "parameters": {
                    "doctor_name": "Dr. Smith",
                    "patient_name": "John Doe",
                    "patient_email": "john.doe@email.com",
                    "appointment_date": "2024-01-20",
                    "appointment_time": "09:00",
                    "symptoms": "Headache and fever"
                }
            }
        ],
        "doctors/list": [
            {
                "description": "Find cardiologists",
                "parameters": {
                    "specialty": "Cardiology"
                }
            }
        ],
        "analytics/appointment_stats": [
            {
                "description": "Get monthly statistics",
                "parameters": {
                    "doctor_name": "Dr. Johnson",
                    "period": "month",
                    "date": "2024-01-01"
                }
            }
        ]
    }
    
    return examples.get(tool_name, [])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)