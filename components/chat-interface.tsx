"use client"

import { useState, useEffect, useRef } from "react"
import { Send, Bot, User, Loader2, Calendar, Stethoscope, BarChart3, Wrench, Tool } from "lucide-react"
import { toolClient, appointmentTools, doctorTools, searchTools } from "@/lib/tool-client"

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

interface ToolDefinition {
  name: string
  description: string
  type: string
  parameters: Array<{
    name: string
    type: string
    description: string
    required: boolean
  }>
  tags: string[]
}

export default function ChatInterface({ userRole = "patient" }: { userRole?: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string>("")
  const [availableTools, setAvailableTools] = useState<ToolDefinition[]>([])
  const [showTools, setShowTools] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    const initializeChat = async () => {
      try {
        // Create session
        const sessionResponse = await fetch("/api/sessions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_role: userRole })
        })
        
        if (sessionResponse.ok) {
          const data = await sessionResponse.json()
          setSessionId(data.session_id)
          
          // Discover available tools
          const tools = await toolClient.discoverTools()
          setAvailableTools(tools)
          
          // Add welcome message
          setMessages([
            {
              id: "welcome",
              role: "assistant",
              content: `Welcome to MedAI! I'm your AI assistant for managing doctor appointments. I can help you schedule appointments, check doctor availability, and more. What would you like to do today?`,
              timestamp: new Date(),
              suggestions: [
                "Schedule an appointment",
                "Check doctor availability", 
                "List available doctors",
                "View my appointments"
              ]
            }
          ])
        }
      } catch (error) {
        console.error("Error initializing chat:", error)
        setMessages([
          {
            id: "error",
            role: "assistant",
            content: "Sorry, I encountered an error while initializing. Please try refreshing the page.",
            timestamp: new Date()
          }
        ])
      }
    }

    initializeChat()
  }, [userRole])

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !sessionId) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: inputValue,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue("")
    setIsLoading(true)

    try {
      // Try to process with tools first
      const toolResponse = await processMessageWithTools(inputValue, userRole)
      
      if (toolResponse) {
        setMessages(prev => [...prev, toolResponse])
      } else {
        // Fallback to regular chat
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: inputValue,
            session_id: sessionId,
            user_role: userRole
          })
        })

        if (response.ok) {
          const data = await response.json()
          const assistantMessage: ChatMessage = {
            id: (Date.now() + 1).toString(),
            role: "assistant",
            content: data.response,
            timestamp: new Date(),
            toolCalls: data.tool_calls
          }
          setMessages(prev => [...prev, assistantMessage])
        } else {
          throw new Error("Failed to get response")
        }
      }
    } catch (error) {
      console.error("Error processing message:", error)
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "I'm sorry, I encountered an error processing your request. Please try again.",
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const processMessageWithTools = async (message: string, role: string): Promise<ChatMessage | null> => {
    const lowerMessage = message.toLowerCase()
    
    // Check for appointment scheduling
    if (lowerMessage.includes("schedule") || lowerMessage.includes("book") || lowerMessage.includes("appointment")) {
      try {
        // Extract basic info from message (in real implementation, this would use NLP)
        const result = await appointmentTools.scheduleAppointment({
          doctor_name: "Dr. Smith", // Default - would be extracted from message
          patient_name: "John Doe", // Default - would be extracted from message
          patient_email: "john@example.com", // Default - would be extracted from message
          appointment_date: "2024-01-15", // Default - would be extracted from message
          appointment_time: "10:00", // Default - would be extracted from message
          symptoms: "General consultation"
        })

        return {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `I've scheduled your appointment! Here are the details:\n\n**Appointment ID:** ${result.result.appointment_id}\n**Status:** ${result.result.status}\n**Calendar Event:** ${result.result.calendar_event_id ? 'Created' : 'Not created'}\n**Email Confirmation:** ${result.result.email_sent ? 'Sent' : 'Not sent'}\n\n${result.result.message}`,
          timestamp: new Date(),
          toolCalls: [{
            tool_name: "schedule_appointment",
            result: result.result,
            success: result.result.status === "scheduled"
          }]
        }
      } catch (error) {
        console.error("Error scheduling appointment:", error)
        return null
      }
    }

    // Check for doctor availability
    if (lowerMessage.includes("availability") || lowerMessage.includes("available")) {
      try {
        const result = await appointmentTools.checkDoctorAvailability({
          doctor_name: "Dr. Smith",
          date: "2024-01-15"
        })

        return {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `Here's the availability for Dr. Smith on 2024-01-15:\n\n**Available Slots:** ${result.result.total_available}\n**Booked Slots:** ${result.result.total_booked}\n\n${result.result.message}`,
          timestamp: new Date(),
          toolCalls: [{
            tool_name: "check_doctor_availability",
            result: result.result,
            success: !result.result.error
          }]
        }
      } catch (error) {
        console.error("Error checking availability:", error)
        return null
      }
    }

    // Check for doctor listing
    if (lowerMessage.includes("doctors") || lowerMessage.includes("list")) {
      try {
        const result = await appointmentTools.listDoctors()

        return {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `Here are the available doctors:\n\n${result.result.doctors.map((d: any) => `• **${d.name}** - ${d.specialty} (${d.location})`).join('\n')}\n\nTotal: ${result.result.count} doctors`,
          timestamp: new Date(),
          toolCalls: [{
            tool_name: "list_doctors",
            result: result.result,
            success: !result.result.error
          }]
        }
      } catch (error) {
        console.error("Error listing doctors:", error)
        return null
      }
    }

    return null
  }

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
              <Stethoscope className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">MedAI Assistant</h1>
              <p className="text-sm text-gray-500">AI-powered doctor appointment system</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowTools(!showTools)}
              className="flex items-center space-x-2 px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <Tool className="w-4 h-4" />
              <span>Tools ({availableTools.length})</span>
            </button>
          </div>
        </div>
      </div>

      {/* Tools Panel */}
      {showTools && (
        <div className="bg-gray-50 border-b border-gray-200 p-4">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Available Tools</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {availableTools.map((tool) => (
              <div key={tool.name} className="bg-white p-3 rounded-lg border border-gray-200">
                <div className="flex items-center space-x-2 mb-2">
                  <Wrench className="w-4 h-4 text-blue-600" />
                  <span className="font-medium text-sm">{tool.name}</span>
                </div>
                <p className="text-xs text-gray-600 mb-2">{tool.description}</p>
                <div className="flex flex-wrap gap-1">
                  {tool.tags.map((tag) => (
                    <span key={tag} className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`flex items-start space-x-3 max-w-[80%] ${message.role === "user" ? "flex-row-reverse space-x-reverse" : ""}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                message.role === "user" ? "bg-blue-600" : "bg-gray-600"
              }`}>
                {message.role === "user" ? (
                  <User className="w-5 h-5 text-white" />
                ) : (
                  <Bot className="w-5 h-5 text-white" />
                )}
              </div>
              
              <div className={`rounded-lg p-3 ${
                message.role === "user" 
                  ? "bg-blue-600 text-white" 
                  : "bg-gray-100 text-gray-900"
              }`}>
                <div className="whitespace-pre-wrap">{message.content}</div>
                
                {/* Tool Calls */}
                {message.toolCalls && message.toolCalls.length > 0 && (
                  <div className="mt-3 space-y-2">
                    {message.toolCalls.map((toolCall, index) => (
                      <div key={index} className={`text-xs p-2 rounded ${
                        toolCall.success ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                      }`}>
                        <div className="font-medium">{toolCall.tool_name}</div>
                        <div className="text-xs opacity-75">
                          {toolCall.success ? "Success" : "Failed"}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                
                {/* Suggestions */}
                {message.suggestions && message.suggestions.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {message.suggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="px-3 py-1 text-xs bg-blue-100 hover:bg-blue-200 text-blue-800 rounded-full transition-colors"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="bg-gray-100 rounded-lg p-3">
                <div className="flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-gray-600">Thinking...</span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 p-4">
        <div className="flex space-x-3">
          <div className="flex-1">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message here..."
              className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={2}
              disabled={isLoading}
            />
          </div>
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
          >
            <Send className="w-4 h-4" />
            <span>Send</span>
          </button>
        </div>
      </div>
    </div>
  )
}
