import { type NextRequest, NextResponse } from "next/server"

// Mock responses for different user types and queries
const generateMockResponse = (message: string, userType: string) => {
  const lowerMessage = message.toLowerCase()

  if (userType === "patient") {
    if (lowerMessage.includes("appointment") && lowerMessage.includes("dr")) {
      return {
        response:
          "I've checked Dr. Ahuja's availability for tomorrow morning. I found an available slot at 10:00 AM. Would you like me to book this appointment for you?",
        tool_calls: [
          {
            function_name: "check_doctor_availability",
            result: { available_slots: ["10:00 AM", "11:30 AM"], doctor: "Dr. Ahuja" },
          },
        ],
      }
    }

    if (lowerMessage.includes("available") && lowerMessage.includes("doctor")) {
      return {
        response:
          "I found several doctors available this Friday afternoon:\n\n• Dr. Johnson (Cardiology) - 2:00 PM, 3:30 PM\n• Dr. Smith (General Medicine) - 1:00 PM, 4:00 PM\n• Dr. Brown (Dermatology) - 2:30 PM\n\nWould you like to book with any of these doctors?",
        tool_calls: [
          {
            function_name: "check_doctor_availability",
            result: { available_doctors: 3, total_slots: 5 },
          },
        ],
      }
    }

    return {
      response:
        "I understand you're looking for medical assistance. I can help you:\n\n• Schedule appointments with available doctors\n• Check doctor availability\n• Answer questions about your healthcare\n\nPlease let me know what specific help you need!",
      tool_calls: [],
    }
  } else {
    // Doctor responses
    if (lowerMessage.includes("patients") && lowerMessage.includes("yesterday")) {
      return {
        response:
          "Based on your appointment records, you had 12 patients yesterday:\n\n• 8 regular checkups\n• 3 follow-up appointments\n• 1 emergency consultation\n\nMost common symptoms: fever (4 patients), headache (3 patients), and routine checkups (5 patients).",
        tool_calls: [
          {
            function_name: "get_appointment_stats",
            result: { total_patients: 12, date: "yesterday" },
          },
        ],
      }
    }

    if (lowerMessage.includes("appointments") && lowerMessage.includes("today")) {
      return {
        response:
          "Your schedule for today:\n\n• 9:00 AM - John Smith (Follow-up)\n• 10:30 AM - Sarah Johnson (Checkup)\n• 2:00 PM - Mike Brown (Consultation)\n• 3:30 PM - Lisa Davis (Routine)\n\nTotal: 4 appointments scheduled",
        tool_calls: [
          {
            function_name: "get_appointment_stats",
            result: { appointments_today: 4 },
          },
        ],
      }
    }

    if (lowerMessage.includes("fever")) {
      return {
        response:
          "This week, you've seen 7 patients with fever symptoms:\n\n• Monday: 2 patients\n• Tuesday: 1 patient\n• Wednesday: 3 patients\n• Thursday: 1 patient\n\nRecommended follow-up actions have been noted in their records.",
        tool_calls: [
          {
            function_name: "search_patients_by_symptoms",
            result: { symptom: "fever", count: 7, week: "current" },
          },
        ],
      }
    }

    return {
      response:
        "I can help you with:\n\n• Patient statistics and reports\n• Appointment summaries\n• Symptom analysis\n• Schedule management\n\nWhat would you like to know about your practice?",
      tool_calls: [],
    }
  }
}

export async function POST(request: NextRequest) {
  try {
    const { message, session_id, user_type } = await request.json()

    // Add a small delay to simulate processing
    await new Promise((resolve) => setTimeout(resolve, 1000))

    const response = generateMockResponse(message, user_type)

    return NextResponse.json(response)
  } catch (error) {
    console.error("Chat error:", error)
    return NextResponse.json({ error: "Failed to process chat message" }, { status: 500 })
  }
}
