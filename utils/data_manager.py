import pandas as pd
from datetime import datetime, date, time as dt_time
import re
from typing import Optional
import config

NOTE_KEYWORDS = {
    "체험", "식사", "이동", "탑승", "복귀", "휴식", "구경", "관람", "산책", "쇼핑", "대기", 
    "정리", "짐", "이용", "체크인", "체크아웃", "자유", "환승", "셔틀", "시간"
}

def looks_like_note(text: str) -> bool:
    compact = text.replace(" ", "")
    return any(keyword in compact for keyword in NOTE_KEYWORDS)

def strip_note_parentheses(text: str) -> str:
    if not text:
        return ""

    def _replace(match: re.Match[str]) -> str:
        inner = match.group(1)
        return "" if looks_like_note(inner) else match.group(0)

    cleaned = re.sub(r"\(([^()]*)\)", _replace, text)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip(" -")
    return cleaned.strip()

def choose_map_query(content: str, place: str, override: str) -> str:
    if override:
        return override.strip()
    place_clean = strip_note_parentheses(place)
    content_clean = strip_note_parentheses(content)
    if place_clean and not looks_like_note(place_clean):
        return place_clean
    if content_clean and not looks_like_note(content_clean):
        return content_clean
    return place_clean or content_clean

def ensure_data_file() -> None:
    """Ensure schedule.csv exists with initial data."""
    if config.SCHEDULE_PATH.exists():
        return
    
    seed = pd.DataFrame(
        [
            {"날짜": "3/4 (수)", "시간": "09:20", "구분": "도착", "내용": "후쿠오카 공항 도착", "장소": "", "이동수단": ""},
        ]
    )
    seed.to_csv(config.SCHEDULE_PATH, index=False)

def load_schedule() -> pd.DataFrame:
    """Load schedule data from CSV."""
    ensure_data_file()
    try:
        df = pd.read_csv(config.SCHEDULE_PATH, dtype=str).fillna("")
    except Exception:
        return pd.DataFrame(columns=config.EXPECTED_COLS)
        
    for col in config.EXPECTED_COLS:
        if col not in df.columns:
            df[col] = ""
    return df[config.EXPECTED_COLS]

def save_schedule(df: pd.DataFrame) -> None:
    """Save schedule data to CSV and create backup."""
    if config.SCHEDULE_PATH.exists():
        config.SCHEDULE_PATH.replace(config.BACKUP_PATH)
    df.to_csv(config.SCHEDULE_PATH, index=False)

def load_expenses() -> pd.DataFrame:
    """Load expenses data from CSV."""
    if not config.EXPENSES_PATH.exists():
        return pd.DataFrame(columns=["날짜", "항목", "금액", "결제자", "메모"])
    
    return pd.read_csv(config.EXPENSES_PATH, dtype=str).fillna("")

def save_expenses(df: pd.DataFrame) -> None:
    """Save expenses data to CSV."""
    df.to_csv(config.EXPENSES_PATH, index=False)

# Date/Time Parsing Helpers
def parse_date(raw: str) -> Optional[date]:
    if not raw:
        return None
    match = re.search(r"(\d{1,2})\s*/\s*(\d{1,2})", raw)
    if not match:
        return None
    month, day = int(match.group(1)), int(match.group(2))
    try:
        return date(config.TRIP_YEAR, month, day)
    except ValueError:
        return None

def parse_time(raw: str) -> Optional[dt_time]:
    if not raw:
        return None
    match = re.search(r"(\d{1,2}):(\d{2})", raw)
    if not match:
        return None
    hour, minute = int(match.group(1)), int(match.group(2))
    try:
        return dt_time(hour, minute)
    except ValueError:
        return None

def time_bucket(t: Optional[dt_time]) -> str:
    if not t:
        return "기타"
    if t < dt_time(12, 0):
        return "오전"
    if t < dt_time(18, 0):
        return "오후"
    return "저녁"
