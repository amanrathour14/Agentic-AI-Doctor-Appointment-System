"""
Gmail API Integration Service
Provides real Gmail API integration with OAuth2 authentication
"""
import os
import base64
import logging
from typing import Dict, List, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify'
]

class GmailService:
    """Gmail API service for sending emails"""
    
    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API using OAuth2"""
        try:
            # Check if we have valid credentials
            if os.path.exists('token.json'):
                self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
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
                with open('token.json', 'w') as token:
                    token.write(self.creds.to_json())
            
            # Build the Gmail service
            self.service = build('gmail', 'v1', credentials=self.creds)
            logger.info("Gmail API authentication successful")
            
        except Exception as e:
            logger.error(f"Gmail API authentication failed: {e}")
            self.service = None
    
    def _create_message(self, sender: str, to: str, subject: str, body: str, 
                       body_type: str = 'html') -> Dict[str, Any]:
        """Create a Gmail message"""
        message = MIMEMultipart('alternative')
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        
        # Create the body of the message
        if body_type == 'html':
            part = MIMEText(body, 'html')
        else:
            part = MIMEText(body, 'plain')
        
        message.attach(part)
        
        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}
    
    def _create_message_with_attachment(self, sender: str, to: str, subject: str, 
                                      body: str, attachment_path: str) -> Dict[str, Any]:
        """Create a Gmail message with attachment"""
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        
        # Add body
        msg = MIMEText(body, 'html')
        message.attach(msg)
        
        # Add attachment
        with open(attachment_path, 'rb') as f:
            attachment = MIMEText(f.read(), 'base64')
            attachment.add_header('Content-Disposition', 'attachment', 
                                filename=os.path.basename(attachment_path))
            message.attach(attachment)
        
        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}
    
    async def send_email(self, to_email: str, subject: str, body: str, 
                        body_type: str = 'html', sender: str = None) -> Dict[str, Any]:
        """Send an email via Gmail API"""
        if not self.service:
            raise ValueError("Gmail service not authenticated")
        
        try:
            # Use default sender if not provided
            if not sender:
                # Get the authenticated user's email
                profile = self.service.users().getProfile(userId='me').execute()
                sender = profile['emailAddress']
            
            # Create the message
            message = self._create_message(sender, to_email, subject, body, body_type)
            
            # Send the message
            sent_message = self.service.users().messages().send(
                userId='me', body=message
            ).execute()
            
            logger.info(f"Email sent successfully to {to_email}. Message ID: {sent_message['id']}")
            
            return {
                "message_id": sent_message['id'],
                "status": "sent",
                "to": to_email,
                "subject": subject,
                "sent_at": datetime.now().isoformat()
            }
            
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return {
                "error": str(error),
                "status": "failed",
                "to": to_email,
                "subject": subject
            }
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "to": to_email,
                "subject": subject
            }
    
    async def send_appointment_confirmation(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send appointment confirmation email"""
        try:
            to_email = appointment_data['to_email']
            patient_name = appointment_data['patient_name']
            doctor_name = appointment_data['doctor_name']
            appointment_date = appointment_data['appointment_date']
            appointment_time = appointment_data['appointment_time']
            appointment_id = appointment_data['appointment_id']
            
            subject = f"Appointment Confirmation - {appointment_date}"
            
            # Create HTML email body
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .appointment-details {{ background-color: white; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Appointment Confirmed</h1>
                    </div>
                    <div class="content">
                        <p>Dear {patient_name},</p>
                        <p>Your appointment has been successfully scheduled. Here are the details:</p>
                        
                        <div class="appointment-details">
                            <h3>Appointment Information</h3>
                            <p><strong>Doctor:</strong> {doctor_name}</p>
                            <p><strong>Date:</strong> {appointment_date}</p>
                            <p><strong>Time:</strong> {appointment_time}</p>
                            <p><strong>Appointment ID:</strong> {appointment_id}</p>
                        </div>
                        
                        <p>Please arrive 10 minutes before your scheduled appointment time.</p>
                        <p>If you need to reschedule or cancel, please contact us at least 24 hours in advance.</p>
                        
                        <p>Best regards,<br>MedAI Team</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated message. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Send the email
            result = await self.send_email(to_email, subject, html_body, 'html')
            
            # Add appointment context to result
            result.update({
                "appointment_id": appointment_id,
                "patient_name": patient_name,
                "doctor_name": doctor_name,
                "appointment_date": appointment_date,
                "appointment_time": appointment_time
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending appointment confirmation: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "appointment_data": appointment_data
            }
    
    async def send_appointment_reminder(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send appointment reminder email"""
        try:
            to_email = appointment_data['to_email']
            patient_name = appointment_data['patient_name']
            doctor_name = appointment_data['doctor_name']
            appointment_date = appointment_data['appointment_date']
            appointment_time = appointment_data['appointment_time']
            
            subject = f"Appointment Reminder - Tomorrow at {appointment_time}"
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #2196F3; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .reminder {{ background-color: white; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Appointment Reminder</h1>
                    </div>
                    <div class="content">
                        <p>Dear {patient_name},</p>
                        <p>This is a friendly reminder about your upcoming appointment:</p>
                        
                        <div class="reminder">
                            <h3>Appointment Details</h3>
                            <p><strong>Doctor:</strong> {doctor_name}</p>
                            <p><strong>Date:</strong> {appointment_date}</p>
                            <p><strong>Time:</strong> {appointment_time}</p>
                        </div>
                        
                        <p>Please remember to:</p>
                        <ul>
                            <li>Arrive 10 minutes early</li>
                            <li>Bring your ID and insurance information</li>
                            <li>Bring a list of current medications</li>
                        </ul>
                        
                        <p>If you need to reschedule, please contact us immediately.</p>
                        
                        <p>Best regards,<br>MedAI Team</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated reminder. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            result = await self.send_email(to_email, subject, html_body, 'html')
            result.update({
                "type": "reminder",
                "patient_name": patient_name,
                "doctor_name": doctor_name,
                "appointment_date": appointment_date,
                "appointment_time": appointment_time
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending appointment reminder: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "appointment_data": appointment_data
            }
    
    async def send_cancellation_notification(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send appointment cancellation notification"""
        try:
            to_email = appointment_data['to_email']
            patient_name = appointment_data['patient_name']
            doctor_name = appointment_data['doctor_name']
            appointment_date = appointment_data['appointment_date']
            appointment_time = appointment_data['appointment_time']
            reason = appointment_data.get('reason', 'No reason provided')
            
            subject = f"Appointment Cancelled - {appointment_date}"
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #f44336; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .cancellation {{ background-color: white; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Appointment Cancelled</h1>
                    </div>
                    <div class="content">
                        <p>Dear {patient_name},</p>
                        <p>Your appointment has been cancelled:</p>
                        
                        <div class="cancellation">
                            <h3>Cancelled Appointment</h3>
                            <p><strong>Doctor:</strong> {doctor_name}</p>
                            <p><strong>Date:</strong> {appointment_date}</p>
                            <p><strong>Time:</strong> {appointment_time}</p>
                            <p><strong>Reason:</strong> {reason}</p>
                        </div>
                        
                        <p>To reschedule, please contact us or use our online booking system.</p>
                        
                        <p>Best regards,<br>MedAI Team</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated notification. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            result = await self.send_email(to_email, subject, html_body, 'html')
            result.update({
                "type": "cancellation",
                "patient_name": patient_name,
                "doctor_name": doctor_name,
                "appointment_date": appointment_date,
                "appointment_time": appointment_time,
                "reason": reason
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending cancellation notification: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "appointment_data": appointment_data
            }
    
    def get_authentication_status(self) -> Dict[str, Any]:
        """Get the current authentication status"""
        if self.service:
            try:
                profile = self.service.users().getProfile(userId='me').execute()
                return {
                    "authenticated": True,
                    "email": profile['emailAddress'],
                    "messages_total": profile.get('messagesTotal', 0),
                    "threads_total": profile.get('threadsTotal', 0)
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

# Global Gmail service instance
gmail_service = GmailService()