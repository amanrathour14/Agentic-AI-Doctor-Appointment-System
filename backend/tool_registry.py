"""
Tool Registry System using OpenAPI Schema
Provides tool discovery and registration for AI agents without MCP endpoints
"""
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime, date, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ToolType(str, Enum):
    """Tool types for different functionalities"""
    APPOINTMENT = "appointment"
    DOCTOR = "doctor"
    CALENDAR = "calendar"
    EMAIL = "email"
    ANALYTICS = "analytics"
    SEARCH = "search"
    NOTIFICATION = "notification"

class ToolParameter(BaseModel):
    """Parameter definition for a tool"""
    name: str
    type: str
    description: str
    required: bool = False
    enum: Optional[List[str]] = None
    default: Optional[Any] = None

class ToolDefinition(BaseModel):
    """Complete tool definition following OpenAPI schema"""
    name: str
    description: str
    type: ToolType
    parameters: List[ToolParameter]
    returns: Dict[str, Any]
    examples: List[Dict[str, Any]] = []
    tags: List[str] = []

class ToolRegistry:
    """Central tool registry for the system"""
    
    def __init__(self):
        self.tools: Dict[str, 'Tool'] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register all default tools with OpenAPI-compliant schemas"""
        
        # Appointment Tools
        self.register_tool(
            name="schedule_appointment",
            description="Schedule a new appointment with a doctor",
            type=ToolType.APPOINTMENT,
            parameters=[
                ToolParameter(name="doctor_name", type="string", description="Name of the doctor", required=True),
                ToolParameter(name="patient_name", type="string", description="Name of the patient", required=True),
                ToolParameter(name="patient_email", type="string", description="Patient's email address", required=True),
                ToolParameter(name="appointment_date", type="string", description="Date in YYYY-MM-DD format", required=True),
                ToolParameter(name="appointment_time", type="string", description="Time in HH:MM format", required=True),
                ToolParameter(name="symptoms", type="string", description="Patient symptoms", required=False),
                ToolParameter(name="duration", type="integer", description="Appointment duration in minutes", required=False, default=30)
            ],
            returns={
                "type": "object",
                "properties": {
                    "appointment_id": {"type": "string"},
                    "status": {"type": "string"},
                    "calendar_event_id": {"type": "string"},
                    "email_sent": {"type": "boolean"},
                    "message": {"type": "string"}
                }
            },
            examples=[
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
            tags=["appointments", "scheduling"]
        )
        
        self.register_tool(
            name="check_doctor_availability",
            description="Check doctor availability for a specific date and time",
            type=ToolType.APPOINTMENT,
            parameters=[
                ToolParameter(name="doctor_name", type="string", description="Name of the doctor", required=True),
                ToolParameter(name="date", type="string", description="Date in YYYY-MM-DD format", required=True),
                ToolParameter(name="time_preference", type="string", description="Time preference", required=False, 
                           enum=["morning", "afternoon", "evening", "any"])
            ],
            returns={
                "type": "object",
                "properties": {
                    "doctor_name": {"type": "string"},
                    "date": {"type": "string"},
                    "available_slots": {"type": "array", "items": {"type": "string"}},
                    "message": {"type": "string"}
                }
            },
            tags=["appointments", "availability"]
        )
        
        # Doctor Tools
        self.register_tool(
            name="list_doctors",
            description="List available doctors with optional filtering",
            type=ToolType.DOCTOR,
            parameters=[
                ToolParameter(name="specialty", type="string", description="Medical specialty filter", required=False),
                ToolParameter(name="available_date", type="string", description="Filter by available date", required=False),
                ToolParameter(name="location", type="string", description="Location filter", required=False)
            ],
            returns={
                "type": "object",
                "properties": {
                    "doctors": {"type": "array", "items": {"type": "object"}},
                    "count": {"type": "integer"},
                    "filters_applied": {"type": "object"}
                }
            },
            tags=["doctors", "search"]
        )
        
        # Calendar Tools
        self.register_tool(
            name="create_calendar_event",
            description="Create a Google Calendar event for an appointment",
            type=ToolType.CALENDAR,
            parameters=[
                ToolParameter(name="summary", type="string", description="Event summary/title", required=True),
                ToolParameter(name="description", type="string", description="Event description", required=False),
                ToolParameter(name="start_time", type="string", description="Start time in ISO format", required=True),
                ToolParameter(name="end_time", type="string", description="End time in ISO format", required=True),
                ToolParameter(name="attendees", type="array", description="List of attendee emails", required=False),
                ToolParameter(name="location", type="string", description="Event location", required=False)
            ],
            returns={
                "type": "object",
                "properties": {
                    "event_id": {"type": "string"},
                    "html_link": {"type": "string"},
                    "status": {"type": "string"},
                    "created": {"type": "string"}
                }
            },
            tags=["calendar", "google"]
        )
        
        # Email Tools
        self.register_tool(
            name="send_appointment_confirmation",
            description="Send appointment confirmation email via Gmail API",
            type=ToolType.EMAIL,
            parameters=[
                ToolParameter(name="to_email", type="string", description="Recipient email address", required=True),
                ToolParameter(name="patient_name", type="string", description="Patient's name", required=True),
                ToolParameter(name="doctor_name", type="string", description="Doctor's name", required=True),
                ToolParameter(name="appointment_date", type="string", description="Appointment date", required=True),
                ToolParameter(name="appointment_time", type="string", description="Appointment time", required=True),
                ToolParameter(name="appointment_id", type="string", description="Unique appointment ID", required=True)
            ],
            returns={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string"},
                    "status": {"type": "string"},
                    "sent_at": {"type": "string"}
                }
            },
            tags=["email", "gmail", "notifications"]
        )
        
        # Analytics Tools
        self.register_tool(
            name="get_appointment_statistics",
            description="Get appointment statistics and analytics for doctors",
            type=ToolType.ANALYTICS,
            parameters=[
                ToolParameter(name="doctor_name", type="string", description="Doctor's name", required=True),
                ToolParameter(name="period", type="string", description="Time period", required=True, 
                           enum=["day", "week", "month", "year"]),
                ToolParameter(name="start_date", type="string", description="Start date", required=False),
                ToolParameter(name="end_date", type="string", description="End date", required=False)
            ],
            returns={
                "type": "object",
                "properties": {
                    "total_appointments": {"type": "integer"},
                    "completed": {"type": "integer"},
                    "cancelled": {"type": "integer"},
                    "no_show": {"type": "integer"},
                    "completion_rate": {"type": "number"},
                    "average_duration": {"type": "number"}
                }
            },
            tags=["analytics", "statistics"]
        )
        
        # Search Tools
        self.register_tool(
            name="search_patients_by_symptoms",
            description="Search patients by symptoms for medical research",
            type=ToolType.SEARCH,
            parameters=[
                ToolParameter(name="symptoms", type="string", description="Symptoms to search for", required=True),
                ToolParameter(name="date_from", type="string", description="Start date for search", required=False),
                ToolParameter(name="date_to", type="string", description="End date for search", required=False),
                ToolParameter(name="doctor_name", type="string", description="Filter by doctor", required=False)
            ],
            returns={
                "type": "object",
                "properties": {
                    "patients": {"type": "array", "items": {"type": "object"}},
                    "count": {"type": "integer"},
                    "search_criteria": {"type": "object"}
                }
            },
            tags=["search", "patients", "symptoms"]
        )
    
    def register_tool(self, name: str, description: str, type: ToolType, 
                     parameters: List[ToolParameter], returns: Dict[str, Any],
                     examples: List[Dict[str, Any]] = None, tags: List[str] = None):
        """Register a new tool in the registry"""
        tool_def = ToolDefinition(
            name=name,
            description=description,
            type=type,
            parameters=parameters,
            returns=returns,
            examples=examples or [],
            tags=tags or []
        )
        
        # Create the actual tool instance
        tool = Tool(tool_def)
        self.tools[name] = tool
        logger.info(f"Registered tool: {name} ({type.value})")
    
    def get_tool(self, name: str) -> Optional['Tool']:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self, type_filter: Optional[ToolType] = None, tag_filter: Optional[str] = None) -> List[ToolDefinition]:
        """List all tools with optional filtering"""
        tools = []
        for tool in self.tools.values():
            if type_filter and tool.definition.type != type_filter:
                continue
            if tag_filter and tag_filter not in tool.definition.tags:
                continue
            tools.append(tool.definition)
        return tools
    
    def get_openapi_schema(self) -> Dict[str, Any]:
        """Generate OpenAPI schema for all registered tools"""
        paths = {}
        components = {
            "schemas": {},
            "parameters": {},
            "responses": {}
        }
        
        for tool_name, tool in self.tools.items():
            # Create path for tool execution
            path_key = f"/tools/{tool_name}"
            paths[path_key] = {
                "post": {
                    "summary": tool.definition.description,
                    "tags": tool.definition.tags,
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        param.name: {
                                            "type": param.type,
                                            "description": param.description,
                                            "required": param.required
                                        } for param in tool.definition.parameters
                                    },
                                    "required": [param.name for param in tool.definition.parameters if param.required]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Tool executed successfully",
                            "content": {
                                "application/json": {
                                    "schema": tool.definition.returns
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid parameters"
                        },
                        "500": {
                            "description": "Tool execution error"
                        }
                    }
                }
            }
        
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "MedAI Tool Registry API",
                "version": "1.0.0",
                "description": "OpenAPI schema for MedAI doctor appointment system tools"
            },
            "paths": paths,
            "components": components,
            "tags": [
                {"name": "appointments", "description": "Appointment management tools"},
                {"name": "doctors", "description": "Doctor management tools"},
                {"name": "calendar", "description": "Google Calendar integration tools"},
                {"name": "email", "description": "Gmail API integration tools"},
                {"name": "analytics", "description": "Analytics and reporting tools"},
                {"name": "search", "description": "Search and query tools"},
                {"name": "notifications", "description": "Notification tools"}
            ]
        }

class Tool:
    """Individual tool implementation"""
    
    def __init__(self, definition: ToolDefinition):
        self.definition = definition
        self.handler: Optional[Callable] = None
    
    def set_handler(self, handler: Callable):
        """Set the function handler for this tool"""
        self.handler = handler
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        if not self.handler:
            raise ValueError(f"Tool {self.definition.name} has no handler set")
        
        # Validate required parameters
        required_params = [param.name for param in self.definition.parameters if param.required]
        missing_params = [param for param in required_params if param not in parameters]
        if missing_params:
            raise ValueError(f"Missing required parameters: {missing_params}")
        
        # Execute the handler
        if hasattr(self.handler, '__call__'):
            if hasattr(self.handler, '__await__'):
                result = await self.handler(**parameters)
            else:
                result = self.handler(**parameters)
        else:
            raise ValueError(f"Handler for tool {self.definition.name} is not callable")
        
        return result

# Global tool registry instance
tool_registry = ToolRegistry()