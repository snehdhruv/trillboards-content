#!/usr/bin/env python3
"""
Generated Directory Organization Script
Cleans up the mess and organizes all files into proper structure
"""
import os
import shutil
import json
from pathlib import Path
from datetime import datetime
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import GENERATED_DIR

def organize_generated_directory():
    """Organize the generated directory mess into proper structure"""
    print("🧹 ORGANIZING GENERATED DIRECTORY")
    print("=" * 50)
    print("📁 Cleaning up the mess and creating organized structure...")
    
    # Create organized directory structure
    blueprints_dir = GENERATED_DIR / "blueprints"
    runs_dir = GENERATED_DIR / "runs"
    archive_dir = GENERATED_DIR / "archive"
    legacy_dir = GENERATED_DIR / "legacy"
    
    # Create directories
    blueprints_dir.mkdir(exist_ok=True)
    runs_dir.mkdir(exist_ok=True)
    archive_dir.mkdir(exist_ok=True)
    legacy_dir.mkdir(exist_ok=True)
    
    organized_files = 0
    
    # Step 1: Organize blueprints (JSON files ending with _blueprint.json)
    print(f"\n📋 Step 1: Organizing blueprints...")
    blueprint_files = list(GENERATED_DIR.glob("*_blueprint.json"))
    for blueprint_file in blueprint_files:
        # Extract blueprint ID from filename
        blueprint_id = blueprint_file.stem.replace("_blueprint", "")
        new_path = blueprints_dir / f"{blueprint_id}.json"
        
        if not new_path.exists():
            shutil.move(str(blueprint_file), str(new_path))
            print(f"📋 Organized blueprint: {blueprint_file.name} → blueprints/{new_path.name}")
            organized_files += 1
    
    # Step 2: Create legacy run for old scene files
    print(f"\n🎬 Step 2: Organizing old scene files...")
    scene_patterns = ["*_scene_*.mp4", "*_scene_*.jpg", "*_final_*.mp4", "*_final_*.jpg"]
    old_scenes = []
    
    for pattern in scene_patterns:
        old_scenes.extend(GENERATED_DIR.glob(pattern))
    
    if old_scenes:
        # Group by blueprint/project
        scene_groups = {}
        for scene_file in old_scenes:
            # Extract project name from filename
            parts = scene_file.name.split("_")
            if len(parts) >= 2:
                project_name = "_".join(parts[:-2])  # Everything except last 2 parts
            else:
                project_name = "unknown"
            
            if project_name not in scene_groups:
                scene_groups[project_name] = []
            scene_groups[project_name].append(scene_file)
        
        # Create legacy runs for each project
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for project_name, files in scene_groups.items():
            legacy_run_dir = runs_dir / f"legacy_{timestamp}_{project_name}"
            legacy_run_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (legacy_run_dir / "scenes").mkdir(exist_ok=True)
            (legacy_run_dir / "frames").mkdir(exist_ok=True)
            (legacy_run_dir / "finals").mkdir(exist_ok=True)
            
            # Organize files by type
            for file_path in files:
                if "_scene_" in file_path.name and file_path.suffix == ".mp4":
                    dest_dir = legacy_run_dir / "scenes"
                elif "_scene_" in file_path.name and file_path.suffix == ".jpg":
                    dest_dir = legacy_run_dir / "frames"
                elif "_final_" in file_path.name:
                    dest_dir = legacy_run_dir / "finals"
                else:
                    dest_dir = legacy_run_dir
                
                dest_path = dest_dir / file_path.name
                if not dest_path.exists():
                    shutil.move(str(file_path), str(dest_path))
                    print(f"🎬 Organized: {file_path.name} → {legacy_run_dir.name}/{dest_dir.name}/")
                    organized_files += 1
    
    # Step 3: Archive other video/image files
    print(f"\n📁 Step 3: Archiving misc files...")
    misc_patterns = ["*.mp4", "*.jpg", "*.png", "*.json", "*.mp3", "*.wav"]
    
    for pattern in misc_patterns:
        misc_files = list(GENERATED_DIR.glob(pattern))
        for misc_file in misc_files:
            # Skip already organized directories and system files
            if (misc_file.parent != GENERATED_DIR or 
                misc_file.name.startswith('.') or
                misc_file.name in ['blueprint.json', 'metadata.json']):
                continue
            
            archive_path = archive_dir / misc_file.name
            if not archive_path.exists():
                shutil.move(str(misc_file), str(archive_path))
                print(f"📦 Archived: {misc_file.name} → archive/")
                organized_files += 1
    
    # Step 4: Create organization metadata
    print(f"\n📊 Step 4: Creating organization metadata...")
    
    metadata = {
        "organization_date": datetime.now().isoformat(),
        "organized_files_count": organized_files,
        "directory_structure": {
            "blueprints/": "All blueprint JSON files organized by ID",
            "runs/": "All video generation runs organized by timestamp",
            "archive/": "Legacy files and miscellaneous content",
            "legacy/": "Reserved for future use"
        },
        "blueprints_count": len(list(blueprints_dir.glob("*.json"))),
        "runs_count": len(list(runs_dir.glob("run_*"))),
        "archived_files_count": len(list(archive_dir.glob("*")))
    }
    
    metadata_path = GENERATED_DIR / "organization_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"📊 Organization metadata: {metadata_path}")
    
    # Final summary
    print(f"\n🎉 ORGANIZATION COMPLETE!")
    print(f"📁 Total files organized: {organized_files}")
    print(f"📋 Blueprints: {metadata['blueprints_count']} files in blueprints/")
    print(f"🎬 Runs: {metadata['runs_count']} directories in runs/")
    print(f"📦 Archived: {metadata['archived_files_count']} files in archive/")
    print(f"📊 Metadata: organization_metadata.json")
    
    print(f"\n✅ ORGANIZED STRUCTURE:")
    print(f"generated/")
    print(f"├── blueprints/          # All blueprint JSON files")
    print(f"├── runs/                # Organized by timestamp and blueprint")
    print(f"│   ├── run_20250909_161226_janitor-hustle-viral-v1/")
    print(f"│   │   ├── blueprint.json")
    print(f"│   │   ├── scenes/")
    print(f"│   │   ├── frames/")
    print(f"│   │   ├── finals/")
    print(f"│   │   └── metadata.json")
    print(f"│   └── legacy_*/        # Old files organized by project")
    print(f"├── archive/             # Miscellaneous files")
    print(f"└── organization_metadata.json")
    
    return metadata

if __name__ == "__main__":
    organize_generated_directory()