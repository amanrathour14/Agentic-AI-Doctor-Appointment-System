"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Stethoscope, MessageCircle, Calendar, BarChart3, Users } from "lucide-react"
import ChatInterface from "@/components/chat-interface"
import RoleSelector from "@/components/role-selector"
import AppointmentDashboard from "@/components/appointment-dashboard"
import DoctorDashboard from "@/components/doctor-dashboard"

export default function HomePage() {
  const [userRole, setUserRole] = useState<"patient" | "doctor" | null>(null)
  const [activeView, setActiveView] = useState<"chat" | "appointments" | "dashboard">("chat")

  if (!userRole) {
    return <RoleSelector onRoleSelect={setUserRole} />
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 bg-primary rounded-lg">
                <Stethoscope className="w-6 h-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-bold font-heading text-foreground">MedAI Assistant</h1>
                <p className="text-sm text-muted-foreground">
                  {userRole === "patient" ? "Patient Portal" : "Doctor Dashboard"}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <nav className="flex items-center gap-2">
                <Button
                  variant={activeView === "chat" ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setActiveView("chat")}
                  className="gap-2"
                >
                  <MessageCircle className="w-4 h-4" />
                  Chat
                </Button>

                {userRole === "patient" && (
                  <Button
                    variant={activeView === "appointments" ? "default" : "ghost"}
                    size="sm"
                    onClick={() => setActiveView("appointments")}
                    className="gap-2"
                  >
                    <Calendar className="w-4 h-4" />
                    Appointments
                  </Button>
                )}

                {userRole === "doctor" && (
                  <Button
                    variant={activeView === "dashboard" ? "default" : "ghost"}
                    size="sm"
                    onClick={() => setActiveView("dashboard")}
                    className="gap-2"
                  >
                    <BarChart3 className="w-4 h-4" />
                    Dashboard
                  </Button>
                )}
              </nav>

              <div className="flex items-center gap-2">
                <Badge variant="secondary" className="gap-1">
                  <Users className="w-3 h-3" />
                  {userRole}
                </Badge>
                <Button variant="outline" size="sm" onClick={() => setUserRole(null)}>
                  Switch Role
                </Button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {activeView === "chat" && (
          <div className="max-w-4xl mx-auto">
            <div className="mb-6">
              <h2 className="text-2xl font-bold font-heading text-foreground mb-2">AI Assistant</h2>
              <p className="text-muted-foreground">
                {userRole === "patient"
                  ? "Ask me to schedule appointments, check availability, or answer questions about your healthcare."
                  : "Get appointment statistics, patient reports, and manage your schedule with natural language."}
              </p>
            </div>
            <ChatInterface userRole={userRole} />
          </div>
        )}

        {activeView === "appointments" && userRole === "patient" && (
          <div className="max-w-6xl mx-auto">
            <div className="mb-6">
              <h2 className="text-2xl font-bold font-heading text-foreground mb-2">My Appointments</h2>
              <p className="text-muted-foreground">View and manage your upcoming appointments</p>
            </div>
            <AppointmentDashboard />
          </div>
        )}

        {activeView === "dashboard" && userRole === "doctor" && (
          <div className="max-w-6xl mx-auto">
            <div className="mb-6">
              <h2 className="text-2xl font-bold font-heading text-foreground mb-2">Doctor Dashboard</h2>
              <p className="text-muted-foreground">Overview of your appointments and patient statistics</p>
            </div>
            <DoctorDashboard />
          </div>
        )}
      </main>
    </div>
  )
}
