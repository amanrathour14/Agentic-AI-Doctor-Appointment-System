import { type NextRequest, NextResponse } from "next/server"

// In-memory session storage for conversation context
const sessionStorage = new Map<string, any>()

// Enhanced AI response generator with conversation context
const generateIntelligentResponse = (message: string, userType: string, sessionId: string) => {
  const lowerMessage = message.toLowerCase()
  const session = sessionStorage.get(sessionId) || {}

  if (userType === "patient") {
    if (
      session.pendingBooking &&
      (lowerMessage.includes("yes") || lowerMessage.includes("book") || lowerMessage.includes("confirm"))
    ) {
      const booking = session.pendingBooking
      // Clear pending booking
      sessionStorage.set(sessionId, { ...session, pendingBooking: null, lastBooking: booking })

      return {
        response: `Appointment Confirmed!\n\nYour appointment has been successfully booked:\n\nDate: ${booking.date}\nTime: ${booking.time}\nDoctor: ${booking.doctor}\nLocation: ${booking.location || "Main Clinic"}\n\nA confirmation email has been sent to your registered email address.\nYou'll receive a reminder 24 hours before your appointment.\n\nAppointment ID: #APT${Math.random().toString(36).substr(2, 8).toUpperCase()}\n\nIs there anything else I can help you with?`,
        tool_calls: [
          {
            function_name: "schedule_appointment",
            result: {
              status: "confirmed",
              appointment_id: `APT${Math.random().toString(36).substr(2, 8).toUpperCase()}`,
              doctor: booking.doctor,
              time: booking.time,
              date: booking.date,
            },
          },
        ],
      }
    }

    if (lowerMessage.includes("cancel") || lowerMessage.includes("reschedule")) {
      return {
        response:
          "I can help you cancel or reschedule your appointment. Could you please provide:\n\n• Your appointment ID (if you have it)\n• The doctor's name\n• The current appointment date/time\n\nOr I can look up your recent appointments if you'd prefer.",
        tool_calls: [],
      }
    }

    if (lowerMessage.includes("appointment") || lowerMessage.includes("book")) {
      let doctor = "Dr. Smith"
      let date = "tomorrow"
      let time = "10:00 AM"
      let location = "Main Clinic"

      // Extract doctor name from message
      if (lowerMessage.includes("dr. ahuja") || lowerMessage.includes("ahuja")) {
        doctor = "Dr. Ahuja"
        location = "Cardiology Wing"
      } else if (lowerMessage.includes("dr. johnson") || lowerMessage.includes("johnson")) {
        doctor = "Dr. Johnson"
        location = "General Medicine"
      } else if (lowerMessage.includes("dr. brown") || lowerMessage.includes("brown")) {
        doctor = "Dr. Brown"
        location = "Dermatology Clinic"
      }

      // Extract time preferences
      if (lowerMessage.includes("morning")) {
        time = "10:00 AM"
      } else if (lowerMessage.includes("afternoon")) {
        time = "2:00 PM"
      } else if (lowerMessage.includes("evening")) {
        time = "5:00 PM"
      }

      // Extract date preferences
      if (lowerMessage.includes("today")) {
        date = "today"
      } else if (lowerMessage.includes("tomorrow")) {
        date = "tomorrow"
      } else if (lowerMessage.includes("friday")) {
        date = "this Friday"
      }

      // Store pending booking in session
      const pendingBooking = { doctor, date, time, location }
      sessionStorage.set(sessionId, { ...session, pendingBooking })

      return {
        response: `I found an available slot with ${doctor}!\n\nAvailable Appointment:\n\nDoctor: ${doctor}\nDate: ${date}\nTime: ${time}\nLocation: ${location}\nDuration: 30 minutes\n\nConsultation Fee: $75\n\nWould you like me to confirm this appointment for you? Just reply with "yes" or "confirm" to book it!`,
        tool_calls: [
          {
            function_name: "check_doctor_availability",
            result: {
              available_slots: [time, "11:30 AM", "2:00 PM"],
              doctor,
              date,
              location,
            },
          },
        ],
      }
    }

    if (lowerMessage.includes("fever") || lowerMessage.includes("headache") || lowerMessage.includes("pain")) {
      let recommendedDoctor = "Dr. Smith (General Medicine)"
      let symptoms = "general symptoms"

      if (lowerMessage.includes("heart") || lowerMessage.includes("chest")) {
        recommendedDoctor = "Dr. Johnson (Cardiology)"
        symptoms = "cardiac symptoms"
      } else if (lowerMessage.includes("skin") || lowerMessage.includes("rash")) {
        recommendedDoctor = "Dr. Brown (Dermatology)"
        symptoms = "skin-related symptoms"
      }

      return {
        response: `Based on your ${symptoms}, I recommend seeing ${recommendedDoctor}.\n\nAvailable slots:\n• Tomorrow 10:00 AM\n• Tomorrow 2:00 PM\n• Friday 11:00 AM\n\nWould you like me to book an appointment for you?`,
        tool_calls: [
          {
            function_name: "search_doctors_by_specialty",
            result: { symptoms, recommended_doctor: recommendedDoctor },
          },
        ],
      }
    }

    return {
      response:
        'Hello! I\'m your AI medical assistant. I can help you with:\n\nBook Appointments\n• "Book appointment with Dr. Ahuja tomorrow morning"\n• "I need to see a cardiologist"\n\nManage Existing Appointments\n• Cancel or reschedule appointments\n• Check appointment status\n\nGet Medical Guidance\n• Find the right specialist for your symptoms\n• Get appointment recommendations\n\nWhat would you like to do today?',
      tool_calls: [],
    }
  } else {
    if (lowerMessage.includes("patients") && (lowerMessage.includes("yesterday") || lowerMessage.includes("today"))) {
      const day = lowerMessage.includes("yesterday") ? "yesterday" : "today"
      const patientCount = day === "yesterday" ? 12 : 8

      return {
        response: `Patient Summary for ${day}:\n\nTotal Patients: ${patientCount}\n\nAppointment Breakdown:\n• Regular checkups: ${Math.floor(patientCount * 0.6)}\n• Follow-up visits: ${Math.floor(patientCount * 0.25)}\n• Emergency consultations: ${Math.floor(patientCount * 0.15)}\n\nMost Common Symptoms:\n• Fever: ${Math.floor(patientCount * 0.3)} patients\n• Headache: ${Math.floor(patientCount * 0.2)} patients\n• Routine checkups: ${Math.floor(patientCount * 0.4)} patients\n\nRevenue: $${patientCount * 75}\n\nWould you like more detailed analytics?`,
        tool_calls: [
          {
            function_name: "get_appointment_stats",
            result: { total_patients: patientCount, date: day, revenue: patientCount * 75 },
          },
        ],
      }
    }

    if (lowerMessage.includes("appointments") && lowerMessage.includes("today")) {
      return {
        response:
          "Today's Schedule:\n\n9:00 AM - John Smith (Follow-up)\n   Hypertension monitoring\n\n10:30 AM - Sarah Johnson (Checkup)\n   Annual physical examination\n\n2:00 PM - Mike Brown (Consultation)\n   Chest pain evaluation\n\n3:30 PM - Lisa Davis (Routine)\n   Diabetes management\n\nSummary: 4 appointments | Est. duration: 6 hours\nExpected revenue: $300",
        tool_calls: [
          {
            function_name: "get_doctor_schedule",
            result: { appointments_today: 4, total_duration: "6 hours" },
          },
        ],
      }
    }

    if (lowerMessage.includes("fever") || lowerMessage.includes("symptoms")) {
      return {
        response:
          "Fever Cases Analysis (This Week):\n\nTotal Cases: 7 patients\n\nDaily Breakdown:\n• Monday: 2 patients (mild fever)\n• Tuesday: 1 patient (high fever)\n• Wednesday: 3 patients (moderate fever)\n• Thursday: 1 patient (recurring fever)\n\nTreatment Patterns:\n• Prescribed antibiotics: 4 cases\n• Recommended rest: 7 cases\n• Follow-up required: 3 cases\n\nAlert: Slight uptick in fever cases - consider seasonal flu precautions.",
        tool_calls: [
          {
            function_name: "analyze_symptom_trends",
            result: { symptom: "fever", count: 7, trend: "increasing", week: "current" },
          },
        ],
      }
    }

    return {
      response:
        'Doctor Dashboard - How can I assist you?\n\nAnalytics & Reports:\n• "How many patients yesterday?"\n• "Show me fever cases this week"\n• "Today\'s appointment schedule"\n\nPatient Management:\n• View patient histories\n• Symptom trend analysis\n• Revenue reports\n\nQuick Actions:\n• Check today\'s schedule\n• Review pending lab results\n• Patient follow-up reminders\n\nWhat would you like to review?',
      tool_calls: [],
    }
  }
}

export async function POST(request: NextRequest) {
  try {
    const { message, session_id, user_type } = await request.json()

    // Add processing delay for realism
    await new Promise((resolve) => setTimeout(resolve, 800))

    const response = generateIntelligentResponse(message, user_type, session_id)

    return NextResponse.json(response)
  } catch (error) {
    console.error("Chat error:", error)
    return NextResponse.json(
      {
        response: "I apologize, but I'm experiencing technical difficulties. Please try again in a moment.",
        tool_calls: [],
        error: "Failed to process chat message",
      },
      { status: 500 },
    )
  }
}
