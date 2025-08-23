"""
Main FastAPI application for MedAI Doctor Appointment System
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
import asyncio
from datetime import datetime, date

# Import services
from llm_agent import LLMAgent
from email_service import gmail_service
from google_calendar_service import calendar_service
from notification_service import NotificationService
from session_manager import SessionManager
from tool_registry import tool_registry
from tool_handlers import tool_handlers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MedAI Doctor Appointment System",
    description="AI-powered doctor appointment scheduling system with Gmail and Google Calendar integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
llm_agent = LLMAgent()
notification_service = NotificationService()
session_manager = SessionManager()

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_role: str = "patient"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: datetime
    tool_calls: Optional[List[Dict[str, Any]]] = None

class AppointmentRequest(BaseModel):
    doctor_name: str
    patient_name: str
    patient_email: str
    appointment_date: str
    appointment_time: str
    symptoms: Optional[str] = None
    duration: int = 30

class DoctorAvailabilityRequest(BaseModel):
    doctor_name: str
    date: str
    time_preference: str = "any"

class ToolExecutionRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "gmail": gmail_service.get_authentication_status(),
            "calendar": calendar_service.get_authentication_status(),
            "llm_agent": "active",
            "notification_service": "active",
            "session_manager": "active"
        }
    }

# Tool discovery endpoint - OpenAPI schema
@app.get("/tools/openapi", response_class=JSONResponse)
async def get_tools_openapi_schema():
    """Get OpenAPI schema for all available tools"""
    try:
        schema = tool_registry.get_openapi_schema()
        return JSONResponse(content=schema)
    except Exception as e:
        logger.error(f"Error generating OpenAPI schema: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating schema: {str(e)}")

# Tool list endpoint
@app.get("/tools")
async def list_tools(type_filter: Optional[str] = None, tag_filter: Optional[str] = None):
    """List all available tools with optional filtering"""
    try:
        from tool_registry import ToolType
        
        type_enum = None
        if type_filter:
            try:
                type_enum = ToolType(type_filter)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid tool type: {type_filter}")
        
        tools = tool_registry.list_tools(type_enum, tag_filter)
        return {
            "tools": [tool.dict() for tool in tools],
            "count": len(tools),
            "filters": {
                "type": type_filter,
                "tag": tag_filter
            }
        }
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing tools: {str(e)}")

# Tool execution endpoint
@app.post("/tools/execute")
async def execute_tool(request: ToolExecutionRequest):
    """Execute a specific tool with given parameters"""
    try:
        tool = tool_registry.get_tool(request.tool_name)
        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool '{request.tool_name}' not found")
        
        if not tool.handler:
            raise HTTPException(status_code=500, detail=f"Tool '{request.tool_name}' has no handler")
        
        # Execute the tool
        result = await tool.execute(request.parameters)
        
        return {
            "tool_name": request.tool_name,
            "parameters": request.parameters,
            "result": result,
            "executed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error executing tool {request.tool_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error executing tool: {str(e)}")

# Chat endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with tool integration"""
    try:
        # Validate session
        if not session_manager.validate_session(request.session_id):
            raise HTTPException(status_code=401, detail="Invalid session")
        
        # Process message with LLM agent
        response = await llm_agent.process_message(
            request.message,
            request.session_id,
            request.user_role
        )
        
        # Check if response contains tool calls
        tool_calls = []
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                try:
                    # Execute the tool
                    tool = tool_registry.get_tool(tool_call.function_name)
                    if tool and tool.handler:
                        result = await tool.execute(tool_call.arguments)
                        tool_calls.append({
                            "tool_name": tool_call.function_name,
                            "arguments": tool_call.arguments,
                            "result": result,
                            "success": True
                        })
                    else:
                        tool_calls.append({
                            "tool_name": tool_call.function_name,
                            "arguments": tool_call.arguments,
                            "result": {"error": "Tool not found or no handler"},
                            "success": False
                        })
                except Exception as e:
                    logger.error(f"Error executing tool {tool_call.function_name}: {e}")
                    tool_calls.append({
                        "tool_name": tool_call.function_name,
                        "arguments": tool_call.arguments,
                        "result": {"error": str(e)},
                        "success": False
                    })
        
        return ChatResponse(
            response=response.content,
            session_id=request.session_id,
            timestamp=datetime.now(),
            tool_calls=tool_calls if tool_calls else None
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

# Session management endpoints
@app.post("/api/sessions")
async def create_session(user_role: str = "patient"):
    """Create a new chat session"""
    try:
        session_id = session_manager.create_session(user_role)
        return {"session_id": session_id, "user_role": user_role}
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting session: {str(e)}")

# Appointment management endpoints
@app.post("/api/appointments")
async def schedule_appointment(request: AppointmentRequest):
    """Schedule a new appointment using the tool handler"""
    try:
        # Use the tool handler to schedule appointment
        result = await tool_handlers.schedule_appointment(
            doctor_name=request.doctor_name,
            patient_name=request.patient_name,
            patient_email=request.patient_email,
            appointment_date=request.appointment_date,
            appointment_time=request.appointment_time,
            symptoms=request.symptoms,
            duration=request.duration
        )
        
        if result.get("status") == "failed":
            raise HTTPException(status_code=400, detail=result.get("message", "Appointment scheduling failed"))
        
        return result
        
    except Exception as e:
        logger.error(f"Error scheduling appointment: {e}")
        raise HTTPException(status_code=500, detail=f"Error scheduling appointment: {str(e)}")

@app.get("/api/doctors/availability")
async def check_doctor_availability(request: DoctorAvailabilityRequest):
    """Check doctor availability using the tool handler"""
    try:
        result = await tool_handlers.check_doctor_availability(
            doctor_name=request.doctor_name,
            date=request.date,
            time_preference=request.time_preference
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error checking doctor availability: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking availability: {str(e)}")

@app.get("/api/doctors")
async def list_doctors(specialty: Optional[str] = None, 
                      available_date: Optional[str] = None,
                      location: Optional[str] = None):
    """List available doctors using the tool handler"""
    try:
        result = await tool_handlers.list_doctors(
            specialty=specialty,
            available_date=available_date,
            location=location
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing doctors: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing doctors: {str(e)}")

# Analytics endpoints
@app.get("/api/analytics/appointments")
async def get_appointment_statistics(doctor_name: str, period: str,
                                   start_date: Optional[str] = None,
                                   end_date: Optional[str] = None):
    """Get appointment statistics using the tool handler"""
    try:
        result = await tool_handlers.get_appointment_statistics(
            doctor_name=doctor_name,
            period=period,
            start_date=start_date,
            end_date=end_date
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting appointment statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")

# Search endpoints
@app.get("/api/search/patients")
async def search_patients_by_symptoms(symptoms: str,
                                    date_from: Optional[str] = None,
                                    date_to: Optional[str] = None,
                                    doctor_name: Optional[str] = None):
    """Search patients by symptoms using the tool handler"""
    try:
        result = await tool_handlers.search_patients_by_symptoms(
            symptoms=symptoms,
            date_from=date_from,
            date_to=date_to,
            doctor_name=doctor_name
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error searching patients: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching patients: {str(e)}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "MedAI Doctor Appointment System",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "AI-powered chat interface",
            "Gmail API integration for email notifications",
            "Google Calendar API integration for appointment management",
            "OpenAPI-based tool discovery and execution",
            "Real-time doctor availability checking",
            "Appointment scheduling with calendar integration",
            "Patient search and analytics"
        ],
        "endpoints": {
            "health": "/health",
            "tools_schema": "/tools/openapi",
            "tools_list": "/tools",
            "tool_execution": "/tools/execute",
            "chat": "/api/chat",
            "sessions": "/api/sessions",
            "appointments": "/api/appointments",
            "doctor_availability": "/api/doctors/availability",
            "doctors": "/api/doctors",
            "analytics": "/api/analytics/appointments",
            "search": "/api/search/patients"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
