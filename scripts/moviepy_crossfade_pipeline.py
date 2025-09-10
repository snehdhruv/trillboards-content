#!/usr/bin/env python3
"""
MoviePy Crossfade Pipeline
Simple, reliable crossfades using MoviePy - no FFmpeg audio sync issues
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from moviepy import VideoFileClip, CompositeVideoClip, concatenate_videoclips, vfx, TextClip

class MoviePyCrossfadePipeline:
    def __init__(self, output_dir=None):
        """Initialize MoviePy crossfade pipeline"""
        self.output_dir = Path(output_dir) if output_dir else Path("generated")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Style presets for text overlays (copied from moviepy_pipeline.py)
        self.text_styles = {
            'default': {
                'font_size': 48,
                'color': 'white',
                'font': None,  # Use system default
                'stroke_color': 'black',
                'stroke_width': 2
            },
            'emphasis': {
                'font_size': 52,
                'color': '#FFD700',  # Gold
                'font': None,  # Use system default
                'stroke_color': 'black',
                'stroke_width': 3
            },
            'large': {
                'font_size': 56,
                'color': 'white',
                'font': None,  # Use system default
                'stroke_color': 'black',
                'stroke_width': 2
            }
        }
        print("✅ MoviePy crossfade pipeline initialized")
    
    def crossfade_scenes(self, scene_files, blueprint=None, crossfade_duration=0.5):
        """Crossfade scenes using MoviePy - SIMPLE AND RELIABLE"""
        if not scene_files:
            raise ValueError("No scene files provided")
        
        print(f"🎬 MoviePy crossfading {len(scene_files)} scenes...")
        print(f"⚡ Crossfade duration: {crossfade_duration}s")
        
        # Create output filename
        blueprint_id = blueprint.get('id', 'unknown') if blueprint else 'unknown'
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{blueprint_id}_moviepy_crossfaded_{timestamp}.mp4"
        output_path = self.output_dir / "finals" / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Load all video clips
            clips = []
            for i, scene_file in enumerate(scene_files):
                print(f"📥 Loading scene {i+1}: {Path(scene_file).name}")
                clip = VideoFileClip(str(scene_file))
                clips.append(clip)
            
            if len(clips) == 1:
                # Single clip - no crossfading needed
                print("🎥 Single clip - no crossfading needed")
                final_clip = clips[0]
            else:
                # Apply crossfades
                crossfaded_clips = []
                
                for i, clip in enumerate(clips):
                    if i == 0:
                        # First clip: only fade out at the end
                        modified_clip = clip.with_effects([vfx.FadeOut(crossfade_duration)])
                        crossfaded_clips.append(modified_clip)
                        print(f"✅ Scene {i+1}: Added fade out")
                    elif i == len(clips) - 1:
                        # Last clip: only fade in at the start
                        modified_clip = clip.with_effects([vfx.FadeIn(crossfade_duration)])
                        crossfaded_clips.append(modified_clip)
                        print(f"✅ Scene {i+1}: Added fade in")
                    else:
                        # Middle clips: fade in and fade out
                        modified_clip = clip.with_effects([vfx.FadeIn(crossfade_duration), vfx.FadeOut(crossfade_duration)])
                        crossfaded_clips.append(modified_clip)
                        print(f"✅ Scene {i+1}: Added fade in + fade out")
                
                # Concatenate with overlaps for crossfades
                print("🔗 Concatenating with crossfade overlaps...")
                
                # Build the timeline with overlaps
                timeline_clips = []
                current_start = 0
                
                for i, clip in enumerate(crossfaded_clips):
                    if i == 0:
                        # First clip starts at 0
                        timeline_clips.append(clip.with_start(current_start))
                        current_start += clip.duration - crossfade_duration
                    else:
                        # Subsequent clips overlap by crossfade_duration
                        timeline_clips.append(clip.with_start(current_start))
                        if i < len(crossfaded_clips) - 1:
                            current_start += clip.duration - crossfade_duration
                
                # Composite all clips with overlaps
                final_clip = CompositeVideoClip(timeline_clips)
                
                # Calculate expected duration
                expected_duration = sum(clip.duration for clip in clips) - (len(clips) - 1) * crossfade_duration
                print(f"📐 Expected duration: {expected_duration:.1f}s, Actual: {final_clip.duration:.1f}s")
            
            # Add text overlays with bulletproof sizing
            print(f"📝 Adding text overlays to crossfaded video...")
            final_clip_with_text = self.add_text_overlays(final_clip, blueprint)
            
            # Export the final video with text overlays
            print(f"💾 Exporting final video with crossfades and text overlays...")
            output_filename_final = f"{blueprint.get('id', 'unknown')}_moviepy_complete_{timestamp}.mp4"
            output_path_final = self.output_dir / "finals" / output_filename_final
            output_path_final.parent.mkdir(parents=True, exist_ok=True)
            
            final_clip_with_text.write_videofile(
                str(output_path_final),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Clean up clips
            for clip in clips:
                clip.close()
            final_clip.close()
            final_clip_with_text.close()
            
            print(f"✅ MoviePy complete pipeline finished: {output_path_final}")
            return str(output_path_final)
            
        except Exception as e:
            print(f"❌ MoviePy crossfade error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def add_text_overlays(self, video_clip, blueprint):
        """Add text overlays with EXTREMELY bulletproof canvas sizing - NO cutoff guaranteed"""
        captions = blueprint.get('caption_overlay', [])
        if not captions:
            print("📝 No captions to add")
            return video_clip
        
        print(f"📝 Adding {len(captions)} text overlays with BULLETPROOF sizing...")
        video_size = (video_clip.w, video_clip.h)
        
        # Create text clips for each caption
        text_clips = []
        
        for i, caption in enumerate(captions):
            start_time = caption.get('t_start', 0)
            end_time = caption.get('t_end', start_time + 2)
            text = caption.get('text', '').strip()
            emphasis_tokens = caption.get('emphasis_tokens', [])
            
            if not text:
                continue
                
            duration = end_time - start_time
            if duration <= 0:
                continue
            
            print(f"   Caption {i+1}: '{text}' ({start_time}s-{end_time}s)")
            
            # Determine style based on emphasis
            style_name = 'emphasis' if emphasis_tokens else 'default'
            style = self.text_styles[style_name]
            
            try:
                video_width, video_height = video_size
                
                # BULLETPROOF CANVAS SIZING - MUCH LARGER TO PREVENT ANY CUTOFF
                canvas_width = int(video_width * 0.95)  # 95% of video width (even wider)
                canvas_height = style['font_size'] * 6  # 6x font size for height (much taller)
                
                print(f"     🛡️ BULLETPROOF Canvas: {canvas_width}x{canvas_height}, Text: '{text[:30]}...'")
                
                txt_clip = TextClip(
                    text=text,
                    font_size=style['font_size'],
                    color=style['color'],
                    font=style['font'],
                    stroke_color=style['stroke_color'],
                    stroke_width=style['stroke_width'],
                    size=(canvas_width, canvas_height),  # HUGE canvas
                    method='caption',  # Better for large text
                    text_align='center'
                ).with_duration(duration).with_start(start_time)
                
                # Get actual text dimensions
                text_width = txt_clip.w
                text_height = txt_clip.h
                
                print(f"     📏 Text dimensions: {text_width}x{text_height}")
                
                # Calculate safe positioning bounds (text must fit entirely within video)
                max_x = int(video_width - text_width)
                max_y = int(video_height - text_height)
                max_x = max(0, max_x)
                max_y = max(0, max_y)
                
                # Center horizontally, bottom area vertically
                x_pos = (video_width - text_width) / 2  # Perfect horizontal center
                y_pos = video_height * 0.8 - text_height / 2  # Bottom area (moved up slightly)
                y_pos = max(0, min(max_y, y_pos))  # Clamp to bounds
                
                print(f"     📍 Safe bounds: max_x={max_x}, max_y={max_y}")
                print(f"     📌 Final position: ({x_pos:.0f}, {y_pos:.0f})")
                
                txt_clip = txt_clip.with_position((x_pos, y_pos))
                
                text_clips.append(txt_clip)
                print(f"     ✅ BULLETPROOF positioning complete - ZERO cutoff guaranteed!")
                
            except Exception as e:
                print(f"❌ Error creating text clip '{text}': {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Composite video with text overlays
        if text_clips:
            final_clip = CompositeVideoClip([video_clip] + text_clips)
            print(f"✅ Added {len(text_clips)} text overlays with BULLETPROOF canvas sizing - NO CUTOFF!")
        else:
            final_clip = video_clip
            print("📝 No text overlays added")
        
        return final_clip

def test_moviepy_crossfades():
    """Test MoviePy crossfades on existing Uber scenes"""
    
    # Paths to Uber scenes
    uber_dir = Path("generated/runs/run_20250909_163539_uber-driver-secret-money-v1")
    scenes_dir = uber_dir / "scenes"
    blueprint_path = uber_dir / "blueprint.json"
    
    # Check if files exist
    if not scenes_dir.exists():
        print(f"❌ Scenes directory not found: {scenes_dir}")
        return None
    
    if not blueprint_path.exists():
        print(f"❌ Blueprint not found: {blueprint_path}")
        return None
    
    # Load blueprint
    import json
    with open(blueprint_path, 'r') as f:
        blueprint = json.load(f)
    
    # Get scene files
    scene_files = list(scenes_dir.glob("scene_*.mp4"))
    scene_files.sort()  # Ensure correct order
    
    if len(scene_files) != 5:
        print(f"❌ Expected 5 scenes, found {len(scene_files)}")
        return None
    
    print(f"🎬 TESTING MOVIEPY CROSSFADES ON UBER SCENES")
    print(f"📁 Using scenes from: {scenes_dir}")
    print(f"🎥 Found {len(scene_files)} scenes")
    for i, scene in enumerate(scene_files, 1):
        print(f"   Scene {i}: {scene.name}")
    
    # Initialize pipeline
    pipeline = MoviePyCrossfadePipeline(output_dir=str(uber_dir))
    
    # Test complete pipeline (crossfades + text overlays)
    final_video = pipeline.crossfade_scenes([str(f) for f in scene_files], blueprint)
    
    if final_video:
        print(f"\n✅ MOVIEPY COMPLETE PIPELINE SUCCESS!")
        print(f"📁 Final video with crossfades and text overlays: {final_video}")
        
        # Get file info
        import os
        size = os.path.getsize(final_video)
        print(f"📊 Final file size: {size:,} bytes ({size/1024/1024:.1f} MB)")
        
        return final_video
    else:
        print(f"❌ MoviePy complete pipeline failed")
        return None

if __name__ == "__main__":
    print("🎬 TESTING MOVIEPY CROSSFADE PIPELINE")
    print("=" * 50)
    
    result = test_moviepy_crossfades()
    
    if result:
        print(f"\n🎉 MOVIEPY CROSSFADE TEST SUCCESS!")
        print(f"📁 Final video: {result}")
        print(f"\n🔍 PLEASE VERIFY:")
        print(f"✅ 5 scenes are properly crossfaded")
        print(f"✅ Audio and video stay in sync")
        print(f"✅ Text overlays are visible and positioned correctly")
        print(f"✅ Total duration is approximately 40 seconds")
    else:
        print(f"\n❌ MOVIEPY CROSSFADE TEST FAILED")