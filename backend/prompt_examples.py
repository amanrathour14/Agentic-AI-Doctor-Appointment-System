"""
Example prompts and expected behaviors for testing the LLM agent
"""

PATIENT_EXAMPLES = [
    {
        "prompt": "I want to book an appointment with Dr. Ahuja tomorrow morning",
        "expected_tools": ["check_doctor_availability", "schedule_appointment"],
        "description": "Should check availability first, then schedule if available"
    },
    {
        "prompt": "What doctors are available this Friday afternoon?",
        "expected_tools": ["check_doctor_availability"],
        "description": "Should check multiple doctors' availability"
    },
    {
        "prompt": "I have a fever and headache, can I see Dr. Johnson today?",
        "expected_tools": ["check_doctor_availability"],
        "description": "Should check availability and note symptoms"
    },
    {
        "prompt": "Book the 2 PM slot",
        "expected_tools": ["schedule_appointment"],
        "description": "Should use context from previous availability check"
    },
    {
        "prompt": "Cancel my appointment",
        "expected_tools": [],
        "description": "Should ask for clarification about which appointment"
    }
]

DOCTOR_EXAMPLES = [
    {
        "prompt": "How many patients visited yesterday?",
        "expected_tools": ["get_appointment_stats"],
        "description": "Should get stats for yesterday"
    },
    {
        "prompt": "Show me appointments for today and tomorrow",
        "expected_tools": ["get_doctor_schedule"],
        "description": "Should get schedule for date range"
    },
    {
        "prompt": "How many patients with fever this week?",
        "expected_tools": ["search_patients_by_symptom"],
        "description": "Should search for fever symptoms in past week"
    },
    {
        "prompt": "Give me a summary of my appointments this month",
        "expected_tools": ["get_appointment_stats"],
        "description": "Should get monthly statistics with breakdown"
    }
]

MULTI_TURN_EXAMPLES = [
    {
        "conversation": [
            {
                "user": "Check Dr. Ahuja's availability for Friday",
                "expected_tools": ["check_doctor_availability"]
            },
            {
                "user": "Book the 3 PM slot for John Smith",
                "expected_tools": ["schedule_appointment"],
                "context": "Should remember the doctor and date from previous message"
            }
        ]
    },
    {
        "conversation": [
            {
                "user": "How many appointments do I have today?",
                "expected_tools": ["get_appointment_stats"]
            },
            {
                "user": "What about tomorrow?",
                "expected_tools": ["get_appointment_stats"],
                "context": "Should understand 'tomorrow' in context"
            }
        ]
    }
]

def get_test_prompts():
    """Get all test prompts for validation"""
    return {
        "patient_examples": PATIENT_EXAMPLES,
        "doctor_examples": DOCTOR_EXAMPLES,
        "multi_turn_examples": MULTI_TURN_EXAMPLES
    }
