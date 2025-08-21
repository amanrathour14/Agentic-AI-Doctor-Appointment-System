"""
Interactive demo script for the agentic AI doctor appointment system
Demonstrates key features and capabilities
"""
import asyncio
import sys
import json
from datetime import datetime, date, timedelta

sys.path.append('.')
sys.path.append('./backend')

from database_models import get_session, Doctor, Patient, Appointment
from backend.session_manager import session_manager
from backend.llm_agent import agent
from backend.config import settings

class DemoRunner:
    def __init__(self):
        self.db = get_session()
        self.session = None
    
    def print_header(self, title):
        print("\n" + "=" * 60)
        print(f"🎯 {title}")
        print("=" * 60)
    
    def print_step(self, step, description):
        print(f"\n📍 Step {step}: {description}")
        print("-" * 40)
    
    async def demo_patient_flow(self):
        """Demonstrate patient appointment booking flow"""
        self.print_header("PATIENT FLOW DEMONSTRATION")
        
        # Create patient session
        self.print_step(1, "Creating Patient Session")
        session_id = session_manager.create_session("patient")
        self.session = session_manager.get_session(session_id)
        print(f"✅ Created patient session: {session_id}")
        
        # Mock MCP tool executor for demo
        async def demo_execute_tool(tool_name, parameters):
            print(f"🔧 Executing MCP Tool: {tool_name}")
            print(f"   Parameters: {json.dumps(parameters, indent=2)}")
            
            # Simulate tool responses
            if tool_name == "check_doctor_availability":
                return {
                    "tool_name": tool_name,
                    "result": {
                        "doctor_name": parameters.get("doctor_name", "Dr. Smith"),
                        "date": parameters.get("date"),
                        "available_slots": ["09:00", "10:30", "14:00", "15:30"],
                        "message": f"Found 4 available slots for {parameters.get('doctor_name', 'Dr. Smith')}"
                    },
                    "success": True
                }
            elif tool_name == "schedule_appointment":
                return {
                    "tool_name": tool_name,
                    "result": {
                        "success": True,
                        "appointment_id": 123,
                        "message": "Appointment scheduled successfully",
                        "details": {
                            "doctor": parameters.get("doctor_name"),
                            "patient": parameters.get("patient_name"),
                            "date": parameters.get("appointment_date"),
                            "time": parameters.get("appointment_time")
                        }
                    },
                    "success": True
                }
            
            return {"tool_name": tool_name, "result": {"message": "Demo result"}, "success": True}
        
        # Demo conversation flow
        demo_messages = [
            "Hello, I need to book an appointment with Dr. Smith",
            "I'm available tomorrow morning, what times do you have?",
            "10:30 AM works perfect for me. My name is John Doe and my email is john@example.com",
            "I've been having headaches for the past week"
        ]
        
        for i, message in enumerate(demo_messages, 1):
            self.print_step(i + 1, f"Patient Message")
            print(f"👤 Patient: {message}")
            
            if settings.openai_api_key:
                try:
                    response = await agent.process_message(
                        message,
                        self.session,
                        demo_execute_tool,
                        "patient"
                    )
                    print(f"🤖 AI Assistant: {response.message}")
                    
                    if response.tool_calls:
                        print(f"🔧 Tools Used: {[tool['name'] for tool in response.tool_calls]}")
                    
                    if response.suggestions:
                        print(f"💡 Suggestions: {', '.join(response.suggestions)}")
                        
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
            else:
                print("🤖 AI Assistant: [OpenAI API key not configured - demo mode]")
                print("   In a real system, the AI would:")
                print("   - Understand your request")
                print("   - Check doctor availability")
                print("   - Schedule the appointment")
                print("   - Send confirmations")
            
            await asyncio.sleep(1)  # Pause for readability
    
    async def demo_doctor_flow(self):
        """Demonstrate doctor dashboard and statistics flow"""
        self.print_header("DOCTOR FLOW DEMONSTRATION")
        
        # Create doctor session
        self.print_step(1, "Creating Doctor Session")
        session_id = session_manager.create_session("doctor")
        self.session = session_manager.get_session(session_id)
        print(f"✅ Created doctor session: {session_id}")
        
        # Mock MCP tool executor for doctor demo
        async def doctor_execute_tool(tool_name, parameters):
            print(f"🔧 Executing MCP Tool: {tool_name}")
            print(f"   Parameters: {json.dumps(parameters, indent=2)}")
            
            if tool_name == "get_appointment_stats":
                return {
                    "tool_name": tool_name,
                    "result": {
                        "stats": {
                            "total_appointments": 25,
                            "scheduled": 18,
                            "completed": 5,
                            "cancelled": 2,
                            "no_show": 0
                        },
                        "date_range": parameters.get("date_range", "week"),
                        "message": "Retrieved statistics for this week"
                    },
                    "success": True
                }
            elif tool_name == "get_doctor_schedule":
                return {
                    "tool_name": tool_name,
                    "result": {
                        "doctor_name": "Dr. Smith",
                        "schedule": [
                            {"date": "2024-01-15", "time": "09:00", "patient": "John Doe", "status": "scheduled", "symptoms": "headache"},
                            {"date": "2024-01-15", "time": "10:30", "patient": "Jane Smith", "status": "scheduled", "symptoms": "checkup"},
                            {"date": "2024-01-15", "time": "14:00", "patient": "Bob Johnson", "status": "scheduled", "symptoms": "fever"}
                        ],
                        "total_appointments": 3,
                        "message": "Retrieved schedule for Dr. Smith"
                    },
                    "success": True
                }
            elif tool_name == "search_patients_by_symptom":
                return {
                    "tool_name": tool_name,
                    "result": {
                        "patients": [
                            {"patient_name": "John Doe", "appointment_date": "2024-01-15", "symptoms": "headache", "doctor": "Dr. Smith", "status": "scheduled"},
                            {"patient_name": "Alice Brown", "appointment_date": "2024-01-12", "symptoms": "severe headache", "doctor": "Dr. Smith", "status": "completed"}
                        ],
                        "count": 2,
                        "symptom": parameters.get("symptom"),
                        "message": f"Found 2 patients with symptom '{parameters.get('symptom')}'"
                    },
                    "success": True
                }
            
            return {"tool_name": tool_name, "result": {"message": "Demo result"}, "success": True}
        
        # Demo doctor conversation flow
        doctor_messages = [
            "Show me my appointment statistics for this week",
            "What's my schedule for today?",
            "How many patients with headaches have I seen recently?"
        ]
        
        for i, message in enumerate(doctor_messages, 1):
            self.print_step(i + 1, f"Doctor Query")
            print(f"👨‍⚕️ Doctor: {message}")
            
            if settings.openai_api_key:
                try:
                    response = await agent.process_message(
                        message,
                        self.session,
                        doctor_execute_tool,
                        "doctor"
                    )
                    print(f"🤖 AI Assistant: {response.message}")
                    
                    if response.tool_calls:
                        print(f"🔧 Tools Used: {[tool['name'] for tool in response.tool_calls]}")
                        
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
            else:
                print("🤖 AI Assistant: [OpenAI API key not configured - demo mode]")
                print("   In a real system, the AI would:")
                print("   - Analyze your request")
                print("   - Query appointment statistics")
                print("   - Generate reports and insights")
                print("   - Provide actionable information")
            
            await asyncio.sleep(1)
    
    def demo_database_content(self):
        """Show current database content"""
        self.print_header("DATABASE CONTENT OVERVIEW")
        
        try:
            # Show doctors
            doctors = self.db.query(Doctor).all()
            print(f"👨‍⚕️ Doctors in system: {len(doctors)}")
            for doctor in doctors[:3]:  # Show first 3
                print(f"   - {doctor.name} ({doctor.specialization})")
            
            # Show patients
            patients = self.db.query(Patient).all()
            print(f"\n👤 Patients in system: {len(patients)}")
            for patient in patients[:3]:  # Show first 3
                print(f"   - {patient.name} ({patient.email})")
            
            # Show appointments
            appointments = self.db.query(Appointment).all()
            print(f"\n📅 Appointments in system: {len(appointments)}")
            for appointment in appointments[:3]:  # Show first 3
                print(f"   - {appointment.patient.name} with {appointment.doctor.name} on {appointment.appointment_date}")
                
        except Exception as e:
            print(f"❌ Error accessing database: {str(e)}")
    
    def demo_system_capabilities(self):
        """Demonstrate system capabilities"""
        self.print_header("SYSTEM CAPABILITIES OVERVIEW")
        
        capabilities = [
            "🤖 Agentic AI with autonomous tool selection",
            "💬 Natural language appointment scheduling",
            "📊 Real-time appointment statistics and analytics",
            "🔔 WebSocket-based real-time notifications",
            "📧 Automated email confirmations and reminders",
            "📅 Google Calendar integration for appointment sync",
            "🏥 Multi-doctor and multi-patient management",
            "🔍 Symptom-based patient search and analysis",
            "📱 Responsive web interface for all devices",
            "🔐 Session-based conversation management",
            "⚡ High-performance FastAPI backend",
            "🗄️ PostgreSQL database with SQLAlchemy ORM"
        ]
        
        print("This system demonstrates:")
        for capability in capabilities:
            print(f"  {capability}")
        
        print(f"\n🔧 MCP Tools Available:")
        mcp_tools = [
            "check_doctor_availability - Find available appointment slots",
            "schedule_appointment - Book appointments with validation",
            "get_appointment_stats - Generate statistical reports",
            "search_patients_by_symptom - Find patients by symptoms",
            "get_doctor_schedule - Retrieve doctor schedules"
        ]
        
        for tool in mcp_tools:
            print(f"  • {tool}")
    
    async def run_full_demo(self):
        """Run the complete system demonstration"""
        print("🎬 AGENTIC AI DOCTOR APPOINTMENT SYSTEM - INTERACTIVE DEMO")
        print("This demo showcases the key features and capabilities of the system")
        
        # System overview
        self.demo_system_capabilities()
        
        # Database content
        self.demo_database_content()
        
        # Patient flow demo
        await self.demo_patient_flow()
        
        # Doctor flow demo
        await self.demo_doctor_flow()
        
        # Conclusion
        self.print_header("DEMO CONCLUSION")
        print("🎉 Demo completed successfully!")
        print("\nKey takeaways:")
        print("  ✅ Agentic AI automatically selects appropriate tools")
        print("  ✅ Natural language processing for complex requests")
        print("  ✅ Multi-turn conversations with context awareness")
        print("  ✅ Real-time notifications and integrations")
        print("  ✅ Comprehensive appointment management system")
        
        print(f"\n🚀 To interact with the live system:")
        print("  1. Ensure the FastAPI backend is running (python backend/main.py)")
        print("  2. Open the React frontend in your browser")
        print("  3. Select your role (Patient or Doctor)")
        print("  4. Start chatting with the AI assistant!")
        
        # Cleanup
        if self.db:
            self.db.close()

async def main():
    """Main demo function"""
    demo = DemoRunner()
    await demo.run_full_demo()

if __name__ == "__main__":
    print("🎯 Starting Interactive System Demo...")
    asyncio.run(main())
