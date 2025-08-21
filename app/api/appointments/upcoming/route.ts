import { type NextRequest, NextResponse } from "next/server"

// Mock appointments data
const mockAppointments = [
  {
    id: 1,
    doctor: "Dr. Sarah Ahuja",
    patient: "Current User",
    date: "2024-01-15",
    time: "10:00 AM",
    symptoms: "Regular checkup and blood pressure monitoring",
  },
  {
    id: 2,
    doctor: "Dr. Michael Chen",
    patient: "Current User",
    date: "2024-01-18",
    time: "2:30 PM",
    symptoms: "Follow-up consultation for chest pain",
  },
  {
    id: 3,
    doctor: "Dr. Emily Rodriguez",
    patient: "Current User",
    date: "2024-01-22",
    time: "11:15 AM",
    symptoms: "Dermatology consultation for skin condition",
  },
]

export async function GET(request: NextRequest) {
  try {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    return NextResponse.json({
      success: true,
      appointments: mockAppointments,
      total: mockAppointments.length,
    })
  } catch (error) {
    console.error("Error fetching appointments:", error)
    return NextResponse.json({ success: false, error: "Failed to fetch appointments" }, { status: 500 })
  }
}
