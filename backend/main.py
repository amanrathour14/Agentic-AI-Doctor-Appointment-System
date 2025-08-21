"""
FastAPI backend with MCP (Model Context Protocol) implementation
for the agentic AI doctor appointment system
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date, time, timedelta
import asyncio
import json
import os
import logging
from sqlalchemy.orm import Session

# Import our modules
from config import settings
from session_manager import session_manager, ConversationSession
from llm_agent import agent, AgentResponse
from google_calendar_service import calendar_service
from email_service import email_service
from notification_service import (
    notification_manager, 
    notify_new_appointment, 
    notify_appointment_cancelled,
    notify_appointment_reminder,
    notify_system_alert,
    NotificationPriority
)

# Import database models
import sys
sys.path.append('../scripts')
from database_models import get_session, Doctor, Patient, Appointment, VisitHistory, DoctorAvailability

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Agentic AI system for doctor appointment scheduling and management"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced Pydantic models
class AppointmentRequest(BaseModel):
    doctor_name: str
    patient_name: str
    patient_email: str
    appointment_date: str
    appointment_time: str
    symptoms: Optional[str] = None
    
    @validator('appointment_date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')
    
    @validator('appointment_time')
    def validate_time(cls, v):
        try:
            datetime.strptime(v, "%H:%M")
            return v
        except ValueError:
            raise ValueError('Time must be in HH:MM format')

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_type: str = "patient"
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    tool_calls: List[Dict[str, Any]] = []
    pending_action: Optional[Dict[str, Any]] = None
    suggestions: List[str] = []

class MCPToolResponse(BaseModel):
    tool_name: str
    result: Dict[str, Any]
    success: bool
    message: str
    execution_time: Optional[float] = None

class SessionInfo(BaseModel):
    session_id: str
    user_type: str
    context: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    created_at: str
    last_activity: str

# Enhanced MCP Tool Registry
MCP_TOOLS = {
    "check_doctor_availability": {
        "description": "Check doctor availability for a specific date and time",
        "parameters": {
            "doctor_name": {"type": "string", "description": "Name of the doctor"},
            "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
            "time_preference": {"type": "string", "description": "morning, afternoon, evening, or specific time"}
        },
        "required": ["doctor_name", "date"]
    },
    "schedule_appointment": {
        "description": "Schedule an appointment with a doctor",
        "parameters": {
            "doctor_name": {"type": "string", "description": "Name of the doctor"},
            "patient_name": {"type": "string", "description": "Patient's full name"},
            "patient_email": {"type": "string", "description": "Patient's email address"},
            "appointment_date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
            "appointment_time": {"type": "string", "description": "Time in HH:MM format"},
            "symptoms": {"type": "string", "description": "Patient's symptoms (optional)"}
        },
        "required": ["doctor_name", "patient_name", "patient_email", "appointment_date", "appointment_time"]
    },
    "get_appointment_stats": {
        "description": "Get appointment statistics for doctors",
        "parameters": {
            "doctor_name": {"type": "string", "description": "Name of the doctor (optional)"},
            "date_range": {"type": "string", "description": "today, yesterday, week, month"},
            "filter_by": {"type": "string", "description": "status, symptoms, or empty"}
        },
        "required": ["date_range"]
    },
    "search_patients_by_symptom": {
        "description": "Search patients by symptoms",
        "parameters": {
            "symptom": {"type": "string", "description": "Symptom to search for"},
            "doctor_name": {"type": "string", "description": "Name of the doctor (optional)"},
            "date_range": {"type": "string", "description": "week, month, or empty for all time"}
        },
        "required": ["symptom"]
    },
    "get_doctor_schedule": {
        "description": "Get doctor's schedule for a specific date range",
        "parameters": {
            "doctor_name": {"type": "string", "description": "Name of the doctor"},
            "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
            "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"}
        },
        "required": ["doctor_name", "start_date", "end_date"]
    }
}

# Database dependency
def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()

# Background task for session cleanup
async def cleanup_sessions():
    """Background task to cleanup expired sessions"""
    session_manager.cleanup_expired_sessions(settings.session_timeout_minutes)

# MCP Tool implementations
async def check_doctor_availability(doctor_name: str, date: str, time_preference: str, db: Session) -> Dict[str, Any]:
    """Check doctor availability for a specific date and time preference"""
    try:
        # Find doctor by name
        doctor = db.query(Doctor).filter(Doctor.name.ilike(f"%{doctor_name}%")).first()
        if not doctor:
            return {"available_slots": [], "message": f"Doctor {doctor_name} not found"}
        
        # Parse date
        appointment_date = datetime.strptime(date, "%Y-%m-%d").date()
        day_of_week = appointment_date.weekday() + 1  # Convert to 1-7 format
        
        # Get doctor's availability for that day
        availability = db.query(DoctorAvailability).filter(
            DoctorAvailability.doctor_id == doctor.id,
            DoctorAvailability.day_of_week == day_of_week,
            DoctorAvailability.is_available == True
        ).first()
        
        if not availability:
            return {"available_slots": [], "message": f"Dr. {doctor.name} is not available on {date}"}
        
        # Get existing appointments for that day
        existing_appointments = db.query(Appointment).filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date == appointment_date,
            Appointment.status.in_(['scheduled', 'confirmed'])
        ).all()
        
        # Generate available time slots
        available_slots = []
        start_time = availability.start_time
        end_time = availability.end_time
        
        # Convert time preference to hour ranges
        if time_preference.lower() == "morning":
            slot_start = max(start_time, time(9, 0))
            slot_end = min(end_time, time(12, 0))
        elif time_preference.lower() == "afternoon":
            slot_start = max(start_time, time(12, 0))
            slot_end = min(end_time, time(17, 0))
        elif time_preference.lower() == "evening":
            slot_start = max(start_time, time(17, 0))
            slot_end = end_time
        else:
            slot_start = start_time
            slot_end = end_time
        
        # Generate 30-minute slots
        current_time = datetime.combine(appointment_date, slot_start)
        end_datetime = datetime.combine(appointment_date, slot_end)
        
        while current_time < end_datetime:
            slot_time = current_time.time()
            # Check if slot is already booked
            is_booked = any(
                appt.appointment_time == slot_time 
                for appt in existing_appointments
            )
            
            if not is_booked:
                available_slots.append(slot_time.strftime("%H:%M"))
            
            current_time += timedelta(minutes=30)
        
        return {
            "doctor_name": doctor.name,
            "date": date,
            "available_slots": available_slots,
            "message": f"Found {len(available_slots)} available slots for Dr. {doctor.name} on {date}"
        }
        
    except Exception as e:
        logger.error(f"Error checking availability: {str(e)}")
        return {"available_slots": [], "message": f"Error checking availability: {str(e)}"}

async def schedule_appointment(doctor_name: str, patient_name: str, patient_email: str, 
                             appointment_date: str, appointment_time: str, symptoms: str, db: Session) -> Dict[str, Any]:
    """Schedule an appointment with a doctor"""
    try:
        # Find or create doctor
        doctor = db.query(Doctor).filter(Doctor.name.ilike(f"%{doctor_name}%")).first()
        if not doctor:
            return {"success": False, "message": f"Doctor {doctor_name} not found"}
        
        # Find or create patient
        patient = db.query(Patient).filter(Patient.email == patient_email).first()
        if not patient:
            patient = Patient(name=patient_name, email=patient_email)
            db.add(patient)
            db.commit()
            db.refresh(patient)
        
        # Parse date and time
        appt_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        appt_time = datetime.strptime(appointment_time, "%H:%M").time()
        
        # Check if slot is available
        existing_appointment = db.query(Appointment).filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date == appt_date,
            Appointment.appointment_time == appt_time,
            Appointment.status.in_(['scheduled', 'confirmed'])
        ).first()
        
        if existing_appointment:
            return {"success": False, "message": f"Time slot {appointment_time} on {appointment_date} is already booked"}
        
        calendar_event_id = None
        if calendar_service.is_available():
            try:
                calendar_event_id = await calendar_service.create_appointment_event(
                    doctor_name=doctor.name,
                    patient_name=patient.name,
                    patient_email=patient.email,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    duration_minutes=30,
                    symptoms=symptoms
                )
                logger.info(f"Created calendar event: {calendar_event_id}")
            except Exception as e:
                logger.error(f"Failed to create calendar event: {str(e)}")
        
        # Create appointment
        appointment = Appointment(
            doctor_id=doctor.id,
            patient_id=patient.id,
            appointment_date=appt_date,
            appointment_time=appt_time,
            symptoms=symptoms,
            status='scheduled',
            google_calendar_event_id=calendar_event_id  # Store calendar event ID
        )
        
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        
        try:
            await notify_new_appointment(
                doctor_id=doctor.id,
                patient_name=patient.name,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                symptoms=symptoms,
                db=db
            )
            logger.info(f"Sent new appointment notification to doctor {doctor.id}")
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
        
        email_results = {"patient_email": False, "doctor_email": False}
        
        if email_service.is_available():
            try:
                # Send confirmation to patient
                patient_email_sent = await email_service.send_appointment_confirmation(
                    patient_email=patient.email,
                    patient_name=patient.name,
                    doctor_name=doctor.name,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    symptoms=symptoms
                )
                email_results["patient_email"] = patient_email_sent
                
                # Send notification to doctor
                doctor_email_sent = await email_service.send_doctor_notification(
                    doctor_email=doctor.email,
                    doctor_name=doctor.name,
                    patient_name=patient.name,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    symptoms=symptoms
                )
                email_results["doctor_email"] = doctor_email_sent
                
                logger.info(f"Email notifications sent - Patient: {patient_email_sent}, Doctor: {doctor_email_sent}")
                
            except Exception as e:
                logger.error(f"Failed to send email notifications: {str(e)}")
        
        return {
            "success": True,
            "appointment_id": appointment.id,
            "message": f"Appointment scheduled successfully with Dr. {doctor.name} on {appointment_date} at {appointment_time}",
            "details": {
                "doctor": doctor.name,
                "patient": patient.name,
                "date": appointment_date,
                "time": appointment_time,
                "symptoms": symptoms,
                "calendar_event_id": calendar_event_id,
                "email_notifications": email_results
            }
        }
        
    except Exception as e:
        logger.error(f"Error scheduling appointment: {str(e)}")
        return {"success": False, "message": f"Error scheduling appointment: {str(e)}"}

async def get_appointment_stats(doctor_name: str, date_range: str, filter_by: str, db: Session) -> Dict[str, Any]:
    """Get appointment statistics for doctors"""
    try:
        # Base query
        query = db.query(Appointment)
        
        # Filter by doctor if specified
        if doctor_name:
            doctor = db.query(Doctor).filter(Doctor.name.ilike(f"%{doctor_name}%")).first()
            if doctor:
                query = query.filter(Appointment.doctor_id == doctor.id)
            else:
                return {"stats": {}, "message": f"Doctor {doctor_name} not found"}
        
        # Filter by date range
        today = date.today()
        if date_range == "today":
            query = query.filter(Appointment.appointment_date == today)
        elif date_range == "yesterday":
            yesterday = today - timedelta(days=1)
            query = query.filter(Appointment.appointment_date == yesterday)
        elif date_range == "week":
            week_ago = today - timedelta(days=7)
            query = query.filter(Appointment.appointment_date >= week_ago)
        elif date_range == "month":
            month_ago = today - timedelta(days=30)
            query = query.filter(Appointment.appointment_date >= month_ago)
        
        appointments = query.all()
        
        # Calculate statistics
        stats = {
            "total_appointments": len(appointments),
            "scheduled": len([a for a in appointments if a.status == 'scheduled']),
            "completed": len([a for a in appointments if a.status == 'completed']),
            "cancelled": len([a for a in appointments if a.status == 'cancelled']),
            "no_show": len([a for a in appointments if a.status == 'no_show'])
        }
        
        # Filter by symptoms if requested
        if filter_by and filter_by.lower() == "symptoms":
            symptom_counts = {}
            for appointment in appointments:
                if appointment.symptoms:
                    symptoms = appointment.symptoms.lower()
                    for symptom in ['fever', 'cough', 'headache', 'chest pain', 'sore throat']:
                        if symptom in symptoms:
                            symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1
            stats["symptom_breakdown"] = symptom_counts
        
        return {
            "stats": stats,
            "date_range": date_range,
            "doctor": doctor_name if doctor_name else "All doctors",
            "message": f"Retrieved statistics for {date_range}"
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return {"stats": {}, "message": f"Error getting statistics: {str(e)}"}

async def search_patients_by_symptom(symptom: str, doctor_name: str, date_range: str, db: Session) -> Dict[str, Any]:
    """Search patients by symptoms"""
    try:
        # Base query for appointments with symptoms
        query = db.query(Appointment).filter(
            Appointment.symptoms.ilike(f"%{symptom}%")
        )
        
        # Filter by doctor if specified
        if doctor_name:
            doctor = db.query(Doctor).filter(Doctor.name.ilike(f"%{doctor_name}%")).first()
            if doctor:
                query = query.filter(Appointment.doctor_id == doctor.id)
        
        # Filter by date range if specified
        if date_range:
            today = date.today()
            if date_range == "week":
                week_ago = today - timedelta(days=7)
                query = query.filter(Appointment.appointment_date >= week_ago)
            elif date_range == "month":
                month_ago = today - timedelta(days=30)
                query = query.filter(Appointment.appointment_date >= month_ago)
        
        appointments = query.all()
        
        # Get patient details
        patients = []
        for appointment in appointments:
            patient_info = {
                "patient_name": appointment.patient.name,
                "appointment_date": appointment.appointment_date.strftime("%Y-%m-%d"),
                "symptoms": appointment.symptoms,
                "doctor": appointment.doctor.name,
                "status": appointment.status
            }
            patients.append(patient_info)
        
        return {
            "patients": patients,
            "count": len(patients),
            "symptom": symptom,
            "message": f"Found {len(patients)} patients with symptom '{symptom}'"
        }
        
    except Exception as e:
        logger.error(f"Error searching patients: {str(e)}")
        return {"patients": [], "message": f"Error searching patients: {str(e)}"}

async def get_doctor_schedule(doctor_name: str, start_date: str, end_date: str, db: Session) -> Dict[str, Any]:
    """Get doctor's schedule for a specific date range"""
    try:
        doctor = db.query(Doctor).filter(Doctor.name.ilike(f"%{doctor_name}%")).first()
        if not doctor:
            return {"schedule": [], "message": f"Doctor {doctor_name} not found"}
        
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        appointments = db.query(Appointment).filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date >= start_dt,
            Appointment.appointment_date <= end_dt
        ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
        
        schedule = []
        for appointment in appointments:
            schedule.append({
                "date": appointment.appointment_date.strftime("%Y-%m-%d"),
                "time": appointment.appointment_time.strftime("%H:%M"),
                "patient": appointment.patient.name,
                "status": appointment.status,
                "symptoms": appointment.symptoms
            })
        
        return {
            "doctor_name": doctor.name,
            "schedule": schedule,
            "total_appointments": len(schedule),
            "message": f"Retrieved schedule for Dr. {doctor.name} from {start_date} to {end_date}"
        }
        
    except Exception as e:
        logger.error(f"Error getting doctor schedule: {str(e)}")
        return {"schedule": [], "message": f"Error getting schedule: {str(e)}"}

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": f"{settings.app_name} API",
        "version": settings.app_version,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/session/create")
