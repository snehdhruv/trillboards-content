#!/usr/bin/env python3
"""
Test script to verify Gemini API connectivity and basic functionality
"""
import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

def test_gemini_api():
    """Test basic Gemini API connectivity"""
    try:
        import google.generativeai as genai
        
        # Get API key from environment
        api_key = os.getenv("GOOGLE_CLOUD_API_KEY")
        if not api_key:
            print("❌ GOOGLE_CLOUD_API_KEY not found in environment")
            return False
            
        print(f"✅ Found API key: {api_key[:10]}...")
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # List available models first
        print("📋 Available models:")
        models = genai.list_models()
        for model in models:
            print(f"  - {model.name}")
            if hasattr(model, 'supported_generation_methods'):
                if 'generateContent' in model.supported_generation_methods:
                    print(f"    ✅ Supports content generation")
        
        # Test with the first available model that supports generateContent
        suitable_model = None
        for model in models:
            if hasattr(model, 'supported_generation_methods'):
                if 'generateContent' in model.supported_generation_methods:
                    suitable_model = model.name
                    break
        
        if not suitable_model:
            print("❌ No models found that support generateContent")
            return False
            
        print(f"🧪 Testing with model: {suitable_model}")
        model = genai.GenerativeModel(suitable_model)
        response = model.generate_content("Say hello and confirm you're working!")
        
        print(f"✅ Gemini API Response: {response.text}")
        return True
        
    except ImportError:
        print("❌ google-generativeai package not installed")
        print("Run: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ Error testing Gemini API: {e}")
        return False

def test_video_blueprint_generation():
    """Test generating a simple video blueprint"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GOOGLE_CLOUD_API_KEY")
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-pro')
        
        # Simple test prompt for video blueprint
        prompt = """
        Create a JSON object for a 30-second vertical video about using screens in a coffee shop.
        Include these fields:
        - title: short catchy title
        - duration: 30
        - concept: brief description
        - script: 3 short lines for a 30-second video
        
        Make it about quietly running local promos on a spare TV.
        """
        
        response = model.generate_content(prompt)
        print("✅ Video Blueprint Generation Test:")
        print(response.text)
        return True
        
    except Exception as e:
        print(f"❌ Error testing video blueprint generation: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Gemini API Integration...")
    
    # Basic connectivity test
    if test_gemini_api():
        print("\n🧪 Testing Video Blueprint Generation...")
        test_video_blueprint_generation()
    else:
        print("🔧 Fix API connectivity before proceeding")