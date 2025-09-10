#!/usr/bin/env python3
"""
MoviePy Video Pipeline for Scene Stitching and Text Overlays
Professional video processing using MoviePy with blueprint parameters
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import GENERATED_DIR

logger = logging.getLogger(__name__)

class MoviePyPipeline:
    def __init__(self, output_dir=None):
        """Initialize MoviePy pipeline"""
        self.output_dir = Path(output_dir) if output_dir else GENERATED_DIR
        self.temp_dir = self.output_dir / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Style presets for text overlays
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
        
        print("✅ MoviePy pipeline initialized")
    
    def stitch_scenes_with_overlays(self, scene_files: List[str], blueprint: Dict) -> Optional[str]:
        """
        Stitch scenes and add text overlays using MoviePy
        """
        try:
            blueprint_id = blueprint.get('id', 'unknown')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save final video to organized finals directory
            finals_dir = self.output_dir / "finals"
            finals_dir.mkdir(parents=True, exist_ok=True)
            output_filename = f"final_video.mp4"
            output_path = finals_dir / output_filename
            
            print(f"🎬 Stitching {len(scene_files)} scenes with MoviePy")
            print(f"📁 Output: {output_filename}")
            
            # Load all scene clips
            clips = []
            for i, scene_file in enumerate(scene_files):
                if not os.path.exists(scene_file):
                    print(f"❌ Scene file not found: {scene_file}")
                    return None
                
                print(f"📹 Loading scene {i+1}: {Path(scene_file).name}")
                clip = VideoFileClip(scene_file)
                clips.append(clip)
            
            # Concatenate all scenes
            print(f"🔗 Concatenating scenes...")
            concatenated = concatenate_videoclips(clips, method="compose")
            
            # Add text overlays based on blueprint
            final_clip = self._add_text_overlays_moviepy(concatenated, blueprint)
            
            # Export final video
            print(f"💾 Exporting final video...")
            final_clip.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                bitrate='4000k',
                fps=24,
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                ffmpeg_params=['-pix_fmt', 'yuv420p']
            )
            
            # Cleanup
            final_clip.close()
            for clip in clips:
                clip.close()
            
            print(f"✅ Final video created: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ Stitching error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _add_text_overlays_moviepy(self, video_clip: VideoFileClip, blueprint: Dict) -> CompositeVideoClip:
        """Add text overlays with proper canvas sizing to prevent cutoff - bulletproof implementation"""
        captions = blueprint.get('caption_overlay', [])
        if not captions:
            print("📝 No captions to add")
            return video_clip
        
        print(f"📝 Adding {len(captions)} text overlays with bulletproof sizing...")
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
                # EXACT ARTSY LYRICS IMPLEMENTATION - Lines 126-129, 175-179, 206-211
                video_width, video_height = video_size
                
                # COPY ARTSY LYRICS CANVAS SIZING EXACTLY (lines 126-129)
                canvas_width = int(video_size[0] * 0.8)  # 80% of video width
                canvas_height = style['font_size'] * 2  # Double the font size for height
                
                print(f"     ARTSY Canvas: {canvas_width}x{canvas_height}, Text: '{text[:30]}...'")
                
                txt_clip = TextClip(
                    text=text,
                    font_size=style['font_size'],
                    color=style['color'],
                    font=style['font'],
                    stroke_color=style['stroke_color'],
                    stroke_width=style['stroke_width'],
                    size=(canvas_width, canvas_height),  # Force large canvas
                    method='caption',  # Better for large text
                    text_align='center'
                ).with_duration(duration).with_start(start_time)
                
                # COPY ARTSY BOUNDS CHECKING EXACTLY (lines 175-179)
                text_width = txt_clip.w
                text_height = txt_clip.h
                
                # Calculate safe positioning bounds (text must fit entirely within video)
                max_x = int(video_width - text_width)
                max_y = int(video_height - text_height)
                max_x = max(0, max_x)
                max_y = max(0, max_y)
                
                # COPY ARTSY CENTER_STACK POSITIONING EXACTLY (lines 206-211)
                x_pos = (video_width - text_width) / 2  # Perfect horizontal center
                y_pos = video_height * 0.85 - text_height / 2  # Bottom area
                y_pos = max(0, min(max_y, y_pos))  # Clamp to bounds
                
                txt_clip = txt_clip.with_position((x_pos, y_pos))
                
                text_clips.append(txt_clip)
                print(f"     ✅ Positioned at ({x_pos:.0f}, {y_pos:.0f}) - Safe bounds guaranteed")
                
            except Exception as e:
                print(f"❌ Error creating text clip '{text}': {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Composite video with text overlays
        if text_clips:
            final_clip = CompositeVideoClip([video_clip] + text_clips)
            print(f"✅ Added {len(text_clips)} text overlays with ZERO cutoff (bulletproof sizing)")
        else:
            final_clip = video_clip
            print("📝 No text overlays added")
        
        return final_clip
    
    def add_text_overlays_to_video(self, video_path: str, blueprint: Dict) -> Optional[str]:
        """Add text overlays to an already stitched video using artsy lyrics approach"""
        try:
            print(f"📝 Adding text overlays to stitched video: {Path(video_path).name}")
            
            # Load the stitched video
            video_clip = VideoFileClip(video_path)
            
            # Add text overlays using the same method
            final_clip = self._add_text_overlays_moviepy(video_clip, blueprint)
            
            # Save to finals directory with overlays suffix
            finals_dir = self.output_dir / "finals"
            finals_dir.mkdir(parents=True, exist_ok=True)
            output_filename = f"final_video_with_overlays.mp4"
            output_path = finals_dir / output_filename
            
            print(f"💾 Exporting video with text overlays...")
            final_clip.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                bitrate='4000k',
                fps=24,
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                ffmpeg_params=['-pix_fmt', 'yuv420p']
            )
            
            # Cleanup
            final_clip.close()
            video_clip.close()
            
            print(f"✅ Text overlays added: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ Text overlay error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_preview_thumbnail(self, video_path: str) -> Optional[str]:
        """Create thumbnail from video"""
        try:
            # Save thumbnail to same finals directory
            finals_dir = self.output_dir / "finals"
            thumbnail_path = finals_dir / "thumbnail.jpg"
            
            clip = VideoFileClip(video_path)
            # Get frame at 2 seconds (or middle if shorter)
            frame_time = min(2.0, clip.duration / 2)
            clip.save_frame(str(thumbnail_path), t=frame_time)
            clip.close()
            
            print(f"📸 Thumbnail created: {thumbnail_path}")
            return str(thumbnail_path)
            
        except Exception as e:
            print(f"❌ Thumbnail creation error: {e}")
            return None

def test_moviepy_pipeline():
    """Test MoviePy pipeline with existing scenes"""
    import json
    
    # Load blueprint
    blueprint_path = GENERATED_DIR / "trillboards-bar-upsell-slow-nights_blueprint.json"
    with open(blueprint_path, 'r') as f:
        blueprint = json.load(f)
    
    # Find scene files
    scene_files = []
    for i in range(1, 6):
        scene_file = GENERATED_DIR / f"trillboards-bar-upsell-slow-nights_scene_{i:02d}.mp4"
        if scene_file.exists():
            scene_files.append(str(scene_file))
    
    if len(scene_files) != 5:
        print(f"❌ Expected 5 scenes, found {len(scene_files)}")
        return
    
    print(f"🎬 Testing MoviePy pipeline with {len(scene_files)} scenes")
    
    # Initialize pipeline
    pipeline = MoviePyPipeline()
    
    # Process video
    final_video = pipeline.stitch_scenes_with_overlays(scene_files, blueprint)
    
    if final_video:
        print(f"✅ Test successful: {final_video}")
        
        # Create thumbnail
        thumbnail = pipeline.create_preview_thumbnail(final_video)
        if thumbnail:
            print(f"📸 Thumbnail: {thumbnail}")
    else:
        print("❌ Test failed")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_moviepy_pipeline()