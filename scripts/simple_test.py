#!/usr/bin/env python3
"""
Simple test to verify we can generate content with proper authentication
"""
import os
from google.auth import default
from google.auth.transport.requests import Request

def test_auth():
    """Test Google Cloud authentication"""
    try:
        # Get default credentials
        credentials, project = default()
        
        print(f"✅ Default credentials found")
        print(f"✅ Project: {project}")
        
        # Refresh credentials to get access token
        request = Request()
        credentials.refresh(request)
        
        print(f"✅ Token refreshed successfully")
        print(f"✅ Access token: {credentials.token[:20]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return False

def test_simple_gemini():
    """Test simple Gemini content generation with default credentials"""
    try:
        import google.generativeai as genai
        
        # Configure with no API key to use default credentials
        genai.configure()
        
        # Try a simple generation
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Write a 2-sentence description of a coffee shop.")
        
        print(f"✅ Gemini response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Authentication & Gemini Access")
    print("=" * 50)
    
    if test_auth():
        print("\n🧪 Testing Gemini API...")
        test_simple_gemini()
    else:
        print("🔧 Fix authentication first")