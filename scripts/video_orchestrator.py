#!/usr/bin/env python3
"""
Trillboards Video Orchestrator
Complete end-to-end pipeline: Blueprint → VEO Scenes → FFmpeg Stitching
"""
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.generate_trillboards_videos import generate_video_blueprint, save_blueprint
from scripts.veo_chain_generator import VEOChainGenerator
from scripts.ffmpeg_pipeline import FFmpegPipeline
from config.settings import SIDE_HUSTLE_THEMES, GENERATED_DIR

class VideoOrchestrator:
    def __init__(self):
        """Initialize the complete video generation pipeline"""
        self.veo_generator = None  # Will initialize when needed
        self.ffmpeg_pipeline = FFmpegPipeline()
        
        print("🎬 Video Orchestrator initialized")
    
    def generate_complete_video(self, theme, test_mode=True):
        """Generate complete video from theme to final MP4"""
        print(f"\n🎯 Starting complete video generation")
        print(f"📋 Theme: {theme}")
        print(f"🧪 Test mode: {test_mode}")
        
        try:
            # Step 1: Generate blueprint with scene breakdown
            print(f"\n📝 Step 1: Generating blueprint...")
            blueprint = generate_video_blueprint(theme)
            
            if not blueprint:
                print("❌ Blueprint generation failed")
                return None
            
            blueprint_path = save_blueprint(blueprint, GENERATED_DIR)
            if not blueprint_path:
                print("❌ Blueprint save failed")
                return None
            
            print(f"✅ Blueprint generated: {blueprint['id']}")
            
            # Validate scene breakdown
            scenes = blueprint.get('scene_breakdown', [])
            if not scenes:
                print("❌ No scenes in blueprint")
                return None
            
            print(f"🎬 {len(scenes)} scenes planned")
            
            if test_mode:
                print("🧪 Test mode: Stopping after blueprint generation")
                return {
                    "status": "blueprint_only",
                    "blueprint": blueprint,
                    "blueprint_path": blueprint_path
                }
            
            # Step 2: Generate VEO 3 scene chain
            print(f"\n🎥 Step 2: Generating VEO 3 scenes...")
            
            if not self.veo_generator:
                self.veo_generator = VEOChainGenerator()
            
            scene_files = self.veo_generator.generate_scene_chain(blueprint)
            
            if not scene_files:
                print("❌ VEO scene generation failed")
                return None
            
            print(f"✅ {len(scene_files)} scenes generated")
            
            # Step 3: Stitch scenes with FFmpeg
            print(f"\n🎞️ Step 3: Stitching scenes...")
            
            final_video = self.ffmpeg_pipeline.stitch_scenes(
                scene_files, blueprint
            )
            
            if not final_video:
                print("❌ Video stitching failed")
                return None
            
            print(f"✅ Final video created: {final_video}")
            
            # Step 4: Create thumbnail
            thumbnail = self.ffmpeg_pipeline.create_preview_thumbnail(final_video)
            
            # Return complete result
            result = {
                "status": "complete",
                "blueprint": blueprint,
                "blueprint_path": blueprint_path,
                "scene_files": scene_files,
                "final_video": final_video,
                "thumbnail": thumbnail,
                "metadata": {
                    "theme": theme,
                    "duration_sec": sum(scene['duration_sec'] for scene in scenes),
                    "scene_count": len(scenes),
                    "generated_at": datetime.now().isoformat()
                }
            }
            
            print(f"\n🎉 Complete video generation successful!")
            print(f"📁 Final video: {final_video}")
            
            return result
            
        except Exception as e:
            print(f"❌ Orchestrator error: {e}")
            return None
    
    def batch_generate_videos(self, themes, test_mode=True, max_videos=3):
        """Generate multiple videos in batch"""
        print(f"\n🎬 Batch video generation")
        print(f"📋 {len(themes)} themes requested")
        print(f"🎯 Max videos: {max_videos}")
        
        results = []
        
        for i, theme in enumerate(themes[:max_videos], 1):
            print(f"\n{'='*60}")
            print(f"🎥 Video {i}/{min(len(themes), max_videos)}")
            
            result = self.generate_complete_video(theme, test_mode=test_mode)
            
            if result:
                results.append(result)
                print(f"✅ Video {i} completed")
            else:
                print(f"❌ Video {i} failed")
            
            # Small delay between generations
            if i < min(len(themes), max_videos):
                print("⏳ Brief pause...")
                time.sleep(2)
        
        print(f"\n🎉 Batch generation complete!")
        print(f"✅ Successful: {len(results)}/{min(len(themes), max_videos)}")
        
        return results
    
    def generate_single_test_video(self):
        """Generate one test video for validation"""
        test_theme = SIDE_HUSTLE_THEMES[0]  # Bar staff theme
        
        print(f"🧪 Generating single test video")
        print(f"📋 Theme: {test_theme}")
        
        # Generate complete video with all scenes
        result = self.generate_complete_video(test_theme, test_mode=False)
        
        if result and result['status'] == 'blueprint_only':
            print(f"\n✅ Test video blueprint generation successful!")
            print(f"📁 Blueprint: {result['blueprint_path']}")
            
            # Show scene breakdown
            scenes = result['blueprint'].get('scene_breakdown', [])
            print(f"\n🎬 Scene Preview:")
            for scene in scenes:
                print(f"  Scene {scene['scene_number']}: {scene['scene_type']} ({scene['duration_sec']}s)")
                print(f"    {scene['prompt_text'][:80]}...")
            
            total_duration = sum(scene['duration_sec'] for scene in scenes)
            print(f"\n📊 Total duration: {total_duration} seconds")
            
            return result
        else:
            print(f"❌ Test video generation failed")
            return None

def main():
    """Main execution"""
    print("🎬 Trillboards Video Generation Pipeline")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = VideoOrchestrator()
    
    # Generate single test video (blueprint only for now)
    result = orchestrator.generate_single_test_video()
    
    if result:
        print(f"\n🎯 Ready for full pipeline testing!")
        print(f"📝 Next steps:")
        print(f"   1. Review generated blueprint")
        print(f"   2. Enable VEO 3 generation (set test_mode=False)")
        print(f"   3. Test complete pipeline")
    else:
        print(f"\n❌ Pipeline setup needs fixes")

if __name__ == "__main__":
    main()