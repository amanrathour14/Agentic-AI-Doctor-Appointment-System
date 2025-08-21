# Agentic AI Doctor Appointment System

A comprehensive full-stack agentic AI system for doctor appointment scheduling and management using MCP (Model Context Protocol), built with FastAPI, React, and OpenAI.

## 🏗️ Architecture Overview

This system implements a true agentic AI architecture where the LLM autonomously decides which tools to use based on natural language input:

<img width="643" height="418" alt="image" src="https://github.com/user-attachments/assets/61f9fb6d-fbae-476c-ad04-5a6e87085bfd" />


<img width="598" height="432" alt="image" src="https://github.com/user-attachments/assets/d7801a65-2c3e-4e25-89b1-4951dcd6e04c" />


## 🚀 Key Features

### Agentic AI Capabilities
- **Natural Language Processing**: Understands complex appointment requests
- **Autonomous Tool Selection**: LLM decides which MCP tools to use
- **Multi-turn Conversations**: Maintains context across interactions
- **Intelligent Suggestions**: Provides helpful next steps and alternatives

### Core Functionality
- **Appointment Scheduling**: AI-powered booking with availability checking
- **Doctor Management**: Comprehensive doctor profiles and availability
- **Patient Management**: Patient records and appointment history
- **Real-time Notifications**: WebSocket-based notifications for doctors
- **Calendar Integration**: Google Calendar sync for appointments
- **Email Notifications**: Automated confirmations and reminders

### MCP (Model Context Protocol) Tools
1. **check_doctor_availability**: Check doctor schedules and available slots
2. **schedule_appointment**: Book appointments with validation and notifications
3. **get_appointment_stats**: Generate statistics and reports for doctors
4. **search_patients_by_symptom**: Find patients by symptoms for analysis
5. **get_doctor_schedule**: Retrieve doctor schedules for specific date ranges

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **SQLAlchemy**: Database ORM with PostgreSQL
- **OpenAI GPT-4**: LLM for agentic AI capabilities
- **WebSockets**: Real-time notifications
- **Google Calendar API**: Calendar integration
- **SendGrid/SMTP**: Email notifications

### Frontend
- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **shadcn/ui**: Professional UI components
- **WebSocket Client**: Real-time notification handling

### Database
- **PostgreSQL**: Primary database
- **SQLAlchemy Models**: Type-safe database operations

## 📋 Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 12+
- OpenAI API key
- Google Calendar API credentials (optional)
- Email service credentials (optional)

## 🚀 Quick Start

### 1. Database Setup

