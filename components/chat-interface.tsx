"use client"

import { useState, useEffect, useRef } from "react"
import { Send, Bot, User, Loader2, Calendar, Stethoscope, BarChart3, Wrench, Tool, AlertCircle } from "lucide-react"
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

interface MCPTool {
  name: string
  description: string
  inputSchema: {
    type: string
    properties: Record<string, any>
    required: string[]
  }
}

export default function ChatInterface({ userRole = "patient" }: { userRole?: string }) {
  // Ensure userRole is always a string
  const safeUserRole = userRole || "patient"
  
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string>("")
  const [availableTools, setAvailableTools] = useState<MCPTool[]>([])
  const [showTools, setShowTools] = useState(false)
  const [mcpStatus, setMcpStatus] = useState<string>("checking")
  const [mcpError, setMcpError] = useState<string>("")
  const [showDebug, setShowDebug] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Ensure sessionId is always a string
  const safeSessionId = sessionId || ""
  
  // Ensure messages is always an array
  const safeMessages = Array.isArray(messages) ? messages : []
  
  // Ensure availableTools is always an array
  const safeAvailableTools = Array.isArray(availableTools) ? availableTools : []
  
  // Ensure mcpStatus is always a string
  const safeMcpStatus = mcpStatus || "checking"
  
  // Ensure mcpError is always a string
  const safeMcpError = mcpError || ""
  
  // Ensure isLoading is always a boolean
  const safeIsLoading = isLoading === true
  
  // Ensure showTools is always a boolean
  const safeShowTools = showTools === true
  
  // Ensure inputValue is always a string
  const safeInputValue = inputValue || ""

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [safeMessages])

  useEffect(() => {
    const initializeChat = async () => {
      try {
        // Create session
        const sessionResponse = await fetch("/api/sessions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_role: safeUserRole })
        })
        
        if (sessionResponse.ok) {
          const data = await sessionResponse.json()
          const sessionId = data?.session_id || `session_${Date.now()}`
          setSessionId(sessionId)
          mcpClient.setSessionId(sessionId)
          
          // Check MCP server status with timeout
          try {
            const mcpHealthy = await Promise.race([
              mcpClient.healthCheck(),
              new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), 5000))
            ])
            
            if (mcpHealthy === true) {
              setMcpStatus("connected")
              setMcpError("")
              
              // Discover available MCP tools
              try {
                const toolsInfo = await mcpClient.discoverTools()
                const tools = Array.isArray(toolsInfo?.tools) ? toolsInfo.tools : []
                setAvailableTools(tools)
                console.log("MCP tools discovered:", tools)
              } catch (error) {
                console.warn("MCP tool discovery failed:", error)
                setMcpStatus("tools_failed")
                setMcpError("Tool discovery failed, but basic chat is available")
                setAvailableTools([])
              }
            } else {
              setMcpStatus("disconnected")
              setMcpError("MCP server not responding")
              setAvailableTools([])
            }
          } catch (error) {
            console.warn("MCP health check failed:", error)
            setMcpStatus("disconnected")
            setMcpError("Cannot connect to MCP server")
            setAvailableTools([])
          }
          
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
        setMcpStatus("error")
        setMcpError("Failed to initialize chat session")
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
  }, [safeUserRole])

  const handleSendMessage = async () => {
    if (!safeInputValue?.trim() || !safeSessionId) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: safeInputValue,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue("")
    setIsLoading(true)

    try {
      // Only try MCP tools if server is connected
      if (safeMcpStatus === "connected") {
        const mcpResponse = await processMessageWithMCP(safeInputValue, safeUserRole)
        
        if (mcpResponse) {
          setMessages(prev => [...prev, mcpResponse])
          setIsLoading(false)
          return
        }
      }
      
      // Fallback to regular chat
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: safeInputValue,
          session_id: safeSessionId,
          user_role: safeUserRole
        })
      })

      if (response.ok) {
        const data = await response.json()
        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: data?.response || "I'm sorry, I didn't get a proper response. Please try again.",
          timestamp: new Date(),
          toolCalls: data?.tool_calls || []
        }
        setMessages(prev => [...prev, assistantMessage])
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
    } catch (error) {
      console.error("Error processing message:", error)
      
      // Provide more helpful error messages based on the error type
      let errorMessage = "I'm sorry, I encountered an error processing your request. Please try again."
      
      if (error instanceof Error) {
        if (error.message.includes("Failed to fetch")) {
          errorMessage = "I'm having trouble connecting to my tools right now. Please check your internet connection and try again."
        } else if (error.message.includes("HTTP 500")) {
          errorMessage = "There's a server error. Please try again in a few moments."
        } else if (error.message.includes("HTTP 404")) {
          errorMessage = "The requested service is not available right now. Please try again later."
        } else if (error.message.includes("timeout")) {
          errorMessage = "The request is taking too long. Please try again."
        }
      }
      
      const errorResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: errorMessage,
        timestamp: new Date(),
        toolCalls: [{
          tool_name: "error_handler",
          result: { error: error instanceof Error ? error.message : String(error) },
          success: false
        }]
      }
      setMessages(prev => [...prev, errorResponse])
    } finally {
      setIsLoading(false)
    }
  }

  const processMessageWithMCP = async (message: string, role: string): Promise<ChatMessage | null> => {
    if (safeMcpStatus !== "connected") {
      console.log("MCP not connected, skipping tool execution")
      return null
    }

    console.log("Processing message with MCP:", message)
    const lowerMessage = message.toLowerCase()
    
    // Check for appointment scheduling
    if (lowerMessage.includes("schedule") || lowerMessage.includes("book") || lowerMessage.includes("appointment") || lowerMessage.includes("confirm")) {
      console.log("Executing schedule_appointment tool")
      try {
        const result = await mcpClient.executeTool('schedule_appointment', {
          doctor_name: "Dr. Smith", // Default - would be extracted from message
          patient_name: "John Doe", // Default - would be extracted from message
          patient_email: "john@example.com", // Default - would be extracted from message
          appointment_date: "2024-01-15", // Default - would be extracted from message
          appointment_time: "10:00", // Default - would be extracted from message
          symptoms: "General consultation"
        })

        console.log("Schedule appointment result:", result)

        // Safe access to result properties with fallbacks
        const resultText = result?.content?.[0]?.text || 'Processing...'
        const isError = result?.isError || false

        return {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `I've scheduled your appointment! Here are the details:\n\n**Appointment ID:** ${resultText}\n\n${isError ? 'There was an error, but I\'m working on it.' : 'Appointment scheduled successfully!'}`,
          timestamp: new Date(),
          toolCalls: [{
            tool_name: "schedule_appointment",
            result: result || {},
            success: !isError
          }]
        }
      } catch (error) {
        console.error("Error scheduling appointment:", error)
        return null
      }
    }

    // Check for doctor availability
    if (lowerMessage.includes("availability") || lowerMessage.includes("available") || lowerMessage.includes("slot") || lowerMessage.includes("time")) {
      console.log("Executing check_doctor_availability tool")
      try {
        const result = await mcpClient.executeTool('check_doctor_availability', {
          doctor_name: "Dr. Smith",
          date: "2024-01-15"
        })

        console.log("Check availability result:", result)

        // Safe access to result properties with fallbacks
        const resultText = result?.content?.[0]?.text || 'Checking availability...'
        const isError = result?.isError || false

        return {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `Here's the availability for Dr. Smith on 2024-01-15:\n\n${resultText}`,
          timestamp: new Date(),
          toolCalls: [{
            tool_name: "check_doctor_availability",
            result: result || {},
            success: !isError
          }]
        }
      } catch (error) {
        console.error("Error checking availability:", error)
        return null
      }
    }

    // Check for doctor listing
    if (lowerMessage.includes("doctors") || lowerMessage.includes("list") || lowerMessage.includes("specialist") || lowerMessage.includes("cardiologist")) {
      console.log("Executing list_doctors tool")
      try {
        const result = await mcpClient.executeTool('list_doctors', {})

        console.log("List doctors result:", result)

        // Safe access to result properties with fallbacks
        const resultText = result?.content?.[0]?.text || 'Loading doctors...'
        const isError = result?.isError || false

        return {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `Here are the available doctors:\n\n${resultText}`,
          timestamp: new Date(),
          toolCalls: [{
            tool_name: "list_doctors",
            result: result || {},
            success: !isError
          }]
        }
      } catch (error) {
        console.error("Error listing doctors:", error)
        return null
      }
    }

    // Check for patient search by symptoms
    if (lowerMessage.includes("search") || lowerMessage.includes("symptoms") || lowerMessage.includes("fever") || lowerMessage.includes("patients")) {
      console.log("Executing search_patients_by_symptoms tool")
      try {
        const result = await mcpClient.executeTool('search_patients_by_symptoms', {
          symptoms: "fever" // Default - would be extracted from message
        })

        console.log("Search patients result:", result)

        // Safe access to result properties with fallbacks
        const resultText = result?.content?.[0]?.text || 'Searching patients...'
        const isError = result?.isError || false

        return {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `Here are the patients with fever symptoms:\n\n${resultText}`,
          timestamp: new Date(),
          toolCalls: [{
            tool_name: "search_patients_by_symptoms",
            result: result || {},
            success: !isError
          }]
        }
      } catch (error) {
        console.error("Error searching patients:", error)
        return null
      }
    }

    // Check for appointment statistics
    if (lowerMessage.includes("statistics") || lowerMessage.includes("analytics") || lowerMessage.includes("how many") || lowerMessage.includes("report")) {
      console.log("Executing get_appointment_statistics tool")
      try {
        const result = await mcpClient.executeTool('get_appointment_statistics', {
          doctor_name: "Dr. Smith",
          period: "week"
        })

        console.log("Get statistics result:", result)

        // Safe access to result properties with fallbacks
        const resultText = result?.content?.[0]?.text || 'Loading statistics...'
        const isError = result?.isError || false

        return {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `Here are the appointment statistics for this week:\n\n${resultText}`,
          timestamp: new Date(),
          toolCalls: [{
            tool_name: "get_appointment_statistics",
            result: result || {},
            success: !isError
          }]
        }
      } catch (error) {
        console.error("Error getting statistics:", error)
        return null
      }
    }

    // Check for appointment cancellation
    if (lowerMessage.includes("cancel") || lowerMessage.includes("reschedule")) {
      console.log("Executing cancel_calendar_event tool")
      try {
        const result = await mcpClient.executeTool('cancel_calendar_event', {
          event_id: "appointment_123", // Default - would be extracted from message
          reason: "Patient request"
        })

        console.log("Cancel appointment result:", result)

        // Safe access to result properties with fallbacks
        const resultText = result?.content?.[0]?.text || 'Processing cancellation...'
        const isError = result?.isError || false

        return {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `I've processed your cancellation request:\n\n${resultText}`,
          timestamp: new Date(),
          toolCalls: [{
            tool_name: "cancel_calendar_event",
            result: result || {},
            success: !isError
          }]
        }
      } catch (error) {
        console.error("Error cancelling appointment:", error)
        return null
      }
    }

    // Check for appointment status
    if (lowerMessage.includes("status") || lowerMessage.includes("check") || lowerMessage.includes("appointment")) {
      console.log("Executing get_appointment_statistics tool for status")
      try {
        const result = await mcpClient.executeTool('get_appointment_statistics', {
          doctor_name: "Dr. Smith",
          period: "today"
        })

        console.log("Check status result:", result)

        // Safe access to result properties with fallbacks
        const resultText = result?.content?.[0]?.text || 'Checking appointment status...'
        const isError = result?.isError || false

        return {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `Here's your appointment status:\n\n${resultText}`,
          timestamp: new Date(),
          toolCalls: [{
            tool_name: "get_appointment_statistics",
            result: result || {},
            success: !isError
          }]
        }
      } catch (error) {
        console.error("Error checking appointment status:", error)
        return null
      }
    }

    console.log("No MCP tool matched for message:", message)
    return null
  }

  const handleSuggestionClick = (suggestion: string) => {
    if (suggestion && typeof suggestion === 'string') {
      setInputValue(suggestion)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const getMCPStatusColor = (): string => {
    switch (safeMcpStatus) {
      case "connected": return "bg-green-500"
      case "disconnected": return "bg-red-500"
      case "tools_failed": return "bg-yellow-500"
      case "error": return "bg-red-600"
      case "checking": return "bg-gray-500"
      default: return "bg-gray-500"
    }
  }

  const getMCPStatusText = (): string => {
    switch (safeMcpStatus) {
      case "connected": return "MCP Connected"
      case "disconnected": return "MCP Disconnected"
      case "tools_failed": return "MCP Tools Failed"
      case "error": return "MCP Error"
      case "checking": return "Checking MCP..."
      default: return "Unknown Status"
    }
  }

  const retryMCPConnection = async () => {
    setMcpStatus("checking")
    setMcpError("")
    
    try {
      const mcpHealthy = await mcpClient.healthCheck()
      if (mcpHealthy === true) {
        setMcpStatus("connected")
        try {
          const toolsInfo = await mcpClient.discoverTools()
          const tools = Array.isArray(toolsInfo?.tools) ? toolsInfo.tools : []
          setAvailableTools(tools)
        } catch (error) {
          console.warn("Tool discovery failed during retry:", error)
          setAvailableTools([])
        }
      } else {
        setMcpStatus("disconnected")
        setMcpError("MCP server not responding")
        setAvailableTools([])
      }
    } catch (error) {
      setMcpStatus("error")
      setMcpError("Connection failed")
      setAvailableTools([])
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
            {/* MCP Status Indicator */}
            <div className="flex items-center space-x-2">
              {safeMcpStatus && typeof safeMcpStatus === 'string' && (
                <div className={`px-3 py-2 rounded-lg text-white text-sm ${getMCPStatusColor()}`}>
                  {getMCPStatusText()}
                </div>
              )}
              
              {safeMcpStatus === "disconnected" && (
                <button
                  onClick={retryMCPConnection}
                  className="px-2 py-1 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded transition-colors"
                >
                  Retry
                </button>
              )}
            </div>
            
            {safeMcpStatus === "connected" && (
              <>
                <button
                  onClick={() => setShowTools(!safeShowTools)}
                  className="flex items-center space-x-2 px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  <Tool className="w-4 h-4" />
                  <span>MCP Tools ({safeAvailableTools.length})</span>
                </button>
                
                {/* Debug Panel Toggle */}
                <button
                  onClick={() => setShowDebug(!showDebug)}
                  className="flex items-center space-x-2 px-3 py-2 text-sm bg-yellow-100 hover:bg-yellow-200 rounded-lg transition-colors"
                >
                  <Wrench className="w-4 h-4" />
                  <span>Debug</span>
                </button>
              </>
            )}
          </div>
        </div>
        
        {/* MCP Error Display */}
        {safeMcpError && typeof safeMcpError === 'string' && safeMcpError.trim() && (
          <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-yellow-600" />
              <span className="text-sm text-yellow-800">
                {safeMcpError}. Basic chat functionality is still available.
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Tools Panel */}
      {safeShowTools && safeMcpStatus === "connected" && (
        <div className="bg-gray-50 border-b border-gray-200 p-4">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Available MCP Tools</h3>
          {safeAvailableTools.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {safeAvailableTools.map((tool) => (
                <div key={tool.name || `tool-${Math.random()}`} className="bg-white p-3 rounded-lg border border-gray-200">
                  <div className="flex items-center space-x-2 mb-2">
                    <Wrench className="w-4 h-4 text-blue-600" />
                    <span className="font-medium text-sm">{tool.name || 'Unnamed Tool'}</span>
                  </div>
                  <p className="text-xs text-gray-600 mb-2">{tool.description || 'No description available'}</p>
                  <div className="text-xs text-gray-500">
                    <strong>Parameters:</strong> {tool.inputSchema?.properties ? Object.keys(tool.inputSchema.properties).join(", ") : 'No parameters'}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-4 text-gray-500">
              {safeMcpStatus === "connected" ? "No tools available" : "Tools not loaded - check MCP connection"}
            </div>
          )}
        </div>
      )}

      {/* Debug Panel */}
      {showDebug && (
        <div className="bg-yellow-50 border-b border-yellow-200 p-4">
          <h3 className="text-sm font-medium text-yellow-700 mb-3">MCP Debug Information</h3>
          <div className="space-y-2 text-xs">
            <div><strong>MCP Status:</strong> {safeMcpStatus}</div>
            <div><strong>MCP Error:</strong> {safeMcpError || 'None'}</div>
            <div><strong>Available Tools:</strong> {safeAvailableTools.length}</div>
            <div><strong>Session ID:</strong> {safeSessionId || 'Not set'}</div>
            <div><strong>User Role:</strong> {safeUserRole}</div>
            <div><strong>MCP Server URL:</strong> {process.env.NEXT_PUBLIC_MCP_SERVER_URL || 'http://localhost:8000'}</div>
            
            {/* Test MCP Connection Button */}
            <button
              onClick={async () => {
                try {
                  const healthy = await mcpClient.healthCheck()
                  console.log("MCP Health Check Result:", healthy)
                  alert(`MCP Health Check: ${healthy ? 'SUCCESS' : 'FAILED'}`)
                } catch (error) {
                  console.error("MCP Health Check Error:", error)
                  alert(`MCP Health Check Error: ${error}`)
                }
              }}
              className="px-3 py-1 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded transition-colors"
            >
              Test MCP Connection
            </button>
            
            {/* Test Tool Discovery Button */}
            <button
              onClick={async () => {
                try {
                  const tools = await mcpClient.discoverTools()
                  console.log("MCP Tools Discovery Result:", tools)
                  alert(`MCP Tools Discovery: ${tools.tools.length} tools found`)
                } catch (error) {
                  console.error("MCP Tools Discovery Error:", error)
                  alert(`MCP Tools Discovery Error: ${error}`)
                }
              }}
              className="px-3 py-1 text-xs bg-green-500 hover:bg-green-600 text-white rounded transition-colors ml-2"
            >
              Test Tool Discovery
            </button>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {safeMessages.map((message) => (
          <div key={message.id || `msg-${Math.random()}`} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
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
                <div className="whitespace-pre-wrap">{message.content || 'No content'}</div>
                
                {/* Tool Calls */}
                {message.toolCalls && Array.isArray(message.toolCalls) && message.toolCalls.length > 0 && (
                  <div className="mt-3 space-y-2">
                    {message.toolCalls.map((toolCall, index) => (
                      <div key={index} className={`text-xs p-2 rounded ${
                        toolCall.success ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                      }`}>
                        <div className="font-medium">{toolCall.tool_name || 'Unknown Tool'}</div>
                        <div className="text-xs opacity-75">
                          {toolCall.success ? "Success" : "Failed"}
                        </div>
                        {toolCall.result && typeof toolCall.result === 'object' && (
                          <div className="text-xs mt-1">
                            <pre className="whitespace-pre-wrap">
                              {JSON.stringify(toolCall.result, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
                
                {/* Suggestions */}
                {message.suggestions && Array.isArray(message.suggestions) && message.suggestions.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {message.suggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => handleSuggestionClick(suggestion || '')}
                        className="px-3 py-1 text-xs bg-blue-100 hover:bg-blue-200 text-blue-800 rounded-full transition-colors"
                      >
                        {suggestion || 'Suggestion'}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {safeIsLoading && (
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
              value={safeInputValue || ''}
              onChange={(e) => setInputValue(e.target.value || '')}
              onKeyPress={handleKeyPress}
              placeholder="Type your message here..."
              className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={2}
              disabled={safeIsLoading}
            />
          </div>
          <button
            onClick={handleSendMessage}
            disabled={!safeInputValue?.trim() || safeIsLoading}
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
