"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Send, Bot, User, Loader2, Calendar, Stethoscope, BarChart3 } from "lucide-react"

interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  toolCalls?: Array<{
    function_name: string
    result: any
  }>
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
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  // Initialize session
  useEffect(() => {
    const initSession = async () => {
      try {
        const response = await fetch("/api/session/create", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_type: userRole }),
        })
        const data = await response.json()
        setSessionId(data.session_id)
        console.log("[v0] Session created:", data.session_id)
      } catch (error) {
        console.error("Failed to create session:", error)
      }
    }
    initSession()
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
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error("Chat error:", error)
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "I apologize, but I encountered an error. Please try again.",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const getToolIcon = (toolName: string) => {
    switch (toolName) {
      case "check_doctor_availability":
      case "schedule_appointment":
        return <Calendar className="w-3 h-3" />
      case "get_appointment_stats":
        return <BarChart3 className="w-3 h-3" />
      default:
        return <Stethoscope className="w-3 h-3" />
    }
  }

  const suggestions =
    userRole === "patient"
      ? [
          "I want to book an appointment with Dr. Ahuja tomorrow morning",
          "What doctors are available this Friday afternoon?",
          "Check Dr. Johnson's availability for next week",
        ]
      : [
          "How many patients visited yesterday?",
          "Show me appointments for today",
          "How many patients with fever this week?",
        ]

  return (
    <div className="flex flex-col h-[600px] max-w-4xl mx-auto">
      <Card className="flex-1 flex flex-col">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Bot className="w-5 h-5 text-secondary" />
            AI Assistant Chat
            {sessionId && (
              <Badge variant="outline" className="text-xs">
                Session Active
              </Badge>
            )}
          </CardTitle>
        </CardHeader>

        <CardContent className="flex-1 flex flex-col p-0">
          {/* Messages */}
          <ScrollArea className="flex-1 px-6" ref={scrollAreaRef}>
            <div className="space-y-4 pb-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  {message.role === "assistant" && (
                    <div className="flex items-center justify-center w-8 h-8 bg-secondary rounded-full flex-shrink-0 mt-1">
                      <Bot className="w-4 h-4 text-secondary-foreground" />
                    </div>
                  )}

                  <div className={`max-w-[80%] ${message.role === "user" ? "order-1" : ""}`}>
                    <div
                      className={`rounded-lg px-4 py-3 ${
                        message.role === "user" ? "chat-message-user" : "chat-message-assistant"
                      }`}
                    >
                      <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                    </div>

                    {/* Tool calls */}
                    {message.toolCalls && message.toolCalls.length > 0 && (
                      <div className="mt-2 space-y-2">
                        {message.toolCalls.map((tool, index) => (
                          <div key={index} className="tool-call-indicator rounded-md px-3 py-2">
                            <div className="flex items-center gap-2 text-xs font-medium text-secondary">
                              {getToolIcon(tool.function_name)}
                              <span>Used: {tool.function_name.replace("_", " ")}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    <p className="text-xs text-muted-foreground mt-1">{message.timestamp.toLocaleTimeString()}</p>
                  </div>

                  {message.role === "user" && (
                    <div className="flex items-center justify-center w-8 h-8 bg-primary rounded-full flex-shrink-0 mt-1">
                      <User className="w-4 h-4 text-primary-foreground" />
                    </div>
                  )}
                </div>
              ))}

              {isLoading && (
                <div className="flex gap-3 justify-start">
                  <div className="flex items-center justify-center w-8 h-8 bg-secondary rounded-full flex-shrink-0">
                    <Bot className="w-4 h-4 text-secondary-foreground" />
                  </div>
                  <div className="chat-message-assistant rounded-lg px-4 py-3">
                    <div className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span className="text-sm">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>

          {/* Suggestions */}
          {messages.length === 1 && (
            <div className="px-6 py-3 border-t border-border">
              <p className="text-xs text-muted-foreground mb-2">Try asking:</p>
              <div className="flex flex-wrap gap-2">
                {suggestions.map((suggestion, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    className="text-xs h-7 bg-transparent"
                    onClick={() => setInputValue(suggestion)}
                  >
                    {suggestion}
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* Input */}
          <div className="p-6 border-t border-border">
            <div className="flex gap-2">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={`Ask me anything about ${userRole === "patient" ? "appointments and healthcare" : "your practice and patients"}...`}
                disabled={isLoading}
                className="flex-1"
              />
              <Button onClick={handleSendMessage} disabled={!inputValue.trim() || isLoading} size="icon">
                {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
