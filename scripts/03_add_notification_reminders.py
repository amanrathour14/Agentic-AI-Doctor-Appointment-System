"""
Background task to send appointment reminders
Run this script periodically (e.g., every 15 minutes) to send reminders
"""
import asyncio
import sys
sys.path.append('.')
from datetime import datetime, timedelta
from database_models import get_session, Appointment, Doctor
from backend.notification_service import notify_appointment_reminder

async def send_appointment_reminders():
    """Send reminders for upcoming appointments"""
    db = get_session()
    
    try:
        # Get appointments in the next 30 minutes
        now = datetime.now()
        reminder_time = now + timedelta(minutes=30)
        
        upcoming_appointments = db.query(Appointment).filter(
            Appointment.appointment_date == now.date(),
            Appointment.appointment_time >= now.time(),
            Appointment.appointment_time <= reminder_time.time(),
            Appointment.status == 'scheduled'
        ).all()
        
        print(f"Found {len(upcoming_appointments)} appointments needing reminders")
        
        for appointment in upcoming_appointments:
            # Calculate minutes until appointment
            appointment_datetime = datetime.combine(
                appointment.appointment_date, 
                appointment.appointment_time
            )
            minutes_until = int((appointment_datetime - now).total_seconds() / 60)
            
            if minutes_until > 0 and minutes_until <= 30:
                await notify_appointment_reminder(
                    doctor_id=appointment.doctor_id,
                    patient_name=appointment.patient.name,
                    appointment_date=appointment.appointment_date.strftime("%Y-%m-%d"),
                    appointment_time=appointment.appointment_time.strftime("%H:%M"),
                    minutes_until=minutes_until,
                    db=db
                )
                print(f"Sent reminder for appointment with {appointment.patient.name} in {minutes_until} minutes")
        
    except Exception as e:
        print(f"Error sending reminders: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(send_appointment_reminders())
