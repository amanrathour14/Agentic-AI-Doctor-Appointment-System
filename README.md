# MedAI - AI-Powered Doctor Appointment System

A comprehensive healthcare appointment management system with MCP (Model Context Protocol) integration, real Gmail API, and Google Calendar API support.

## 🏗️ Architecture

### MCP (Model Context Protocol) Implementation
- **FastAPI MCP Server**: Implements MCP standard with tool discovery and execution
- **Tool Registry**: OpenAPI-compliant tool definitions for AI agent discovery
- **Real Service Integration**: Gmail API (OAuth2) and Google Calendar API (OAuth2)
- **WebSocket Support**: Real-time communication for tool execution

### Frontend
- **Next.js 14**: React-based frontend with TypeScript
- **MCP Client**: TypeScript client for MCP server communication
- **Real-time Chat**: AI-powered appointment scheduling and management
- **Responsive UI**: Modern, accessible interface

### Backend Services
- **FastAPI**: High-performance Python web framework
- **Gmail Service**: Real email sending via Gmail API
- **Calendar Service**: Real calendar event management
- **Session Management**: User session handling
- **Tool Handlers**: MCP tool implementation

## 🚀 Getting Started

### Prerequisites
- Python 3.11+ (3.13 not recommended due to compatibility issues)
- Node.js 18+ and pnpm
- Google Cloud Platform account with APIs enabled
- PostgreSQL (optional, for production)

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd medai-appointment-system
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up Google API credentials
# Download credentials.json from Google Cloud Console
# Place in backend/ directory
```

### 3. Frontend Setup
```bash
cd ..
pnpm install
```

### 4. Environment Configuration
Create `.env.local` for development:
```bash
NEXT_PUBLIC_MCP_SERVER_URL=http://localhost:8000
NODE_ENV=development
```

### 5. Start Services
```bash
# Terminal 1: Start MCP Server
./start-mcp-server.sh

# Terminal 2: Start Frontend
pnpm dev
```

## 🌐 Deployment

### Vercel Frontend Deployment

1. **Set Environment Variables in Vercel Dashboard:**
   ```
   NEXT_PUBLIC_MCP_SERVER_URL=https://your-backend-domain.com
   ```

2. **Deploy:**
   ```bash
   vercel --prod
   ```

### Backend Deployment

1. **Deploy to your preferred platform** (Railway, Render, DigitalOcean, etc.)
2. **Set environment variables:**
   ```
   GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
   DATABASE_URL=your_database_url
   ```

3. **Update frontend environment variable** with your backend URL

## 🔧 MCP Endpoints

### HTTP Endpoints
- `GET /mcp` - Server information and capabilities
- `GET /mcp/tools` - List available tools
- `POST /mcp/tools/call` - Execute tool with parameters

### WebSocket Endpoint
- `WS /mcp/ws` - Real-time tool execution

## 🛠️ Available Tools

### Appointment Management
- `schedule_appointment` - Book new appointments
- `check_doctor_availability` - Check doctor schedules
- `list_doctors` - Get available doctors

### Calendar Integration
- `create_calendar_event` - Create Google Calendar events
- `update_calendar_event` - Modify existing events
- `cancel_calendar_event` - Cancel appointments

### Email Services
- `send_appointment_confirmation` - Send booking confirmations
- `send_appointment_reminder` - Send appointment reminders
- `send_cancellation_notification` - Send cancellation notices

### Analytics & Search
- `get_appointment_statistics` - Get appointment analytics
- `search_patients_by_symptoms` - Search patient records

## 🧪 Testing

### MCP Server Testing
```bash
# Check server status
curl http://localhost:8000/mcp

# List available tools
curl http://localhost:8000/mcp/tools

# Execute tool
curl -X POST http://localhost:8000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "list_doctors", "arguments": {}}'
```

### Frontend Testing
1. Open browser to `http://localhost:3000`
2. Check MCP connection status
3. Test tool discovery panel
4. Try appointment scheduling via chat

## 🔐 Google API Setup

### 1. Enable APIs
- Gmail API
- Google Calendar API
- Google+ API

### 2. Create OAuth2 Credentials
- Download `credentials.json`
- Place in `backend/` directory
- First run will create `token.json`

### 3. Grant Permissions
- Email access for appointment notifications
- Calendar access for event management

## 📁 Project Structure

```
├── backend/
│   ├── mcp_server.py          # MCP server implementation
│   ├── tool_registry.py       # Tool definitions and registry
│   ├── gmail_service.py       # Gmail API integration
│   ├── google_calendar_service.py # Calendar API integration
│   ├── requirements.txt       # Python dependencies
│   └── start-mcp-server.sh   # Server startup script
├── components/
│   └── chat-interface.tsx    # Main chat interface
├── lib/
│   └── mcp-client.ts         # MCP client implementation
├── app/                      # Next.js app directory
├── .env.local               # Development environment
├── .env.production          # Production environment template
├── vercel.json              # Vercel configuration
└── README.md                # This file
```

## 🚨 Troubleshooting

### Common Issues

1. **MCP Connection Failed**
   - Check backend server is running
   - Verify environment variables
   - Check firewall/network settings

2. **Google API Errors**
   - Verify `credentials.json` exists
   - Check API quotas and billing
   - Ensure OAuth2 consent screen is configured

3. **Frontend Build Errors**
   - Clear `.next` directory
   - Run `pnpm install` again
   - Check Node.js version compatibility

4. **Vercel Deployment Issues**
   - Set environment variables in Vercel dashboard
   - Check build logs for errors
   - Verify `vercel.json` configuration

### Debug Mode
Enable debug logging in MCP server:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Check troubleshooting section
- Review MCP server logs
- Check browser console for frontend errors
- Verify environment variable configuration

## 🔄 Updates

### Recent Changes
- ✅ Complete MCP implementation
- ✅ Real Gmail API integration
- ✅ Real Google Calendar API integration
- ✅ Production-ready deployment configuration
- ✅ Enhanced error handling and fallbacks
- ✅ Environment variable support for Vercel

### Next Steps
- [ ] Add more sophisticated appointment matching
- [ ] Implement patient authentication
- [ ] Add payment processing
- [ ] Enhanced analytics dashboard
- [ ] Mobile app development
