"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
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

  const handleTodaySchedule = () => {
    console.log("[v0] Opening today's schedule")
    // In a real app, this would navigate to schedule view
    alert("Opening today's schedule...")
  }

  const handlePatientSearch = () => {
    console.log("[v0] Opening patient search")
    // In a real app, this would open patient search modal
    alert("Opening patient search by symptoms...")
  }

  const handleMonthlyReport = () => {
    console.log("[v0] Generating monthly report")
    // In a real app, this would generate and download report
    alert("Generating monthly report...")
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Doctor Dashboard
          </h1>
          <NotificationPanel doctorId={doctorId} />
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="animate-pulse bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200">
              <CardHeader>
                <div className="h-4 bg-gradient-to-r from-blue-200 to-purple-200 rounded w-3/4"></div>
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-gradient-to-r from-blue-200 to-purple-200 rounded w-1/2"></div>
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
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Doctor Dashboard
          </h1>
          <p className="text-slate-600 mt-1">Monitor your appointments and patient statistics</p>
        </div>
        <NotificationPanel doctorId={doctorId} />
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="bg-gradient-to-br from-blue-50 to-indigo-100 border-blue-200 hover:shadow-lg transition-all duration-300 hover:scale-105">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-blue-800">Total Appointments</CardTitle>
            <Calendar className="h-5 w-5 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-700">{stats?.total_appointments || 0}</div>
            <p className="text-xs text-blue-600">This week</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-pink-100 border-purple-200 hover:shadow-lg transition-all duration-300 hover:scale-105">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-purple-800">Scheduled</CardTitle>
            <Clock className="h-5 w-5 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-700">{stats?.scheduled || 0}</div>
            <p className="text-xs text-purple-600">Upcoming appointments</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-emerald-50 to-teal-100 border-emerald-200 hover:shadow-lg transition-all duration-300 hover:scale-105">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-emerald-800">Completed</CardTitle>
            <Users className="h-5 w-5 text-emerald-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-emerald-700">{stats?.completed || 0}</div>
            <p className="text-xs text-emerald-600">Patients seen</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-orange-50 to-red-100 border-orange-200 hover:shadow-lg transition-all duration-300 hover:scale-105">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-orange-800">Completion Rate</CardTitle>
            <TrendingUp className="h-5 w-5 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-700">
              {stats?.total_appointments ? Math.round((stats.completed / stats.total_appointments) * 100) : 0}%
            </div>
            <p className="text-xs text-orange-600">Success rate</p>
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

      <Card className="bg-gradient-to-br from-slate-50 to-blue-50 border-slate-200">
        <CardHeader>
          <CardTitle className="text-slate-800">Quick Actions</CardTitle>
          <CardDescription className="text-slate-600">Common tasks and reports</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <Button
              onClick={handleTodaySchedule}
              className="flex items-center gap-3 p-4 h-auto bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
            >
              <Calendar className="w-5 h-5" />
              <div className="text-left">
                <p className="font-medium text-sm">Today's Schedule</p>
                <p className="text-xs opacity-90">View appointments</p>
              </div>
            </Button>
            <Button
              onClick={handlePatientSearch}
              className="flex items-center gap-3 p-4 h-auto bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
            >
              <Users className="w-5 h-5" />
              <div className="text-left">
                <p className="font-medium text-sm">Patient Search</p>
                <p className="text-xs opacity-90">Find by symptoms</p>
              </div>
            </Button>
            <Button
              onClick={handleMonthlyReport}
              className="flex items-center gap-3 p-4 h-auto bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
            >
              <TrendingUp className="w-5 h-5" />
              <div className="text-left">
                <p className="font-medium text-sm">Monthly Report</p>
                <p className="text-xs opacity-90">Generate summary</p>
              </div>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
