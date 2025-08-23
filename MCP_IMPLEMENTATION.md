# MedAI MCP (Model Context Protocol) Implementation

## Overview

This document describes the implementation of the Model Context Protocol (MCP) server for the MedAI doctor appointment system. The MCP server provides standardized tool discovery and execution capabilities, enabling AI agents to interact with the system's functionality in a consistent manner.

## Architecture

### MCP Server Components

1. **Core MCP Server** (`backend/mcp_server.py`)
   - Implements the MCP protocol standard
   - Manages tool registration and discovery
   - Handles WebSocket connections for real-time communication

2. **FastAPI MCP Server** (`backend/fastapi_mcp_server.py`)
   - RESTful API endpoints for MCP operations
   - Integrates with existing backend services
   - Provides enhanced tool execution with real service integration

3. **Frontend MCP Client** (`lib/mcp-client.ts`)
   - TypeScript client for frontend integration
   - Provides convenient tool execution methods
   - Handles session management and error handling

## MCP Tools Available

### Appointment Management
- `appointments/schedule` - Basic appointment scheduling
- `appointments/schedule_enhanced` - Full integration with calendar, email, and notifications
- `appointments/check_availability` - Check doctor availability
- `appointments/list` - List appointments for doctors or patients

### Doctor Management
- `doctors/list` - List available doctors with filtering
- `doctors/get_schedule` - Get doctor's schedule for specific dates

### Analytics
- `analytics/appointment_stats` - Get appointment statistics and reports

### Search
- `search/patients_by_symptoms` - Search patients by symptoms

### Tool Discovery
- `tools/list` - List all available tools
- `tools/get` - Get detailed schema for specific tools

## Getting Started

### 1. Start the MCP Server

```bash
# Make the script executable (first time only)
chmod +x start-mcp-server.sh

# Start the MCP server
./start-mcp-server.sh
```

The server will start on `http://localhost:8001`

### 2. Verify MCP Server Status

```bash
# Health check
curl http://localhost:8001/health

# Get server info
curl http://localhost:8001/mcp/info

# Discover tools
curl http://localhost:8001/mcp/tools
```

### 3. Frontend Integration

The frontend automatically integrates with the MCP server through the `mcp-client.ts` library. The chat interface will:

- Discover available tools on initialization
- Execute tools based on user input
- Display tool execution results
- Provide fallback to regular chat API when needed

## API Endpoints

### MCP Tool Discovery
- `GET /mcp/tools` - List all available tools
- `GET /mcp/tools/{tool_name}/schema` - Get tool schema and examples

### MCP Tool Execution
- `POST /mcp/tools/execute` - Execute multiple tools in batch
- `WebSocket /mcp/ws` - Real-time MCP communication

### Server Information
- `GET /mcp/info` - Server capabilities and tool statistics
- `GET /health` - Health check endpoint

## Tool Execution Examples

### Schedule an Appointment

```typescript
import { appointmentTools } from '@/lib/mcp-client'

const result = await appointmentTools.scheduleAppointment({
  doctor_name: "Dr. Smith",
  patient_name: "John Doe",
  patient_email: "john.doe@email.com",
  appointment_date: "2024-01-20",
  appointment_time: "09:00",
  symptoms: "Headache and fever"
})
```

### Check Doctor Availability

```typescript
import { appointmentTools } from '@/lib/mcp-client'

const result = await appointmentTools.checkAvailability(
  "Dr. Johnson",
  "2024-01-20",
  "morning"
)
```

### Get Appointment Statistics

```typescript
import { doctorTools } from '@/lib/mcp-client'

const result = await doctorTools.getAppointmentStats(
  "Dr. Williams",
  "month",
  "2024-01-01"
)
```

## WebSocket Communication

The MCP server supports WebSocket connections for real-time communication:

```typescript
const ws = mcpClient.createWebSocketConnection()

// Send MCP message
ws.send(JSON.stringify({
  jsonrpc: "2.0",
  id: "1",
  method: "tools/list",
  params: {}
}))
```

## Error Handling

The MCP client provides comprehensive error handling:

```typescript
try {
  const result = await mcpClient.executeTool("appointments/schedule", params)
  // Handle success
} catch (error) {
  if (error.message.includes("Tool not found")) {
    // Handle tool not found
  } else if (error.message.includes("Tool execution failed")) {
    // Handle execution failure
  }
}
```

## Integration with Existing Services

The MCP server integrates with existing backend services:

- **Google Calendar Service** - For appointment scheduling
- **Email Service** - For confirmation emails
- **Notification Service** - For real-time notifications
- **LLM Agent** - For AI-powered conversations

## Development and Testing

### Running Tests

```bash
cd backend
python -m pytest tests/
```

### Adding New Tools

1. Define the tool in `mcp_server.py`:
```python
async def new_tool_function(params: Dict[str, Any]) -> Dict[str, Any]:
    # Tool implementation
    return {"result": "success"}

mcp_server.register_tool(
    name="category/new_tool",
    description="Description of the new tool",
    inputSchema={"type": "object", "properties": {}},
    handler=new_tool_function
)
```

2. Add corresponding methods to the frontend client classes

### Tool Schema Validation

All tools use JSON Schema for input validation:

```python
inputSchema={
    "type": "object",
    "properties": {
        "required_field": {"type": "string", "description": "Required field description"}
    },
    "required": ["required_field"]
}
```

## Security Considerations

- CORS is configured for development (configure appropriately for production)
- Input validation through Pydantic models
- Session-based authentication (extend as needed)
- Rate limiting (implement as needed)

## Performance Optimization

- Async/await for I/O operations
- Batch tool execution support
- Connection pooling for database operations
- Caching for frequently accessed data

## Monitoring and Logging

The MCP server includes comprehensive logging:

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Tool executed successfully")
logger.error("Tool execution failed", exc_info=True)
logger.warning("Service integration unavailable")
```

## Troubleshooting

### Common Issues

1. **Port 8001 already in use**
   ```bash
   lsof -ti:8001 | xargs kill -9
   ```

2. **MCP client connection failed**
   - Check if MCP server is running
   - Verify CORS configuration
   - Check network connectivity

3. **Tool execution errors**
   - Verify tool parameters match schema
   - Check backend service availability
   - Review server logs

### Debug Mode

Enable debug logging:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- [ ] Authentication and authorization
- [ ] Rate limiting and quotas
- [ ] Tool execution metrics
- [ ] Advanced error handling
- [ ] Tool versioning
- [ ] Plugin system for custom tools
- [ ] Integration with external MCP clients

## References

- [MCP Specification](https://modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [WebSocket Protocol](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [JSON-RPC 2.0](https://www.jsonrpc.org/specification)