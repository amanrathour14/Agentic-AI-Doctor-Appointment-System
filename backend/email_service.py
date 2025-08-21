"""
Email service integration for appointment confirmations and notifications
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
import logging
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.sendgrid_client = None
        self.smtp_config = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize email service with available providers"""
        # Try SendGrid first
        sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        if sendgrid_api_key:
            try:
                self.sendgrid_client = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)
                logger.info("Email service initialized with SendGrid")
                return
            except Exception as e:
                logger.error(f"Failed to initialize SendGrid: {str(e)}")
        
        # Fallback to SMTP
        smtp_host = os.getenv('SMTP_HOST')
        smtp_port = os.getenv('SMTP_PORT', '587')
        smtp_user = os.getenv('SMTP_USER')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        if all([smtp_host, smtp_user, smtp_password]):
            self.smtp_config = {
                'host': smtp_host,
                'port': int(smtp_port),
                'user': smtp_user,
                'password': smtp_password
            }
            logger.info("Email service initialized with SMTP")
        else:
            logger.warning("No email service configured. Email notifications disabled.")
    
    def is_available(self) -> bool:
        """Check if email service is available"""
        return self.sendgrid_client is not None or self.smtp_config is not None
    
    async def send_appointment_confirmation(
        self,
        patient_email: str,
        patient_name: str,
        doctor_name: str,
        appointment_date: str,
        appointment_time: str,
        symptoms: Optional[str] = None
    ) -> bool:
        """Send appointment confirmation email to patient"""
        if not self.is_available():
            logger.warning("Email service not available")
            return False
        
        subject = f"Appointment Confirmation - {doctor_name}"
        
        # Create email content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #8b5cf6; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
                .appointment-details {{ background-color: white; padding: 15px; border-radius: 6px; margin: 15px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 Appointment Confirmed</h1>
                </div>
                <div class="content">
                    <p>Dear {patient_name},</p>
                    
                    <p>Your appointment has been successfully scheduled. Here are the details:</p>
                    
                    <div class="appointment-details">
                        <h3>📅 Appointment Details</h3>
                        <p><strong>Doctor:</strong> {doctor_name}</p>
                        <p><strong>Date:</strong> {appointment_date}</p>
                        <p><strong>Time:</strong> {appointment_time}</p>
                        {f"<p><strong>Reason for visit:</strong> {symptoms}</p>" if symptoms else ""}
                    </div>
                    
                    <h3>📋 Important Reminders</h3>
                    <ul>
                        <li>Please arrive 15 minutes early for check-in</li>
                        <li>Bring a valid ID and insurance card</li>
                        <li>If you need to reschedule, please contact us at least 24 hours in advance</li>
                    </ul>
                    
                    <p>If you have any questions or need to make changes to your appointment, please reply to this email or contact our office.</p>
                    
                    <p>Thank you for choosing our healthcare services!</p>
                    
                    <p>Best regards,<br>
                    MedAI Assistant Team</p>
                </div>
                <div class="footer">
                    <p>This email was sent by MedAI Assistant - Intelligent Healthcare Scheduling</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Appointment Confirmation
        
        Dear {patient_name},
        
        Your appointment has been successfully scheduled:
        
        Doctor: {doctor_name}
        Date: {appointment_date}
        Time: {appointment_time}
        {f"Reason for visit: {symptoms}" if symptoms else ""}
        
        Important Reminders:
        - Please arrive 15 minutes early for check-in
        - Bring a valid ID and insurance card
        - Contact us 24 hours in advance for rescheduling
        
        Thank you for choosing our healthcare services!
        
        Best regards,
        MedAI Assistant Team
        """
        
        return await self._send_email(
            to_email=patient_email,
            to_name=patient_name,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_doctor_notification(
        self,
        doctor_email: str,
        doctor_name: str,
        patient_name: str,
        appointment_date: str,
        appointment_time: str,
        symptoms: Optional[str] = None
    ) -> bool:
        """Send appointment notification to doctor"""
        if not self.is_available():
            return False
        
        subject = f"New Appointment Scheduled - {patient_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #1f2937; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
                .appointment-details {{ background-color: white; padding: 15px; border-radius: 6px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🩺 New Appointment Scheduled</h1>
                </div>
                <div class="content">
                    <p>Dear Dr. {doctor_name},</p>
                    
                    <p>A new appointment has been scheduled with you:</p>
                    
                    <div class="appointment-details">
                        <h3>📅 Appointment Details</h3>
                        <p><strong>Patient:</strong> {patient_name}</p>
                        <p><strong>Date:</strong> {appointment_date}</p>
                        <p><strong>Time:</strong> {appointment_time}</p>
                        {f"<p><strong>Symptoms/Reason:</strong> {symptoms}</p>" if symptoms else ""}
                    </div>
                    
                    <p>This appointment was scheduled via the MedAI Assistant system.</p>
                    
                    <p>Best regards,<br>
                    MedAI Assistant System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        New Appointment Scheduled
        
        Dear Dr. {doctor_name},
        
        A new appointment has been scheduled:
        
        Patient: {patient_name}
        Date: {appointment_date}
        Time: {appointment_time}
        {f"Symptoms/Reason: {symptoms}" if symptoms else ""}
        
        This appointment was scheduled via the MedAI Assistant system.
        
        Best regards,
        MedAI Assistant System
        """
        
        return await self._send_email(
            to_email=doctor_email,
            to_name=doctor_name,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    async def _send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> bool:
        """Send email using available service"""
        try:
            if self.sendgrid_client:
                return await self._send_via_sendgrid(to_email, to_name, subject, html_content, text_content)
            elif self.smtp_config:
                return await self._send_via_smtp(to_email, to_name, subject, html_content, text_content)
            else:
                logger.error("No email service available")
                return False
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    async def _send_via_sendgrid(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> bool:
        """Send email via SendGrid"""
        try:
            from_email = Email(os.getenv('FROM_EMAIL', 'noreply@medai-assistant.com'), 'MedAI Assistant')
            to_email_obj = To(to_email, to_name)
            
            mail = Mail(
                from_email=from_email,
                to_emails=to_email_obj,
                subject=subject,
                html_content=Content("text/html", html_content),
                plain_text_content=Content("text/plain", text_content)
            )
            
            response = self.sendgrid_client.send(mail)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"SendGrid error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"SendGrid error: {str(e)}")
            return False
    
    async def _send_via_smtp(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> bool:
        """Send email via SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = os.getenv('FROM_EMAIL', 'noreply@medai-assistant.com')
            msg['To'] = to_email
            
            # Add text and HTML parts
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['user'], self.smtp_config['password'])
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email} via SMTP")
            return True
            
        except Exception as e:
            logger.error(f"SMTP error: {str(e)}")
            return False

# Global email service instance
email_service = EmailService()
