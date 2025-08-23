"""
Google Calendar API Integration Service
Provides real Google Calendar integration for appointment scheduling
"""
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Google Calendar API scopes
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]

class GoogleCalendarService:
    """Google Calendar API service for appointment management"""
    
    def __init__(self):
        self.creds = None
        self.service = None
        self.calendar_id = 'primary'  # Default to primary calendar
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API using OAuth2"""
        try:
            # Check if we have valid credentials
            if os.path.exists('calendar_token.json'):
                self.creds = Credentials.from_authorized_user_file('calendar_token.json', SCOPES)
            
            # If no valid credentials available, let the user log in
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    # Load client secrets from a local file
                    if os.path.exists('credentials.json'):
                        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                        self.creds = flow.run_local_server(port=0)
                    else:
                        logger.warning("No credentials.json found. Please set up OAuth2 credentials.")
                        return
                
                # Save the credentials for the next run
                with open('calendar_token.json', 'w') as token:
                    token.write(self.creds.to_json())
            
            # Build the Calendar service
            self.service = build('calendar', 'v3', credentials=self.creds)
            logger.info("Google Calendar API authentication successful")
            
        except Exception as e:
            logger.error(f"Google Calendar API authentication failed: {e}")
            self.service = None
    
    def set_calendar_id(self, calendar_id: str):
        """Set the calendar ID to use for operations"""
        self.calendar_id = calendar_id
    
    def list_calendars(self) -> List[Dict[str, Any]]:
        """List all available calendars"""
        if not self.service:
            return []
        
        try:
            calendar_list = self.service.calendarList().list().execute()
            calendars = calendar_list.get('items', [])
            
            return [
                {
                    'id': cal['id'],
                    'summary': cal['summary'],
                    'description': cal.get('description', ''),
                    'primary': cal.get('primary', False),
                    'accessRole': cal.get('accessRole', '')
                }
                for cal in calendars
            ]
        except HttpError as error:
            logger.error(f"Error listing calendars: {error}")
            return []
    
    async def create_appointment_event(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Google Calendar event for an appointment"""
        if not self.service:
            raise ValueError("Calendar service not authenticated")
        
        try:
            # Extract appointment details
            doctor_name = appointment_data['doctor_name']
            patient_name = appointment_data['patient_name']
            patient_email = appointment_data['patient_email']
            appointment_date = appointment_data['appointment_date']
            appointment_time = appointment_data['appointment_time']
            duration = appointment_data.get('duration', 30)  # Default 30 minutes
            symptoms = appointment_data.get('symptoms', 'General consultation')
            location = appointment_data.get('location', 'Medical Office')
            
            # Parse date and time
            if isinstance(appointment_date, str):
                appointment_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
            
            if isinstance(appointment_time, str):
                time_parts = appointment_time.split(':')
                hour, minute = int(time_parts[0]), int(time_parts[1])
            else:
                hour, minute = 9, 0  # Default to 9:00 AM
            
            # Create start and end times
            start_datetime = datetime.combine(appointment_date, datetime.min.time().replace(hour=hour, minute=minute))
            end_datetime = start_datetime + timedelta(minutes=duration)
            
            # Format for Google Calendar API
            start_time = start_datetime.isoformat() + 'Z'
            end_time = end_datetime.isoformat() + 'Z'
            
            # Create event body
            event = {
                'summary': f'Appointment: {patient_name} with {doctor_name}',
                'description': f"""
Appointment Details:
Patient: {patient_name}
Doctor: {doctor_name}
Symptoms: {symptoms}
Duration: {duration} minutes

Please arrive 10 minutes early.
                """.strip(),
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC',
                },
                'location': location,
                'attendees': [
                    {'email': patient_email, 'displayName': patient_name},
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 30},       # 30 minutes before
                    ],
                },
                'colorId': '1',  # Blue color for medical appointments
                'transparency': 'opaque',
                'visibility': 'private'
            }
            
            # Create the event
            event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event,
                sendUpdates='all'  # Send email notifications to attendees
            ).execute()
            
            logger.info(f"Calendar event created successfully: {event['id']}")
            
            return {
                "event_id": event['id'],
                "html_link": event['htmlLink'],
                "status": event['status'],
                "created": event['created'],
                "start_time": start_time,
                "end_time": end_time,
                "summary": event['summary'],
                "attendees": [attendee['email'] for attendee in event.get('attendees', [])]
            }
            
        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            return {
                "error": str(error),
                "status": "failed",
                "appointment_data": appointment_data
            }
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "appointment_data": appointment_data
            }
    
    async def update_appointment_event(self, event_id: str, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing calendar event"""
        if not self.service:
            raise ValueError("Calendar service not authenticated")
        
        try:
            # Get the existing event
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            # Update event details
            if 'doctor_name' in appointment_data:
                event['summary'] = f"Appointment: {appointment_data['patient_name']} with {appointment_data['doctor_name']}"
            
            if 'appointment_date' in appointment_data and 'appointment_time' in appointment_data:
                # Parse new date and time
                appointment_date = appointment_data['appointment_date']
                appointment_time = appointment_data['appointment_time']
                duration = appointment_data.get('duration', 30)
                
                if isinstance(appointment_date, str):
                    appointment_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
                
                if isinstance(appointment_time, str):
                    time_parts = appointment_time.split(':')
                    hour, minute = int(time_parts[0]), int(time_parts[1])
                else:
                    hour, minute = 9, 0
                
                start_datetime = datetime.combine(appointment_date, datetime.min.time().replace(hour=hour, minute=minute))
                end_datetime = start_datetime + timedelta(minutes=duration)
                
                event['start']['dateTime'] = start_datetime.isoformat() + 'Z'
                event['end']['dateTime'] = end_datetime.isoformat() + 'Z'
            
            if 'symptoms' in appointment_data:
                event['description'] = f"""
Appointment Details:
Patient: {appointment_data['patient_name']}
Doctor: {appointment_data['doctor_name']}
Symptoms: {appointment_data['symptoms']}
Duration: {appointment_data.get('duration', 30)} minutes

Please arrive 10 minutes early.
                """.strip()
            
            # Update the event
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Calendar event updated successfully: {event_id}")
            
            return {
                "event_id": updated_event['id'],
                "html_link": updated_event['htmlLink'],
                "status": updated_event['status'],
                "updated": updated_event['updated'],
                "summary": updated_event['summary']
            }
            
        except HttpError as error:
            logger.error(f"Google Calendar API error updating event: {error}")
            return {
                "error": str(error),
                "status": "failed",
                "event_id": event_id
            }
        except Exception as e:
            logger.error(f"Error updating calendar event: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "event_id": event_id
            }
    
    async def cancel_appointment_event(self, event_id: str, reason: str = "Appointment cancelled") -> Dict[str, Any]:
        """Cancel a calendar event"""
        if not self.service:
            raise ValueError("Calendar service not authenticated")
        
        try:
            # Get the existing event
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            # Update event to show it's cancelled
            event['summary'] = f"CANCELLED: {event['summary']}"
            event['description'] = f"{event['description']}\n\nCANCELLED: {reason}"
            event['colorId'] = '11'  # Red color for cancelled events
            
            # Update the event
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Calendar event cancelled successfully: {event_id}")
            
            return {
                "event_id": updated_event['id'],
                "status": "cancelled",
                "reason": reason,
                "updated": updated_event['updated']
            }
            
        except HttpError as error:
            logger.error(f"Google Calendar API error cancelling event: {error}")
            return {
                "error": str(error),
                "status": "failed",
                "event_id": event_id
            }
        except Exception as e:
            logger.error(f"Error cancelling calendar event: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "event_id": event_id
            }
    
    async def get_appointment_events(self, start_date: str, end_date: str, 
                                   doctor_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all appointment events within a date range"""
        if not self.service:
            return []
        
        try:
            # Format dates for API
            start_datetime = f"{start_date}T00:00:00Z"
            end_datetime = f"{end_date}T23:59:59Z"
            
            # Build query
            query = "Appointment:"
            if doctor_name:
                query += f" {doctor_name}"
            
            # Get events
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_datetime,
                timeMax=end_datetime,
                q=query,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Filter and format events
            appointment_events = []
            for event in events:
                if 'Appointment:' in event.get('summary', ''):
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    end = event['end'].get('dateTime', event['end'].get('date'))
                    
                    appointment_events.append({
                        'id': event['id'],
                        'summary': event['summary'],
                        'description': event.get('description', ''),
                        'start': start,
                        'end': end,
                        'status': event['status'],
                        'attendees': [
                            attendee['email'] for attendee in event.get('attendees', [])
                        ],
                        'html_link': event['htmlLink']
                    })
            
            return appointment_events
            
        except HttpError as error:
            logger.error(f"Google Calendar API error getting events: {error}")
            return []
        except Exception as e:
            logger.error(f"Error getting calendar events: {e}")
            return []
    
    async def check_doctor_availability(self, doctor_name: str, date_str: str, 
                                      time_preference: str = "any") -> Dict[str, Any]:
        """Check doctor availability for a specific date"""
        if not self.service:
            return {"error": "Calendar service not authenticated"}
        
        try:
            # Get all events for the date
            start_datetime = f"{date_str}T00:00:00Z"
            end_datetime = f"{date_str}T23:59:59Z"
            
            query = f"Appointment: {doctor_name}"
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_datetime,
                timeMax=end_datetime,
                q=query,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Define time slots
            time_slots = {
                'morning': ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30'],
                'afternoon': ['14:00', '14:30', '15:00', '15:30', '16:00', '16:30'],
                'evening': ['17:00', '17:30', '18:00', '18:30', '19:00', '19:30']
            }
            
            # Get all available slots
            all_slots = []
            for period, slots in time_slots.items():
                all_slots.extend(slots)
            
            # Filter out booked slots
            booked_slots = []
            for event in events:
                if event['status'] != 'cancelled':
                    start_time = event['start'].get('dateTime', event['start'].get('date'))
                    if 'T' in start_time:  # Has time component
                        time_part = start_time.split('T')[1][:5]  # Extract HH:MM
                        if time_part in all_slots:
                            booked_slots.append(time_part)
            
            # Calculate available slots
            available_slots = [slot for slot in all_slots if slot not in booked_slots]
            
            # Filter by time preference if specified
            if time_preference != "any" and time_preference in time_slots:
                available_slots = [slot for slot in available_slots if slot in time_slots[time_preference]]
            
            return {
                "doctor_name": doctor_name,
                "date": date_str,
                "time_preference": time_preference,
                "available_slots": available_slots,
                "booked_slots": booked_slots,
                "total_available": len(available_slots),
                "total_booked": len(booked_slots)
            }
            
        except HttpError as error:
            logger.error(f"Google Calendar API error checking availability: {error}")
            return {"error": str(error)}
        except Exception as e:
            logger.error(f"Error checking doctor availability: {e}")
            return {"error": str(e)}
    
    def get_authentication_status(self) -> Dict[str, Any]:
        """Get the current authentication status"""
        if self.service:
            try:
                # Try to get calendar list to verify authentication
                calendar_list = self.service.calendarList().list().execute()
                calendars = calendar_list.get('items', [])
                
                return {
                    "authenticated": True,
                    "calendars_count": len(calendars),
                    "primary_calendar": next((cal['id'] for cal in calendars if cal.get('primary')), None),
                    "current_calendar": self.calendar_id
                }
            except Exception as e:
                return {
                    "authenticated": False,
                    "error": str(e)
                }
        else:
            return {
                "authenticated": False,
                "error": "Service not initialized"
            }

# Global Google Calendar service instance
calendar_service = GoogleCalendarService()
