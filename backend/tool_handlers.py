"""
Tool Handlers Implementation
Provides actual functionality for the registered tools
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
import uuid

from tool_registry import tool_registry, ToolType
from gmail_service import gmail_service
from google_calendar_service import calendar_service

logger = logging.getLogger(__name__)

class ToolHandlers:
    """Implementation of all tool handlers"""
    
    def __init__(self):
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all tool handlers with the registry"""
        
        # Appointment Tools
        tool_registry.get_tool("schedule_appointment").set_handler(self.schedule_appointment)
        tool_registry.get_tool("check_doctor_availability").set_handler(self.check_doctor_availability)
        
        # Doctor Tools
        tool_registry.get_tool("list_doctors").set_handler(self.list_doctors)
        
        # Calendar Tools
        tool_registry.get_tool("create_calendar_event").set_handler(self.create_calendar_event)
        
        # Email Tools
        tool_registry.get_tool("send_appointment_confirmation").set_handler(self.send_appointment_confirmation)
        
        # Analytics Tools
        tool_registry.get_tool("get_appointment_statistics").set_handler(self.get_appointment_statistics)
        
        # Search Tools
        tool_registry.get_tool("search_patients_by_symptoms").set_handler(self.search_patients_by_symptoms)
        
        logger.info("All tool handlers registered successfully")
    
    async def schedule_appointment(self, doctor_name: str, patient_name: str, patient_email: str,
                                 appointment_date: str, appointment_time: str, 
                                 symptoms: str = None, duration: int = 30) -> Dict[str, Any]:
        """Schedule a new appointment with full integration"""
        try:
            # Generate appointment ID
            appointment_id = f"apt_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
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
                logger.error(f"Calendar event creation failed: {calendar_result['error']}")
                return {
                    "appointment_id": appointment_id,
                    "status": "failed",
                    "error": f"Calendar integration failed: {calendar_result['error']}",
                    "calendar_event_id": None,
                    "email_sent": False,
                    "message": "Appointment scheduling failed due to calendar integration error"
                }
            
            # Send confirmation email
            email_data = {
                'to_email': patient_email,
                'patient_name': patient_name,
                'doctor_name': doctor_name,
                'appointment_date': appointment_date,
                'appointment_time': appointment_time,
                'appointment_id': appointment_id
            }
            
            email_result = await gmail_service.send_appointment_confirmation(email_data)
            
            if email_result.get('error'):
                logger.warning(f"Email sending failed: {email_result['error']}")
                email_sent = False
            else:
                email_sent = True
            
            # Return success result
            return {
                "appointment_id": appointment_id,
                "status": "scheduled",
                "calendar_event_id": calendar_result.get('event_id'),
                "email_sent": email_sent,
                "message": "Appointment scheduled successfully",
                "calendar_link": calendar_result.get('html_link'),
                "email_message_id": email_result.get('message_id') if email_sent else None
            }
            
        except Exception as e:
            logger.error(f"Error scheduling appointment: {e}")
            return {
                "appointment_id": appointment_id if 'appointment_id' in locals() else "unknown",
                "status": "failed",
                "error": str(e),
                "calendar_event_id": None,
                "email_sent": False,
                "message": f"Appointment scheduling failed: {str(e)}"
            }
    
    async def check_doctor_availability(self, doctor_name: str, date: str, 
                                      time_preference: str = "any") -> Dict[str, Any]:
        """Check doctor availability using Google Calendar"""
        try:
            # Use the real calendar service to check availability
            availability = await calendar_service.check_doctor_availability(doctor_name, date, time_preference)
            
            if availability.get('error'):
                return {
                    "doctor_name": doctor_name,
                    "date": date,
                    "available_slots": [],
                    "message": f"Error checking availability: {availability['error']}"
                }
            
            return {
                "doctor_name": doctor_name,
                "date": date,
                "available_slots": availability.get('available_slots', []),
                "booked_slots": availability.get('booked_slots', []),
                "total_available": availability.get('total_available', 0),
                "total_booked": availability.get('total_booked', 0),
                "message": f"Found {availability.get('total_available', 0)} available slots for {doctor_name} on {date}"
            }
            
        except Exception as e:
            logger.error(f"Error checking doctor availability: {e}")
            return {
                "doctor_name": doctor_name,
                "date": date,
                "available_slots": [],
                "message": f"Error checking availability: {str(e)}"
            }
    
    async def list_doctors(self, specialty: str = None, available_date: str = None, 
                          location: str = None) -> Dict[str, Any]:
        """List available doctors with filtering"""
        try:
            # Mock doctors data - in real implementation, this would query a database
            doctors = [
                {"name": "Dr. Smith", "specialty": "Cardiology", "available": True, "location": "Main Office"},
                {"name": "Dr. Johnson", "specialty": "Dermatology", "available": True, "location": "Main Office"},
                {"name": "Dr. Williams", "specialty": "Pediatrics", "available": False, "location": "Downtown Office"},
                {"name": "Dr. Brown", "specialty": "Neurology", "available": True, "location": "Main Office"},
                {"name": "Dr. Davis", "specialty": "Orthopedics", "available": True, "location": "Downtown Office"}
            ]
            
            # Apply filters
            filtered_doctors = doctors
            
            if specialty:
                filtered_doctors = [d for d in filtered_doctors if d["specialty"].lower() == specialty.lower()]
            
            if location:
                filtered_doctors = [d for d in filtered_doctors if d["location"].lower() == location.lower()]
            
            if available_date:
                # Check calendar availability for the date
                available_doctors = []
                for doctor in filtered_doctors:
                    if doctor["available"]:
                        availability = await calendar_service.check_doctor_availability(
                            doctor["name"], available_date
                        )
                        if not availability.get('error') and availability.get('total_available', 0) > 0:
                            available_doctors.append(doctor)
                filtered_doctors = available_doctors
            
            return {
                "doctors": filtered_doctors,
                "count": len(filtered_doctors),
                "filters_applied": {
                    "specialty": specialty,
                    "available_date": available_date,
                    "location": location
                }
            }
            
        except Exception as e:
            logger.error(f"Error listing doctors: {e}")
            return {
                "doctors": [],
                "count": 0,
                "error": str(e)
            }
    
    async def create_calendar_event(self, summary: str, start_time: str, end_time: str,
                                  description: str = None, attendees: List[str] = None,
                                  location: str = None) -> Dict[str, Any]:
        """Create a Google Calendar event"""
        try:
            event_data = {
                'summary': summary,
                'start_time': start_time,
                'end_time': end_time,
                'description': description,
                'attendees': attendees or [],
                'location': location
            }
            
            # Use the real calendar service
            result = await calendar_service.create_appointment_event(event_data)
            
            if result.get('error'):
                return {
                    "error": result['error'],
                    "status": "failed"
                }
            
            return {
                "event_id": result.get('event_id'),
                "html_link": result.get('html_link'),
                "status": result.get('status'),
                "created": result.get('created')
            }
            
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def send_appointment_confirmation(self, to_email: str, patient_name: str,
                                         doctor_name: str, appointment_date: str,
                                         appointment_time: str, appointment_id: str) -> Dict[str, Any]:
        """Send appointment confirmation email via Gmail API"""
        try:
            email_data = {
                'to_email': to_email,
                'patient_name': patient_name,
                'doctor_name': doctor_name,
                'appointment_date': appointment_date,
                'appointment_time': appointment_time,
                'appointment_id': appointment_id
            }
            
            # Use the real Gmail service
            result = await gmail_service.send_appointment_confirmation(email_data)
            
            if result.get('error'):
                return {
                    "error": result['error'],
                    "status": "failed"
                }
            
            return {
                "message_id": result.get('message_id'),
                "status": result.get('status'),
                "sent_at": result.get('sent_at')
            }
            
        except Exception as e:
            logger.error(f"Error sending appointment confirmation: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def get_appointment_statistics(self, doctor_name: str, period: str,
                                       start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get appointment statistics from Google Calendar"""
        try:
            # Calculate date range based on period
            today = date.today()
            if period == "day":
                start_date = today.strftime("%Y-%m-%d")
                end_date = today.strftime("%Y-%m-%d")
            elif period == "week":
                start_date = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
                end_date = (today + timedelta(days=6-today.weekday())).strftime("%Y-%m-%d")
            elif period == "month":
                start_date = today.replace(day=1).strftime("%Y-%m-%d")
                if today.month == 12:
                    end_date = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
                else:
                    end_date = today.replace(month=today.month+1, day=1) - timedelta(days=1)
                end_date = end_date.strftime("%Y-%m-%d")
            elif period == "year":
                start_date = today.replace(month=1, day=1).strftime("%Y-%m-%d")
                end_date = today.replace(month=12, day=31).strftime("%Y-%m-%d")
            
            # Get events from Google Calendar
            events = await calendar_service.get_appointment_events(start_date, end_date, doctor_name)
            
            # Calculate statistics
            total_appointments = len(events)
            completed = len([e for e in events if e['status'] == 'confirmed'])
            cancelled = len([e for e in events if 'CANCELLED' in e.get('summary', '')])
            no_show = 0  # Would need additional tracking for no-shows
            
            completion_rate = (completed / total_appointments * 100) if total_appointments > 0 else 0
            
            return {
                "doctor_name": doctor_name,
                "period": period,
                "start_date": start_date,
                "end_date": end_date,
                "total_appointments": total_appointments,
                "completed": completed,
                "cancelled": cancelled,
                "no_show": no_show,
                "completion_rate": round(completion_rate, 1),
                "events": events
            }
            
        except Exception as e:
            logger.error(f"Error getting appointment statistics: {e}")
            return {
                "doctor_name": doctor_name,
                "period": period,
                "error": str(e),
                "total_appointments": 0,
                "completed": 0,
                "cancelled": 0,
                "no_show": 0,
                "completion_rate": 0
            }
    
    async def search_patients_by_symptoms(self, symptoms: str, date_from: str = None,
                                        date_to: str = None, doctor_name: str = None) -> Dict[str, Any]:
        """Search patients by symptoms using calendar data"""
        try:
            # Set default date range if not provided
            if not date_from:
                date_from = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
            if not date_to:
                date_to = date.today().strftime("%Y-%m-%d")
            
            # Get events from Google Calendar
            events = await calendar_service.get_appointment_events(date_from, date_to, doctor_name)
            
            # Filter events by symptoms (this would be more sophisticated in a real system)
            matching_patients = []
            for event in events:
                if 'symptoms' in event.get('description', '').lower():
                    if symptoms.lower() in event.get('description', '').lower():
                        # Extract patient name from event summary
                        summary = event.get('summary', '')
                        if 'Appointment:' in summary:
                            patient_name = summary.split('Appointment:')[1].split('with')[0].strip()
                            
                            matching_patients.append({
                                "name": patient_name,
                                "symptoms": symptoms,
                                "last_visit": event.get('start', ''),
                                "doctor": doctor_name or "Any",
                                "appointment_id": event.get('id'),
                                "event_link": event.get('html_link')
                            })
            
            return {
                "symptoms": symptoms,
                "patients": matching_patients,
                "count": len(matching_patients),
                "search_criteria": {
                    "date_from": date_from,
                    "date_to": date_to,
                    "doctor_name": doctor_name
                }
            }
            
        except Exception as e:
            logger.error(f"Error searching patients by symptoms: {e}")
            return {
                "symptoms": symptoms,
                "patients": [],
                "count": 0,
                "error": str(e)
            }

# Initialize tool handlers
tool_handlers = ToolHandlers()