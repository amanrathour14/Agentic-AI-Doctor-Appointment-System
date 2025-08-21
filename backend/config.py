"""
Configuration management for the doctor appointment system
"""
import os
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/doctor_appointments')
    
    # API Keys
    openai_api_key: Optional[str] = os.getenv('OPENAI_API_KEY')
    google_calendar_credentials: Optional[str] = os.getenv('GOOGLE_CALENDAR_CREDENTIALS')
    sendgrid_api_key: Optional[str] = os.getenv('SENDGRID_API_KEY')
    
    # Application settings
    app_name: str = "Doctor Appointment AI System"
    app_version: str = "1.0.0"
    debug: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # CORS settings
    allowed_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Session settings
    session_timeout_minutes: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
