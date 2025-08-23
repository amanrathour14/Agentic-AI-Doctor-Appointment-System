# MedAI Doctor Appointment System

A modern, AI-powered doctor appointment scheduling system with real Gmail and Google Calendar integration, built using Next.js, FastAPI, and OpenAPI-based tool discovery.

## 🚀 Features

### Core Functionality
- **AI-powered chat interface** for natural language appointment scheduling
- **Real Gmail API integration** for sending appointment confirmations, reminders, and cancellations
- **Real Google Calendar API integration** for creating, updating, and managing calendar events
- **OpenAPI-based tool discovery** for AI agents to discover and execute available tools
- **Session management** for maintaining conversation context
- **Role-based access** (patient/doctor) with different capabilities

### Tool System
- **Appointment Management**: Schedule, check availability, list doctors
- **Calendar Integration**: Create, update, cancel calendar events
- **Email Services**: Send confirmation emails, reminders, notifications
- **Analytics**: Appointment statistics and reporting
- **Search**: Patient search by symptoms and other criteria

## 🏗️ Architecture

### Frontend (Next.js)
- **React 19** with TypeScript
- **Modern UI** with Tailwind CSS
- **Tool discovery** via OpenAPI schema
- **Real-time chat** interface with tool execution

### Backend (FastAPI)
- **Python 3.8+** with FastAPI framework
- **OpenAPI schema** generation for tool discovery
- **Tool registry** system for managing available tools
- **Real service integration** with Gmail and Google Calendar APIs

### Tool Discovery System
- **No MCP endpoints** - uses standard OpenAPI schema
- **Tool registry** with automatic schema generation
- **Handler system** for executing tool logic
- **Real service integration** for actual functionality

## 🛠️ Installation

### Prerequisites
- Node.js 18+ and pnpm
- Python 3.8+
- Google API credentials (for Gmail and Calendar integration)

### Frontend Setup
```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev
```

### Backend Setup
```bash
# Make startup script executable
chmod +x start-backend.sh

# Start backend (creates venv and installs dependencies)
./start-backend.sh
```

### Google API Setup
1. Create a Google Cloud Project
2. Enable Gmail API and Google Calendar API
3. Create OAuth 2.0 credentials
4. Download `credentials.json` and place in `backend/` directory
5. First run will create `token.json` files for each service

## 📡 API Endpoints

### Tool Discovery
- `GET /tools/openapi` - OpenAPI schema for all tools
- `GET /tools` - List available tools with filtering
- `POST /tools/execute` - Execute a specific tool

### Chat & Sessions
- `POST /api/chat` - Main chat endpoint with tool integration
- `POST /api/sessions` - Create new chat session
- `GET /api/sessions/{session_id}` - Get session information

### Appointments
- `POST /api/appointments` - Schedule new appointment
- `GET /api/doctors/availability` - Check doctor availability
- `GET /api/doctors` - List available doctors

### Analytics & Search
- `GET /api/analytics/appointments` - Get appointment statistics
- `GET /api/search/patients` - Search patients by symptoms

## 🔧 Available Tools

### Appointment Tools
- `schedule_appointment` - Schedule new appointment with calendar and email integration
- `check_doctor_availability` - Check real-time doctor availability
- `list_doctors` - List doctors with filtering options

### Calendar Tools
- `create_calendar_event` - Create Google Calendar events
- `update_appointment_event` - Update existing calendar events
- `cancel_appointment_event` - Cancel calendar events

### Email Tools
- `send_appointment_confirmation` - Send confirmation emails via Gmail
- `send_appointment_reminder` - Send reminder emails
- `send_cancellation_notification` - Send cancellation notices

### Analytics Tools
- `get_appointment_statistics` - Generate appointment reports
- `search_patients_by_symptoms` - Search patient database

## 💬 Usage Examples

### Scheduling an Appointment
```
User: "I'd like to schedule an appointment with Dr. Smith for tomorrow at 2 PM"
Assistant: "I'll schedule that appointment for you. Let me check availability and create the calendar event..."
```

### Checking Doctor Availability
```
User: "Is Dr. Johnson available next Tuesday?"
Assistant: "Let me check Dr. Johnson's availability for next Tuesday..."
```

### Tool Discovery
The system automatically discovers available tools via the OpenAPI schema at `/tools/openapi`, allowing AI agents to understand what capabilities are available.

## 🔒 Security & Authentication

- **OAuth 2.0** for Google API integration
- **Session-based** authentication for chat
- **Role-based** access control
- **Secure token storage** for API credentials

## 🧪 Testing

### Backend Health Check
```bash
curl http://localhost:8000/health
```

### Tool Discovery
```bash
curl http://localhost:8000/tools/openapi
```

### Tool Execution
```bash
curl -X POST http://localhost:8000/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "list_doctors", "parameters": {}}'
```

## 🚨 Troubleshooting

### Common Issues
1. **Google API errors**: Check credentials.json and token.json files
2. **Tool discovery fails**: Verify backend is running and accessible
3. **Frontend build errors**: Clear node_modules and reinstall dependencies

### Logs
- Backend logs are displayed in the terminal
- Frontend errors appear in browser console
- Tool execution results are logged for debugging

## 🔄 Development

### Adding New Tools
1. Define tool in `backend/tool_registry.py`
2. Implement handler in `backend/tool_handlers.py`
3. Register handler in `ToolHandlers._register_handlers()`
4. Tool automatically appears in OpenAPI schema

### Modifying Existing Tools
- Update tool definition in registry
- Modify handler implementation
- Update frontend tool client if needed

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support and questions, please open an issue in the repository.
