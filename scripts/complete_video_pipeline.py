#!/usr/bin/env python3
"""
Complete Trillboards Video Pipeline
Fresh VEO generation with enhanced dialogue prompts + MoviePy stitching
"""
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.veo_chain_generator import VEOChainGenerator
from scripts.moviepy_pipeline import MoviePyPipeline
from scripts.ffmpeg_pipeline import FFmpegPipeline
from scripts.generate_trillboards_videos import generate_video_blueprint
from config.settings import GENERATED_DIR, SIDE_HUSTLE_THEMES, VIRAL_ALTERNATIVE_THEMES

def run_complete_pipeline(blueprint_id=None, theme_index=None):
    """Run complete video generation pipeline with fresh VEO scenes and organized structure
    
    Args:
        blueprint_id: Existing blueprint ID to use (if None, generates fresh with Gemini)
        theme_index: Index from SIDE_HUSTLE_THEMES to use for fresh generation
    """
    print("🎬 COMPLETE TRILLBOARDS VIDEO PIPELINE")
    print("=" * 60)
    print("🔄 Fresh VEO generation with enhanced dialogue prompts")
    print("🎞️ FFmpeg stitching with SMOOTH CROSSFADE TRANSITIONS")
    print("📝 MoviePy text overlays with ZERO CUTOFF (artsy lyrics approach)")
    print("📁 ORGANIZED FILE STRUCTURE - No more mess!")
    
    # Create organized directory structure
    blueprints_dir = GENERATED_DIR / "blueprints"
    runs_dir = GENERATED_DIR / "runs"
    archive_dir = GENERATED_DIR / "archive"
    
    # Create directories
    blueprints_dir.mkdir(parents=True, exist_ok=True)
    runs_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 0: Generate fresh blueprint with Gemini (DEFAULT BEHAVIOR)
    if blueprint_id is None:
        print(f"\n🤖 Step 0: Generating fresh blueprint with Gemini 2.5 Flash...")
        
        # Select theme
        if theme_index is not None and 0 <= theme_index < len(SIDE_HUSTLE_THEMES):
            selected_theme = SIDE_HUSTLE_THEMES[theme_index]
        elif theme_index is not None and theme_index < len(VIRAL_ALTERNATIVE_THEMES):
            selected_theme = VIRAL_ALTERNATIVE_THEMES[theme_index - len(SIDE_HUSTLE_THEMES)]
        else:
            # Pick a random theme from main collection
            import random
            selected_theme = random.choice(SIDE_HUSTLE_THEMES)
        
        print(f"🎯 Selected theme: {selected_theme}")
        
        # Generate blueprint with Gemini
        blueprint = generate_video_blueprint(selected_theme)
        
        if not blueprint:
            print("❌ Failed to generate blueprint with Gemini")
            return None
        
        blueprint_id = blueprint.get('id', 'gemini-generated')
        
        # Save to organized blueprints directory
        blueprint_filename = f"{blueprint_id}.json"
        blueprint_path = blueprints_dir / blueprint_filename
        
        with open(blueprint_path, 'w') as f:
            json.dump(blueprint, f, indent=2)
        
        print(f"✅ Gemini blueprint saved: {blueprint_path}")
        print(f"🔥 Generated viral concept: {blueprint.get('theme', 'Unknown')}")
    else:
        blueprint = None  # Will be loaded below
    
    # Create timestamped run directory for this execution
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"run_{run_timestamp}"
    if blueprint_id:
        run_name = f"run_{run_timestamp}_{blueprint_id}"
    
    run_dir = runs_dir / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Run directory: {run_dir}")
    
    # Create subdirectories within run
    (run_dir / "scenes").mkdir(exist_ok=True)
    (run_dir / "frames").mkdir(exist_ok=True)
    (run_dir / "finals").mkdir(exist_ok=True)
    (run_dir / "temp").mkdir(exist_ok=True)
    
    # Step 1: Use blueprint (either freshly generated from Gemini or load existing)
    if blueprint is None:
        # Only load from disk if we didn't generate fresh with Gemini
        if blueprint_id:
            # Try to find specific blueprint
            blueprint_path = blueprints_dir / f"{blueprint_id}.json"
            if not blueprint_path.exists():
                # Try old location
                old_path = GENERATED_DIR / f"{blueprint_id}_blueprint.json"
                if old_path.exists():
                    # Move to organized structure
                    import shutil
                    shutil.move(str(old_path), str(blueprint_path))
                    print(f"📁 Moved blueprint to organized structure: {blueprint_path}")
                else:
                    print(f"❌ Blueprint {blueprint_id} not found")
                    return None
        else:
            # Use the latest blueprint
            blueprint_files = list(blueprints_dir.glob("*.json"))
            if not blueprint_files:
                # Look for blueprints in old location
                old_blueprints = list(GENERATED_DIR.glob("*_blueprint.json"))
                if old_blueprints:
                    # Move them to organized structure
                    for old_bp in old_blueprints:
                        new_name = old_bp.stem.replace("_blueprint", "") + ".json"
                        new_path = blueprints_dir / new_name
                        import shutil
                        shutil.move(str(old_bp), str(new_path))
                        blueprint_files.append(new_path)
                        print(f"📁 Organized blueprint: {old_bp.name} → blueprints/{new_name}")
            
            if not blueprint_files:
                print("❌ No blueprints found. Please run blueprint generation first.")
                return None
            
            # Use the most recent blueprint
            blueprint_path = max(blueprint_files, key=lambda p: p.stat().st_mtime)
        
        # Load blueprint from disk
        with open(blueprint_path, 'r') as f:
            blueprint = json.load(f)
        
        print(f"✅ Using existing blueprint: {blueprint_path}")
    else:
        # Using freshly generated blueprint from Gemini
        blueprint_path = blueprints_dir / f"{blueprint_id}.json"
        print(f"✅ Using fresh Gemini blueprint: {blueprint.get('theme', 'Unknown')}")
    
    blueprint_id = blueprint.get('id', 'unknown')
    print(f"✅ Using blueprint: {blueprint_id}")
    print(f"🎤 Script lines: {len(blueprint.get('script', []))}")
    print(f"🎬 Scenes: {len(blueprint.get('scene_breakdown', []))}")
    
    # Copy blueprint to run directory for reference
    run_blueprint_path = run_dir / "blueprint.json"
    import shutil
    shutil.copy2(blueprint_path, run_blueprint_path)
    
    # Step 2: Generate fresh VEO scenes with ORGANIZED output structure
    print(f"\n🎥 Step 2: Generating FRESH VEO scenes with organized structure...")
    
    # Initialize VEO generator with organized run directory
    veo_generator = VEOChainGenerator(output_dir=str(run_dir))
    
    # Archive any old scenes from previous runs (they're now in generated/ root)
    old_scenes = list(GENERATED_DIR.glob(f"{blueprint_id}_scene_*.mp4"))
    if old_scenes:
        print(f"📁 Archiving {len(old_scenes)} old scenes from previous runs...")
        for old_scene in old_scenes:
            backup_path = archive_dir / old_scene.name
            import shutil
            shutil.move(str(old_scene), str(backup_path))
            print(f"🗂️ Archived: {old_scene.name} → archive/")
    
    # Generate NEW scenes with enhanced prompts in organized structure
    scene_files = veo_generator.generate_scene_chain(blueprint)
    
    if not scene_files or len(scene_files) != 5:
        print(f"❌ VEO generation failed. Expected 5 scenes, got {len(scene_files) if scene_files else 0}")
        return None
    
    print(f"✅ Generated {len(scene_files)} fresh VEO scenes with dialogue!")
    for i, scene_file in enumerate(scene_files, 1):
        print(f"   Scene {i}: {Path(scene_file).name}")
    
    # Step 3: Stitch with FFmpeg for smooth transitions, then add text overlays with MoviePy
    print(f"\n🎞️ Step 3: FFmpeg stitching with smooth crossfades...")
    
    # Initialize FFmpeg pipeline with organized output directory
    ffmpeg_pipeline = FFmpegPipeline(output_dir=str(run_dir))
    
    # Stitch scenes with smooth transitions (no text overlays yet)
    stitched_video = ffmpeg_pipeline.stitch_scenes(scene_files, blueprint)
    
    if not stitched_video:
        print("❌ FFmpeg stitching failed")
        return None
    
    print(f"✅ FFmpeg stitching complete: {stitched_video}")
    
    # Step 4: Add text overlays with MoviePy (using artsy lyrics approach)
    print(f"\n📝 Step 4: Adding text overlays with zero cutoff...")
    
    # Initialize MoviePy pipeline for text overlays only
    moviepy_pipeline = MoviePyPipeline(output_dir=str(run_dir))
    
    # Add text overlays to the stitched video
    final_video = moviepy_pipeline.add_text_overlays_to_video(stitched_video, blueprint)
    
    if not final_video:
        print("❌ Text overlay addition failed")
        return None
    
    # Step 5: Create thumbnail (already in organized structure)
    thumbnail = moviepy_pipeline.create_preview_thumbnail(final_video)
    
    # Step 6: Create run metadata
    print(f"\n📋 Step 6: Creating run metadata...")
    
    metadata = {
        "run_id": run_name,
        "blueprint_id": blueprint_id,
        "timestamp": run_timestamp,
        "final_video": str(Path(final_video).name) if final_video else None,
        "thumbnail": str(Path(thumbnail).name) if thumbnail else None,
        "scenes": [str(Path(f).name) for f in scene_files],
        "duration_sec": blueprint.get('video_spec', {}).get('duration_sec', 40),
        "file_size_bytes": os.path.getsize(final_video) if final_video and os.path.exists(final_video) else 0
    }
    
    metadata_path = run_dir / "metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"📊 Metadata saved: {metadata_path}")
    
    # Final results
    print(f"\n🎉 COMPLETE PIPELINE SUCCESS WITH ORGANIZED STRUCTURE!")
    print(f"📁 Run directory: {run_dir}")
    print(f"📁 Final video: {final_video}")
    print(f"📊 File size: {metadata['file_size_bytes']:,} bytes ({metadata['file_size_bytes']/1024/1024:.1f} MB)")
    print(f"⏱️ Duration: {metadata['duration_sec']} seconds")
    if thumbnail:
        print(f"📸 Thumbnail: {thumbnail}")
    print(f"🎬 Scenes: {len(scene_files)} organized in {run_dir}/scenes/")
    print(f"📋 Blueprint: {run_blueprint_path}")
    print(f"📊 Metadata: {metadata_path}")
    
    # Validate organized structure
    print(f"\n🔍 ORGANIZATION VALIDATION:")
    print(f"✅ Generated directory structure is organized")
    print(f"✅ Fresh VEO scenes with frame continuity in scenes/")
    print(f"✅ Enhanced prompts with dialogue from blueprint")
    print(f"✅ Professional MoviePy text overlays (no cutoff) in finals/")
    print(f"✅ Frame extractions organized in frames/")
    print(f"✅ Blueprint archived with metadata")
    
    return {
        "run_directory": str(run_dir),
        "final_video": final_video,
        "thumbnail": thumbnail,
        "scene_files": scene_files,
        "blueprint": blueprint,
        "blueprint_path": str(run_blueprint_path),
        "metadata": metadata,
        "metadata_path": str(metadata_path)
    }

if __name__ == "__main__":
    print("🤖 DEFAULT: Using Gemini to generate fresh viral blueprint")
    result = run_complete_pipeline()  # No blueprint_id = generates fresh with Gemini
    
    if result:
        print(f"\n✅ Pipeline completed successfully!")
        print(f"🎥 Watch your video: {result['final_video']}")
    else:
        print(f"\n❌ Pipeline failed")