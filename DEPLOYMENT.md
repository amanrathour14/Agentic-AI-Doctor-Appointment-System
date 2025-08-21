# Deployment Guide

## Production Deployment

### Prerequisites
- PostgreSQL database (AWS RDS, Google Cloud SQL, or similar)
- Domain name with SSL certificate
- OpenAI API key
- Email service credentials (SendGrid, SMTP)
- Google Calendar API credentials (optional)

### Backend Deployment

#### Option 1: Docker Deployment
\`\`\`dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .
COPY scripts/ ./scripts/

# Set environment variables
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
\`\`\`

#### Option 2: Direct Deployment
\`\`\`bash
# Install dependencies
pip install -r backend/requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
export OPENAI_API_KEY="your-openai-key"

# Run with Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app --bind 0.0.0.0:8000
\`\`\`

### Frontend Deployment

#### Vercel Deployment (Recommended)
\`\`\`bash
# Deploy to Vercel
vercel --prod

# Set environment variables in Vercel dashboard:
# NEXT_PUBLIC_API_URL=https://your-backend-domain.com
\`\`\`

#### Docker Deployment
\`\`\`dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
\`\`\`

### Environment Variables

#### Backend (.env)
\`\`\`env
# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key

# Application
DEBUG=false
SESSION_TIMEOUT_MINUTES=30
ALLOWED_ORIGINS=["https://your-frontend-domain.com"]

# Google Calendar (Optional)
GOOGLE_CALENDAR_CREDENTIALS_FILE=/path/to/credentials.json
GOOGLE_CALENDAR_TOKEN_FILE=/path/to/token.json

# Email Service
SENDGRID_API_KEY=your-sendgrid-key
# OR
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
\`\`\`

#### Frontend
\`\`\`env
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
NEXT_PUBLIC_WS_URL=wss://your-backend-domain.com
\`\`\`

### Database Setup

1. Create PostgreSQL database
2. Run migration scripts:
\`\`\`bash
python scripts/01_create_database_schema.sql
python scripts/02_seed_sample_data.sql
\`\`\`

### SSL/HTTPS Configuration

#### Nginx Configuration
\`\`\`nginx
server {
    listen 443 ssl;
    server_name your-backend-domain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
\`\`\`

### Monitoring and Logging

#### Application Monitoring
\`\`\`python
# Add to main.py
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        RotatingFileHandler('app.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
\`\`\`

#### Health Checks
\`\`\`python
# Add health check endpoint
@app.get("/health/detailed")
async def detailed_health_check():
    checks = {
        "database": await check_database_connection(),
        "openai": check_openai_api(),
        "email": check_email_service(),
        "calendar": check_calendar_service()
    }
    
    all_healthy = all(checks.values())
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "checks": checks,
        "timestamp": datetime.now().isoformat()
    }
\`\`\`

### Performance Optimization

#### Database Optimization
\`\`\`sql
-- Add indexes for better performance
CREATE INDEX idx_appointments_doctor_date ON appointments(doctor_id, appointment_date);
CREATE INDEX idx_appointments_patient_date ON appointments(patient_id, appointment_date);
CREATE INDEX idx_appointments_status ON appointments(status);
\`\`\`

#### Caching
\`\`\`python
# Add Redis caching for frequently accessed data
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached = redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator
\`\`\`

### Security Considerations

1. **API Rate Limiting**
\`\`\`python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/chat")
@limiter.limit("10/minute")
async def chat_endpoint(request: Request, message: ChatMessage):
    # ... existing code
\`\`\`

2. **Input Validation**
\`\`\`python
from pydantic import validator, EmailStr

class AppointmentRequest(BaseModel):
    patient_email: EmailStr
    
    @validator('appointment_date')
    def validate_future_date(cls, v):
        if datetime.strptime(v, "%Y-%m-%d").date() < date.today():
            raise ValueError('Appointment date must be in the future')
        return v
\`\`\`

3. **CORS Configuration**
\`\`\`python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
\`\`\`

### Backup and Recovery

#### Database Backup
\`\`\`bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > backup_$DATE.sql
aws s3 cp backup_$DATE.sql s3://your-backup-bucket/
\`\`\`

#### Application Backup
\`\`\`bash
# Backup application files and configurations
tar -czf app_backup_$(date +%Y%m%d).tar.gz \
    backend/ \
    scripts/ \
    .env \
    docker-compose.yml
\`\`\`

This deployment guide ensures a production-ready setup with proper security, monitoring, and scalability considerations.
