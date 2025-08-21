"""
Notification service for real-time doctor notifications
Handles WebSocket connections, notification storage, and delivery
"""
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import logging
import asyncio
from enum import Enum

# Import database models
import sys
sys.path.append('../scripts')
from database_models import get_session

logger = logging.getLogger(__name__)

class NotificationType(str, Enum):
    NEW_APPOINTMENT = "new_appointment"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    APPOINTMENT_REMINDER = "appointment_reminder"
    PATIENT_MESSAGE = "patient_message"
    SYSTEM_ALERT = "system_alert"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationManager:
    def __init__(self):
        # Store active WebSocket connections by doctor_id
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # Store notifications for offline doctors
        self.pending_notifications: Dict[int, List[Dict[str, Any]]] = {}
    
    async def connect(self, websocket: WebSocket, doctor_id: int):
        """Connect a doctor's WebSocket"""
        await websocket.accept()
        
        if doctor_id not in self.active_connections:
            self.active_connections[doctor_id] = []
        
        self.active_connections[doctor_id].append(websocket)
        logger.info(f"Doctor {doctor_id} connected to notifications")
        
        # Send any pending notifications
        if doctor_id in self.pending_notifications:
            for notification in self.pending_notifications[doctor_id]:
                await self.send_to_doctor(doctor_id, notification)
            # Clear pending notifications after sending
            del self.pending_notifications[doctor_id]
    
    def disconnect(self, websocket: WebSocket, doctor_id: int):
        """Disconnect a doctor's WebSocket"""
        if doctor_id in self.active_connections:
            if websocket in self.active_connections[doctor_id]:
                self.active_connections[doctor_id].remove(websocket)
            
            # Remove empty connection lists
            if not self.active_connections[doctor_id]:
                del self.active_connections[doctor_id]
        
        logger.info(f"Doctor {doctor_id} disconnected from notifications")
    
    async def send_to_doctor(self, doctor_id: int, notification: Dict[str, Any]):
        """Send notification to a specific doctor"""
        if doctor_id in self.active_connections:
            # Send to all active connections for this doctor
            disconnected_connections = []
            
            for connection in self.active_connections[doctor_id]:
                try:
                    await connection.send_text(json.dumps(notification))
                except Exception as e:
                    logger.error(f"Failed to send notification to doctor {doctor_id}: {str(e)}")
                    disconnected_connections.append(connection)
            
            # Remove disconnected connections
            for connection in disconnected_connections:
                self.active_connections[doctor_id].remove(connection)
            
            # Remove empty connection lists
            if not self.active_connections[doctor_id]:
                del self.active_connections[doctor_id]
        else:
            # Doctor is offline, store notification for later
            if doctor_id not in self.pending_notifications:
                self.pending_notifications[doctor_id] = []
            
            self.pending_notifications[doctor_id].append(notification)
            logger.info(f"Stored pending notification for offline doctor {doctor_id}")
    
    async def broadcast_to_all_doctors(self, notification: Dict[str, Any]):
        """Broadcast notification to all connected doctors"""
        for doctor_id in list(self.active_connections.keys()):
            await self.send_to_doctor(doctor_id, notification)
    
    async def create_notification(
        self,
        doctor_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        data: Optional[Dict[str, Any]] = None,
        db: Optional[Session] = None
    ):
        """Create and send a notification"""
        notification = {
            "id": f"notif_{datetime.now().timestamp()}",
            "doctor_id": doctor_id,
            "type": notification_type.value,
            "title": title,
            "message": message,
            "priority": priority.value,
            "data": data or {},
            "timestamp": datetime.now().isoformat(),
            "read": False
        }
        
        # Store in database if session provided
        if db:
            try:
                # Note: You would need to create a Notification table in your database
                # For now, we'll just log it
                logger.info(f"Notification created: {notification}")
            except Exception as e:
                logger.error(f"Failed to store notification in database: {str(e)}")
        
        # Send real-time notification
        await self.send_to_doctor(doctor_id, notification)
        
        return notification

# Global notification manager instance
notification_manager = NotificationManager()

# Helper functions for common notification types
async def notify_new_appointment(
    doctor_id: int,
    patient_name: str,
    appointment_date: str,
    appointment_time: str,
    symptoms: Optional[str] = None,
    db: Optional[Session] = None
):
    """Send notification for new appointment"""
    title = "New Appointment Scheduled"
    message = f"New appointment with {patient_name} on {appointment_date} at {appointment_time}"
    
    data = {
        "patient_name": patient_name,
        "appointment_date": appointment_date,
        "appointment_time": appointment_time,
        "symptoms": symptoms
    }
    
    await notification_manager.create_notification(
        doctor_id=doctor_id,
        notification_type=NotificationType.NEW_APPOINTMENT,
        title=title,
        message=message,
        priority=NotificationPriority.HIGH,
        data=data,
        db=db
    )

async def notify_appointment_cancelled(
    doctor_id: int,
    patient_name: str,
    appointment_date: str,
    appointment_time: str,
    db: Optional[Session] = None
):
    """Send notification for cancelled appointment"""
    title = "Appointment Cancelled"
    message = f"Appointment with {patient_name} on {appointment_date} at {appointment_time} has been cancelled"
    
    data = {
        "patient_name": patient_name,
        "appointment_date": appointment_date,
        "appointment_time": appointment_time
    }
    
    await notification_manager.create_notification(
        doctor_id=doctor_id,
        notification_type=NotificationType.APPOINTMENT_CANCELLED,
        title=title,
        message=message,
        priority=NotificationPriority.MEDIUM,
        data=data,
        db=db
    )

async def notify_appointment_reminder(
    doctor_id: int,
    patient_name: str,
    appointment_date: str,
    appointment_time: str,
    minutes_until: int,
    db: Optional[Session] = None
):
    """Send appointment reminder notification"""
    title = "Upcoming Appointment"
    message = f"Appointment with {patient_name} in {minutes_until} minutes ({appointment_time})"
    
    data = {
        "patient_name": patient_name,
        "appointment_date": appointment_date,
        "appointment_time": appointment_time,
        "minutes_until": minutes_until
    }
    
    await notification_manager.create_notification(
        doctor_id=doctor_id,
        notification_type=NotificationType.APPOINTMENT_REMINDER,
        title=title,
        message=message,
        priority=NotificationPriority.HIGH,
        data=data,
        db=db
    )

async def notify_system_alert(
    message: str,
    priority: NotificationPriority = NotificationPriority.MEDIUM,
    target_doctor_id: Optional[int] = None,
    db: Optional[Session] = None
):
    """Send system alert notification"""
    title = "System Alert"
    
    notification_data = {
        "alert_type": "system",
        "message": message
    }
    
    if target_doctor_id:
        await notification_manager.create_notification(
            doctor_id=target_doctor_id,
            notification_type=NotificationType.SYSTEM_ALERT,
            title=title,
            message=message,
            priority=priority,
            data=notification_data,
            db=db
        )
    else:
        # Broadcast to all doctors
        notification = {
            "id": f"notif_{datetime.now().timestamp()}",
            "type": NotificationType.SYSTEM_ALERT.value,
            "title": title,
            "message": message,
            "priority": priority.value,
            "data": notification_data,
            "timestamp": datetime.now().isoformat(),
            "read": False
        }
        await notification_manager.broadcast_to_all_doctors(notification)