async def create_session(user_type: str = "patient"):
    """Create a new conversation session"""
    session_id = session_manager.create_session(user_type)
    return {"session_id": session_id, "user_type": user_type}

@app.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """Get session information"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    return SessionInfo(
        session_id=session.session_id,
        user_type=session.user_type,
        context=session.context,
        conversation_history=session.conversation_history,
        created_at=session.created_at.isoformat(),
        last_activity=session.last_activity.isoformat()
    )

@app.get("/mcp/tools")
async def get_mcp_tools():
    """Get available MCP tools for the AI agent"""
    return {"tools": MCP_TOOLS, "count": len(MCP_TOOLS)}

@app.post("/mcp/execute")
async def execute_mcp_tool(
    tool_name: str, 
    parameters: Dict[str, Any], 
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Execute an MCP tool with given parameters"""
    start_time = datetime.now()
    
    try:
        # Get session if provided
        session = None
        if session_id:
            session = session_manager.get_session(session_id)
        
        # Execute the appropriate tool
        if tool_name == "check_doctor_availability":
            result = await check_doctor_availability(
                parameters.get("doctor_name"),
                parameters.get("date"),
                parameters.get("time_preference", ""),
                db
            )
        elif tool_name == "schedule_appointment":
            result = await schedule_appointment(
                parameters.get("doctor_name"),
                parameters.get("patient_name"),
                parameters.get("patient_email"),
                parameters.get("appointment_date"),
                parameters.get("appointment_time"),
                parameters.get("symptoms", ""),
                db
            )
            # Update session context if appointment was scheduled
            if session and result.get("success"):
                session.update_context("last_appointment", result.get("details"))
                
        elif tool_name == "get_appointment_stats":
            result = await get_appointment_stats(
                parameters.get("doctor_name", ""),
                parameters.get("date_range", "today"),
                parameters.get("filter_by", ""),
                db
            )
        elif tool_name == "search_patients_by_symptom":
            result = await search_patients_by_symptom(
                parameters.get("symptom"),
                parameters.get("doctor_name", ""),
                parameters.get("date_range", ""),
                db
            )
        elif tool_name == "get_doctor_schedule":
            result = await get_doctor_schedule(
                parameters.get("doctor_name"),
                parameters.get("start_date"),
                parameters.get("end_date"),
                db
            )
        else:
            return MCPToolResponse(
                tool_name=tool_name,
                result={},
                success=False,
                message=f"Unknown tool: {tool_name}",
                execution_time=0.0
            )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return MCPToolResponse(
            tool_name=tool_name,
            result=result,
            success=True,
            message="Tool executed successfully",
            execution_time=execution_time
        )
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"Error executing tool {tool_name}: {str(e)}")
        
        return MCPToolResponse(
            tool_name=tool_name,
            result={},
            success=False,
            message=f"Error executing tool: {str(e)}",
            execution_time=execution_time
        )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    message: ChatMessage, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Enhanced chat endpoint with session management and LLM agent integration"""
    try:
        # Get or create session
        session = None
        if message.session_id:
            session = session_manager.get_session(message.session_id)
        
        if not session:
            session_id = session_manager.create_session(message.user_type)
            session = session_manager.get_session(session_id)
        
        # Add cleanup task
        background_tasks.add_task(cleanup_sessions)
        
        if not settings.openai_api_key:
            # Fallback if no OpenAI key
            response_text = f"OpenAI API key not configured. Received: '{message.message}'"
            agent_response = AgentResponse(
                message=response_text,
                tool_calls=[],
                suggestions=["Configure OpenAI API key to enable AI features"]
            )
        else:
            # Process with LLM agent
            agent_response = await agent.process_message(
                message.message,
                session,
                execute_mcp_tool_internal,
                message.user_type
            )
        
        # Add to conversation history
        session.add_message(
            message.message, 
            agent_response.message, 
            agent_response.tool_calls
        )
        
        # Update pending action if any
        if agent_response.pending_action:
            session.set_pending_action(agent_response.pending_action)
        
        return ChatResponse(
            response=agent_response.message,
            session_id=session.session_id,
            tool_calls=agent_response.tool_calls,
            pending_action=agent_response.pending_action,
            suggestions=agent_response.suggestions or []
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/doctors")
async def get_doctors(db: Session = Depends(get_db)):
    """Get list of all doctors"""
    doctors = db.query(Doctor).all()
    return {
        "doctors": [
            {
                "id": doctor.id,
                "name": doctor.name,
                "specialization": doctor.specialization,
                "email": doctor.email
            }
            for doctor in doctors
        ]
    }

@app.get("/appointments/upcoming")
async def get_upcoming_appointments(
    doctor_id: Optional[int] = None,
    patient_email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get upcoming appointments"""
    query = db.query(Appointment).filter(
        Appointment.appointment_date >= date.today(),
        Appointment.status == 'scheduled'
    )
    
    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)
    
    if patient_email:
        patient = db.query(Patient).filter(Patient.email == patient_email).first()
        if patient:
            query = query.filter(Appointment.patient_id == patient.id)
    
    appointments = query.order_by(
        Appointment.appointment_date, 
        Appointment.appointment_time
    ).all()
    
    return {
        "appointments": [
            {
                "id": appt.id,
                "doctor": appt.doctor.name,
                "patient": appt.patient.name,
                "date": appt.appointment_date.strftime("%Y-%m-%d"),
                "time": appt.appointment_time.strftime("%H:%M"),
                "symptoms": appt.symptoms
            }
            for appt in appointments
        ]
    }