\`\`\`bash
# Run the database setup scripts
python scripts/01_create_database_schema.sql
python scripts/02_seed_sample_data.sql
python scripts/database_models.py
\`\`\`

### 2. Backend Setup

\`\`\`bash
cd backend
pip install -r requirements.txt

Copy environment template
cp .env.example .env

Edit .env with your credentials:
- DATABASE_URL
- OPENAI_API_KEY
- Google Calendar credentials (optional)
- Email service credentials (optional)

Start the backend server
python main.py
\`\`\`

### 3. Frontend Setup


Install dependencies (automatically handled by v0)
Start the development server (automatically handled by v0)
\`\`\`

### 4. Test the System


Run comprehensive tests
python scripts/test_complete_system.py

Test individual components
python scripts/test_agent.py
python scripts/test_mcp_tools.py


## 🧪 Testing

### Automated Tests

Run the comprehensive test suite:

bash
python scripts/test_complete_system.py


This tests:
- Database connectivity and models
- MCP tool functionality
- LLM agent responses
- API endpoints
- WebSocket notifications
- External API integrations

### Manual Testing

1. **Patient Flow**:
   - Select "I'm a Patient" role
   - Ask: "I want to book an appointment with Dr. Smith tomorrow morning"
   - Verify AI checks availability and schedules appointment

2. **Doctor Flow**:
   - Select "I'm a Doctor" role
   - Ask: "Show me my appointments for this week"
   - Verify statistics and schedule display

3. **Notifications**:
   - Book an appointment
   - Verify real-time notification appears for doctor
   - Check email confirmations sent

## 📖 API Documentation

### Core Endpoints

#### Chat Endpoint
\`\`\`http
POST /chat
Content-Type: application/json

{
  "message": "I want to book an appointment with Dr. Smith tomorrow at 2 PM",
  "session_id": "optional-session-id",
  "user_type": "patient"
}
\`\`\`

#### MCP Tool Execution
\`\`\`http
POST /mcp/execute
Content-Type: application/json

{
  "tool_name": "check_doctor_availability",
  "parameters": {
    "doctor_name": "Dr. Smith",
    "date": "2024-01-15",
    "time_preference": "afternoon"
  }
}
\`\`\`

#### WebSocket Notifications
\`\`\`javascript
const ws = new WebSocket('ws://localhost:8000/ws/notifications/1');
ws.onmessage = (event) => {
  const notification = JSON.parse(event.data);
  console.log('New notification:', notification);
};
\`\`\`

### Available MCP Tools

1. **check_doctor_availability**
   - Parameters: `doctor_name`, `date`, `time_preference`
   - Returns: Available time slots

2. **schedule_appointment**
   - Parameters: `doctor_name`, `patient_name`, `patient_email`, `appointment_date`, `appointment_time`, `symptoms`
   - Returns: Appointment confirmation with calendar/email integration

3. **get_appointment_stats**
   - Parameters: `doctor_name`, `date_range`, `filter_by`
   - Returns: Statistical analysis of appointments

4. **search_patients_by_symptom**
   - Parameters: `symptom`, `doctor_name`, `date_range`
   - Returns: Patients matching symptom criteria

5. **get_doctor_schedule**
   - Parameters: `doctor_name`, `start_date`, `end_date`
   - Returns: Complete doctor schedule

## 🔧 Configuration

### Environment Variables

env
# Database
DATABASE_URL=postgresql://user:password@localhost/doctor_appointments

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Google Calendar (Optional)
GOOGLE_CALENDAR_CREDENTIALS_FILE=path/to/credentials.json
GOOGLE_CALENDAR_TOKEN_FILE=path/to/token.json

# Email Service (Optional)
SENDGRID_API_KEY=your-sendgrid-key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Application
DEBUG=true
SESSION_TIMEOUT_MINUTES=30
ALLOWED_ORIGINS=["http://localhost:3000"]


## 🏥 Usage Examples

### Patient Interactions


Patient: "I need to see Dr. Johnson next week for a headache"
AI: "I'll check Dr. Johnson's availability next week for you."
    [Executes: check_doctor_availability]
    "Dr. Johnson has these available slots next week:
    - Monday 2:00 PM
    - Wednesday 10:30 AM
    - Friday 3:00 PM
    Which time works best for you?"

Patient: "Monday 2 PM works"
AI: "Perfect! I'll schedule your appointment with Dr. Johnson for Monday at 2:00 PM."
    [Executes: schedule_appointment]
    "✅ Appointment confirmed! You'll receive an email confirmation shortly."


### Doctor Interactions


Doctor: "Show me my schedule for today"
AI: [Executes: get_doctor_schedule]
    "Here's your schedule for today:
    - 9:00 AM: Sarah Wilson (routine checkup)
    - 10:30 AM: Mike Chen (follow-up)
    - 2:00 PM: Lisa Brown (headache)
    You have 3 appointments scheduled."

Doctor: "How many patients with fever did I see this month?"
AI: [Executes: search_patients_by_symptom]
    "You saw 12 patients with fever this month. Would you like to see the detailed list?"


## 🔔 Notification System

### Real-time Notifications
- **New Appointments**: Instant alerts when patients book
- **Cancellations**: Immediate notification of cancelled appointments
- **Reminders**: 30-minute appointment reminders
- **System Alerts**: Important system notifications

### Notification Types
- `new_appointment`: High priority, includes patient details
- `appointment_cancelled`: Medium priority, includes cancellation details
- `appointment_reminder`: High priority, includes timing information
- `patient_message`: Medium priority, includes message content
- `system_alert`: Variable priority, includes system information

## 🚀 Deployment

### Production Setup

1. **Database**: Use managed PostgreSQL (AWS RDS, Google Cloud SQL)
2. **Backend**: Deploy FastAPI with Gunicorn/Uvicorn
3. **Frontend**: Deploy Next.js to Vercel or similar platform
4. **Environment**: Set production environment variables
5. **SSL**: Enable HTTPS for WebSocket connections



## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
Made by Aman Rathour @ 2025

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Run the test suite to identify issues
4. Check logs for detailed error information

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection**: Verify PostgreSQL is running and credentials are correct
2. **OpenAI API**: Ensure API key is valid and has sufficient credits
3. **WebSocket Issues**: Check CORS settings and firewall rules
4. **Email Not Sending**: Verify SMTP credentials and settings
5. **Calendar Integration**: Check Google API credentials and permissions

### Debug Mode

Enable debug logging:
python
import logging
logging.basicConfig(level=logging.DEBUG)

This comprehensive system demonstrates advanced agentic AI capabilities with real-world medical appointment scheduling functionality.
