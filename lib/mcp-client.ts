/**
 * MCP (Model Context Protocol) Client for Frontend
 * Provides tool discovery and execution capabilities
 */

export interface MCPTool {
  name: string;
  description: string;
  inputSchema: any;
  type: string;
}

export interface MCPToolCall {
  tool_name: string;
  parameters: Record<string, any>;
}

export interface MCPToolExecutionRequest {
  tool_calls: MCPToolCall[];
  session_id?: string;
}

export interface MCPToolExecutionResponse {
  results: Array<{
    tool_name: string;
    success: boolean;
    result?: any;
    error?: string;
    execution_time: string;
  }>;
  session_id?: string;
  errors: string[];
}

export interface MCPToolSchema {
  name: string;
  description: string;
  inputSchema: any;
  type: string;
  examples: Array<{
    description: string;
    parameters: Record<string, any>;
  }>;
}

export class MCPClient {
  private baseUrl: string;
  private sessionId: string | null = null;

  constructor(baseUrl: string = 'http://localhost:8001') {
    this.baseUrl = baseUrl;
  }

  /**
   * Discover all available MCP tools
   */
  async discoverTools(includeSchemas: boolean = false): Promise<{
    tools: MCPTool[];
    count: number;
    server_info: any;
  }> {
    const response = await fetch(
      `${this.baseUrl}/mcp/tools?include_schemas=${includeSchemas}`
    );
    
    if (!response.ok) {
      throw new Error(`Tool discovery failed: ${response.statusText}`);
    }
    
    return response.json();
  }

  /**
   * Get detailed schema for a specific tool
   */
  async getToolSchema(toolName: string): Promise<MCPToolSchema> {
    const response = await fetch(`${this.baseUrl}/mcp/tools/${toolName}/schema`);
    
    if (!response.ok) {
      throw new Error(`Failed to get tool schema: ${response.statusText}`);
    }
    
    return response.json();
  }

  /**
   * Execute multiple MCP tools
   */
  async executeTools(
    toolCalls: MCPToolCall[],
    sessionId?: string
  ): Promise<MCPToolExecutionResponse> {
    const request: MCPToolExecutionRequest = {
      tool_calls: toolCalls,
      session_id: sessionId || this.sessionId || undefined,
    };

    const response = await fetch(`${this.baseUrl}/mcp/tools/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Tool execution failed: ${response.statusText}`);
    }

    const result = await response.json();
    
    // Update session ID if provided
    if (result.session_id) {
      this.sessionId = result.session_id;
    }
    
    return result;
  }

  /**
   * Execute a single MCP tool
   */
  async executeTool(
    toolName: string,
    parameters: Record<string, any>,
    sessionId?: string
  ): Promise<any> {
    const result = await this.executeTools(
      [{ tool_name: toolName, parameters }],
      sessionId
    );
    
    if (result.errors.length > 0) {
      throw new Error(`Tool execution errors: ${result.errors.join(', ')}`);
    }
    
    const toolResult = result.results[0];
    if (!toolResult.success) {
      throw new Error(`Tool execution failed: ${toolResult.error}`);
    }
    
    return toolResult.result;
  }

  /**
   * Get server information and capabilities
   */
  async getServerInfo(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/mcp/info`);
    
    if (!response.ok) {
      throw new Error(`Failed to get server info: ${response.statusText}`);
    }
    
    return response.json();
  }

  /**
   * Check server health
   */
  async healthCheck(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/health`);
    
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }
    
    return response.json();
  }

  /**
   * Create a WebSocket connection for real-time MCP communication
   */
  createWebSocketConnection(): WebSocket {
    const ws = new WebSocket(`ws://localhost:8001/mcp/ws`);
    
    ws.onopen = () => {
      console.log('MCP WebSocket connection established');
    };
    
    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        console.log('MCP WebSocket message received:', message);
        // Handle incoming messages as needed
      } catch (error) {
        console.error('Error parsing MCP WebSocket message:', error);
      }
    };
    
    ws.onerror = (error) => {
      console.error('MCP WebSocket error:', error);
    };
    
    ws.onclose = () => {
      console.log('MCP WebSocket connection closed');
    };
    
    return ws;
  }

  /**
   * Set session ID for conversation context
   */
  setSessionId(sessionId: string): void {
    this.sessionId = sessionId;
  }

  /**
   * Get current session ID
   */
  getSessionId(): string | null {
    return this.sessionId;
  }

  /**
   * Clear session ID
   */
  clearSession(): void {
    this.sessionId = null;
  }
}

