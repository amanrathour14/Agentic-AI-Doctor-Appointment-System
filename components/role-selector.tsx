"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Stethoscope, User, Calendar, BarChart3 } from "lucide-react"

interface RoleSelectorProps {
  onRoleSelect: (role: "patient" | "doctor") => void
}

export default function RoleSelector({ onRoleSelect }: RoleSelectorProps) {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="flex items-center justify-center w-16 h-16 bg-primary rounded-xl">
              <Stethoscope className="w-8 h-8 text-primary-foreground" />
            </div>
          </div>
          <h1 className="text-3xl font-bold font-heading text-foreground mb-2">Welcome to MedAI Assistant</h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Your intelligent healthcare companion for appointment scheduling and medical assistance. Choose your role to
            get started.
          </p>
        </div>

        {/* Role Selection Cards */}
        <div className="grid md:grid-cols-2 gap-6 max-w-3xl mx-auto">
          {/* Patient Card */}
          <Card className="relative overflow-hidden border-2 hover:border-primary/50 transition-all duration-200 hover:shadow-lg cursor-pointer group">
            <div className="absolute inset-0 medical-gradient opacity-50 group-hover:opacity-70 transition-opacity" />
            <CardHeader className="relative z-10 text-center pb-4">
              <div className="flex items-center justify-center w-12 h-12 bg-secondary rounded-lg mx-auto mb-3">
                <User className="w-6 h-6 text-secondary-foreground" />
              </div>
              <CardTitle className="text-xl font-heading">I'm a Patient</CardTitle>
              <CardDescription className="text-base">Schedule appointments and manage your healthcare</CardDescription>
            </CardHeader>
            <CardContent className="relative z-10 pt-0">
              <div className="space-y-3 mb-6">
                <div className="flex items-center gap-3 text-sm text-muted-foreground">
                  <Calendar className="w-4 h-4 text-secondary" />
                  <span>Book and manage appointments</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-muted-foreground">
                  <Stethoscope className="w-4 h-4 text-secondary" />
                  <span>Find available doctors</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-muted-foreground">
                  <User className="w-4 h-4 text-secondary" />
                  <span>Get personalized health assistance</span>
                </div>
              </div>
              <Button onClick={() => onRoleSelect("patient")} className="w-full" size="lg">
                Continue as Patient
              </Button>
            </CardContent>
          </Card>

          {/* Doctor Card */}
          <Card className="relative overflow-hidden border-2 hover:border-primary/50 transition-all duration-200 hover:shadow-lg cursor-pointer group">
            <div className="absolute inset-0 medical-gradient opacity-50 group-hover:opacity-70 transition-opacity" />
            <CardHeader className="relative z-10 text-center pb-4">
              <div className="flex items-center justify-center w-12 h-12 bg-secondary rounded-lg mx-auto mb-3">
                <Stethoscope className="w-6 h-6 text-secondary-foreground" />
              </div>
              <CardTitle className="text-xl font-heading">I'm a Doctor</CardTitle>
              <CardDescription className="text-base">Manage your practice and view patient insights</CardDescription>
            </CardHeader>
            <CardContent className="relative z-10 pt-0">
              <div className="space-y-3 mb-6">
                <div className="flex items-center gap-3 text-sm text-muted-foreground">
                  <BarChart3 className="w-4 h-4 text-secondary" />
                  <span>View appointment statistics</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-muted-foreground">
                  <Calendar className="w-4 h-4 text-secondary" />
                  <span>Manage your schedule</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-muted-foreground">
                  <User className="w-4 h-4 text-secondary" />
                  <span>Track patient trends</span>
                </div>
              </div>
              <Button onClick={() => onRoleSelect("doctor")} className="w-full" size="lg">
                Continue as Doctor
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-sm text-muted-foreground">
            Powered by advanced AI technology for intelligent healthcare assistance
          </p>
        </div>
      </div>
    </div>
  )
}
