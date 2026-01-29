"""앱 전역 설정(경로/환경변수/상수)을 모아두는 설정 모듈."""

import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# .env 파일에 정의된 환경 변수를 먼저 로드
load_dotenv()

# 프로젝트 루트 및 데이터 관련 경로 정의
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SCHEDULE_PATH = DATA_DIR / "schedule.csv"
BACKUP_PATH = DATA_DIR / "schedule.backup.csv"
EXPENSES_PATH = DATA_DIR / "expenses.csv"
CANDIDATES_PATH = DATA_DIR / "candidates.csv"
CANDIDATES_BACKUP_PATH = DATA_DIR / "candidates.backup.csv"
PHOTOS_DIR = DATA_DIR / "photos"

# 앱 표기/여행 정보 등 UI에 표시될 기본 정보
APP_TITLE = "지민쓰와 떠나는 후쿠오카 찐친 패밀리 투어"
TRIP_YEAR = 2026
TRIP_DATES = "2026.03.04 ~ 03.07"
TRIP_MEMBERS = "5명"
HOTEL_NAME = "APA Hotel Hakata Eki Chikushiguchi"

# 공통 상수(자동 번역 대기 시간, 일정 데이터 컬럼 등)
AUTO_TRANSLATE_COOLDOWN_SEC = 1.2
EXPECTED_COLS = ["날짜", "시간", "구분", "내용", "장소", "지도검색어", "이동수단"]

def get_secret(name: str, default: str = "") -> str:
    """Streamlit Secrets 또는 환경 변수에서 키 값을 안전하게 가져온다."""
    # Streamlit Cloud 배포 환경에서는 st.secrets를 우선 사용
    if name in st.secrets:
        return str(st.secrets[name]).strip()
    # 로컬 실행 환경에서는 .env 또는 OS 환경 변수를 사용
    return os.getenv(name, default).strip()

# API 키 및 모델 설정(Secrets 우선)
OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
GOOGLE_MAPS_API_KEY = get_secret("GOOGLE_MAPS_API_KEY")

OPENAI_MODEL = get_secret("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TRANSLATE_MODEL = get_secret("OPENAI_TRANSLATE_MODEL", "gpt-4o-mini")
OPENAI_STT_MODEL = get_secret("OPENAI_STT_MODEL", "whisper-1")
OPENAI_OCR_MODEL = get_secret("OPENAI_OCR_MODEL", "gpt-4o-mini")
OPENAI_TTS_MODEL = get_secret("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
OPENAI_TTS_VOICE = get_secret("OPENAI_TTS_VOICE", "alloy")

# 앱 실행 시 필요한 디렉터리가 없으면 생성
DATA_DIR.mkdir(parents=True, exist_ok=True)
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
