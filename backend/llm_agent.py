"""
LLM Agent implementation for agentic AI doctor appointment system
Uses OpenAI's function calling to orchestrate MCP tools
"""
import openai
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
import logging
from dataclasses import dataclass

from config import settings
from session_manager import ConversationSession

logger = logging.getLogger(__name__)

@dataclass
class AgentResponse:
    message: str
    tool_calls: List[Dict[str, Any]]
    requires_confirmation: bool = False
    pending_action: Optional[Dict[str, Any]] = None
    suggestions: List[str] = None

class DoctorAppointmentAgent:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.system_prompt = self._build_system_prompt()
        self.function_definitions = self._build_function_definitions()
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the AI agent"""
        return """You are an intelligent medical appointment assistant that helps patients schedule appointments and provides doctors with appointment analytics.

CORE CAPABILITIES:
- Schedule appointments with doctors based on availability
- Check doctor availability for specific dates/times
- Provide appointment statistics and reports for doctors
- Search patients by symptoms
- Handle multi-turn conversations with context

PERSONALITY:
- Professional, empathetic, and helpful
- Clear and concise communication
- Proactive in suggesting alternatives when requested slots aren't available
- Always confirm important details before taking actions

WORKFLOW GUIDELINES:
1. For appointment scheduling:
   - Always check availability first before scheduling
   - Confirm patient details (name, email, symptoms)
   - Offer alternative times if preferred slot is unavailable
   - Ask for confirmation before finalizing appointments

2. For doctor queries:
   - Provide clear, actionable statistics
   - Highlight important trends or patterns
   - Suggest follow-up actions when appropriate

3. For multi-turn conversations:
   - Remember context from previous messages
   - Reference earlier conversation points
   - Handle confirmations and modifications gracefully

IMPORTANT RULES:
- Always use tools to get real-time data rather than making assumptions
- Confirm appointment details before scheduling
- Be helpful in suggesting alternatives
- Maintain patient privacy and professionalism
- Handle errors gracefully and suggest solutions

