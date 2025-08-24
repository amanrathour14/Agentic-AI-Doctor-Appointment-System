# 🚀 MedAI Quick Start Guide

Get your MedAI Doctor Appointment System up and running with all integrations in minutes!

## 📋 Prerequisites

- Python 3.8+ installed
- PostgreSQL database
- Google Cloud Platform account (for Gmail & Calendar)
- OpenAI API key

## ⚡ Quick Setup (5 minutes)

### 1. Environment Setup

```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit with your credentials
nano backend/.env
```

**Required (fill these in):**
- `OPENAI_API_KEY` - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- `DATABASE_URL` - Your PostgreSQL connection string

### 2. Install Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-simple.txt
```

### 3. Database Setup

```bash
# Start MySQL (if not running)
sudo systemctl start mysql

# Run MySQL setup script
chmod +x scripts/setup_mysql.sh
./scripts/setup_mysql.sh

# Run MySQL schema setup
mysql -u medai_user -pmedai_password doctor_appointments < scripts/01_create_database_schema_mysql.sql
```

### 4. Test Basic System

```bash
# Test MCP functionality
python test_mcp_basic.py

# Test complete integration
python test_complete_integration.py
```

## 🔧 Advanced Integrations

### Gmail API Setup (OAuth2)

1. Follow [Gmail Setup Guide](backend/GMAIL_SETUP.md)
2. Add credentials to `.env`:
   ```env
   GMAIL_CLIENT_ID=your_client_id
   GMAIL_CLIENT_SECRET=your_client_secret
   GMAIL_REFRESH_TOKEN=your_refresh_token
   GMAIL_USER_EMAIL=your_email@gmail.com
   ```

### Google Calendar Setup

1. Follow [Calendar Setup Guide](backend/GOOGLE_CALENDAR_SETUP.md)
2. Add to `.env`:
   ```env
   GOOGLE_CALENDAR_CREDENTIALS=/path/to/credentials.json
   ```

### Email Service Setup

1. Follow [Email Setup Guide](backend/EMAIL_SETUP.md)
2. Choose SendGrid (recommended) or SMTP
3. Add to `.env`:
   ```env
   SENDGRID_API_KEY=your_api_key
   # OR
   SMTP_HOST=smtp.gmail.com
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   ```

## 🚀 Start the System

### Option 1: MCP Server Only
```bash
cd backend
source venv/bin/activate
python fastapi_mcp_server.py
```

### Option 2: Full Backend
```bash
cd backend
source venv/bin/activate
python main.py
```

### Option 3: Frontend + Backend
```bash
# Terminal 1: Backend
cd backend && source venv/bin/activate && python main.py

# Terminal 2: Frontend
cd .. && npm run dev
```

## 🧪 Verify Everything Works

### 1. Health Check
```bash
curl http://localhost:8001/health
```

### 2. MCP Tool Discovery
```bash
curl http://localhost:8001/mcp/tools
```

### 3. Test Appointment Scheduling
```bash
curl -X POST http://localhost:8001/mcp/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_calls": [{
      "tool_name": "appointments/schedule",
      "parameters": {
        "doctor_name": "Dr. Smith",
        "patient_name": "John Doe",
        "patient_email": "john@example.com",
        "appointment_date": "2024-01-20",
        "appointment_time": "10:00",
        "symptoms": "Headache"
      }
    }]
  }'
```

## 📱 Frontend Access

- **URL**: http://localhost:3000
- **Features**: Chat interface, appointment booking, doctor search
- **MCP Integration**: Automatic tool discovery and execution

## 🔍 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements-simple.txt`

2. **Database connection failed**
   - Check PostgreSQL is running
   - Verify `DATABASE_URL` in `.env`

3. **Google API errors**
   - Check credentials in `.env`
   - Follow setup guides for proper configuration

4. **Port already in use**
   - Kill existing process: `lsof -ti:8001 | xargs kill -9`
   - Or use different port in configuration

### Get Help

- Check [MCP Implementation Guide](MCP_IMPLEMENTATION.md)
- Review [Deployment Guide](DEPLOYMENT.md)
- Run integration tests: `python test_complete_integration.py`

## 🎯 What You Get

✅ **MCP Architecture** - Full Model Context Protocol implementation  
✅ **Tool Discovery** - OpenAPI-compliant tool schemas  
✅ **Gmail Integration** - OAuth2-based email sending  
✅ **Google Calendar** - Real calendar event creation  
✅ **FastAPI Backend** - RESTful API with MCP endpoints  
✅ **Frontend Client** - React-based chat interface  
✅ **LLM Agent** - AI-powered appointment scheduling  

## 🚀 Next Steps

1. **Customize** - Modify appointment workflows
2. **Scale** - Add more doctors and specialties  
3. **Integrate** - Connect with hospital systems
4. **Deploy** - Move to production environment

---

**🎉 You're all set!** Your MedAI system now has all the features your recruiter requested.