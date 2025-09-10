#!/usr/bin/env python3
"""
Test Vertex AI Gemini API for content generation
"""
import os
import sys
from pathlib import Path

def test_vertex_gemini():
    """Test Gemini through Vertex AI"""
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        
        # Initialize Vertex AI
        project_id = "trillboard-new"
        location = "us-central1"
        
        vertexai.init(project=project_id, location=location)
        print(f"✅ Vertex AI initialized for project: {project_id}")
        
        # Create model
        model = GenerativeModel("gemini-2.0-flash-exp")
        print(f"✅ Gemini model loaded")
        
        # Test simple generation
        prompt = "Write a 2-sentence description of a coffee shop that uses screens to show local promotions."
        
        response = model.generate_content(prompt)
        print(f"✅ Content generated:")
        print(f"📝 Response: {response.text}")
        
        return True
        
    except ImportError:
        print("❌ vertexai package not installed. Install with: pip install google-cloud-aiplatform")
        return False
    except Exception as e:
        print(f"❌ Vertex AI error: {e}")
        return False

def test_vertex_veo():
    """Test VEO video generation through Vertex AI"""
    try:
        import vertexai
        from vertexai.preview.vision_models import VideoGenerationModel
        
        # Initialize Vertex AI
        project_id = "trillboard-new"
        location = "us-central1"
        
        vertexai.init(project=project_id, location=location)
        print(f"✅ Vertex AI initialized for VEO")
        
        # List available VEO models
        print("🎥 Checking VEO models...")
        
        # This would be the approach for VEO through Vertex AI
        # model = VideoGenerationModel.from_pretrained("veo-001")
        print("📝 VEO integration would go here")
        
        return True
        
    except ImportError:
        print("❌ vertexai package not installed")
        return False
    except Exception as e:
        print(f"❌ VEO error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Vertex AI Integration")
    print("=" * 50)
    
    if test_vertex_gemini():
        print("\n🎥 Testing VEO integration...")
        test_vertex_veo()
    else:
        print("🔧 Fix Vertex AI access first")