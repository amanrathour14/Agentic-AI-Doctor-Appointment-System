"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts"
import { Calendar, Users, TrendingUp, Clock, Stethoscope, Activity } from "lucide-react"
import { NotificationPanel } from "./notification-panel"

interface AppointmentStats {
  total_appointments: number
  scheduled: number
  completed: number
  cancelled: number
  no_show: number
  symptom_breakdown?: Record<string, number>
}

interface DoctorDashboardProps {
  doctorId?: number
}

export default function DoctorDashboard({ doctorId = 1 }: DoctorDashboardProps) {
  const [stats, setStats] = useState<AppointmentStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch("http://localhost:8000/mcp/execute", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            tool_name: "get_appointment_stats",
            parameters: {
              date_range: "week",
              filter_by: "symptoms",
            },
          }),
        })
        const data = await response.json()
        if (data.success) {
          setStats(data.result.stats)
        }
      } catch (error) {
        console.error("Failed to fetch stats:", error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchStats()
  }, [])

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Doctor Dashboard</h1>
          <NotificationPanel doctorId={doctorId} />
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-muted rounded w-3/4"></div>
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-muted rounded w-1/2"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  const appointmentData = stats
    ? [
        { name: "Scheduled", value: stats.scheduled, color: "#8b5cf6" },
        { name: "Completed", value: stats.completed, color: "#22c55e" },
        { name: "Cancelled", value: stats.cancelled, color: "#f59e0b" },
        { name: "No Show", value: stats.no_show, color: "#ef4444" },
      ]
    : []

  const symptomData = stats?.symptom_breakdown
    ? Object.entries(stats.symptom_breakdown).map(([symptom, count]) => ({
        symptom: symptom.charAt(0).toUpperCase() + symptom.slice(1),
        count,
      }))
    : []

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Doctor Dashboard</h1>
          <p className="text-muted-foreground">Monitor your appointments and patient statistics</p>
        </div>
        <NotificationPanel doctorId={doctorId} />
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Appointments</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_appointments || 0}</div>
            <p className="text-xs text-muted-foreground">This week</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Scheduled</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-secondary">{stats?.scheduled || 0}</div>
            <p className="text-xs text-muted-foreground">Upcoming appointments</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats?.completed || 0}</div>
            <p className="text-xs text-muted-foreground">Patients seen</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completion Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.total_appointments ? Math.round((stats.completed / stats.total_appointments) * 100) : 0}%
            </div>
            <p className="text-xs text-muted-foreground">Success rate</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Appointment Status
            </CardTitle>
            <CardDescription>Distribution of appointment statuses this week</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={appointmentData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {appointmentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex flex-wrap gap-2 mt-4">
              {appointmentData.map((item, index) => (
                <div key={index} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-sm text-muted-foreground">
                    {item.name}: {item.value}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Stethoscope className="w-5 h-5" />
              Common Symptoms
            </CardTitle>
            <CardDescription>Most frequent patient symptoms this week</CardDescription>
          </CardHeader>
          <CardContent>
            {symptomData.length > 0 ? (
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={symptomData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="symptom" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-[300px] flex items-center justify-center">
                <div className="text-center">
                  <Stethoscope className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">No symptom data available</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks and reports</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-3">
            <div className="flex items-center gap-3 p-3 border border-border rounded-lg hover:bg-muted/50 cursor-pointer transition-colors">
              <Calendar className="w-5 h-5 text-secondary" />
              <div>
                <p className="font-medium text-sm">Today's Schedule</p>
                <p className="text-xs text-muted-foreground">View appointments</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 border border-border rounded-lg hover:bg-muted/50 cursor-pointer transition-colors">
              <Users className="w-5 h-5 text-secondary" />
              <div>
                <p className="font-medium text-sm">Patient Search</p>
                <p className="text-xs text-muted-foreground">Find by symptoms</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 border border-border rounded-lg hover:bg-muted/50 cursor-pointer transition-colors">
              <TrendingUp className="w-5 h-5 text-secondary" />
              <div>
                <p className="font-medium text-sm">Monthly Report</p>
                <p className="text-xs text-muted-foreground">Generate summary</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