// Convenience functions for common MCP operations
export class MCPAppointmentTools {
  private client: MCPClient;

  constructor(client: MCPClient) {
    this.client = client;
  }

  /**
   * Schedule a new appointment
   */
  async scheduleAppointment(appointmentData: {
    doctor_name: string;
    patient_name: string;
    patient_email: string;
    appointment_date: string;
    appointment_time: string;
    symptoms?: string;
  }): Promise<any> {
    return this.client.executeTool('appointments/schedule_enhanced', appointmentData);
  }

  /**
   * Check doctor availability
   */
  async checkAvailability(
    doctorName: string,
    date: string,
    timePreference?: string
  ): Promise<any> {
    const parameters: Record<string, any> = {
      doctor_name: doctorName,
      date: date,
    };
    
    if (timePreference) {
      parameters.time_preference = timePreference;
    }
    
    return this.client.executeTool('appointments/check_availability', parameters);
  }

  /**
   * List appointments for a doctor or patient
   */
  async listAppointments(
    entityType: 'doctor' | 'patient',
    entityName: string,
    dateFrom?: string,
    dateTo?: string
  ): Promise<any> {
    const parameters: Record<string, any> = {
      entity_type: entityType,
      entity_name: entityName,
    };
    
    if (dateFrom) parameters.date_from = dateFrom;
    if (dateTo) parameters.date_to = dateTo;
    
    return this.client.executeTool('appointments/list', parameters);
  }
}

export class MCPDoctorTools {
  private client: MCPClient;

  constructor(client: MCPClient) {
    this.client = client;
  }

  /**
   * List available doctors
   */
  async listDoctors(specialty?: string, availableDate?: string): Promise<any> {
    const parameters: Record<string, any> = {};
    
    if (specialty) parameters.specialty = specialty;
    if (availableDate) parameters.available_date = availableDate;
    
    return this.client.executeTool('doctors/list', parameters);
  }

  /**
   * Get doctor's schedule
   */
  async getDoctorSchedule(doctorName: string, date: string): Promise<any> {
    return this.client.executeTool('doctors/get_schedule', {
      doctor_name: doctorName,
      date: date,
    });
  }

  /**
   * Get appointment statistics
   */
  async getAppointmentStats(
    doctorName: string,
    period: 'day' | 'week' | 'month' | 'year',
    date?: string
  ): Promise<any> {
    const parameters: Record<string, any> = {
      doctor_name: doctorName,
      period: period,
    };
    
    if (date) parameters.date = date;
    
    return this.client.executeTool('analytics/appointment_stats', parameters);
  }
}

export class MCPSearchTools {
  private client: MCPClient;

  constructor(client: MCPClient) {
    this.client = client;
  }

  /**
   * Search patients by symptoms
   */
  async searchPatientsBySymptoms(
    symptoms: string,
    dateFrom?: string,
    dateTo?: string
  ): Promise<any> {
    const parameters: Record<string, any> = {
      symptoms: symptoms,
    };
    
    if (dateFrom) parameters.date_from = dateFrom;
    if (dateTo) parameters.date_to = dateTo;
    
    return this.client.executeTool('search/patients_by_symptoms', parameters);
  }
}

// Create and export default instances
export const mcpClient = new MCPClient();
export const appointmentTools = new MCPAppointmentTools(mcpClient);
export const doctorTools = new MCPDoctorTools(mcpClient);
export const searchTools = new MCPSearchTools(mcpClient);