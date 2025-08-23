/**
 * Tool Client for MedAI System
 * Provides tool discovery and execution via OpenAPI schema
 */

export interface ToolParameter {
  name: string
  type: string
  description: string
  required: boolean
  enum?: string[]
  default?: any
}

export interface ToolDefinition {
  name: string
  description: string
  type: string
  parameters: ToolParameter[]
  returns: Record<string, any>
  examples: Record<string, any>[]
  tags: string[]
}

export interface ToolExecutionRequest {
  tool_name: string
  parameters: Record<string, any>
}

export interface ToolExecutionResponse {
  tool_name: string
  parameters: Record<string, any>
  result: any
  executed_at: string
}

export interface ToolListResponse {
  tools: ToolDefinition[]
  count: number
  filters: {
    type?: string
    tag?: string
  }
}

export class ToolClient {
  private baseUrl: string
  private openApiSchema: any = null

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl
  }

  /**
   * Discover all available tools via OpenAPI schema
   */
  async discoverTools(): Promise<ToolDefinition[]> {
    try {
      if (!this.openApiSchema) {
        const response = await fetch(`${this.baseUrl}/tools/openapi`)
        if (!response.ok) {
          throw new Error(`Failed to fetch OpenAPI schema: ${response.statusText}`)
        }
        this.openApiSchema = await response.json()
      }

      // Extract tool definitions from OpenAPI schema
      const tools: ToolDefinition[] = []
      
      if (this.openApiSchema.paths) {
        for (const [path, pathItem] of Object.entries(this.openApiSchema.paths)) {
          if (path.startsWith('/tools/') && path !== '/tools/openapi') {
            // This is a tool endpoint
            const toolName = path.split('/').pop()
            if (toolName && pathItem.post) {
              const postItem = (pathItem as any).post
              const toolDef: ToolDefinition = {
                name: toolName,
                description: postItem.summary || postItem.description || `Tool: ${toolName}`,
                type: 'tool',
                parameters: [],
                returns: {},
                examples: [],
                tags: postItem.tags || []
              }

              // Extract parameters from request body schema
              if (postItem.requestBody?.content?.['application/json']?.schema) {
                const schema = postItem.requestBody.content['application/json'].schema
                if (schema.properties) {
                  for (const [paramName, paramSchema] of Object.entries(schema.properties)) {
                    const param = paramSchema as any
                    toolDef.parameters.push({
                      name: paramName,
                      type: param.type || 'string',
                      description: param.description || `Parameter: ${paramName}`,
                      required: schema.required?.includes(paramName) || false,
                      enum: param.enum,
                      default: param.default
                    })
                  }
                }
              }

              tools.push(toolDef)
            }
          }
        }
      }

      return tools
    } catch (error) {
      console.error('Error discovering tools:', error)
      return []
    }
  }

  /**
   * List tools with optional filtering
   */
  async listTools(typeFilter?: string, tagFilter?: string): Promise<ToolListResponse> {
    try {
      const params = new URLSearchParams()
      if (typeFilter) params.append('type_filter', typeFilter)
      if (tagFilter) params.append('tag_filter', tagFilter)

      const response = await fetch(`${this.baseUrl}/tools?${params}`)
      if (!response.ok) {
        throw new Error(`Failed to list tools: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error listing tools:', error)
      throw error
    }
  }

  /**
   * Execute a specific tool
   */
  async executeTool(toolName: string, parameters: Record<string, any>): Promise<ToolExecutionResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/tools/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tool_name: toolName,
          parameters
        })
      })

      if (!response.ok) {
        throw new Error(`Failed to execute tool: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`Error executing tool ${toolName}:`, error)
      throw error
    }
  }

  /**
   * Get tool definition by name
   */
  async getToolDefinition(toolName: string): Promise<ToolDefinition | null> {
    try {
      const tools = await this.listTools()
      return tools.tools.find(tool => tool.name === toolName) || null
    } catch (error) {
      console.error(`Error getting tool definition for ${toolName}:`, error)
      return null
    }
  }

  /**
   * Check if a tool exists and is available
   */
  async isToolAvailable(toolName: string): Promise<boolean> {
    try {
      const tool = await this.getToolDefinition(toolName)
      return tool !== null
    } catch (error) {
      return false
    }
  }

  /**
   * Get available tool types
   */
  async getToolTypes(): Promise<string[]> {
    try {
      const tools = await this.listTools()
      const types = new Set<string>()
      tools.tools.forEach(tool => {
        if (tool.type) types.add(tool.type)
      })
      return Array.from(types)
    } catch (error) {
      console.error('Error getting tool types:', error)
      return []
    }
  }

  /**
   * Get available tool tags
   */
  async getToolTags(): Promise<string[]> {
    try {
      const tools = await this.listTools()
      const tags = new Set<string>()
      tools.tools.forEach(tool => {
        tool.tags.forEach(tag => tags.add(tag))
      })
      return Array.from(tags)
    } catch (error) {
      console.error('Error getting tool tags:', error)
      return []
    }
  }

  /**
   * Health check for the tool service
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`)
      return response.ok
    } catch (error) {
      return false
    }
  }
}

// Export singleton instance
export const toolClient = new ToolClient()

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
    return toolClient.executeTool('schedule_appointment', params)
  },

  checkDoctorAvailability: async (params: {
    doctor_name: string
    date: string
    time_preference?: string
  }) => {
    return toolClient.executeTool('check_doctor_availability', params)
  },

  listDoctors: async (params: {
    specialty?: string
    available_date?: string
    location?: string
  } = {}) => {
    return toolClient.executeTool('list_doctors', params)
  }
}

export const calendarTools = {
  createCalendarEvent: async (params: {
    summary: string
    start_time: string
    end_time: string
    description?: string
    attendees?: string[]
    location?: string
  }) => {
    return toolClient.executeTool('create_calendar_event', params)
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
    return toolClient.executeTool('send_appointment_confirmation', params)
  }
}

export const analyticsTools = {
  getAppointmentStatistics: async (params: {
    doctor_name: string
    period: string
    start_date?: string
    end_date?: string
  }) => {
    return toolClient.executeTool('get_appointment_statistics', params)
  }
}

export const searchTools = {
  searchPatientsBySymptoms: async (params: {
    symptoms: string
    date_from?: string
    date_to?: string
    doctor_name?: string
  }) => {
    return toolClient.executeTool('search_patients_by_symptoms', params)
  }
}