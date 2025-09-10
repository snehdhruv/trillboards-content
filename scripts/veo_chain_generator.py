#!/usr/bin/env python3
"""
VEO 3 Chain Generation System
Generates multiple 8-second scenes with proper continuity
"""
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
import requests
from google.cloud import storage

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import GOOGLE_CLOUD_PROJECT, GENERATED_DIR

class VEOChainGenerator:
    def __init__(self, project_id="trillboard-new", location="us-central1", output_dir=None):
        """Initialize VEO 3 chain generator"""
        self.project_id = project_id
        self.location = location
        self.bucket_name = f"{project_id}-trillboards-scenes"
        self.output_dir = Path(output_dir) if output_dir else GENERATED_DIR
        
        # VEO 3 API endpoints (correct format from documentation)
        self.predict_endpoint = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/veo-3.0-generate-001:predictLongRunning"
        self.poll_endpoint = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/veo-3.0-generate-001:fetchPredictOperation"
        
        # Initialize Cloud Storage
        self.storage_client = storage.Client(project=project_id)
        self._ensure_bucket_exists()
        
        print(f"✅ VEO Chain Generator initialized")
        print(f"📦 Using bucket: {self.bucket_name}")
        print(f"🎥 Using VEO 3 via REST API (official format)")
    
    def _build_complete_prompt(self, scene, blueprint):
        """Combine visual description with script dialogue for complete VEO prompt"""
        if not blueprint:
            return None
            
        scene_start = scene.get('scene_number', 1) - 1  # Convert to 0-based index
        scene_duration = scene.get('duration_sec', 8)
        
        # Calculate time window for this scene
        scene_end_time = sum(s['duration_sec'] for s in blueprint['scene_breakdown'][:scene_start+1])
        scene_start_time = scene_end_time - scene_duration
        
        # Find matching script lines for this time window
        script_lines = []
        for script_item in blueprint.get('script', []):
            if (script_item['t_start'] >= scene_start_time and 
                script_item['t_start'] < scene_end_time):
                script_lines.append(script_item)
        
        if not script_lines:
            return None
        
        # Build enhanced prompt combining visual and dialogue
        visual_prompt = scene['prompt_text']
        
        # Add dialogue context
        dialogue_parts = []
        for script_item in script_lines:
            speaker = script_item.get('speaker', 'host')
            line = script_item.get('line', '')
            broll_cue = script_item.get('broll_cue', '')
            
            dialogue_parts.append(f"The {speaker} says: \"{line}\" while {broll_cue.lower()}")
        
        if dialogue_parts:
            enhanced_prompt = f"{visual_prompt} {' '.join(dialogue_parts)} The video should show the person speaking these words naturally with appropriate facial expressions and body language."
            return enhanced_prompt
        
        return None
    
    def _ensure_bucket_exists(self):
        """Create storage bucket if it doesn't exist"""
        try:
            self.bucket = self.storage_client.bucket(self.bucket_name)
            # Try to get bucket info to check if it exists
            self.bucket.reload()
            print(f"✅ Bucket {self.bucket_name} exists")
        except Exception as e:
            print(f"🔧 Creating bucket {self.bucket_name}...")
            self.bucket = self.storage_client.create_bucket(
                self.bucket_name,
                location="US-CENTRAL1"  # Must be consistent with Vertex AI location
            )
            print(f"✅ Bucket created: {self.bucket_name}")
    
    def generate_scene_chain(self, blueprint):
        """Generate a chain of connected VEO 3 scenes"""
        scenes = blueprint.get('scene_breakdown', [])
        if not scenes:
            raise ValueError("Blueprint missing scene_breakdown")
        
        blueprint_id = blueprint.get('id', 'unknown')
        scene_files = []
        
        print(f"🎬 Starting chain generation for {blueprint_id}")
        print(f"📋 {len(scenes)} scenes to generate")
        print(f"🎤 Integrating script dialogue from {len(blueprint.get('script', []))} script lines")
        
        previous_frame = None
        
        for i, scene in enumerate(scenes, 1):
            print(f"\n🎥 Generating Scene {i}/{len(scenes)}")
            print(f"   Type: {scene['scene_type']}")
            print(f"   Duration: {scene['duration_sec']}s")
            print(f"   Prompt: {scene['prompt_text'][:80]}...")
            
            try:
                # RELIABILITY FIX: Add retry logic for VEO API failures
                max_retries = 3
                retry_count = 0
                scene_file = None
                
                while retry_count <= max_retries and not scene_file:
                    if retry_count > 0:
                        print(f"🔄 RETRY {retry_count}/{max_retries} for Scene {i}")
                        time.sleep(30)  # Wait 30 seconds before retry
                    
                    scene_file = self._generate_single_scene(
                        scene=scene,
                        blueprint_id=blueprint_id,
                        previous_frame=previous_frame,
                        blueprint=blueprint
                    )
                    
                    if not scene_file:
                        retry_count += 1
                        if retry_count <= max_retries:
                            print(f"⚠️ Scene {i} failed, retrying in 30 seconds...")
                
                if scene_file:
                    scene_files.append(scene_file)
                    print(f"✅ Scene {i} generated: {scene_file}")
                    
                    # Extract last frame for next scene
                    if i < len(scenes):  # Not the last scene
                        previous_frame = self._extract_last_frame(scene_file)
                        if previous_frame and isinstance(previous_frame, dict):
                            print(f"🖼️ Last frame extracted for Scene {i+1}")
                        else:
                            print(f"⚠️ Frame extraction failed for Scene {i}")
                            previous_frame = None
                else:
                    print(f"❌ CRITICAL: Failed to generate Scene {i} after {max_retries} retries")
                    print(f"❌ PIPELINE RELIABILITY FAILURE - Cannot generate hundreds of videos")
                    return None
                    
            except Exception as e:
                print(f"❌ Error generating Scene {i}: {e}")
                return None
        
        print(f"\n🎉 Chain generation complete!")
        print(f"📁 Generated {len(scene_files)} scene files")
        
        return scene_files
    
    def _generate_single_scene(self, scene, blueprint_id, previous_frame=None, blueprint=None):
        """Generate a single VEO 3 scene and wait for completion"""
        try:
            scene_type = scene['scene_type']
            base_prompt = scene['prompt_text']
            duration = min(scene.get('duration_sec', 8), 8)  # VEO 3 max is 8 seconds
            
            # Integrate script dialogue with visual prompt
            prompt = self._build_complete_prompt(scene, blueprint)
            if not prompt:
                prompt = base_prompt  # Fallback to visual-only prompt
            
            print(f"📝 Generating {scene_type} scene...")
            print(f"🎬 Prompt: {prompt[:80]}...")
            print(f"⏱️ Duration: {duration}s")
            
            # Get OAuth token
            token = os.popen('gcloud auth application-default print-access-token').read().strip()
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json; charset=utf-8'
            }
            
            # Build VEO 3 request payload (exact format from documentation)
            instance_data = {"prompt": prompt}
            
            # Add image data if previous frame is provided
            if previous_frame and isinstance(previous_frame, dict):
                instance_data["image"] = {
                    "bytesBase64Encoded": previous_frame['base64_data'],
                    "mimeType": previous_frame['mime_type']
                }
                print(f"🖼️ Using previous frame for continuity")
            
            data = {
                "instances": [instance_data],
                "parameters": {
                    "aspectRatio": "9:16",
                    "durationSeconds": duration,
                    "sampleCount": 1,
                    "personGeneration": "allow_adult",
                    "storageUri": f"gs://{self.bucket_name}/scenes/"
                }
            }
            
            print(f"🚀 Starting VEO 3 generation...")
            response = requests.post(self.predict_endpoint, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                operation_data = response.json()
                operation_name = operation_data.get('name')
                
                print(f"✅ Operation started: {operation_name}")
                print(f"⏳ Polling for completion (this takes 3-5 minutes)...")
                
                # Poll until completion using fetchPredictOperation
                video_gcs_uri = self._poll_operation_completion(operation_name, token)
                
                if video_gcs_uri:
                    # Download the video to organized scenes directory
                    scene_filename = f"scene_{scene['scene_number']:02d}.mp4"
                    scenes_dir = self.output_dir / "scenes"
                    scenes_dir.mkdir(parents=True, exist_ok=True)
                    local_path = scenes_dir / scene_filename
                    
                    if self._download_from_gcs(video_gcs_uri, local_path):
                        print(f"✅ Video downloaded: {local_path}")
                        return str(local_path)
                    else:
                        print(f"❌ Failed to download video")
                        return None
                else:
                    print(f"❌ Video generation failed or timed out")
                    return None
                
            else:
                print(f"❌ VEO API error: {response.status_code}")
                print(f"📋 Response: {response.text}")
                return None
            
        except Exception as e:
            print(f"❌ VEO generation error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _poll_operation_completion(self, operation_name, token):
        """Poll operation until completion using fetchPredictOperation"""
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json; charset=utf-8'
        }
        
        poll_data = {
            "operationName": operation_name
        }
        
        max_attempts = 40  # Max 10 minutes (15s * 40 = 600s)
        attempts = 0
        
        while attempts < max_attempts:
            try:
                response = requests.post(self.poll_endpoint, headers=headers, json=poll_data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    done = result.get('done', False)
                    
                    if done:
                        print(f"🎉 Video generation completed!")
                        
                        # Extract video URI from response with comprehensive logging
                        response_data = result.get('response', {})
                        videos = response_data.get('videos', [])
                        
                        # CRITICAL: Log full response structure for debugging VEO API issues
                        print(f"🔍 DEBUG: Full response structure:")
                        print(f"   - done: {done}")
                        print(f"   - response keys: {list(response_data.keys())}")
                        print(f"   - videos array length: {len(videos) if videos else 'None'}")
                        if videos:
                            for i, video in enumerate(videos):
                                print(f"   - video[{i}] keys: {list(video.keys()) if isinstance(video, dict) else type(video)}")
                        
                        if videos and len(videos) > 0:
                            video_gcs_uri = videos[0].get('gcsUri')
                            if video_gcs_uri:
                                print(f"📁 Video saved to: {video_gcs_uri}")
                                return video_gcs_uri
                            else:
                                print(f"❌ RELIABILITY ISSUE: Video exists but no gcsUri")
                                print(f"   - video[0] content: {videos[0]}")
                                return None
                        else:
                            print(f"❌ RELIABILITY ISSUE: No videos in completed response")
                            print(f"   - Full response_data: {response_data}")
                            print(f"   - Raw result: {result}")
                            
                            # VEO API sometimes returns empty videos array even when successful
                            # Let's check if there are other ways to get the video
                            if 'output' in response_data:
                                print(f"🔍 Checking alternative 'output' field...")
                                output = response_data.get('output', {})
                                print(f"   - output keys: {list(output.keys()) if isinstance(output, dict) else type(output)}")
                            
                            return None
                    else:
                        attempts += 1
                        print(f"🔄 Still generating... ({attempts}/{max_attempts}) - {time.strftime('%H:%M:%S')}")
                        time.sleep(15)
                else:
                    print(f"❌ Poll error: {response.status_code} - {response.text}")
                    return None
                    
            except Exception as e:
                print(f"⚠️ Poll exception: {e}")
                attempts += 1
                time.sleep(15)
        
        print(f"⏰ Operation timed out after {max_attempts * 15} seconds")
        return None
    
    def _extract_last_frame(self, video_path):
        """Extract last frame from video for next scene"""
        import subprocess
        import base64
        
        # Save frame to organized frames directory
        video_name = Path(video_path).stem
        frames_dir = self.output_dir / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)
        frame_path = frames_dir / f"{video_name}_last_frame.jpg"
        
        try:
            print(f"🖼️ Extracting last frame from {video_path}")
            
            # Use FFmpeg to extract the last frame
            cmd = [
                'ffmpeg', '-y',  # Overwrite output
                '-i', str(video_path),  # Input video
                '-vf', 'select=eq(n\\,0)',  # Select last frame (need to get actual last frame)
                '-vframes', '1',  # Extract 1 frame
                '-update', '1',  # Update the same output file
                str(frame_path)
            ]
            
            # Actually get the last frame by seeking to end
            cmd = [
                'ffmpeg', '-y',
                '-sseof', '-1',  # Seek to 1 second before end
                '-i', str(video_path),
                '-vframes', '1',
                '-update', '1',
                str(frame_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Last frame extracted: {frame_path}")
                
                # Convert to base64 for API
                with open(frame_path, 'rb') as f:
                    image_data = f.read()
                    base64_data = base64.b64encode(image_data).decode('utf-8')
                
                return {
                    'frame_path': frame_path,
                    'base64_data': base64_data,
                    'mime_type': 'image/jpeg'
                }
            else:
                print(f"❌ Frame extraction failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Frame extraction error: {e}")
            return None
    
    def _download_from_gcs(self, gcs_uri, local_path):
        """Download video file from Google Cloud Storage"""
        try:
            import subprocess
            print(f"📥 Downloading {gcs_uri} to {local_path}")
            
            # Use gsutil to download
            result = subprocess.run(
                ['gsutil', 'cp', gcs_uri, str(local_path)],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Downloaded successfully")
                return True
            else:
                print(f"❌ Download failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Download error: {e}")
            return False

def test_veo_chain_generation(blueprint_path):
    """Test VEO chain generation with a blueprint"""
    try:
        # Load blueprint
        with open(blueprint_path, 'r') as f:
            blueprint = json.load(f)
        
        # Initialize generator
        generator = VEOChainGenerator()
        
        # Generate scene chain
        scene_files = generator.generate_scene_chain(blueprint)
        
        if scene_files:
            print(f"✅ VEO chain generation successful!")
            print(f"📁 Generated scenes: {scene_files}")
            return scene_files
        else:
            print(f"❌ VEO chain generation failed")
            return None
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return None

if __name__ == "__main__":
    print("🧪 Testing VEO 3 Chain Generation")
    print("=" * 50)
    
    # Find the most recent blueprint file
    blueprint_files = list(GENERATED_DIR.glob("*_blueprint.json"))
    if not blueprint_files:
        print("❌ No blueprint files found. Run blueprint generation first.")
        sys.exit(1)
    
    latest_blueprint = max(blueprint_files, key=lambda p: p.stat().st_mtime)
    print(f"📋 Using blueprint: {latest_blueprint.name}")
    
    # Test VEO chain generation
    scene_files = test_veo_chain_generation(latest_blueprint)
    
    if scene_files:
        print(f"\n🎉 Test completed successfully!")
    else:
        print(f"\n❌ Test failed")