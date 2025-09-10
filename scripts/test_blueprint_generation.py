#!/usr/bin/env python3
"""
Test script to generate and validate video blueprints before full video generation
"""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

import vertexai
from generate_trillboards_videos import generate_video_blueprint, save_blueprint
from config.settings import SIDE_HUSTLE_THEMES, GENERATED_DIR

def test_blueprint_generation():
    """Test generating a single blueprint"""
    
    # Initialize Vertex AI
    print("🔑 Initializing Vertex AI...")
    vertexai.init(project="trillboard-new", location="us-central1")
    
    # Test with first theme
    test_theme = SIDE_HUSTLE_THEMES[0]
    print(f"🧪 Testing blueprint generation for: {test_theme}")
    print(f"🤖 Using Gemini 2.5 Flash via Vertex AI")
    
    try:
        blueprint = generate_video_blueprint(test_theme)
        
        if blueprint:
            print(f"✅ Blueprint generated successfully!")
            print(f"📋 ID: {blueprint.get('id', 'N/A')}")
            print(f"📋 Theme: {blueprint.get('theme', 'N/A')}")
            print(f"📋 Duration: {blueprint.get('video_spec', {}).get('duration_sec', 'N/A')} seconds")
            
            # Count script segments
            script_segments = len(blueprint.get('script', []))
            print(f"📋 Script segments: {script_segments}")
            
            # Show first few lines of script
            if blueprint.get('script'):
                print(f"📋 Sample script lines:")
                for i, segment in enumerate(blueprint['script'][:3]):
                    print(f"  {i+1}. ({segment['t_start']}-{segment['t_end']}s): {segment['line']}")
            
            # Check Trillboards touchpoints
            touchpoints = blueprint.get('trillboards_touchpoints', [])
            print(f"📋 Trillboards touchpoints: {len(touchpoints)}")
            for tp in touchpoints:
                print(f"  - {tp['moment']}: {tp['action']}")
            
            # Check scene breakdown
            scenes = blueprint.get('scene_breakdown', [])
            print(f"🎬 Scene breakdown: {len(scenes)} scenes")
            for scene in scenes:
                print(f"  Scene {scene['scene_number']}: {scene['scene_type']} ({scene['duration_sec']}s)")
                print(f"    Prompt: {scene['prompt_text'][:60]}...")
            
            # Save blueprint
            saved_path = save_blueprint(blueprint, GENERATED_DIR)
            if saved_path:
                print(f"💾 Blueprint saved to: {saved_path}")
                return True
        else:
            print("❌ No blueprint generated")
            return False
            
    except Exception as e:
        print(f"❌ Error testing blueprint generation: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Blueprint Generation...")
    print("🔑 Using Vertex AI with gcloud application default credentials")
    
    success = test_blueprint_generation()
    
    if success:
        print("\n✅ Blueprint generation test passed!")
        print("🎯 Ready to generate full video blueprints")
    else:
        print("\n❌ Blueprint generation test failed!")
        print("🔧 Fix issues before proceeding")