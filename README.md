# Trillboards Content Generation System

This system generates authentic side-hustle videos featuring Trillboards as a natural workflow tool.

## Directory Structure

- `scripts/` - Video generation and management scripts
- `templates/` - Video blueprint JSON templates  
- `generated/` - Local video storage before Drive upload
- `config/` - Configuration files and API settings
- `logs/` - Generation and processing logs

## Workflow

1. **Generate**: Create videos using VEO3/Gemini API
2. **Review**: Download and review generated videos locally
3. **Upload**: Push approved videos to Google Drive
4. **Track**: Update Google Sheets with video metadata
5. **Publish**: n8n automation picks up "ready to post" videos

## Setup

Requires:
- Google Cloud authentication (`gcloud auth login`)
- Gemini API access 
- Google Drive/Sheets API permissions