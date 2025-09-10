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

from moviepy import VideoFileClip, CompositeVideoClip, concatenate_videoclips, vfx

class MoviePyCrossfadePipeline:
    def __init__(self, output_dir=None):
        """Initialize MoviePy crossfade pipeline"""
        self.output_dir = Path(output_dir) if output_dir else Path("generated")
        self.output_dir.mkdir(parents=True, exist_ok=True)
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
            
            # Export the final video
            print(f"💾 Exporting crossfaded video to: {output_filename}")
            final_clip.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Clean up clips
            for clip in clips:
                clip.close()
            final_clip.close()
            
            print(f"✅ MoviePy crossfade complete: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ MoviePy crossfade error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def add_text_overlays(self, video_path, blueprint):
        """Add text overlays to crossfaded video"""
        from scripts.moviepy_pipeline import MoviePyPipeline
        
        print("📝 Adding text overlays to crossfaded video...")
        moviepy_pipeline = MoviePyPipeline(output_dir=str(self.output_dir))
        return moviepy_pipeline.add_text_overlays_to_video(video_path, blueprint)

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
    
    # Test crossfades
    crossfaded_video = pipeline.crossfade_scenes([str(f) for f in scene_files], blueprint)
    
    if crossfaded_video:
        print(f"\n✅ MOVIEPY CROSSFADE SUCCESS!")
        print(f"📁 Crossfaded video: {crossfaded_video}")
        
        # Add text overlays
        final_video = pipeline.add_text_overlays(crossfaded_video, blueprint)
        
        if final_video:
            print(f"✅ Text overlays added: {final_video}")
            
            # Get file info
            import os
            size = os.path.getsize(final_video)
            print(f"📊 Final file size: {size:,} bytes ({size/1024/1024:.1f} MB)")
            
            return final_video
        else:
            print(f"❌ Text overlay failed")
            return crossfaded_video
    else:
        print(f"❌ MoviePy crossfade failed")
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