Current date: {current_date}
Current time: {current_time}
""".format(
            current_date=date.today().strftime("%Y-%m-%d"),
            current_time=datetime.now().strftime("%H:%M")
        )
    
    def _build_function_definitions(self) -> List[Dict[str, Any]]:
        """Build OpenAI function definitions for MCP tools"""
        return [
            {
                "name": "check_doctor_availability",
                "description": "Check doctor availability for a specific date and time preference",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "doctor_name": {
                            "type": "string",
                            "description": "Name of the doctor (e.g., 'Dr. Ahuja', 'Dr. Johnson')"
                        },
                        "date": {
                            "type": "string",
                            "description": "Date in YYYY-MM-DD format"
                        },
                        "time_preference": {
                            "type": "string",
                            "description": "Time preference: 'morning', 'afternoon', 'evening', or specific time like '14:00'"
                        }
                    },
                    "required": ["doctor_name", "date"]
                }
            },
            {
                "name": "schedule_appointment",
                "description": "Schedule an appointment with a doctor",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "doctor_name": {
                            "type": "string",
                            "description": "Name of the doctor"
                        },
                        "patient_name": {
                            "type": "string",
                            "description": "Patient's full name"
                        },
                        "patient_email": {
                            "type": "string",
                            "description": "Patient's email address"
                        },
                        "appointment_date": {
                            "type": "string",
                            "description": "Date in YYYY-MM-DD format"
                        },
                        "appointment_time": {
                            "type": "string",
                            "description": "Time in HH:MM format (24-hour)"
                        },
                        "symptoms": {
                            "type": "string",
                            "description": "Patient's symptoms or reason for visit"
                        }
                    },
                    "required": ["doctor_name", "patient_name", "patient_email", "appointment_date", "appointment_time"]
                }
            },
            {
                "name": "get_appointment_stats",
                "description": "Get appointment statistics for doctors",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "doctor_name": {
                            "type": "string",
                            "description": "Name of the doctor (optional, leave empty for all doctors)"
                        },
                        "date_range": {
                            "type": "string",
                            "description": "Date range: 'today', 'yesterday', 'week', 'month'"
                        },
                        "filter_by": {
                            "type": "string",
                            "description": "Filter by 'symptoms' to get symptom breakdown, or leave empty"
                        }
                    },
                    "required": ["date_range"]
                }
            },
            {
                "name": "search_patients_by_symptom",
                "description": "Search patients by symptoms",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symptom": {
                            "type": "string",
                            "description": "Symptom to search for (e.g., 'fever', 'cough', 'headache')"
                        },
                        "doctor_name": {
                            "type": "string",
                            "description": "Name of the doctor (optional)"
                        },
                        "date_range": {
                            "type": "string",
                            "description": "Date range: 'week', 'month', or leave empty for all time"
                        }
                    },
                    "required": ["symptom"]
                }
            },
            {
                "name": "get_doctor_schedule",
                "description": "Get doctor's schedule for a specific date range",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "doctor_name": {
                            "type": "string",
                            "description": "Name of the doctor"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DD format"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date in YYYY-MM-DD format"
                        }
                    },
                    "required": ["doctor_name", "start_date", "end_date"]
                }
            }
        ]
    
    def _parse_relative_date(self, date_str: str) -> str:
        """Parse relative dates like 'tomorrow', 'today', 'next Friday'"""
        date_str = date_str.lower().strip()
        today = date.today()
        
        if date_str in ['today']:
            return today.strftime("%Y-%m-%d")
        elif date_str in ['tomorrow']:
            return (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif date_str in ['yesterday']:
            return (today - timedelta(days=1)).strftime("%Y-%m-%d")
        elif 'next week' in date_str:
            return (today + timedelta(days=7)).strftime("%Y-%m-%d")
        elif 'next' in date_str and 'monday' in date_str:
            days_ahead = 0 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        # Add more relative date parsing as needed
        else:
            # Try to parse as regular date
            try:
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
                return parsed_date.strftime("%Y-%m-%d")
            except:
                return today.strftime("%Y-%m-%d")  # Default to today
    
    def _extract_patient_info_from_context(self, session: ConversationSession, message: str) -> Dict[str, str]:
        """Extract patient information from session context or message"""
        patient_info = {}
        
        # Check session context first
        if session:
            patient_info['name'] = session.get_context('patient_name', '')
            patient_info['email'] = session.get_context('patient_email', '')
        
        # Try to extract from message if not in context
        # This is a simple implementation - could be enhanced with NER
        words = message.split()
        
        # Look for email patterns
        for word in words:
            if '@' in word and '.' in word:
                patient_info['email'] = word
                break
        
        return patient_info
    
    async def _execute_tool_call(self, tool_call: Dict[str, Any], mcp_executor) -> Dict[str, Any]:
        """Execute a single tool call using the MCP executor"""
        try:
            function_name = tool_call['function']['name']
            function_args = json.loads(tool_call['function']['arguments'])
            
            # Execute the MCP tool
            result = await mcp_executor(function_name, function_args)
            
            return {
                "tool_call_id": tool_call['id'],
                "function_name": function_name,
                "result": result
            }
        except Exception as e:
            logger.error(f"Error executing tool call: {str(e)}")
            return {
                "tool_call_id": tool_call['id'],
                "function_name": tool_call.get('function', {}).get('name', 'unknown'),
                "result": {"success": False, "message": f"Error: {str(e)}"}
            }
    
    async def process_message(
        self, 
        message: str, 
        session: ConversationSession,
        mcp_executor,
        user_type: str = "patient"
    ) -> AgentResponse:
        """Process a user message and return an agent response"""
        try:
            # Build conversation history for context
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history
            for hist in session.conversation_history[-5:]:  # Last 5 messages for context
                messages.append({"role": "user", "content": hist["user_message"]})
                messages.append({"role": "assistant", "content": hist["ai_response"]})
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Add user type context
            if user_type == "doctor":
                messages.append({
                    "role": "system", 
                    "content": "The user is a doctor asking for statistics or reports about their appointments."
                })
            
            # Call OpenAI with function calling
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                functions=self.function_definitions,
                function_call="auto",
                temperature=0.7,
                max_tokens=1000
            )
            
            assistant_message = response.choices[0].message
            tool_calls = []
            
            # Handle function calls
            if assistant_message.function_call:
                # Single function call (older format)
                function_call = assistant_message.function_call
                tool_call = {
                    "id": f"call_{datetime.now().timestamp()}",
                    "function": {
                        "name": function_call.name,
                        "arguments": function_call.arguments
                    }
                }
                
                # Execute the tool
                tool_result = await self._execute_tool_call(tool_call, mcp_executor)
                tool_calls.append(tool_result)
                
                # Generate follow-up response based on tool results
                follow_up_messages = messages + [
                    {"role": "assistant", "content": None, "function_call": function_call},
                    {"role": "function", "name": function_call.name, "content": json.dumps(tool_result["result"])}
                ]
                
                follow_up_response = await self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=follow_up_messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                final_message = follow_up_response.choices[0].message.content
                
            elif hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
                # Multiple function calls (newer format)
                for tool_call in assistant_message.tool_calls:
                    tool_result = await self._execute_tool_call(tool_call, mcp_executor)
                    tool_calls.append(tool_result)
                
                # Generate follow-up response
                tool_messages = []
                for tool_result in tool_calls:
                    tool_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_result["tool_call_id"],
                        "content": json.dumps(tool_result["result"])
                    })
                
                follow_up_messages = messages + [assistant_message] + tool_messages
                
                follow_up_response = await self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=follow_up_messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                final_message = follow_up_response.choices[0].message.content
                
            else:
                # No function calls, just return the message
                final_message = assistant_message.content
            
            # Check if we need confirmation for scheduling
            requires_confirmation = False
            pending_action = None
            
            if any(tool["function_name"] == "schedule_appointment" for tool in tool_calls):
                # Check if scheduling was successful
                schedule_results = [tool for tool in tool_calls if tool["function_name"] == "schedule_appointment"]
                if schedule_results and schedule_results[0]["result"].get("success"):
                    # Update session context
                    session.update_context("last_appointment", schedule_results[0]["result"].get("details"))
            
            # Generate suggestions based on context
            suggestions = self._generate_suggestions(message, tool_calls, user_type)
            
            return AgentResponse(
                message=final_message,
                tool_calls=tool_calls,
                requires_confirmation=requires_confirmation,
                pending_action=pending_action,
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return AgentResponse(
                message=f"I apologize, but I encountered an error processing your request: {str(e)}. Please try again or rephrase your request.",
                tool_calls=[],
                requires_confirmation=False,
                pending_action=None,
                suggestions=["Try rephrasing your request", "Check if all required information is provided"]
            )
    
    def _generate_suggestions(self, message: str, tool_calls: List[Dict], user_type: str) -> List[str]:
        """Generate helpful suggestions based on the conversation context"""
        suggestions = []
        
        if user_type == "patient":
            if not tool_calls:
                suggestions.extend([
                    "Try: 'I want to book an appointment with Dr. Ahuja tomorrow morning'",
                    "Ask: 'What doctors are available this week?'",
                    "Say: 'Check Dr. Johnson's availability for Friday afternoon'"
                ])
            elif any(tool["function_name"] == "check_doctor_availability" for tool in tool_calls):
                suggestions.extend([
                    "Book one of the available slots",
                    "Check another doctor's availability",
                    "Try a different date or time"
                ])
            elif any(tool["function_name"] == "schedule_appointment" for tool in tool_calls):
                suggestions.extend([
                    "Ask about appointment preparation",
                    "Request appointment reminder",
                    "Check other available appointments"
                ])
        
        elif user_type == "doctor":
            if not tool_calls:
                suggestions.extend([
                    "Ask: 'How many patients visited yesterday?'",
                    "Try: 'Show me appointments for today'",
                    "Say: 'How many patients with fever this week?'"
                ])
            elif any(tool["function_name"] == "get_appointment_stats" for tool in tool_calls):
                suggestions.extend([
                    "Get detailed symptom breakdown",
                    "Check different date ranges",
                    "Compare with previous periods"
                ])
        
        return suggestions[:3]  # Limit to 3 suggestions

# Global agent instance
agent = DoctorAppointmentAgent()
