import os
from dotenv import load_dotenv

# Load environment variables from anthropic.env file
load_dotenv("anthropic.env")

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Audio Processing Settings
SUPPORTED_AUDIO_FORMATS = [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".wma"]
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
WHISPER_MODEL = "base"  # Options: tiny, base, small, medium, large

# Document Settings
OUTPUT_DIR = "output"
SAMPLE_AUDIO_DIR = "sample_audio"

# Streamlit Settings
PAGE_TITLE = "Debate Audio to Formal Logic Converter"
PAGE_ICON = "🎯"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SAMPLE_AUDIO_DIR, exist_ok=True) 