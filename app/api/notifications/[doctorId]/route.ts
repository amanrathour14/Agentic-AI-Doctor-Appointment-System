import { type NextRequest, NextResponse } from "next/server"

// Mock notifications data
const mockNotifications = [
  {
    id: "notif_1",
    doctor_id: 1,
    type: "new_appointment",
    title: "New Appointment Booked",
    message: "Sarah Johnson has booked an appointment for tomorrow at 10:00 AM",
    priority: "high" as const,
    data: {
      patient_name: "Sarah Johnson",
      appointment_date: "2024-01-15",
      appointment_time: "10:00 AM",
    },
    timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
    read: false,
  },
  {
    id: "notif_2",
    doctor_id: 1,
    type: "appointment_reminder",
    title: "Upcoming Appointment",
    message: "Reminder: You have an appointment with Michael Brown in 1 hour",
    priority: "medium" as const,
    data: {
      patient_name: "Michael Brown",
      appointment_date: "2024-01-14",
      appointment_time: "2:00 PM",
    },
    timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    read: false,
  },
  {
    id: "notif_3",
    doctor_id: 1,
    type: "system_alert",
    title: "System Maintenance",
    message: "Scheduled maintenance will occur tonight from 11 PM to 1 AM",
    priority: "low" as const,
    data: {},
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    read: true,
  },
]

export async function GET(request: NextRequest, { params }: { params: { doctorId: string } }) {
  try {
    const doctorId = Number.parseInt(params.doctorId)

    // Filter notifications for this doctor
    const doctorNotifications = mockNotifications.filter((n) => n.doctor_id === doctorId)

    return NextResponse.json({
      notifications: doctorNotifications,
      total: doctorNotifications.length,
      unread: doctorNotifications.filter((n) => !n.read).length,
    })
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch notifications" }, { status: 500 })
  }
}
