"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Send, Bot, User, Loader2, Calendar, Stethoscope, BarChart3, Wrench } from "lucide-react"
import { mcpClient, appointmentTools, doctorTools, searchTools } from "@/lib/mcp-client"

interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  toolCalls?: Array<{
    tool_name: string
    result: any
    success: boolean
  }>
  suggestions?: string[]
}

interface ChatInterfaceProps {
  userRole: "patient" | "doctor"
}

export default function ChatInterface({ userRole }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      role: "assistant",
      content:
        userRole === "patient"
          ? "Hello! I'm your AI medical assistant. I can help you schedule appointments, check doctor availability, and answer questions about your healthcare. How can I assist you today?"
          : "Hello Doctor! I can help you get appointment statistics, view patient reports, and manage your schedule. What would you like to know?",
      timestamp: new Date(),
      suggestions: userRole === "patient" 
        ? ["Schedule an appointment", "Check doctor availability", "Find doctors by specialty"]
        : ["View appointment stats", "Check my schedule", "Search patients by symptoms"]
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [availableTools, setAvailableTools] = useState<any[]>([])
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  // Initialize session and discover tools
  useEffect(() => {
    const initializeChat = async () => {
      try {
        // Create session
        const response = await fetch("/api/session/create", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_type: userRole }),
        })
        const data = await response.json()
        setSessionId(data.session_id)
        mcpClient.setSessionId(data.session_id)
        console.log("[v0] Session created:", data.session_id)

        // Discover MCP tools
        try {
          const toolsInfo = await mcpClient.discoverTools(true)
          setAvailableTools(toolsInfo.tools)
          console.log("[MCP] Available tools:", toolsInfo.tools)
        } catch (error) {
          console.warn("MCP tool discovery failed, using fallback:", error)
        }
      } catch (error) {
        console.error("Failed to initialize chat:", error)
      }
    }
    initializeChat()
  }, [userRole])

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue("")
    setIsLoading(true)

    try {
      // First, try to use MCP tools directly
      const mcpResponse = await processMessageWithMCP(inputValue, userRole)
      
      if (mcpResponse) {
        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: mcpResponse.content,
          timestamp: new Date(),
          toolCalls: mcpResponse.toolCalls,
          suggestions: mcpResponse.suggestions
        }
        
        setMessages((prev) => [...prev, assistantMessage])
      } else {
        // Fallback to regular chat API
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: inputValue,
            session_id: sessionId,
            user_type: userRole,
          }),
        })

        const data = await response.json()
        console.log("[v0] Chat response received:", data)

        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: data.response,
          timestamp: new Date(),
          toolCalls: data.tool_calls,
          suggestions: data.suggestions
        }

        setMessages((prev) => [...prev, assistantMessage])
      }
    } catch (error) {
      console.error("Error processing message:", error)
      
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "I apologize, but I encountered an error processing your request. Please try again or rephrase your question.",
        timestamp: new Date(),
      }
      
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const processMessageWithMCP = async (message: string, userRole: "patient" | "doctor") => {
    try {
      const lowerMessage = message.toLowerCase()
      
      // Patient-specific tool calls
      if (userRole === "patient") {
        // Schedule appointment
        if (lowerMessage.includes("schedule") || lowerMessage.includes("book") || lowerMessage.includes("make appointment")) {
          const result = await handleAppointmentScheduling(message)
          return {
            content: result.content,
            toolCalls: result.toolCalls,
            suggestions: ["Check appointment status", "Modify appointment", "Cancel appointment"]
          }
        }
        
        // Check availability
        if (lowerMessage.includes("available") || lowerMessage.includes("availability") || lowerMessage.includes("when")) {
          const result = await handleAvailabilityCheck(message)
          return {
            content: result.content,
            toolCalls: result.toolCalls,
            suggestions: ["Schedule appointment", "Find other doctors", "Check different dates"]
          }
        }
        
        // List doctors
        if (lowerMessage.includes("doctor") || lowerMessage.includes("specialist") || lowerMessage.includes("find")) {
          const result = await handleDoctorSearch(message)
          return {
            content: result.content,
            toolCalls: result.toolCalls,
            suggestions: ["Schedule with this doctor", "Check availability", "Find other specialists"]
          }
        }
      }
      
      // Doctor-specific tool calls
      if (userRole === "doctor") {
        // Get appointment stats
        if (lowerMessage.includes("stats") || lowerMessage.includes("statistics") || lowerMessage.includes("report")) {
          const result = await handleAppointmentStats(message)
          return {
            content: result.content,
            toolCalls: result.toolCalls,
            suggestions: ["View detailed report", "Check patient history", "Export data"]
          }
        }
        
        // Search patients
        if (lowerMessage.includes("patient") || lowerMessage.includes("search") || lowerMessage.includes("symptoms")) {
          const result = await handlePatientSearch(message)
          return {
            content: result.content,
            toolCalls: result.toolCalls,
            suggestions: ["View patient details", "Check appointment history", "Send notification"]
          }
        }
      }
      
      return null // No MCP tool matched, fall back to regular chat
      
    } catch (error) {
      console.error("Error in MCP processing:", error)
      return null
    }
  }

  const handleAppointmentScheduling = async (message: string) => {
    // Extract appointment details from message (simplified)
    const doctorMatch = message.match(/dr\.?\s*(\w+)/i)
    const dateMatch = message.match(/(\d{1,2}\/\d{1,2}|\d{4}-\d{2}-\d{2})/)
    const timeMatch = message.match(/(\d{1,2}:\d{2}\s*(?:am|pm)?)/i)
    
    if (doctorMatch && dateMatch) {
      const doctorName = `Dr. ${doctorMatch[1]}`
      const date = dateMatch[1]
      const time = timeMatch ? timeMatch[1] : "09:00"
      
      try {
        const result = await appointmentTools.scheduleAppointment({
          doctor_name: doctorName,
          patient_name: "Patient", // Would come from user profile
          patient_email: "patient@example.com", // Would come from user profile
          appointment_date: date,
          appointment_time: time,
          symptoms: "General consultation"
        })
        
        return {
          content: `Great! I've scheduled your appointment with ${doctorName} on ${date} at ${time}. You'll receive a confirmation email shortly.`,
          toolCalls: [{
            tool_name: "appointments/schedule_enhanced",
            result: result,
            success: true
          }]
        }
      } catch (error) {
        return {
          content: "I'm sorry, but I couldn't schedule the appointment. Please try again or contact our support team.",
          toolCalls: [{
            tool_name: "appointments/schedule_enhanced",
            result: { error: error.message },
            success: false
          }]
        }
      }
    }
    
    return {
      content: "I'd be happy to help you schedule an appointment! Please provide the doctor's name and preferred date/time.",
      toolCalls: []
    }
  }

  const handleAvailabilityCheck = async (message: string) => {
    const doctorMatch = message.match(/dr\.?\s*(\w+)/i)
    const dateMatch = message.match(/(\d{1,2}\/\d{1,2}|\d{4}-\d{2}-\d{2})/)
    
    if (doctorMatch && dateMatch) {
      const doctorName = `Dr. ${doctorMatch[1]}`
      const date = dateMatch[1]
      
      try {
        const result = await appointmentTools.checkAvailability(doctorName, date)
        
        return {
          content: `Here are the available slots for ${doctorName} on ${date}: ${result.available_slots.join(", ")}`,
          toolCalls: [{
            tool_name: "appointments/check_availability",
            result: result,
            success: true
          }]
        }
      } catch (error) {
        return {
          content: "I couldn't check the availability. Please try again.",
          toolCalls: [{
            tool_name: "appointments/check_availability",
            result: { error: error.message },
            success: false
          }]
        }
      }
    }
    
    return {
      content: "I can check doctor availability for you. Please provide the doctor's name and date.",
      toolCalls: []
    }
  }

  const handleDoctorSearch = async (message: string) => {
    const specialtyMatch = message.match(/(?:specialist|specialty|find)\s+(?:in\s+)?(\w+)/i)
    const specialty = specialtyMatch ? specialtyMatch[1] : undefined
    
    try {
      const result = await doctorTools.listDoctors(specialty)
      
      const doctorList = result.doctors.map((d: any) => 
        `${d.name} (${d.specialty}) - ${d.available ? 'Available' : 'Unavailable'}`
      ).join('\n')
      
      return {
        content: `Here are the available doctors${specialty ? ` in ${specialty}` : ''}:\n${doctorList}`,
        toolCalls: [{
          tool_name: "doctors/list",
          result: result,
          success: true
        }]
      }
    } catch (error) {
      return {
        content: "I couldn't find the doctors. Please try again.",
        toolCalls: [{
          tool_name: "doctors/list",
          result: { error: error.message },
          success: false
        }]
      }
    }
  }

  const handleAppointmentStats = async (message: string) => {
    const doctorMatch = message.match(/dr\.?\s*(\w+)/i)
    const periodMatch = message.match(/(day|week|month|year)/i)
    
    const doctorName = doctorMatch ? `Dr. ${doctorMatch[1]}` : "Dr. Smith"
    const period = periodMatch ? periodMatch[1] as 'day' | 'week' | 'month' | 'year' : 'month'
    
    try {
      const result = await doctorTools.getAppointmentStats(doctorName, period)
      
      return {
        content: `Here are the appointment statistics for ${doctorName} (${period}):\nTotal: ${result.total_appointments}\nCompleted: ${result.completed}\nCancelled: ${result.cancelled}\nCompletion Rate: ${result.completion_rate}%`,
        toolCalls: [{
          tool_name: "analytics/appointment_stats",
          result: result,
          success: true
        }]
      }
    } catch (error) {
      return {
        content: "I couldn't get the appointment statistics. Please try again.",
        toolCalls: [{
          tool_name: "analytics/appointment_stats",
          result: { error: error.message },
          success: false
        }]
      }
    }
  }

  const handlePatientSearch = async (message: string) => {
    const symptomsMatch = message.match(/symptoms?[:\s]+(.+)/i)
    const symptoms = symptomsMatch ? symptomsMatch[1] : "general"
    
    try {
      const result = await searchTools.searchPatientsBySymptoms(symptoms)
      
      if (result.patients.length > 0) {
        const patientList = result.patients.map((p: any) => 
          `${p.name} - ${p.symptoms} (Last visit: ${p.last_visit})`
        ).join('\n')
        
        return {
          content: `Found ${result.count} patients with symptoms: ${symptoms}\n${patientList}`,
          toolCalls: [{
            tool_name: "search/patients_by_symptoms",
            result: result,
            success: true
          }]
        }
      } else {
        return {
          content: `No patients found with symptoms: ${symptoms}`,
          toolCalls: [{
            tool_name: "search/patients_by_symptoms",
            result: result,
            success: true
          }]
        }
      }
    } catch (error) {
      return {
        content: "I couldn't search for patients. Please try again.",
        toolCalls: [{
          tool_name: "search/patients_by_symptoms",
          result: { error: error.message },
          success: false
        }]
      }
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Chat Messages */}
      <ScrollArea ref={scrollAreaRef} className="flex-1 p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted"
              }`}
            >
              <div className="flex items-start gap-2">
                {message.role === "assistant" && (
                  <Bot className="w-5 h-5 mt-0.5 text-primary" />
                )}
                <div className="flex-1">
                  <p className="text-sm">{message.content}</p>
                  
                  {/* Tool Calls Display */}
                  {message.toolCalls && message.toolCalls.length > 0 && (
                    <div className="mt-2 space-y-2">
                      {message.toolCalls.map((toolCall, index) => (
                        <div key={index} className="text-xs bg-background/50 rounded p-2">
                          <div className="flex items-center gap-1 mb-1">
                            <Wrench className="w-3 h-3" />
                            <span className="font-medium">{toolCall.tool_name}</span>
                            <Badge variant={toolCall.success ? "default" : "destructive"} className="text-xs">
                              {toolCall.success ? "Success" : "Failed"}
                            </Badge>
                          </div>
                          {toolCall.success && (
                            <pre className="text-xs overflow-x-auto">
                              {JSON.stringify(toolCall.result, null, 2)}
                            </pre>
                          )}
                          {!toolCall.success && (
                            <span className="text-destructive">{toolCall.result?.error}</span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {/* Suggestions */}
                  {message.suggestions && message.suggestions.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {message.suggestions.map((suggestion, index) => (
                        <Button
                          key={index}
                          variant="outline"
                          size="sm"
                          className="text-xs h-7"
                          onClick={() => handleSuggestionClick(suggestion)}
                        >
                          {suggestion}
                        </Button>
                      ))}
                    </div>
                  )}
                </div>
                {message.role === "user" && (
                  <User className="w-5 h-5 mt-0.5 text-primary" />
                )}
              </div>
              <div className="text-xs opacity-70 mt-2">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-muted rounded-lg p-3">
              <div className="flex items-center gap-2">
                <Loader2 className="w-5 h-5 animate-spin text-primary" />
                <span className="text-sm">Thinking...</span>
              </div>
            </div>
          </div>
        )}
      </ScrollArea>

      {/* Input Area */}
      <div className="border-t p-4">
        <div className="flex gap-2">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
            placeholder={
              userRole === "patient"
                ? "Ask me to schedule an appointment, check availability..."
                : "Ask me about appointment stats, patient reports..."
            }
            disabled={isLoading}
            className="flex-1"
          />
          <Button onClick={handleSendMessage} disabled={isLoading || !inputValue.trim()}>
            <Send className="w-4 h-4" />
          </Button>
        </div>
        
        {/* Quick Actions */}
        <div className="mt-3 flex flex-wrap gap-2">
          {userRole === "patient" ? (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSuggestionClick("Schedule an appointment")}
                className="text-xs h-7"
              >
                <Calendar className="w-3 h-3 mr-1" />
                Schedule
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSuggestionClick("Check doctor availability")}
                className="text-xs h-7"
              >
                <Stethoscope className="w-3 h-3 mr-1" />
                Check Availability
              </Button>
            </>
          ) : (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSuggestionClick("View appointment stats")}
                className="text-xs h-7"
              >
                <BarChart3 className="w-3 h-3 mr-1" />
                View Stats
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSuggestionClick("Search patients by symptoms")}
                className="text-xs h-7"
              >
                <Stethoscope className="w-3 h-3 mr-1" />
                Search Patients
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
