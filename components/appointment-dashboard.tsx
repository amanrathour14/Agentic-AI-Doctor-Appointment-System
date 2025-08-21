"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Calendar, Clock, User, Stethoscope, Plus } from "lucide-react"

interface Appointment {
  id: number
  doctor: string
  patient: string
  date: string
  time: string
  symptoms?: string
}

export default function AppointmentDashboard() {
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        const response = await fetch("/api/appointments/upcoming")
        const data = await response.json()
        setAppointments(data.appointments || [])
      } catch (error) {
        console.error("Failed to fetch appointments:", error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchAppointments()
  }, [])

  const handleBookAppointment = () => {
    console.log("[v0] Opening appointment booking")
    alert("Opening appointment booking form...")
  }

  const handleFindDoctors = () => {
    console.log("[v0] Opening doctor search")
    alert("Opening doctor search...")
  }

  const handleCheckAvailability = () => {
    console.log("[v0] Checking availability")
    alert("Checking doctor availability...")
  }

  const handleReschedule = (appointmentId: number) => {
    console.log("[v0] Rescheduling appointment:", appointmentId)
    alert(`Rescheduling appointment #${appointmentId}...`)
  }

  const handleCancel = (appointmentId: number) => {
    console.log("[v0] Cancelling appointment:", appointmentId)
    if (confirm("Are you sure you want to cancel this appointment?")) {
      alert(`Appointment #${appointmentId} cancelled.`)
    }
  }

  if (isLoading) {
    return (
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="animate-pulse bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200">
            <CardHeader>
              <div className="h-4 bg-gradient-to-r from-blue-200 to-purple-200 rounded w-3/4"></div>
              <div className="h-3 bg-gradient-to-r from-blue-200 to-purple-200 rounded w-1/2"></div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="h-3 bg-gradient-to-r from-blue-200 to-purple-200 rounded"></div>
                <div className="h-3 bg-gradient-to-r from-blue-200 to-purple-200 rounded w-2/3"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <Card className="bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-blue-800">
            <Plus className="w-5 h-5 text-blue-600" />
            Quick Actions
          </CardTitle>
          <CardDescription className="text-blue-600">Schedule new appointments or manage existing ones</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Button
              onClick={handleBookAppointment}
              className="gap-2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
            >
              <Calendar className="w-4 h-4" />
              Book New Appointment
            </Button>
            <Button
              onClick={handleFindDoctors}
              variant="outline"
              className="gap-2 bg-gradient-to-r from-emerald-50 to-teal-50 border-emerald-200 text-emerald-700 hover:bg-gradient-to-r hover:from-emerald-100 hover:to-teal-100 hover:border-emerald-300 transition-all duration-300 hover:scale-105"
            >
              <Stethoscope className="w-4 h-4" />
              Find Doctors
            </Button>
            <Button
              onClick={handleCheckAvailability}
              variant="outline"
              className="gap-2 bg-gradient-to-r from-orange-50 to-red-50 border-orange-200 text-orange-700 hover:bg-gradient-to-r hover:from-orange-100 hover:to-red-100 hover:border-orange-300 transition-all duration-300 hover:scale-105"
            >
              <Clock className="w-4 h-4" />
              Check Availability
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Upcoming Appointments */}
      <div>
        <h3 className="text-xl font-semibold bg-gradient-to-r from-slate-700 to-blue-600 bg-clip-text text-transparent mb-4">
          Upcoming Appointments ({appointments.length})
        </h3>

        {appointments.length === 0 ? (
          <Card className="bg-gradient-to-br from-slate-50 to-blue-50 border-slate-200">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Calendar className="w-12 h-12 text-blue-400 mb-4" />
              <h4 className="text-lg font-medium text-slate-700 mb-2">No upcoming appointments</h4>
              <p className="text-slate-600 text-center mb-4">
                You don't have any scheduled appointments. Book one to get started.
              </p>
              <Button
                onClick={handleBookAppointment}
                className="gap-2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
              >
                <Plus className="w-4 h-4" />
                Schedule Appointment
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {appointments.map((appointment) => (
              <Card
                key={appointment.id}
                className="bg-gradient-to-br from-white to-blue-50 border-blue-200 hover:shadow-lg transition-all duration-300 hover:scale-105"
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-base text-slate-800">{appointment.doctor}</CardTitle>
                      <CardDescription className="flex items-center gap-1 mt-1 text-slate-600">
                        <User className="w-3 h-3" />
                        {appointment.patient}
                      </CardDescription>
                    </div>
                    <Badge className="bg-gradient-to-r from-emerald-100 to-teal-100 text-emerald-700 border-emerald-200">
                      Scheduled
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-sm text-slate-600">
                      <Calendar className="w-4 h-4 text-blue-500" />
                      <span>{new Date(appointment.date).toLocaleDateString()}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-slate-600">
                      <Clock className="w-4 h-4 text-purple-500" />
                      <span>{appointment.time}</span>
                    </div>
                    {appointment.symptoms && (
                      <div className="flex items-start gap-2 text-sm">
                        <Stethoscope className="w-4 h-4 text-emerald-500 mt-0.5" />
                        <span className="text-slate-600">{appointment.symptoms}</span>
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2 mt-4">
                    <Button
                      onClick={() => handleReschedule(appointment.id)}
                      variant="outline"
                      size="sm"
                      className="flex-1 bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200 text-blue-700 hover:bg-gradient-to-r hover:from-blue-100 hover:to-purple-100 hover:border-blue-300 transition-all duration-300"
                    >
                      Reschedule
                    </Button>
                    <Button
                      onClick={() => handleCancel(appointment.id)}
                      variant="outline"
                      size="sm"
                      className="flex-1 bg-gradient-to-r from-red-50 to-orange-50 border-red-200 text-red-700 hover:bg-gradient-to-r hover:from-red-100 hover:to-orange-100 hover:border-red-300 transition-all duration-300"
                    >
                      Cancel
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
