"""
Database models for the doctor appointment system using SQLAlchemy with MySQL
"""
from sqlalchemy import create_engine, Column, Integer, String, Date, Time, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
from datetime import datetime, date, time
import os

Base = declarative_base()

class Doctor(Base):
    __tablename__ = 'doctors'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    specialization = Column(String(255), nullable=False)
    phone = Column(String(20))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    appointments = relationship("Appointment", back_populates="doctor")
    availability = relationship("DoctorAvailability", back_populates="doctor")
    visit_history = relationship("VisitHistory", back_populates="doctor")

class Patient(Base):
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    date_of_birth = Column(Date)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    appointments = relationship("Appointment", back_populates="patient")
    visit_history = relationship("VisitHistory", back_populates="patient")

class Appointment(Base):
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    doctor_id = Column(Integer, ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)
    patient_id = Column(Integer, ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, default=30)
    status = Column(String(50), default='scheduled')  # scheduled, completed, cancelled, no_show
    notes = Column(Text)
    symptoms = Column(Text)
    google_calendar_event_id = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    doctor = relationship("Doctor", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")
    visit_history = relationship("VisitHistory", back_populates="appointment")

class VisitHistory(Base):
    __tablename__ = 'visit_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id', ondelete='CASCADE'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)
    patient_id = Column(Integer, ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    visit_date = Column(Date, nullable=False)
    diagnosis = Column(Text)
    symptoms = Column(Text)
    treatment = Column(Text)
    follow_up_required = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    appointment = relationship("Appointment", back_populates="visit_history")
    doctor = relationship("Doctor", back_populates="visit_history")
    patient = relationship("Patient", back_populates="visit_history")

class DoctorAvailability(Base):
    __tablename__ = 'doctor_availability'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    doctor_id = Column(Integer, ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 1=Monday, 2=Tuesday, etc.
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    doctor = relationship("Doctor", back_populates="availability")

# Database connection and session management
def get_database_url():
    """Get database URL from environment variables"""
    return os.getenv('DATABASE_URL', 'mysql+pymysql://medai_user:medai_password@127.0.0.1:3306/doctor_appointments')

def create_database_engine():
    """Create database engine with MySQL-specific configurations"""
    database_url = get_database_url()
    return create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False,
        # MySQL-specific configurations
        connect_args={
            "charset": "utf8mb4",
            "use_unicode": True,
            "autocommit": False
        }
    )

def get_session():
    """Get database session"""
    engine = create_database_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def create_tables():
    """Create all tables"""
    engine = create_database_engine()
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    # Create tables when run directly
    create_tables()
    print("MySQL database tables created successfully!")
