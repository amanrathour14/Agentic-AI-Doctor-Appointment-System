# MedAI MCP (Model Context Protocol) Implementation

This document describes the complete MCP implementation for the MedAI doctor appointment system, including FastApiMCP integration, real Gmail and Google Calendar API integrations, and tool discovery following MCP standards.

## 🏗️ MCP Architecture Overview

The system implements a complete MCP (Model Context Protocol) architecture with the following components:

### 1. **MCP Server** (`backend/mcp_server.py`)
- **FastAPI-based MCP server** following MCP standards
- **Tool registry** with automatic schema generation
- **Real service integration** with Gmail and Google Calendar APIs
- **WebSocket support** for real-time communication
- **JSON-RPC 2.0** compliant request/response handling

### 2. **MCP Client** (`lib/mcp-client.ts`)
- **TypeScript MCP client** for frontend integration
- **Tool discovery** via MCP protocol
- **Tool execution** with proper error handling
- **WebSocket support** for real-time tool calls

### 3. **Tool Registry** (`backend/tool_registry.py`)
- **OpenAPI-compliant** tool definitions
- **Automatic schema generation** for MCP discovery
- **Tool categorization** by type and tags
- **Parameter validation** and documentation

## 🚀 MCP Endpoints

### Core MCP Endpoints
```
GET  /mcp                    - Server information and capabilities
GET  /mcp/tools             - List all available tools
POST /mcp/tools/call        - Execute a specific tool
WS   /mcp/ws                - WebSocket endpoint for real-time communication
```

### MCP Server Information
```bash
curl http://localhost:8000/mcp
```
Response:
```json
{
  "name": "MedAI MCP Server",
  "version": "1.0.0",
  "description": "MCP server for MedAI doctor appointment system",
  "capabilities": {
    "tools": true,
    "resources": false,
    "prompts": false
  }
}
```

### Tool Discovery
```bash
curl http://localhost:8000/mcp/tools
```
Response includes all available tools with their schemas, parameters, and descriptions.

### Tool Execution
```bash
curl -X POST http://localhost:8000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "list_doctors",
    "arguments": {}
  }'
```

## 🔧 Available MCP Tools

### Appointment Management Tools
1. **`schedule_appointment`**
   - **Description**: Schedule a new appointment with real calendar and email integration
   - **Parameters**: `doctor_name`, `patient_name`, `patient_email`, `appointment_date`, `appointment_time`, `symptoms`, `duration`
   - **Real Integration**: Creates Google Calendar events and sends Gmail confirmation emails

2. **`check_doctor_availability`**
   - **Description**: Check real-time doctor availability using Google Calendar
   - **Parameters**: `doctor_name`, `date`, `time_preference`
   - **Real Integration**: Queries actual Google Calendar data for availability

3. **`list_doctors`**
   - **Description**: List available doctors with filtering options
   - **Parameters**: `specialty`, `location`
   - **Real Integration**: Integrates with calendar availability checking

### Calendar Integration Tools
4. **`create_calendar_event`**
   - **Description**: Create Google Calendar events
   - **Parameters**: `summary`, `start_time`, `end_time`, `description`, `attendees`, `location`
   - **Real Integration**: Creates actual Google Calendar events via API

5. **`update_calendar_event`**
   - **Description**: Update existing calendar events
   - **Parameters**: `event_id`, `updates`
   - **Real Integration**: Modifies actual Google Calendar events

6. **`cancel_calendar_event`**
   - **Description**: Cancel calendar events
   - **Parameters**: `event_id`, `reason`
   - **Real Integration**: Cancels actual Google Calendar events

### Email Integration Tools
7. **`send_appointment_confirmation`**
   - **Description**: Send appointment confirmation emails via Gmail API
   - **Parameters**: `to_email`, `patient_name`, `doctor_name`, `appointment_date`, `appointment_time`, `appointment_id`
   - **Real Integration**: Sends actual emails via Gmail API with OAuth2

8. **`send_appointment_reminder`**
   - **Description**: Send appointment reminder emails
   - **Parameters**: `to_email`, `patient_name`, `doctor_name`, `appointment_date`, `appointment_time`
   - **Real Integration**: Sends actual reminder emails via Gmail API

9. **`send_cancellation_notification`**
   - **Description**: Send cancellation notification emails
   - **Parameters**: `to_email`, `patient_name`, `doctor_name`, `appointment_date`, `appointment_time`, `reason`
   - **Real Integration**: Sends actual cancellation emails via Gmail API

### Analytics and Search Tools
10. **`get_appointment_statistics`**
    - **Description**: Generate appointment statistics and reports
    - **Parameters**: `doctor_name`, `period`, `start_date`, `end_date`
    - **Real Integration**: Analyzes actual Google Calendar data

11. **`search_patients_by_symptoms`**
    - **Description**: Search patients by symptoms for medical research
    - **Parameters**: `symptoms`, `date_from`, `date_to`, `doctor_name`
    - **Real Integration**: Searches actual calendar event descriptions

