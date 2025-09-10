#!/usr/bin/env python3
"""
Trillboards Video Generation System
Uses VEO-3 (Google's video generation model) to create side-hustle content
"""
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
import vertexai
from vertexai.generative_models import GenerativeModel

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import (
    GOOGLE_CLOUD_API_KEY, TRILLBOARDS_CONTEXT, SIDE_HUSTLE_THEMES,
    DEFAULT_VIDEO_COUNT, GENERATED_DIR, LOGS_DIR
)

def setup_logging():
    """Setup logging for the generation process"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"video_generation_{timestamp}.log"
    return log_file

def generate_video_blueprint(theme, model_name="gemini-2.5-flash"):
    """Generate a single video blueprint using Vertex AI Gemini with DYNAMIC theme-aware content"""
    
    prompt = f"""
    {TRILLBOARDS_CONTEXT}
    
    Generate a VIRAL, provocative video based on this EXACT theme: "{theme}"
    
    CRITICAL REQUIREMENTS:
    1. EXTRACT character archetype, wardrobe, and setting directly from the theme
    2. CREATE script lines that match the theme's specific persona and scenario
    3. AVOID generic templates - make everything theme-specific
    4. MAINTAIN the sexy, provocative energy from the theme
    
    Create SCROLL-STOPPING content with:
    - OUTRAGEOUS hook in first 2 seconds (numbers, shock, controversy)
    - Underground economy / rebellion angle  
    - "Forbidden knowledge" storytelling
    - Specific dollar amounts that sound believable but exciting
    - FOMO triggers and exclusivity
    - Anti-establishment undertones
    - Raw, authentic struggle-to-success narrative
    
    Generate a complete JSON blueprint that captures the ESSENCE of this theme:
    
    {{
        "id": "unique-identifier-based-on-theme",
        "theme": "{theme}",
        "avatar_style": {{
            "persona": "CHARACTER ARCHETYPE from theme (runway model, gym influencer, bartender, office worker, etc.) who discovered underground money method",
            "wardrobe": "SPECIFIC CLOTHING from theme (elegant dress, crop top, lingerie under blazer, bar uniform, etc.)",
            "setting": "ENVIRONMENT from theme (lounge, gym, bar, office, restaurant, etc.) with appropriate lighting and atmosphere"
        }},
        "video_spec": {{
            "duration_sec": 40,
            "framerate": 30,
            "aspect_ratio": "9:16"
        }},
        "script": [
            {{"t_start": 0.0, "t_end": 3.0, "speaker": "host", "line": "THEME-SPECIFIC HOOK with money amount and controversy", "broll_cue": "dramatic reveal matching theme setting", "on_screen_text": "VIRAL HOOK"}},
            {{"t_start": 3.0, "t_end": 8.0, "speaker": "host", "line": "THEME-SPECIFIC struggle story", "broll_cue": "authentic struggle in theme environment", "on_screen_text": "THE STRUGGLE"}},
            {{"t_start": 8.0, "t_end": 16.0, "speaker": "host", "line": "THEME-SPECIFIC method explanation", "broll_cue": "showing method in theme setting", "on_screen_text": "THE METHOD"}},
            {{"t_start": 16.0, "t_end": 24.0, "speaker": "host", "line": "THEME-SPECIFIC secret revelation", "broll_cue": "demonstrating trillboards in theme context", "on_screen_text": "SECRET REVEALED"}},
            {{"t_start": 24.0, "t_end": 32.0, "speaker": "host", "line": "THEME-SPECIFIC earnings reveal", "broll_cue": "counting money in theme setting", "on_screen_text": "RESULTS"}},
            {{"t_start": 32.0, "t_end": 40.0, "speaker": "host", "line": "THEME-SPECIFIC call to action", "broll_cue": "theme-appropriate closing", "on_screen_text": "YOUR TURN"}}
        ],
        "caption_overlay": [
            {{"t_start": 0.0, "t_end": 3.0, "text": "THEME-SPECIFIC viral caption", "emphasis_tokens": ["money", "theme-keyword"]}},
            {{"t_start": 3.0, "t_end": 8.0, "text": "THEME-SPECIFIC secret caption", "emphasis_tokens": ["secret", "theme-keyword"]}},
            {{"t_start": 8.0, "t_end": 16.0, "text": "THEME-SPECIFIC method caption", "emphasis_tokens": ["method", "theme-keyword"]}},
            {{"t_start": 16.0, "t_end": 24.0, "text": "THEME-SPECIFIC revelation caption", "emphasis_tokens": ["secret", "revealed"]}},
            {{"t_start": 24.0, "t_end": 32.0, "text": "THEME-SPECIFIC earnings caption", "emphasis_tokens": ["money", "EXTRA"]}},
            {{"t_start": 32.0, "t_end": 40.0, "text": "THEME-SPECIFIC action caption", "emphasis_tokens": ["theme-keyword", "NOW"]}}
        ],
        "visual_cues": {{
            "primary": ["money counting", "secret phone usage", "TV screen transformations", "THEME-SPECIFIC setting elements"],
            "secondary": ["QR codes", "app interface", "cash/payments", "THEME-SPECIFIC props"]
        }},
        "trillboards_touchpoints": [
            {{"moment": "The Reveal", "action": "Shows trillboards app in theme context", "why_it_helps": "Monetizes dead screen time in theme setting"}},
            {{"moment": "The Setup", "action": "QR code scan in theme environment", "why_it_helps": "Quick setup in theme-appropriate location"}},
            {{"moment": "The Results", "action": "Shows earnings dashboard in theme context", "why_it_helps": "Proof of concept with theme-specific validation"}}
        ],
        "constraints_and_risks": ["Keep it legal but edgy", "Focus on theme-appropriate unused screen monetization", "Maintain theme's provocative energy"],
        "metrics_hypothesis": {{
            "hook_strength_guess": 9,
            "retention_spikes_at_sec": [1.0, 8.0, 24.0],
            "shareability_notes": "Theme-specific controversy + money claims + FOMO + theme archetype appeal"
        }},
        "variants": {{
            "alt_hooks": ["THEME-SPECIFIC hook variant 1", "THEME-SPECIFIC hook variant 2", "THEME-SPECIFIC hook variant 3"],
            "alt_pacing": ["money_first_method_second", "struggle_story_then_revelation", "controversy_then_proof"]
        }},
        "rights_and_clearance_notes": "Theme-appropriate edgy but legal content - focus on legitimate unused screen monetization",
        "scene_breakdown": [
            {{
                "scene_number": 1,
                "duration_sec": 8,
                "scene_type": "text_to_video",
                "prompt_text": "THEME-SPECIFIC dramatic scene 1 with character in theme setting",
                "continuity_notes": "Establish theme atmosphere and character archetype",
                "key_visual_elements": ["cash money", "theme-specific TV location", "theme atmosphere", "character archetype"],
                "camera_instruction": "Theme-appropriate camera style",
                "lighting_notes": "Theme-appropriate lighting and mood"
            }},
            {{
                "scene_number": 2,
                "duration_sec": 8,
                "scene_type": "image_to_video",
                "prompt_text": "Continue from scene 1 - THEME-SPECIFIC action with phone/app",
                "continuity_notes": "Maintain theme atmosphere and character",
                "key_visual_elements": ["phone usage", "theme-specific movements", "app interface"],
                "camera_instruction": "Theme-appropriate camera movement",
                "lighting_notes": "Consistent theme lighting with phone glow"
            }},
            {{
                "scene_number": 3,
                "duration_sec": 8,
                "scene_type": "image_to_video",
                "prompt_text": "Continue - THEME-SPECIFIC QR code setup in theme environment",
                "continuity_notes": "Build tension of secret operation in theme context",
                "key_visual_elements": ["QR code on TV", "scanning action", "theme-specific stealth behavior"],
                "camera_instruction": "Theme-appropriate quick cuts",
                "lighting_notes": "TV brightness in theme environment"
            }},
            {{
                "scene_number": 4,
                "duration_sec": 8,
                "scene_type": "image_to_video",
                "prompt_text": "Continue - THEME-SPECIFIC success demonstration",
                "continuity_notes": "Show method working in theme setting",
                "key_visual_elements": ["TV displaying ads", "theme-specific satisfaction", "setup complete"],
                "camera_instruction": "Theme-appropriate wide shots",
                "lighting_notes": "Brighter theme environment with TV content"
            }},
            {{
                "scene_number": 5,
                "duration_sec": 8,
                "scene_type": "image_to_video",
                "prompt_text": "Continue - THEME-SPECIFIC earnings reveal and conclusion",
                "continuity_notes": "Reveal payoff in theme context",
                "key_visual_elements": ["earnings dashboard", "theme-specific money/cash", "direct camera address"],
                "camera_instruction": "Theme-appropriate close-up finale",
                "lighting_notes": "Phone screen brightness on character face"
            }}
        ]
    }}
    
    CRITICAL: Every element must reflect the specific theme's character, setting, and scenario. No generic content!
    """
    
    try:
        # Initialize Vertex AI
        vertexai.init(project="trillboard-new", location="us-central1")
        
        model = GenerativeModel(model_name)
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        text = response.text
        
        # Find JSON content (handle markdown code blocks)
        if "```json" in text:
            json_start = text.find("```json") + 7
            json_end = text.find("```", json_start)
            json_text = text[json_start:json_end].strip()
        elif "```" in text:
            json_start = text.find("```") + 3
            json_end = text.find("```", json_start)
            json_text = text[json_start:json_end].strip()
        else:
            json_text = text.strip()
        
        # Parse JSON
        blueprint = json.loads(json_text)
        return blueprint
        
    except Exception as e:
        print(f"❌ Error generating blueprint for {theme}: {e}")
        return None

def save_blueprint(blueprint, output_dir):
    """Save blueprint to JSON file"""
    if not blueprint:
        return None
        
    filename = f"{blueprint['id']}_blueprint.json"
    filepath = output_dir / filename
    
    with open(filepath, 'w') as f:
        json.dump(blueprint, f, indent=2)
    
    print(f"💾 Saved blueprint: {filepath}")
    return filepath

def main():
    """Main generation workflow"""
    print("🎬 Trillboards Video Generation System")
    print("=" * 50)
    
    # Setup Vertex AI (uses application default credentials)
    print("🔑 Using Vertex AI with application default credentials")
    vertexai.init(project="trillboard-new", location="us-central1")
    log_file = setup_logging()
    
    # Generate blueprints for each theme
    blueprints = []
    
    print(f"📝 Generating blueprints for {len(SIDE_HUSTLE_THEMES)} themes...")
    
    for i, theme in enumerate(SIDE_HUSTLE_THEMES[:DEFAULT_VIDEO_COUNT], 1):
        print(f"\n🎯 [{i}/{len(SIDE_HUSTLE_THEMES[:DEFAULT_VIDEO_COUNT])}] Theme: {theme}")
        
        blueprint = generate_video_blueprint(theme)
        if blueprint:
            # Save blueprint
            saved_path = save_blueprint(blueprint, GENERATED_DIR)
            if saved_path:
                blueprints.append(blueprint)
                print(f"✅ Blueprint created: {blueprint['id']}")
                
                # Generate title and caption for spreadsheet
                title = f"{blueprint['theme'][:50]}..." if len(blueprint['theme']) > 50 else blueprint['theme']
                caption = " ".join([segment["line"] for segment in blueprint["script"][:2]])  # First 2 lines
                
                print(f"📋 Title: {title}")
                print(f"📋 Caption preview: {caption[:100]}...")
        else:
            print(f"❌ Failed to generate blueprint for: {theme}")
        
        # Small delay to avoid rate limits
        time.sleep(1)
    
    print(f"\n🎉 Generated {len(blueprints)} video blueprints!")
    print(f"📁 Blueprints saved to: {GENERATED_DIR}")
    
    # For now, we're just generating blueprints
    # Video generation with VEO would require additional setup
    print("\n⚠️ Note: Actual video generation with VEO requires further API integration")
    print("📝 Next steps:")
    print("1. Review generated blueprints")
    print("2. Implement VEO video generation")
    print("3. Setup Google Drive/Sheets integration")

if __name__ == "__main__":
    main()