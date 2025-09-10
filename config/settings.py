"""
Trillboards Content Generation Configuration
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
GENERATED_DIR = PROJECT_ROOT / "generated"
LOGS_DIR = PROJECT_ROOT / "logs"

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT = "trillboard-new"
GOOGLE_CLOUD_REGION = "us-central1"

# Google Drive Configuration  
GOOGLE_DRIVE_FOLDER_ID = "11y0xecSWeSJacO0fS-3VMRP90wsbsaiR"

# Google Sheets Configuration
GOOGLE_SHEETS_ID = "1Z3U35QnAGh9gDeBEYrHsPR952MS86DCGkZos_GTVvjQ"

# Video Generation Configuration
DEFAULT_VIDEO_COUNT = 10
MAX_VIDEO_DURATION = 75  # seconds
MIN_VIDEO_DURATION = 30  # seconds
TARGET_ASPECT_RATIO = "9:16"
DEFAULT_FRAMERATE = 30

# Trillboards Context for AI Generation
TRILLBOARDS_CONTEXT = """
Trillboards — context for generation
• What it is: Trillboards turns any TV into a programmable screen for local promos and short ads. It's software-only (no hardware box).
• Who uses it:
  - EARNER (screen owner or staff at a venue) pairs a TV and schedules rotating cards (house specials, events, community notices) plus optional paid local promos.
  - ADVERTISER (brand or local biz) books time on those screens.
• How it works (typical flow):
  1. Open the Trillboards app on phone.
  2. Pair the TV by scanning a QR code at screen.trillboards.com.
  3. Choose a playlist template (bar specials, class fill, neighborhood bundle, lobby info, etc.).
  4. Set rotation (e.g., every 5–8 minutes) and quiet hours.
  5. (Optional) Add paid local promos from the marketplace.
  6. Let it run; swap cards on the fly from the app.
• Positioning (for scripts): Trillboards is a tool in the workflow—the quiet step that solves "how do we actually put this on a screen and keep it rotating without babysitting?"
• Money reality: EARNERs can receive small, variable daily payouts or CPM-based earnings when demand exists. Ranges depend on foot traffic, hours, location, and fill rate. Avoid promises; use plausible ranges and hedges.
• Prefer "local promos," "offers," "events," "sign-ups" language over "ads."
"""

# 🔥 VIRAL Side-hustle themes - SMOKING HOT MODELS, AROUSAL ENERGY
SIDE_HUSTLE_THEMES = [
    "Runway goddess turned the lounge TV into a $300 side hustle — champagne glass in hand, curves stealing the spotlight",
    "Made $80/day lighting up a dead restaurant screen — every promo looked like a flirt, every glance turned heads",
    "After-hours fantasy: lingerie under the blazer, $200/week pulsing on office TVs — no one knows, but you’d never forget",
    "Gym babe in crop top dropped crypto promos on the TVs — flexed, winked, made $400 before anyone caught on",
    "College knockout pulling $150/week off campus TVs — every clip looked like a music video, every walk a runway",
    "Seductive bartender turned slow Tuesdays into $60 — neon lights, smoky eyes, TV glowing like a boudoir set",
    "How I made $100/day glamorizing other people’s TVs — hips swaying, eyes locking, no one dared to stop me",
    "Model-off-duty stacking $50/hour on graveyard shifts — screens glowing, lips glossed, fantasy alive at 3 a.m.",
    "I turned a blank restaurant TV into $250/week — lace slip under my apron, customers begging for more",
    "Unemployed hottie transformed a coffee shop TV into $300/week — every promo was a tease, every glance an invite"
]

# 🎯 ALTERNATIVE CONTROVERSIAL ANGLES — SMOKING HOT MODELS, SEXY
VIRAL_ALTERNATIVE_THEMES = [
    "Boss clueless, screen dripping with seduction — $400 slipped into my pocket while heels clicked across the floor",
    "Minimum wage turned into runway money: $200/week, every promo felt like lingerie on display",
    "This hustle only works with screens — lounges, gyms, offices — and when you look like you stepped out of a magazine",
    "Making $60+ per shift with one sultry trick — every TV a spotlight, every look a slow undress",
    "Turned a dead TV into $180 this month — lips parted, eyes daring, vibe irresistible",
    "Night shift angels stacking TV hustle cash — glossed lips, tight dresses, screens burning like desire",
    "Workplace TV into $250 last week — fishnets, champagne fizz, every frame a fantasy",
    "The underground TV hustle: sexy, forbidden, intoxicating — the kind corporations pray you never learn",
    "I made more from the workplace TV than my paycheck — every night a catwalk, every glance a hook",
    "Secret model-tier hustle: bars, gyms, offices — screens as lingerie, dollars as perfume"
]

# Environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_CLOUD_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Ensure required directories exist
GENERATED_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)