@app.get("/api/status")
async def get_api_status():
    """Get status of external API integrations"""
    return {
        "google_calendar": {
            "available": calendar_service.is_available(),
            "status": "connected" if calendar_service.is_available() else "not configured"
        },
        "email_service": {
            "available": email_service.is_available(),
            "status": "connected" if email_service.is_available() else "not configured"
        }
    }

@app.post("/appointments/{appointment_id}/cancel")
async def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Cancel an appointment and clean up external integrations"""
    try:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Cancel Google Calendar event if exists
        if appointment.google_calendar_event_id and calendar_service.is_available():
            try:
                await calendar_service.cancel_appointment_event(appointment.google_calendar_event_id)
                logger.info(f"Cancelled calendar event: {appointment.google_calendar_event_id}")
            except Exception as e:
                logger.error(f"Failed to cancel calendar event: {str(e)}")
        
        try:
            await notify_appointment_cancelled(
                doctor_id=appointment.doctor_id,
                patient_name=appointment.patient.name,
                appointment_date=appointment.appointment_date.strftime("%Y-%m-%d"),
                appointment_time=appointment.appointment_time.strftime("%H:%M"),
                db=db
            )
            logger.info(f"Sent cancellation notification to doctor {appointment.doctor_id}")
        except Exception as e:
            logger.error(f"Failed to send cancellation notification: {str(e)}")
        
        # Update appointment status
        appointment.status = 'cancelled'
        db.commit()
        
        return {
            "success": True,
            "message": "Appointment cancelled successfully",
            "appointment_id": appointment_id
        }
        
    except Exception as e:
        logger.error(f"Error cancelling appointment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error cancelling appointment: {str(e)}")

@app.websocket("/ws/notifications/{doctor_id}")
async def websocket_notifications(websocket: WebSocket, doctor_id: int):
    """WebSocket endpoint for real-time doctor notifications"""
    await notification_manager.connect(websocket, doctor_id)
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            # Handle ping/pong or other client messages if needed
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        notification_manager.disconnect(websocket, doctor_id)

@app.get("/notifications/{doctor_id}")
async def get_doctor_notifications(doctor_id: int, db: Session = Depends(get_db)):
    """Get pending notifications for a doctor"""
    # In a real implementation, you'd query the database for stored notifications
    # For now, return pending notifications from memory
    pending = notification_manager.pending_notifications.get(doctor_id, [])
    return {
        "doctor_id": doctor_id,
        "notifications": pending,
        "count": len(pending)
    }

@app.post("/notifications/{doctor_id}/mark-read")
async def mark_notifications_read(doctor_id: int, notification_ids: List[str]):
    """Mark notifications as read"""
    # In a real implementation, you'd update the database
    # For now, just return success
    return {
        "success": True,
        "marked_read": len(notification_ids),
        "message": f"Marked {len(notification_ids)} notifications as read"
    }

@app.post("/notifications/system-alert")
async def send_system_alert(
    message: str,
    priority: str = "medium",
    target_doctor_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Send system alert to doctors"""
    try:
        priority_enum = NotificationPriority(priority.lower())
        await notify_system_alert(
            message=message,
            priority=priority_enum,
            target_doctor_id=target_doctor_id,
            db=db
        )
        
        return {
            "success": True,
            "message": "System alert sent successfully"
        }
    except Exception as e:
        logger.error(f"Error sending system alert: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending alert: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=settings.debug
    )