## 🔐 Real Service Integration

### Gmail API Integration
- **OAuth2 Authentication**: Uses `credentials.json` for secure API access
- **Real Email Sending**: Actually sends emails via Gmail API
- **HTML Email Support**: Rich formatting for appointment confirmations
- **Error Handling**: Comprehensive error handling and logging

### Google Calendar API Integration
- **OAuth2 Authentication**: Secure calendar access
- **Real Event Creation**: Creates actual calendar events
- **Event Management**: Full CRUD operations on calendar events
- **Availability Checking**: Real-time availability based on calendar data

## 🚀 Getting Started

### 1. Start the MCP Server
```bash
# Make script executable
chmod +x start-mcp-server.sh

# Start MCP server
./start-mcp-server.sh
```

### 2. Start the Frontend
```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev
```

### 3. Test MCP Endpoints
```bash
# Check server status
curl http://localhost:8000/mcp

# Discover tools
curl http://localhost:8000/mcp/tools

# Execute a tool
curl -X POST http://localhost:8000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "list_doctors", "arguments": {}}'
```

## 🔧 Configuration

### Google API Setup
1. Create a Google Cloud Project
2. Enable Gmail API and Google Calendar API
3. Create OAuth 2.0 credentials
4. Download `credentials.json` and place in `backend/` directory
5. First run will create `token.json` files for each service

### Environment Variables
```bash
# Backend configuration
GOOGLE_APPLICATION_CREDENTIALS=credentials.json
MCP_SERVER_PORT=8000
MCP_SERVER_HOST=0.0.0.0
```

## 📡 MCP Protocol Implementation

### JSON-RPC 2.0 Compliance
- **Request Format**: Follows JSON-RPC 2.0 specification
- **Response Format**: Proper error handling with error codes
- **Method Support**: `tools/list`, `tools/call`, `tools/get`

### WebSocket Support
- **Real-time Communication**: WebSocket endpoint for live tool execution
- **Connection Management**: Automatic connection cleanup
- **Error Handling**: Comprehensive error handling and logging

### Tool Schema Generation
- **OpenAPI Compliance**: Automatic OpenAPI schema generation
- **Parameter Validation**: Built-in parameter validation
- **Type Safety**: Full TypeScript support for frontend

## 🧪 Testing

### Backend Testing
```bash
# Test MCP server import
python -c "import mcp_server; print('Success')"

# Test tool execution
curl -X POST http://localhost:8000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "list_doctors", "arguments": {}}'
```

### Frontend Testing
```bash
# Test MCP client
curl http://localhost:3000

# Check browser console for MCP connection status
```

## 🔍 Troubleshooting

### Common Issues
1. **Google API Errors**: Check `credentials.json` and `token.json` files
2. **MCP Connection Failed**: Verify backend is running on port 8000
3. **Tool Execution Errors**: Check tool parameters and backend logs
4. **Frontend Build Errors**: Clear node_modules and reinstall dependencies

### Debug Mode
```bash
# Enable debug logging
export PYTHONPATH=.
python -c "import logging; logging.basicConfig(level=logging.DEBUG); import mcp_server"
```

## 📚 API Documentation

### MCP Tool Schemas
Each tool automatically generates its OpenAPI schema:
- **Parameter Types**: String, integer, boolean, array
- **Required Fields**: Clearly marked required parameters
- **Default Values**: Default parameter values where applicable
- **Description**: Comprehensive tool and parameter descriptions

### Error Handling
- **HTTP Status Codes**: Proper HTTP status codes for different error types
- **Error Messages**: Descriptive error messages for debugging
- **Validation Errors**: Parameter validation with clear error messages

## 🔄 Development

### Adding New Tools
1. **Define Tool**: Add tool definition in `tool_registry.py`
2. **Implement Handler**: Create handler function in `mcp_server.py`
3. **Register Tool**: Add tool to `_register_tools()` method
4. **Test Integration**: Test tool discovery and execution

### Modifying Existing Tools
- **Update Definition**: Modify tool definition in registry
- **Update Handler**: Modify handler implementation
- **Update Schema**: Schema automatically updates from definition

## 🚀 Production Deployment

### Backend Deployment
- **Gunicorn**: Production WSGI server
- **Environment Variables**: Secure configuration management
- **SSL/TLS**: HTTPS support for secure communication
- **Load Balancing**: Multiple MCP server instances

### Frontend Deployment
- **Next.js Build**: Production build optimization
- **CDN**: Static asset delivery
- **Environment Configuration**: Production API endpoints

## 📝 License

This MCP implementation is part of the MedAI system and follows the same license terms.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement MCP tool or enhancement
4. Test thoroughly with real services
5. Submit pull request with documentation

---

This MCP implementation provides a complete, production-ready solution for AI agent tool discovery and execution, with real integrations to Gmail and Google Calendar APIs, following MCP standards and best practices.