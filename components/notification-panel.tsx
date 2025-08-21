"use client"

import { useState, useEffect } from "react"
import { Bell, X, Clock, Calendar, User, AlertTriangle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"

interface Notification {
  id: string
  doctor_id: number
  type: string
  title: string
  message: string
  priority: "low" | "medium" | "high" | "urgent"
  data: any
  timestamp: string
  read: boolean
}

interface NotificationPanelProps {
  doctorId: number
  className?: string
}

export function NotificationPanel({ doctorId, className }: NotificationPanelProps) {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [unreadCount, setUnreadCount] = useState(0)
  const [ws, setWs] = useState<WebSocket | null>(null)

  // Connect to WebSocket for real-time notifications
  useEffect(() => {
    const connectWebSocket = () => {
      const websocket = new WebSocket(`ws://localhost:8000/ws/notifications/${doctorId}`)

      websocket.onopen = () => {
        console.log("[v0] Connected to notification WebSocket")
        setWs(websocket)
      }

      websocket.onmessage = (event) => {
        const notification: Notification = JSON.parse(event.data)
        console.log("[v0] Received notification:", notification)

        setNotifications((prev) => [notification, ...prev])
        setUnreadCount((prev) => prev + 1)

        // Show browser notification if permission granted
        if (Notification.permission === "granted") {
          new Notification(notification.title, {
            body: notification.message,
            icon: "/favicon.ico",
          })
        }
      }

      websocket.onclose = () => {
        console.log("[v0] WebSocket connection closed, attempting to reconnect...")
        setTimeout(connectWebSocket, 3000)
      }

      websocket.onerror = (error) => {
        console.error("[v0] WebSocket error:", error)
      }
    }

    connectWebSocket()

    // Request notification permission
    if (Notification.permission === "default") {
      Notification.requestPermission()
    }

    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [doctorId])

  // Load existing notifications
  useEffect(() => {
    const loadNotifications = async () => {
      try {
        const response = await fetch(`http://localhost:8000/notifications/${doctorId}`)
        const data = await response.json()

        if (data.notifications) {
          setNotifications(data.notifications)
          setUnreadCount(data.notifications.filter((n: Notification) => !n.read).length)
        }
      } catch (error) {
        console.error("[v0] Failed to load notifications:", error)
      }
    }

    loadNotifications()
  }, [doctorId])

  const markAsRead = async (notificationId: string) => {
    try {
      await fetch(`http://localhost:8000/notifications/${doctorId}/mark-read`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify([notificationId]),
      })

      setNotifications((prev) => prev.map((n) => (n.id === notificationId ? { ...n, read: true } : n)))
      setUnreadCount((prev) => Math.max(0, prev - 1))
    } catch (error) {
      console.error("[v0] Failed to mark notification as read:", error)
    }
  }

  const markAllAsRead = async () => {
    const unreadIds = notifications.filter((n) => !n.read).map((n) => n.id)
    if (unreadIds.length === 0) return

    try {
      await fetch(`http://localhost:8000/notifications/${doctorId}/mark-read`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(unreadIds),
      })

      setNotifications((prev) => prev.map((n) => ({ ...n, read: true })))
      setUnreadCount(0)
    } catch (error) {
      console.error("[v0] Failed to mark all notifications as read:", error)
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "urgent":
        return "bg-red-500"
      case "high":
        return "bg-orange-500"
      case "medium":
        return "bg-blue-500"
      case "low":
        return "bg-gray-500"
      default:
        return "bg-gray-500"
    }
  }

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case "new_appointment":
        return <Calendar className="h-4 w-4" />
      case "appointment_cancelled":
        return <X className="h-4 w-4" />
      case "appointment_reminder":
        return <Clock className="h-4 w-4" />
      case "patient_message":
        return <User className="h-4 w-4" />
      case "system_alert":
        return <AlertTriangle className="h-4 w-4" />
      default:
        return <Bell className="h-4 w-4" />
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)

    if (diffMins < 1) return "Just now"
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`
    return date.toLocaleDateString()
  }

  return (
    <div className={cn("relative", className)}>
      {/* Notification Bell Button */}
      <Button variant="outline" size="icon" onClick={() => setIsOpen(!isOpen)} className="relative">
        <Bell className="h-4 w-4" />
        {unreadCount > 0 && (
          <Badge
            variant="destructive"
            className="absolute -top-2 -right-2 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
          >
            {unreadCount > 99 ? "99+" : unreadCount}
          </Badge>
        )}
      </Button>

      {/* Notification Panel */}
      {isOpen && (
        <Card className="absolute right-0 top-12 w-96 max-h-96 shadow-lg z-50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Notifications</CardTitle>
            <div className="flex items-center gap-2">
              {unreadCount > 0 && (
                <Button variant="ghost" size="sm" onClick={markAllAsRead} className="text-xs">
                  Mark all read
                </Button>
              )}
              <Button variant="ghost" size="icon" onClick={() => setIsOpen(false)} className="h-6 w-6">
                <X className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <ScrollArea className="h-80">
              {notifications.length === 0 ? (
                <div className="p-4 text-center text-muted-foreground">No notifications yet</div>
              ) : (
                <div className="space-y-1">
                  {notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={cn(
                        "p-3 border-b cursor-pointer hover:bg-muted/50 transition-colors",
                        !notification.read && "bg-blue-50 border-l-4 border-l-blue-500",
                      )}
                      onClick={() => !notification.read && markAsRead(notification.id)}
                    >
                      <div className="flex items-start gap-3">
                        <div className={cn("p-1 rounded-full text-white", getPriorityColor(notification.priority))}>
                          {getNotificationIcon(notification.type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <p className="text-sm font-medium truncate">{notification.title}</p>
                            <span className="text-xs text-muted-foreground">
                              {formatTimestamp(notification.timestamp)}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground mt-1">{notification.message}</p>
                          {notification.data?.patient_name && (
                            <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                              <User className="h-3 w-3" />
                              <span>{notification.data.patient_name}</span>
                              {notification.data.appointment_date && (
                                <>
                                  <Calendar className="h-3 w-3 ml-2" />
                                  <span>
                                    {notification.data.appointment_date} {notification.data.appointment_time}
                                  </span>
                                </>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
