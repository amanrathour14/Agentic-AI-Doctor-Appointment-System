"""
Google Calendar API integration for appointment scheduling
"""
import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class GoogleCalendarService:
    def __init__(self):
        self.service = None
        self.calendar_id = 'primary'  # Use primary calendar or specific calendar ID
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Calendar service with credentials"""
        try:
            # Try to load service account credentials
            credentials_path = os.getenv('GOOGLE_CALENDAR_CREDENTIALS')
            if credentials_path and os.path.exists(credentials_path):
                credentials = ServiceAccountCredentials.from_service_account_file(
                    credentials_path,
                    scopes=['https://www.googleapis.com/auth/calendar']
                )
                self.service = build('calendar', 'v3', credentials=credentials)
                logger.info("Google Calendar service initialized with service account")
            else:
                logger.warning("Google Calendar credentials not found. Calendar integration disabled.")
                
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar service: {str(e)}")
            self.service = None
    
    def is_available(self) -> bool:
        """Check if Google Calendar service is available"""
        return self.service is not None
    
    async def create_appointment_event(
        self, 
        doctor_name: str,
        patient_name: str,
        patient_email: str,
        appointment_date: str,
        appointment_time: str,
        duration_minutes: int = 30,
        symptoms: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a calendar event for the appointment
        Returns the event ID if successful, None otherwise
        """
        if not self.is_available():
            logger.warning("Google Calendar service not available")
            return None
        
        try:
            # Parse date and time
            start_datetime = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
            end_datetime = start_datetime + timedelta(minutes=duration_minutes)
            
            # Create event details
            event = {
                'summary': f'Medical Appointment - {patient_name}',
                'description': f"""
Medical Appointment Details:
- Doctor: {doctor_name}
- Patient: {patient_name}
- Duration: {duration_minutes} minutes
{f"- Symptoms: {symptoms}" if symptoms else ""}

This appointment was scheduled via MedAI Assistant.
                """.strip(),
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'UTC',  # You might want to make this configurable
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'UTC',
                },
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
                'colorId': '2',  # Green color for medical appointments
            }
            
            # Create the event
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event,
                sendUpdates='all'  # Send email invitations
            ).execute()
            
            event_id = created_event.get('id')
            logger.info(f"Created calendar event {event_id} for appointment with {doctor_name}")
            
            return event_id
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error creating calendar event: {str(e)}")
            return None
    
    async def update_appointment_event(
        self,
        event_id: str,
        doctor_name: str,
        patient_name: str,
        appointment_date: str,
        appointment_time: str,
        duration_minutes: int = 30
    ) -> bool:
        """Update an existing calendar event"""
        if not self.is_available():
            return False
        
        try:
            # Get existing event
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            # Parse new date and time
            start_datetime = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
            end_datetime = start_datetime + timedelta(minutes=duration_minutes)
            
            # Update event
            event['start']['dateTime'] = start_datetime.isoformat()
            event['end']['dateTime'] = end_datetime.isoformat()
            event['summary'] = f'Medical Appointment - {patient_name} (Updated)'
            
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Updated calendar event {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating calendar event: {str(e)}")
            return False
    
    async def cancel_appointment_event(self, event_id: str) -> bool:
        """Cancel/delete a calendar event"""
        if not self.is_available():
            return False
        
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Cancelled calendar event {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling calendar event: {str(e)}")
            return False

# Global calendar service instance
calendar_service = GoogleCalendarService()
