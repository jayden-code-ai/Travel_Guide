import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SCHEDULE_PATH = DATA_DIR / "schedule.csv"
BACKUP_PATH = DATA_DIR / "schedule.backup.csv"
EXPENSES_PATH = DATA_DIR / "expenses.csv"
CANDIDATES_PATH = DATA_DIR / "candidates.csv"
PHOTOS_DIR = DATA_DIR / "photos"

# App Configuration
APP_TITLE = "지민쓰와 떠나는 후쿠오카 찐친 패밀리 투어"
TRIP_YEAR = 2026
TRIP_DATES = "2026.03.04 ~ 03.07"
TRIP_MEMBERS = "5명"
HOTEL_NAME = "APA Hotel Hakata Eki Chikushiguchi"

# Constants
AUTO_TRANSLATE_COOLDOWN_SEC = 1.2
EXPECTED_COLS = ["날짜", "시간", "구분", "내용", "장소", "지도검색어", "이동수단"]

def get_secret(name: str, default: str = "") -> str:
    """Get secret from streamlit secrets or environment variables."""
    if name in st.secrets:
        return str(st.secrets[name]).strip()
    return os.getenv(name, default).strip()

# API Keys & Models
OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
GOOGLE_MAPS_API_KEY = get_secret("GOOGLE_MAPS_API_KEY")

OPENAI_MODEL = get_secret("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TRANSLATE_MODEL = get_secret("OPENAI_TRANSLATE_MODEL", "gpt-4o-mini")
OPENAI_STT_MODEL = get_secret("OPENAI_STT_MODEL", "whisper-1")
OPENAI_OCR_MODEL = get_secret("OPENAI_OCR_MODEL", "gpt-4o-mini")
OPENAI_TTS_MODEL = get_secret("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
OPENAI_TTS_VOICE = get_secret("OPENAI_TTS_VOICE", "alloy")

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
