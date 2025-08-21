"""
Test script for the LLM agent functionality
"""
import asyncio
import sys
import os
sys.path.append('../backend')

from llm_agent import agent
from session_manager import session_manager
from prompt_examples import get_test_prompts
from config import settings

async def mock_mcp_executor(tool_name: str, parameters: dict):
    """Mock MCP executor for testing"""
    print(f"🔧 Tool called: {tool_name}")
    print(f"📋 Parameters: {parameters}")
    
    # Return mock responses
    if tool_name == "check_doctor_availability":
        return {
            "doctor_name": parameters.get("doctor_name", "Dr. Test"),
            "date": parameters.get("date"),
            "available_slots": ["09:00", "10:30", "14:00", "15:30"],
            "message": "Found 4 available slots"
        }
    elif tool_name == "schedule_appointment":
        return {
            "success": True,
            "appointment_id": 123,
            "message": "Appointment scheduled successfully",
            "details": {
                "doctor": parameters.get("doctor_name"),
                "patient": parameters.get("patient_name"),
                "date": parameters.get("appointment_date"),
                "time": parameters.get("appointment_time")
            }
        }
    elif tool_name == "get_appointment_stats":
        return {
            "stats": {
                "total_appointments": 15,
                "scheduled": 8,
                "completed": 5,
                "cancelled": 2
            },
            "message": "Retrieved statistics"
        }
    else:
        return {"message": f"Mock response for {tool_name}"}

async def test_single_prompt(prompt: str, user_type: str = "patient"):
    """Test a single prompt"""
    print(f"\n{'='*50}")
    print(f"🧪 Testing: {prompt}")
    print(f"👤 User type: {user_type}")
    print(f"{'='*50}")
    
    # Create session
    session_id = session_manager.create_session(user_type)
    session = session_manager.get_session(session_id)
    
    # Process message
    response = await agent.process_message(
        prompt, 
        session, 
        mock_mcp_executor, 
        user_type
    )
    
    print(f"🤖 Response: {response.message}")
    print(f"🔧 Tools used: {len(response.tool_calls)}")
    for tool in response.tool_calls:
        print(f"   - {tool['function_name']}")
    print(f"💡 Suggestions: {response.suggestions}")
    
    return response

async def test_multi_turn_conversation():
    """Test multi-turn conversation"""
    print(f"\n{'='*50}")
    print(f"🔄 Testing Multi-turn Conversation")
    print(f"{'='*50}")
    
    # Create session
    session_id = session_manager.create_session("patient")
    session = session_manager.get_session(session_id)
    
    conversation = [
        "Check Dr. Ahuja's availability for tomorrow",
        "Book the 2 PM slot for John Smith, email john@example.com",
        "What symptoms should I mention?"
    ]
    
    for i, message in enumerate(conversation, 1):
        print(f"\n--- Turn {i} ---")
        print(f"👤 User: {message}")
        
        response = await agent.process_message(
            message, 
            session, 
            mock_mcp_executor, 
            "patient"
        )
        
        print(f"🤖 Assistant: {response.message}")
        if response.tool_calls:
            print(f"🔧 Tools: {[tool['function_name'] for tool in response.tool_calls]}")

async def main():
    """Main test function"""
    if not settings.openai_api_key:
        print("❌ OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        return
    
    print("🚀 Starting LLM Agent Tests")
    
    # Test patient prompts
    print("\n📋 Testing Patient Prompts")
    patient_prompts = [
        "I want to book an appointment with Dr. Ahuja tomorrow morning",
        "What doctors are available this Friday?",
        "I have a fever and need to see a doctor today"
    ]
    
    for prompt in patient_prompts:
        await test_single_prompt(prompt, "patient")
    
    # Test doctor prompts
    print("\n👨‍⚕️ Testing Doctor Prompts")
    doctor_prompts = [
        "How many patients visited yesterday?",
        "Show me my appointments for today",
        "How many patients with fever this week?"
    ]
    
    for prompt in doctor_prompts:
        await test_single_prompt(prompt, "doctor")
    
    # Test multi-turn conversation
    await test_multi_turn_conversation()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
