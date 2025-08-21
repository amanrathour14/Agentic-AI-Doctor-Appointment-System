"""
Session management for multi-turn conversations
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import json

class ConversationSession:
    def __init__(self, session_id: str, user_type: str = "patient"):
        self.session_id = session_id
        self.user_type = user_type
        self.context = {}
        self.conversation_history = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.pending_action = None
    
    def add_message(self, message: str, response: str, tool_calls: Optional[list] = None):
        """Add a message and response to conversation history"""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_message": message,
            "ai_response": response,
            "tool_calls": tool_calls or []
        })
        self.last_activity = datetime.now()
    
    def update_context(self, key: str, value: Any):
        """Update conversation context"""
        self.context[key] = value
        self.last_activity = datetime.now()
    
    def get_context(self, key: str, default: Any = None):
        """Get value from conversation context"""
        return self.context.get(key, default)
    
    def set_pending_action(self, action: Dict[str, Any]):
        """Set a pending action that requires confirmation"""
        self.pending_action = action
        self.last_activity = datetime.now()
    
    def clear_pending_action(self):
        """Clear pending action"""
        self.pending_action = None
        self.last_activity = datetime.now()
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session is expired"""
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, ConversationSession] = {}
    
    def create_session(self, user_type: str = "patient") -> str:
        """Create a new conversation session"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = ConversationSession(session_id, user_type)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get session by ID"""
        session = self.sessions.get(session_id)
        if session and session.is_expired():
            del self.sessions[session_id]
            return None
        return session
    
    def cleanup_expired_sessions(self, timeout_minutes: int = 30):
        """Remove expired sessions"""
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if session.is_expired(timeout_minutes)
        ]
        for sid in expired_sessions:
            del self.sessions[sid]

# Global session manager instance
session_manager = SessionManager()
