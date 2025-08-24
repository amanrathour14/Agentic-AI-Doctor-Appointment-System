#!/usr/bin/env python3
"""
Complete Integration Test for MedAI System
Tests MCP, Google Calendar, Email, and Gmail integrations
"""
import asyncio
import sys
import os
import json
from datetime import datetime, timedelta

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_mcp_integration():
    """Test MCP server integration"""
    print("🔧 Testing MCP Integration...")
    
    try:
        from mcp_server import MCPServer
        
        mcp_server = MCPServer()
        tools_count = len(mcp_server.tools)
        
        print(f"   ✅ MCP server running with {tools_count} tools")
        
        # Test tool discovery
        if "tools/list" in mcp_server.tools:
            result = await mcp_server.tools["tools/list"].handler({})
            print(f"   ✅ Tool discovery working: {result['count']} tools found")
        
        # Test appointment scheduling tool
        if "appointments/schedule" in mcp_server.tools:
            tool = mcp_server.tools["appointments/schedule"]
            print(f"   ✅ Appointment tool available: {tool.description}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ MCP integration failed: {str(e)}")
        return False

async def test_google_calendar_integration():
    """Test Google Calendar integration"""
    print("📅 Testing Google Calendar Integration...")
    
    try:
        from google_calendar_service import calendar_service
        
        if calendar_service.is_available():
            print("   ✅ Google Calendar service available")
            
            # Test creating a test event
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            test_event = await calendar_service.create_appointment_event(
                doctor_name="Dr. Test",
                patient_name="Test Patient",
                patient_email="test@example.com",
                appointment_date=tomorrow,
                appointment_time="10:00",
                symptoms="Test symptoms"
            )
            
            if test_event:
                print(f"   ✅ Calendar event created: {test_event}")
                return True
            else:
                print("   ⚠️  Calendar event creation failed")
                return False
        else:
            print("   ⚠️  Google Calendar service not configured")
            print("   📖 Follow: backend/GOOGLE_CALENDAR_SETUP.md")
            return False
        
    except Exception as e:
        print(f"   ❌ Google Calendar integration failed: {str(e)}")
        return False

async def test_email_integration():
    """Test Email service integration"""
    print("📧 Testing Email Integration...")
    
    try:
        from email_service import email_service
        
        if email_service.is_available():
            print("   ✅ Email service available")
            
            # Test sending a test email
            test_result = await email_service.send_appointment_confirmation(
                patient_email="test@example.com",
                patient_name="Test Patient",
                doctor_name="Dr. Test",
                appointment_date="2024-01-20",
                appointment_time="10:00",
                symptoms="Test symptoms"
            )
            
            if test_result:
                print(f"   ✅ Test email sent: {test_result}")
                return True
            else:
                print("   ⚠️  Test email failed")
                return False
        else:
            print("   ⚠️  Email service not configured")
            print("   📖 Follow: backend/EMAIL_SETUP.md")
            return False
        
    except Exception as e:
        print(f"   ❌ Email integration failed: {str(e)}")
        return False

async def test_gmail_api_integration():
    """Test Gmail API integration"""
    print("📬 Testing Gmail API Integration...")
    
    try:
        # Check if Gmail environment variables are set
        gmail_client_id = os.getenv('GMAIL_CLIENT_ID')
        gmail_client_secret = os.getenv('GMAIL_CLIENT_SECRET')
        gmail_refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')
        
        if all([gmail_client_id, gmail_client_secret, gmail_refresh_token]):
            print("   ✅ Gmail API credentials configured")
            
            # Test Gmail API connection
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            
            creds = Credentials(
                None,  # No access token initially
                refresh_token=gmail_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=gmail_client_id,
                client_secret=gmail_client_secret
            )
            
            # Refresh credentials
            creds.refresh(Request())
            
            # Build Gmail service
            service = build('gmail', 'v1', credentials=creds)
            
            # Test API call
            profile = service.users().getProfile(userId='me').execute()
            print(f"   ✅ Gmail API connected: {profile['emailAddress']}")
            
            return True
            
        else:
            print("   ⚠️  Gmail API credentials not configured")
            print("   📖 Follow: backend/GMAIL_SETUP.md")
            return False
        
    except Exception as e:
        print(f"   ❌ Gmail API integration failed: {str(e)}")
        return False

async def test_fastapi_endpoints():
    """Test FastAPI MCP endpoints"""
    print("🌐 Testing FastAPI MCP Endpoints...")
    
    try:
        from fastapi_mcp_server import app
        print("   ✅ FastAPI MCP server imported successfully")
        
        # Check if all required endpoints are defined
        routes = [route.path for route in app.routes]
        required_endpoints = [
            "/mcp/tools",
            "/mcp/tools/{tool_name}/schema",
            "/mcp/tools/execute",
            "/mcp/ws",
            "/health",
            "/mcp/info"
        ]
        
        missing_endpoints = [ep for ep in required_endpoints if ep not in routes]
        
        if not missing_endpoints:
            print("   ✅ All required MCP endpoints defined")
            return True
        else:
            print(f"   ❌ Missing endpoints: {missing_endpoints}")
            return False
        
    except Exception as e:
        print(f"   ❌ FastAPI endpoints test failed: {str(e)}")
        return False

async def test_environment_configuration():
    """Test environment configuration"""
    print("⚙️  Testing Environment Configuration...")
    
    try:
        from config import settings
        
        # Check required settings
        required_settings = [
            'app_name',
            'app_version',
            'debug'
        ]
        
        missing_settings = []
        for setting in required_settings:
            if not hasattr(settings, setting):
                missing_settings.append(setting)
        
        if not missing_settings:
            print("   ✅ All required settings configured")
            print(f"   📋 App: {settings.app_name} v{settings.app_version}")
            print(f"   🐛 Debug mode: {settings.debug}")
            return True
        else:
            print(f"   ❌ Missing settings: {missing_settings}")
            return False
        
    except Exception as e:
        print(f"   ❌ Environment configuration test failed: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting Complete Integration Tests...\n")
    
    tests = [
        ("Environment Configuration", test_environment_configuration),
        ("MCP Integration", test_mcp_integration),
        ("FastAPI Endpoints", test_fastapi_endpoints),
        ("Google Calendar Integration", test_google_calendar_integration),
        ("Email Integration", test_email_integration),
        ("Gmail API Integration", test_gmail_api_integration),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 {test_name}")
        print('='*60)
        
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"   ❌ Test crashed: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 INTEGRATION TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All integration tests passed! Your system is fully configured.")
        return 0
    elif passed >= total * 0.8:
        print("\n⚠️  Most tests passed. Check failed tests above for configuration issues.")
        return 1
    else:
        print("\n❌ Many tests failed. Review configuration and setup guides.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)