#!/usr/bin/env python3
"""
FFmpeg Video Stitching Pipeline
Seamlessly combines VEO 3 scene files into final video
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import GENERATED_DIR

class FFmpegPipeline:
    def __init__(self, output_dir=None):
        """Initialize FFmpeg pipeline"""
        self.output_dir = Path(output_dir) if output_dir else GENERATED_DIR
        self.temp_dir = self.output_dir / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if FFmpeg is available
        if not self._check_ffmpeg():
            raise RuntimeError("FFmpeg not found. Install with: brew install ffmpeg")
        
        print("✅ FFmpeg pipeline initialized")
    
    def _check_ffmpeg(self):
        """Check if FFmpeg is installed"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def stitch_scenes(self, scene_files, blueprint, output_filename=None):
        """Stitch multiple scene files - SIMPLE CONCATENATION (no crossfades)"""
        if not scene_files:
            raise ValueError("No scene files provided")
        
        blueprint_id = blueprint.get('id', 'unknown')
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{blueprint_id}_concat_{timestamp}.mp4"
        
        output_path = self.output_dir / "finals" / output_filename
        # Ensure finals directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"🎬 Stitching {len(scene_files)} scenes with SIMPLE CONCATENATION")
        print(f"📁 Output: {output_filename}")
        
        try:
            if len(scene_files) == 1:
                # Single file - just copy it (no stitching needed)
                import shutil
                shutil.copy2(scene_files[0], output_path)
                return str(output_path)
            
            # Simple concatenation - RELIABLE
            return self._simple_concat_only(scene_files, output_path)
                
        except Exception as e:
            print(f"❌ Stitching error: {e}")
            return None
    
    def _stitch_with_crossfades_only(self, scene_files, output_path, blueprint):
        """Proper crossfade stitching with synchronized audio and video transitions"""
        print(f"🎨 Creating synchronized audio/video crossfades...")
        
        # Normalize all videos first (frame rate, color, resolution)
        normalized_files = self._normalize_videos(scene_files)
        if not normalized_files:
            print("❌ Video normalization failed")
            return None
        
        # Build complex filter graph for synchronized crossfades
        filter_parts = []
        input_args = []
        
        # Add all input files
        for i, file in enumerate(normalized_files):
            input_args.extend(['-i', str(file)])
        
        # Build crossfade parameters
        crossfade_duration = 0.5  # 0.5 second crossfades
        scene_duration = 8.0  # Each VEO scene is 8 seconds
        
        if len(normalized_files) == 2:
            # Simple case: 2 videos with synchronized audio/video crossfade
            offset = scene_duration - crossfade_duration  # 7.5s
            filter_parts.append(f"[0:v][1:v]xfade=transition=fade:duration={crossfade_duration}:offset={offset}[v]")
            filter_parts.append(f"[0:a][1:a]acrossfade=d={crossfade_duration}:c1=tri:c2=tri[a]")
        else:
            # Multiple videos: Build synchronized crossfade chains
            # CRITICAL: Both video and audio must use SAME timing calculations
            
            # Calculate total duration accounting for overlaps
            total_duration = len(normalized_files) * scene_duration - (len(normalized_files) - 1) * crossfade_duration
            print(f"📐 Total final duration: {total_duration}s (5 scenes, {len(normalized_files)-1} crossfades)")
            
            # Build video crossfade chain
            current_video_label = "0:v"
            
            for i in range(1, len(normalized_files)):
                next_video_input = f"{i}:v"
                video_output_label = f"v{i}" if i < len(normalized_files) - 1 else "v"
                
                # Calculate when this crossfade should start within the CURRENT video
                # Each video is 8s, crossfade starts at 7.5s mark of current video
                offset_in_current_video = scene_duration - crossfade_duration  # 7.5s
                
                print(f"🎬 Video crossfade {i}: starts at {offset_in_current_video}s in current video, duration={crossfade_duration}s")
                filter_parts.append(f"[{current_video_label}][{next_video_input}]xfade=transition=fade:duration={crossfade_duration}:offset={offset_in_current_video}[{video_output_label}]")
                current_video_label = video_output_label
            
            # Build audio crossfade chain with IDENTICAL timing as video
            current_audio_label = "0:a"
            
            for i in range(1, len(normalized_files)):
                next_audio_input = f"{i}:a"
                audio_output_label = f"a{i}" if i < len(normalized_files) - 1 else "a"
                
                # CRITICAL: Use IDENTICAL duration and timing as video crossfades
                print(f"🎵 Audio crossfade {i}: duration={crossfade_duration}s (synchronized with video)")
                filter_parts.append(f"[{current_audio_label}][{next_audio_input}]acrossfade=d={crossfade_duration}:c1=tri:c2=tri[{audio_output_label}]")
                current_audio_label = audio_output_label
        
        # Combine all filter parts
        filter_complex = ';'.join(filter_parts)
        
        # Build final command
        cmd = [
            'ffmpeg', '-y'
        ] + input_args + [
            '-filter_complex', filter_complex,
            '-map', '[v]',
            '-map', '[a]',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-pix_fmt', 'yuv420p',
            '-preset', 'fast',
            '-crf', '18',  # High quality
            str(output_path)
        ]
        
        print(f"🔧 Running advanced FFmpeg with crossfades...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Smooth transitions complete: {output_path}")
            
            # Cleanup normalized files
            self._cleanup_temp_files(normalized_files)
            
            return str(output_path)
        else:
            print(f"❌ Crossfade stitching error: {result.stderr}")
            # Fallback to basic concat
            return self._fallback_basic_concat(scene_files, output_path)
    
    def _normalize_videos(self, scene_files):
        """Normalize frame rate, resolution, and color space"""
        normalized_files = []
        
        print(f"🔧 Normalizing {len(scene_files)} videos...")
        
        for i, scene_file in enumerate(scene_files):
            normalized_path = self.temp_dir / f"normalized_{i}.mp4"
            
            cmd = [
                'ffmpeg', '-y',
                '-i', str(scene_file),
                '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black',
                '-r', '24',  # Standardize to 24fps
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-pix_fmt', 'yuv420p',
                str(normalized_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                normalized_files.append(normalized_path)
                print(f"✅ Normalized scene {i+1}")
            else:
                print(f"❌ Failed to normalize scene {i+1}: {result.stderr}")
                return None
        
        return normalized_files
    
    def _fallback_basic_concat(self, scene_files, output_path):
        """Fallback to basic concatenation if crossfades fail"""
        print(f"🔄 Falling back to basic concatenation...")
        
        filelist_path = self._create_concat_file(scene_files)
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(filelist_path),
            '-c', 'copy',
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Basic fallback complete: {output_path}")
            self._cleanup_temp_files([filelist_path])
            return str(output_path)
        else:
            print(f"❌ Fallback also failed: {result.stderr}")
            return None
    
    def _create_concat_file(self, scene_files):
        """Create FFmpeg concat file list"""
        filelist_path = self.temp_dir / "scenes_concat.txt"
        
        with open(filelist_path, 'w') as f:
            for scene_file in scene_files:
                # Convert GCS paths to local paths if needed
                local_path = self._ensure_local_file(scene_file)
                f.write(f"file '{local_path}'\n")
        
        print(f"📝 Created concat file: {filelist_path}")
        return filelist_path
    
    def _ensure_local_file(self, file_path):
        """Ensure file is available locally (download from GCS if needed)"""
        if str(file_path).startswith('gs://'):
            # TODO: Download from Google Cloud Storage
            print(f"📥 Would download: {file_path}")
            # For now, return a placeholder local path
            return f"./temp/{Path(file_path).name}"
        return file_path
    
    
    def _cleanup_temp_files(self, temp_files):
        """Clean up temporary files"""
        for temp_file in temp_files:
            try:
                Path(temp_file).unlink(missing_ok=True)
                print(f"🗑️ Cleaned up: {temp_file}")
            except Exception as e:
                print(f"⚠️ Cleanup error: {e}")
    
    def create_preview_thumbnail(self, video_path):
        """Create thumbnail preview of final video"""
        thumbnail_path = Path(video_path).with_suffix('.jpg')
        
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-ss', '00:00:05',  # Take frame at 5 seconds
            '-frames:v', '1',
            str(thumbnail_path)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"📸 Thumbnail created: {thumbnail_path}")
                return thumbnail_path
        except Exception as e:
            print(f"⚠️ Thumbnail error: {e}")
        
        return None

def test_ffmpeg_pipeline():
    """Test FFmpeg pipeline with mock scene files"""
    try:
        # Create mock scene files for testing
        mock_scenes = [
            "/path/to/scene_01.mp4",
            "/path/to/scene_02.mp4", 
            "/path/to/scene_03.mp4"
        ]
        
        # Create mock blueprint
        mock_blueprint = {
            "id": "test-video",
            "caption_overlay": [
                {"t_start": 2.0, "t_end": 5.0, "text": "Test Caption 1"},
                {"t_start": 10.0, "t_end": 13.0, "text": "Test Caption 2"}
            ]
        }
        
        # Initialize pipeline
        pipeline = FFmpegPipeline()
        
        print("✅ FFmpeg pipeline test setup complete")
        print("⚠️ Mock scene files - actual stitching needs real video files")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing FFmpeg Pipeline")
    print("=" * 50)
    
    success = test_ffmpeg_pipeline()
    
    if success:
        print("\n✅ FFmpeg pipeline test passed!")
    else:
        print("\n❌ FFmpeg pipeline test failed")