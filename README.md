# MedAI Doctor Appointment System

An intelligent, agentic AI system for managing doctor appointments with natural language processing, MCP (Model Context Protocol) integration, and automated scheduling capabilities.

## 🚀 Features

- **AI-Powered Appointment Scheduling**: Natural language appointment booking
- **MCP Integration**: Model Context Protocol for tool discovery and execution
- **Smart Doctor Matching**: AI-driven doctor-patient matching based on symptoms
- **Automated Notifications**: Email and SMS reminders
- **Google Calendar Integration**: Real calendar event creation
- **Gmail API Integration**: Email utilities and automation
- **Real-time Chat Interface**: Interactive appointment booking
- **Advanced Analytics**: Appointment statistics and insights

## 🏗️ Architecture

### MCP (Model Context Protocol) Implementation
- **Client-Server-Tool Architecture**: Standard MCP implementation
- **Tool Discovery**: OpenAPI schema-based tool registration
- **Tool Execution**: Secure tool invocation with parameter validation
- **WebSocket Support**: Real-time communication

### Backend Technologies
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM with MySQL
- **Pydantic**: Data validation and serialization
- **OpenAI API**: LLM integration for natural language processing

### Database
- **MySQL**: Primary database with UTF8MB4 support
- **Optimized Schema**: Efficient indexing and relationships
- **Data Integrity**: Foreign key constraints and cascading deletes

## 📋 Prerequisites

- Python 3.8+
- MySQL 8.0+
- Node.js 18+
- OpenAI API key
- Google Cloud credentials (for Calendar/Gmail integration)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Agentic-AI-Doctor-Appointment-System
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials
```

### 3. Database Setup
```bash
# Run MySQL setup script
chmod +x ../scripts/setup_mysql.sh
../scripts/setup_mysql.sh

# Create database schema
mysql -u medai_user -p doctor_appointments < ../scripts/01_create_database_schema_mysql.sql
```

### 4. Frontend Setup
```bash
cd ..
npm install
```

## 🔧 Configuration

### Environment Variables
Required variables in `backend/.env`:
- `OPENAI_API_KEY`: Your OpenAI API key
- `DATABASE_URL`: MySQL connection string

Optional integrations:
- `GOOGLE_CALENDAR_CREDENTIALS`: Path to Google service account JSON
- `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN`
- `SENDGRID_API_KEY`: For email notifications

### Database Configuration
The system uses MySQL with the following optimized settings:
- UTF8MB4 character set for full Unicode support
- InnoDB storage engine for ACID compliance
- Optimized indexes for appointment queries
- Connection pooling for performance

## 🚀 Usage

### Start the Backend
```bash
cd backend
source venv/bin/activate
python main.py
```

### Start the Frontend
```bash
npm run dev
```

### Access the System
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- MCP Server: http://localhost:8001

## 🔌 MCP Tools

The system exposes the following MCP tools:

1. **check_doctor_availability**: Check doctor availability for specific dates
2. **schedule_appointment**: Book appointments with natural language
3. **get_appointment_stats**: Retrieve appointment statistics
4. **search_patients_by_symptom**: Search patients by symptoms
5. **get_doctor_schedule**: Get doctor schedules

## 📊 Database Schema

### Core Tables
- `doctors`: Doctor information and specializations
- `patients`: Patient demographics and contact info
- `appointments`: Appointment details and status
- `doctor_availability`: Doctor working hours
- `visit_history`: Patient visit records

### Key Features
- **Referential Integrity**: Foreign key constraints
- **Audit Trail**: Created/updated timestamps
- **Soft Deletes**: Data preservation
- **Indexing**: Optimized query performance

## 🧪 Testing

### Database Connection Test
```bash
cd backend
python test_db_connection.py
```

### MCP Integration Test
```bash
python test_complete_integration.py
```

## 📚 API Documentation

### MCP Endpoints
- `GET /mcp/tools`: List available tools
- `GET /mcp/tools/{tool_name}/schema`: Get tool schema
- `POST /mcp/tools/execute`: Execute tool
- `GET /mcp/ws`: WebSocket connection
- `GET /health`: Health check

### Appointment Endpoints
- `POST /appointments`: Create appointment
- `GET /appointments`: List appointments
- `PUT /appointments/{id}`: Update appointment
- `DELETE /appointments/{id}`: Cancel appointment

## 🔒 Security Features

- **Input Validation**: Pydantic model validation
- **SQL Injection Protection**: SQLAlchemy ORM
- **CORS Configuration**: Controlled cross-origin access
- **Session Management**: Secure session handling
- **API Rate Limiting**: Request throttling

## 🚀 Deployment

### Production Considerations
1. **Database**: Use managed MySQL (AWS RDS, Google Cloud SQL)
2. **Environment**: Set DEBUG=False
3. **HTTPS**: Enable SSL/TLS
4. **Monitoring**: Add logging and health checks
5. **Scaling**: Use load balancers and connection pooling

### Docker Support
```bash
# Build and run with Docker
docker-compose up --build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation
- Review setup guides in the `backend/` directory
- Open an issue on GitHub

## 🔄 Changelog

### v1.0.0
- Initial release with MCP integration
- MySQL database support
- Google Calendar and Gmail API integration
- Complete appointment management system
