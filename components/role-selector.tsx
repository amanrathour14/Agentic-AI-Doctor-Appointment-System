"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Stethoscope, User, Calendar, BarChart3 } from "lucide-react"

interface RoleSelectorProps {
  onRoleSelect: (role: "patient" | "doctor") => void
}

export default function RoleSelector({ onRoleSelect }: RoleSelectorProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-6">
            <div className="flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl shadow-lg">
              <Stethoscope className="w-10 h-10 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold font-heading bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            Welcome to MedAI Assistant
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Your intelligent healthcare companion for appointment scheduling and medical assistance. Choose your role to
            get started.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Patient Card */}
          <Card className="relative overflow-hidden border-0 shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105 cursor-pointer group bg-gradient-to-br from-emerald-50 to-teal-50">
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-400/20 to-teal-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            <CardHeader className="relative z-10 text-center pb-6 pt-8">
              <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl mx-auto mb-4 shadow-lg">
                <User className="w-8 h-8 text-white" />
              </div>
              <CardTitle className="text-2xl font-heading text-gray-800">I'm a Patient</CardTitle>
              <CardDescription className="text-lg text-gray-600">
                Schedule appointments and manage your healthcare
              </CardDescription>
            </CardHeader>
            <CardContent className="relative z-10 pt-0 pb-8">
              <div className="space-y-4 mb-8">
                <div className="flex items-center gap-4 text-base text-gray-700 bg-white/50 rounded-lg p-3">
                  <Calendar className="w-5 h-5 text-emerald-600" />
                  <span>Book and manage appointments</span>
                </div>
                <div className="flex items-center gap-4 text-base text-gray-700 bg-white/50 rounded-lg p-3">
                  <Stethoscope className="w-5 h-5 text-emerald-600" />
                  <span>Find available doctors</span>
                </div>
                <div className="flex items-center gap-4 text-base text-gray-700 bg-white/50 rounded-lg p-3">
                  <User className="w-5 h-5 text-emerald-600" />
                  <span>Get personalized health assistance</span>
                </div>
              </div>
              <Button
                onClick={() => onRoleSelect("patient")}
                className="w-full bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white font-semibold py-3 px-6 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200"
                size="lg"
              >
                Continue as Patient
              </Button>
            </CardContent>
          </Card>

          {/* Doctor Card */}
          <Card className="relative overflow-hidden border-0 shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105 cursor-pointer group bg-gradient-to-br from-blue-50 to-indigo-50">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-400/20 to-indigo-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            <CardHeader className="relative z-10 text-center pb-6 pt-8">
              <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl mx-auto mb-4 shadow-lg">
                <Stethoscope className="w-8 h-8 text-white" />
              </div>
              <CardTitle className="text-2xl font-heading text-gray-800">I'm a Doctor</CardTitle>
              <CardDescription className="text-lg text-gray-600">
                Manage your practice and view patient insights
              </CardDescription>
            </CardHeader>
            <CardContent className="relative z-10 pt-0 pb-8">
              <div className="space-y-4 mb-8">
                <div className="flex items-center gap-4 text-base text-gray-700 bg-white/50 rounded-lg p-3">
                  <BarChart3 className="w-5 h-5 text-blue-600" />
                  <span>View appointment statistics</span>
                </div>
                <div className="flex items-center gap-4 text-base text-gray-700 bg-white/50 rounded-lg p-3">
                  <Calendar className="w-5 h-5 text-blue-600" />
                  <span>Manage your schedule</span>
                </div>
                <div className="flex items-center gap-4 text-base text-gray-700 bg-white/50 rounded-lg p-3">
                  <User className="w-5 h-5 text-blue-600" />
                  <span>Track patient trends</span>
                </div>
              </div>
              <Button
                onClick={() => onRoleSelect("doctor")}
                className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-semibold py-3 px-6 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200"
                size="lg"
              >
                Continue as Doctor
              </Button>
            </CardContent>
          </Card>
        </div>

        <div className="text-center mt-12">
          <p className="text-base text-gray-500 bg-white/60 rounded-full px-6 py-2 inline-block shadow-sm">
            Powered by advanced AI technology for intelligent healthcare assistance
          </p>
        </div>
      </div>
    </div>
  )
}
