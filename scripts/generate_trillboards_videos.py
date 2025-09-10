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
    """Generate a single video blueprint using Vertex AI Gemini"""
    
    prompt = f"""
    {TRILLBOARDS_CONTEXT}
    
    Generate a VIRAL, provocative video with this controversial theme: "{theme}"
    
    Create SCROLL-STOPPING content with:
    - OUTRAGEOUS hook in first 2 seconds (numbers, shock, controversy)
    - Underground economy / rebellion angle
    - "Forbidden knowledge" storytelling
    - Specific dollar amounts that sound believable but exciting
    - FOMO triggers and exclusivity
    - Anti-establishment undertones
    - Raw, authentic struggle-to-success narrative
    
    Follow this exact JSON structure:
    {{
        "id": "unique-identifier",
        "theme": "{theme}",
        "avatar_style": {{
            "persona": "Rebellious, street-smart character who discovered underground money-making method",
            "wardrobe": "Casual, relatable clothing that signals 'regular person who cracked the code'",
            "setting": "Gritty, authentic workplace setting - dim lighting, real environment not staged"
        }},
        "video_spec": {{
            "duration_sec": 40,
            "framerate": 30,
            "aspect_ratio": "9:16"
        }},
        "script": [
            {{"t_start": 0.0, "t_end": 3.0, "speaker": "host", "line": "SHOCKING HOOK with specific dollar amount + controversy", "broll_cue": "dramatic reveal of money/screen", "on_screen_text": "VIRAL HOOK"}},
            {{"t_start": 3.0, "t_end": 8.0, "speaker": "host", "line": "I was struggling until I discovered this loophole", "broll_cue": "authentic struggle story", "on_screen_text": "THE STRUGGLE"}},
            {{"t_start": 8.0, "t_end": 16.0, "speaker": "host", "line": "Here's exactly how I hack dead TV screens for money", "broll_cue": "showing the method", "on_screen_text": "THE METHOD"}},
            {{"t_start": 16.0, "t_end": 24.0, "speaker": "host", "line": "Most people don't know you can monetize workplace TVs", "broll_cue": "demonstrating trillboards", "on_screen_text": "SECRET REVEALED"}},
            {{"t_start": 24.0, "t_end": 32.0, "speaker": "host", "line": "I'm making $X per week and my boss has no idea", "broll_cue": "counting money secretly", "on_screen_text": "RESULTS"}},
            {{"t_start": 32.0, "t_end": 40.0, "speaker": "host", "line": "Only works if you have access to screens - but if you do...", "broll_cue": "call to action", "on_screen_text": "YOUR TURN"}}
        ],
        "caption_overlay": [
            {{"t_start": 0.0, "t_end": 3.0, "text": "Made $XXX doing THIS at work", "emphasis_tokens": ["$XXX", "THIS"]}},
            {{"t_start": 3.0, "t_end": 8.0, "text": "They still don't know...", "emphasis_tokens": ["don't", "know"]}},
            {{"t_start": 8.0, "t_end": 16.0, "text": "Underground TV money method", "emphasis_tokens": ["Underground", "money"]}},
            {{"t_start": 16.0, "t_end": 24.0, "text": "Your boss won't tell you this", "emphasis_tokens": ["boss", "won't"]}},
            {{"t_start": 24.0, "t_end": 32.0, "text": "$XXX/week EXTRA income", "emphasis_tokens": ["$XXX/week", "EXTRA"]}},
            {{"t_start": 32.0, "t_end": 40.0, "text": "Works with ANY workplace TV", "emphasis_tokens": ["ANY", "workplace"}}
        ],
        "visual_cues": {{
            "primary": ["money counting", "secret phone usage", "TV screen transformations", "workplace settings"],
            "secondary": ["QR codes", "app interface", "cash/payments", "stealth operations"]
        }},
        "trillboards_touchpoints": [
            {{"moment": "The Reveal", "action": "Shows trillboards app secretly", "why_it_helps": "Monetizes dead screen time"}},
            {{"moment": "The Setup", "action": "QR code scan on workplace TV", "why_it_helps": "Takes 30 seconds to set up passive income"}},
            {{"moment": "The Results", "action": "Shows earnings dashboard", "why_it_helps": "Proof of concept with real numbers"}}
        ],
        "constraints_and_risks": ["Keep it legal but edgy", "Don't encourage actual rule-breaking", "Focus on unused/dead screen time"],
        "metrics_hypothesis": {{
            "hook_strength_guess": 9,
            "retention_spikes_at_sec": [1.0, 8.0, 24.0],
            "shareability_notes": "Controversial angle + specific money claims + FOMO"
        }},
        "variants": {{
            "alt_hooks": ["I made $XXX this month and my boss is clueless", "This side hustle only works if you have TV access", "Your workplace is sitting on money and doesn't know it"],
            "alt_pacing": ["money_first_method_second", "struggle_story_then_revelation", "controversy_then_proof"]
        }},
        "rights_and_clearance_notes": "Edgy but legal content - focus on legitimate unused screen monetization",
        "scene_breakdown": [
            {{
                "scene_number": 1,
                "duration_sec": 8,
                "scene_type": "text_to_video",
                "prompt_text": "Dramatic close-up of a person in dim workplace lighting, counting cash secretly with a shocked/excited expression, TV screen glowing in background",
                "continuity_notes": "Establish the underground/secret money-making vibe with dramatic lighting",
                "key_visual_elements": ["cash money", "workplace TV", "secretive atmosphere", "authentic person"],
                "camera_instruction": "Close-up handheld style, slight shake for authenticity",
                "lighting_notes": "Dim, dramatic lighting with TV glow"
            }},
            {{
                "scene_number": 2,
                "duration_sec": 8,
                "scene_type": "image_to_video",
                "prompt_text": "Continue from last frame. Person looks around cautiously then pulls out phone, starts opening trillboards app with sneaky movements",
                "continuity_notes": "Maintain secretive atmosphere and character",
                "key_visual_elements": ["phone usage", "cautious movements", "app interface"],
                "camera_instruction": "Over shoulder shot of phone screen",
                "lighting_notes": "Same dim lighting with phone screen glow"
            }},
            {{
                "scene_number": 3,
                "duration_sec": 8,
                "scene_type": "image_to_video", 
                "prompt_text": "Continue from last frame. TV screen transforms showing QR code, person scans it quickly while looking around to make sure nobody sees",
                "continuity_notes": "Build tension of secret operation",
                "key_visual_elements": ["QR code on TV", "scanning action", "stealth behavior"],
                "camera_instruction": "Quick cuts between phone and TV screen",
                "lighting_notes": "TV brightness illuminates face dramatically"
            }},
            {{
                "scene_number": 4,
                "duration_sec": 8,
                "scene_type": "image_to_video",
                "prompt_text": "Continue from last frame. Person sets up rotating ads on TV screen, content starts displaying, they step back with satisfied smile",
                "continuity_notes": "Show the method working",
                "key_visual_elements": ["TV displaying ads", "satisfied expression", "setup complete"],
                "camera_instruction": "Wide shot showing full TV and person",
                "lighting_notes": "Brighter as TV content illuminates space"
            }},
            {{
                "scene_number": 5,
                "duration_sec": 8,
                "scene_type": "image_to_video",
                "prompt_text": "Continue from last frame. Person checks earnings on phone app, shows growing numbers, then pockets money with a wink to camera",
                "continuity_notes": "Reveal the payoff and success",
                "key_visual_elements": ["earnings dashboard", "money/cash", "direct camera address"],
                "camera_instruction": "Close-up on phone then face for wink",
                "lighting_notes": "Phone screen brightness on face for reveal"
            }}
        ]
    }}
    
    CRITICAL: Make this VIRAL and PROVOCATIVE. Use specific dollar amounts ($247, $180, $60) that are believable but exciting.
    Focus on underground economy, rebellion against corporate systems, secret knowledge.
    Create FOMO around TV access - "only works if you have access to screens".
    Make it feel forbidden and exclusive while staying technically legal.
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

def generate_video_with_veo(blueprint, model_name="veo-3.0-generate-preview"):
    """Generate actual video using VEO-3 model with proper API"""
    
    # Create a detailed prompt for video generation from the blueprint
    script_text = " ".join([segment["line"] for segment in blueprint["script"]])
    visual_cues = ", ".join(blueprint["visual_cues"]["primary"])
    
    video_prompt = f"""
    Create a {blueprint["video_spec"]["duration_sec"]}-second vertical video (9:16 aspect ratio) featuring:
    
    Setting: {blueprint["avatar_style"]["setting"]}
    Character: {blueprint["avatar_style"]["persona"]} wearing {blueprint["avatar_style"]["wardrobe"]}
    
    Visual elements: {visual_cues}
    
    Action: {script_text}
    
    Style: Authentic, documentary-like, casual phone recording. Show real workplace scenarios with natural lighting.
    Camera: Vertical phone recording, jump cuts, close-ups on screens showing QR codes and digital displays.
    
    Make it look like an authentic side-hustle tutorial filmed by someone sharing their real experience.
    """
    
    # Negative prompt to avoid unwanted elements
    negative_prompt = "blurry, low quality, fake, staged, overly professional, studio lighting, brand logos, copyrighted material"
    
    try:
        print(f"🎬 Generating {blueprint['video_spec']['duration_sec']}-second video with VEO-3...")
        print(f"📝 Prompt: {video_prompt[:100]}...")
        
        client = genai_client.Client()
        
        # Generate video using VEO-3
        operation = client.models.generate_videos(
            model=model_name,
            prompt=video_prompt,
            config=types.GenerateVideosConfig(
                negative_prompt=negative_prompt,
            ),
        )
        
        print(f"🔄 Video generation started. Operation ID: {operation.name}")
        
        # Poll for completion
        max_wait_time = 600  # 10 minutes max wait
        poll_interval = 20   # Check every 20 seconds
        elapsed_time = 0
        
        while not operation.done and elapsed_time < max_wait_time:
            print(f"⏳ Generating video... ({elapsed_time}s elapsed)")
            time.sleep(poll_interval)
            elapsed_time += poll_interval
            operation = client.operations.get(operation)
        
        if not operation.done:
            print(f"⏰ Timeout after {max_wait_time}s. Video generation may still be processing.")
            return {"status": "timeout", "operation": operation}
        
        if operation.result and operation.result.generated_videos:
            generated_video = operation.result.generated_videos[0]
            print(f"✅ Video generated successfully!")
            
            # Save video file
            video_filename = f"{blueprint['id']}_video.mp4"
            video_path = GENERATED_DIR / video_filename
            
            # Download the video
            client.files.download(file=generated_video.video)
            generated_video.video.save(str(video_path))
            
            print(f"💾 Video saved: {video_path}")
            
            return {
                "status": "success",
                "video_path": video_path,
                "video_file": generated_video.video,
                "operation": operation
            }
        else:
            print("❌ No video generated in operation result")
            return {"status": "error", "message": "No video in result", "operation": operation}
        
    except Exception as e:
        print(f"❌ Error generating video with VEO: {e}")
        return {"status": "error", "message": str(e)}

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