/**
 * MCP (Model Context Protocol) Client Implementation
 * Provides tool discovery and execution following MCP standard
 */

export interface MCPTool {
  name: string
  description: string
  inputSchema: {
    type: string
    properties: Record<string, any>
    required: string[]
  }
}

export interface MCPToolCall {
  name: string
  arguments: Record<string, any>
}

export interface MCPToolResult {
  content: Array<{
    type: string
    text: string
  }>
  isError: boolean
}

export interface MCPRequest {
  jsonrpc: string
  id: string
  method: string
  params?: Record<string, any>
}

export interface MCPResponse {
  jsonrpc: string
  id: string
  result?: any
  error?: {
    code: number
    message: string
  }
}

export class MCPClient {
  private baseUrl: string
  private sessionId: string | null = null
  private requestId: number = 0

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl
  }

  setSessionId(sessionId: string) {
    this.sessionId = sessionId
  }

  private generateId(): string {
    return `req_${++this.requestId}_${Date.now()}`
  }

  /**
   * Discover available tools via MCP protocol
   */
  async discoverTools(): Promise<{ tools: MCPTool[] }> {
    try {
      const response = await fetch(`${this.baseUrl}/mcp/tools`)
      if (!response.ok) {
        throw new Error(`Failed to discover tools: ${response.statusText}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error discovering MCP tools:', error)
      throw error
    }
  }

  /**
   * Get specific tool information
   */
  async getTool(toolName: string): Promise<MCPTool | null> {
    try {
      const request: MCPRequest = {
        jsonrpc: "2.0",
        id: this.generateId(),
        method: "tools/get",
        params: { name: toolName }
      }

      const response = await fetch(`${this.baseUrl}/mcp/ws`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
      })

      if (!response.ok) {
        throw new Error(`Failed to get tool: ${response.statusText}`)
      }

      const data = await response.json()
      if (data.error) {
        throw new Error(data.error.message)
      }

      return data.result
    } catch (error) {
      console.error(`Error getting tool ${toolName}:`, error)
      return null
    }
  }

  /**
   * Execute a tool via MCP protocol
   */
  async executeTool(toolName: string, args: Record<string, any>): Promise<MCPToolResult> {
    try {
      const request: MCPRequest = {
        jsonrpc: "2.0",
        id: this.generateId(),
        method: "tools/call",
        params: {
          name: toolName,
          arguments: args
        }
      }

      const response = await fetch(`${this.baseUrl}/mcp/tools/call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: toolName,
          arguments: args
        })
      })

      if (!response.ok) {
        throw new Error(`Failed to execute tool: ${response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error(`Error executing tool ${toolName}:`, error)
      return {
        content: [{
          type: "text",
          text: `Error executing tool: ${error instanceof Error ? error.message : String(error)}`
        }],
        isError: true
      }
    }
  }

  /**
   * Execute tool via WebSocket for real-time communication
   */
  async executeToolWebSocket(toolName: string, args: Record<string, any>): Promise<MCPToolResult> {
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(`ws://${this.baseUrl.replace('http://', '')}/mcp/ws`)
      
      ws.onopen = () => {
        const request: MCPRequest = {
          jsonrpc: "2.0",
          id: this.generateId(),
          method: "tools/call",
          params: {
            name: toolName,
            arguments: args
          }
        }
        ws.send(JSON.stringify(request))
      }

      ws.onmessage = (event) => {
        try {
          const response: MCPResponse = JSON.parse(event.data)
          ws.close()
          
          if (response.error) {
            reject(new Error(response.error.message))
          } else {
            resolve(response.result)
          }
        } catch (error) {
          ws.close()
          reject(error)
        }
      }

      ws.onerror = (error) => {
        ws.close()
        reject(error)
      }

      // Timeout after 10 seconds
      setTimeout(() => {
        ws.close()
        reject(new Error('WebSocket timeout'))
      }, 10000)
    })
  }

  /**
   * Check server health and MCP capabilities
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/mcp`)
      return response.ok
    } catch (error) {
      return false
    }
  }

  /**
   * Get server capabilities
   */
  async getCapabilities(): Promise<Record<string, boolean>> {
    try {
      const response = await fetch(`${this.baseUrl}/mcp`)
      if (!response.ok) {
        throw new Error('Server not responding')
      }
      const data = await response.json()
      return data.capabilities || {}
    } catch (error) {
      console.error('Error getting capabilities:', error)
      return {}
    }
  }
}

// Export singleton instance
export const mcpClient = new MCPClient()

// Export specific tool execution functions for common operations
export const appointmentTools = {
  scheduleAppointment: async (params: {
    doctor_name: string
    patient_name: string
    patient_email: string
    appointment_date: string
    appointment_time: string
    symptoms?: string
    duration?: number
  }) => {
    return mcpClient.executeTool('schedule_appointment', params)
  },

  checkDoctorAvailability: async (params: {
    doctor_name: string
    date: string
    time_preference?: string
  }) => {
    return mcpClient.executeTool('check_doctor_availability', params)
  },

  listDoctors: async (params: {
    specialty?: string
    location?: string
  } = {}) => {
    return mcpClient.executeTool('list_doctors', params)
  }
}

export const calendarTools = {
  createCalendarEvent: async (params: {
    summary: string
    start_time: string
    end_time: string
    description?: string
    attendees?: string[]
  }) => {
    return mcpClient.executeTool('create_calendar_event', params)
  },

  updateCalendarEvent: async (eventId: string, updates: Record<string, any>) => {
    return mcpClient.executeTool('update_calendar_event', { event_id: eventId, ...updates })
  },

  cancelCalendarEvent: async (eventId: string, reason?: string) => {
    return mcpClient.executeTool('cancel_calendar_event', { event_id: eventId, reason })
  }
}

export const emailTools = {
  sendAppointmentConfirmation: async (params: {
    to_email: string
    patient_name: string
    doctor_name: string
    appointment_date: string
    appointment_time: string
    appointment_id: string
  }) => {
    return mcpClient.executeTool('send_appointment_confirmation', params)
  },

  sendAppointmentReminder: async (params: {
    to_email: string
    patient_name: string
    doctor_name: string
    appointment_date: string
    appointment_time: string
  }) => {
    return mcpClient.executeTool('send_appointment_reminder', params)
  },

  sendCancellationNotification: async (params: {
    to_email: string
    patient_name: string
    doctor_name: string
    appointment_date: string
    appointment_time: string
    reason?: string
  }) => {
    return mcpClient.executeTool('send_cancellation_notification', params)
  }
}

export const analyticsTools = {
  getAppointmentStatistics: async (params: {
    doctor_name: string
    period: string
    start_date?: string
    end_date?: string
  }) => {
    return mcpClient.executeTool('get_appointment_statistics', params)
  }
}

export const searchTools = {
  searchPatientsBySymptoms: async (params: {
    symptoms: string
    date_from?: string
    date_to?: string
    doctor_name?: string
  }) => {
    return mcpClient.executeTool('search_patients_by_symptoms', params)
  }
}

// Export doctor tools alias for backward compatibility
export const doctorTools = appointmentTools