"""
Configuration settings for the MedAI Doctor Appointment System
"""
import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database Configuration
    database_url: str = os.getenv('DATABASE_URL', 'mysql+pymysql://medai_user:medai_password@127.0.0.1:3306/doctor_appointments')
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv('OPENAI_API_KEY', '')
    
    # Application Settings
    app_name: str = "MedAI Doctor Appointment System"
    app_version: str = "1.0.0"
    debug: bool = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # CORS Settings
    allowed_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Session Settings
    session_timeout_minutes: int = int(os.getenv('SESSION_TIMEOUT_MINUTES', '30'))
    
    # Google Calendar Integration
    google_calendar_credentials: str = os.getenv('GOOGLE_CALENDAR_CREDENTIALS', '')
    
    # Gmail API Integration
    gmail_client_id: str = os.getenv('GMAIL_CLIENT_ID', '')
    gmail_client_secret: str = os.getenv('GMAIL_CLIENT_SECRET', '')
    gmail_refresh_token: str = os.getenv('GMAIL_REFRESH_TOKEN', '')
    gmail_user_email: str = os.getenv('GMAIL_USER_EMAIL', '')
    
    # Email Service Configuration
    sendgrid_api_key: str = os.getenv('SENDGRID_API_KEY', '')
    from_email: str = os.getenv('FROM_EMAIL', 'noreply@medai.com')
    
    # SMTP Configuration (alternative to SendGrid)
    smtp_host: str = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port: int = int(os.getenv('SMTP_PORT', '587'))
    smtp_user: str = os.getenv('SMTP_USER', '')
    smtp_password: str = os.getenv('SMTP_PASSWORD', '')
    
    class Config:
        env_file = ".env"
        extra = "allow"

# Create settings instance
settings = Settings()
