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
        const response = await fetch("http://localhost:8000/appointments/upcoming")
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

  if (isLoading) {
    return (
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-4 bg-muted rounded w-3/4"></div>
              <div className="h-3 bg-muted rounded w-1/2"></div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="h-3 bg-muted rounded"></div>
                <div className="h-3 bg-muted rounded w-2/3"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Plus className="w-5 h-5" />
            Quick Actions
          </CardTitle>
          <CardDescription>Schedule new appointments or manage existing ones</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Button className="gap-2">
              <Calendar className="w-4 h-4" />
              Book New Appointment
            </Button>
            <Button variant="outline" className="gap-2 bg-transparent">
              <Stethoscope className="w-4 h-4" />
              Find Doctors
            </Button>
            <Button variant="outline" className="gap-2 bg-transparent">
              <Clock className="w-4 h-4" />
              Check Availability
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Upcoming Appointments */}
      <div>
        <h3 className="text-lg font-semibold font-heading mb-4">Upcoming Appointments ({appointments.length})</h3>

        {appointments.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Calendar className="w-12 h-12 text-muted-foreground mb-4" />
              <h4 className="text-lg font-medium text-foreground mb-2">No upcoming appointments</h4>
              <p className="text-muted-foreground text-center mb-4">
                You don't have any scheduled appointments. Book one to get started.
              </p>
              <Button className="gap-2">
                <Plus className="w-4 h-4" />
                Schedule Appointment
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {appointments.map((appointment) => (
              <Card key={appointment.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-base font-heading">{appointment.doctor}</CardTitle>
                      <CardDescription className="flex items-center gap-1 mt-1">
                        <User className="w-3 h-3" />
                        {appointment.patient}
                      </CardDescription>
                    </div>
                    <Badge variant="secondary">Scheduled</Badge>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-sm">
                      <Calendar className="w-4 h-4 text-muted-foreground" />
                      <span>{new Date(appointment.date).toLocaleDateString()}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="w-4 h-4 text-muted-foreground" />
                      <span>{appointment.time}</span>
                    </div>
                    {appointment.symptoms && (
                      <div className="flex items-start gap-2 text-sm">
                        <Stethoscope className="w-4 h-4 text-muted-foreground mt-0.5" />
                        <span className="text-muted-foreground">{appointment.symptoms}</span>
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2 mt-4">
                    <Button variant="outline" size="sm" className="flex-1 bg-transparent">
                      Reschedule
                    </Button>
                    <Button variant="outline" size="sm" className="flex-1 bg-transparent">
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
