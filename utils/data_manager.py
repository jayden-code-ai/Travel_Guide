"""CSV 기반 데이터 로딩/저장과 일정 가공 로직을 담당하는 유틸리티."""

import pandas as pd
from datetime import datetime, date, time as dt_time
import re
from typing import Optional
import shutil
import config

# 지도 검색어에서 제외할 메모성 키워드(괄호 안 텍스트 제거에 사용)
NOTE_KEYWORDS = {
    "체험", "식사", "이동", "탑승", "복귀", "휴식", "구경", "관람", "산책", "쇼핑", "대기", 
    "정리", "짐", "이용", "체크인", "체크아웃", "자유", "환승", "셔틀", "시간", "구매"
}

# 후보 리스트 CSV의 표준 컬럼 정의
CANDIDATE_COLS = ["장소명", "지도링크"]

def looks_like_note(text: str) -> bool:
    """메모성 키워드 포함 여부를 검사하여 '장소명'인지 판단한다."""
    # 공백 제거 후 키워드 포함 여부를 빠르게 검사
    compact = text.replace(" ", "")
    return any(keyword in compact for keyword in NOTE_KEYWORDS)

def strip_note_parentheses(text: str) -> str:
    """괄호 안 메모 텍스트를 제거하여 지도 검색어로 쓸 문자열만 남긴다."""
    if not text:
        return ""

    def _replace(match: re.Match[str]) -> str:
        inner = match.group(1)
        # 괄호 안 내용이 메모로 판단되면 제거, 아니면 원문 유지
        return "" if looks_like_note(inner) else match.group(0)

    # 괄호 안 메모성 텍스트 제거 → 중복 공백 정리
    cleaned = re.sub(r"\(([^()]*)\)", _replace, text)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip(" -")
    return cleaned.strip()

def choose_map_query(content: str, place: str, override: str) -> str:
    """지도 검색에 사용할 최적 문자열을 우선순위로 선택한다."""
    # 사용자가 직접 지정한 검색어가 있으면 최우선
    if override:
        return override.strip()
    # 괄호 메모 제거 후 장소/내용을 후보로 사용
    place_clean = strip_note_parentheses(place)
    content_clean = strip_note_parentheses(content)
    # 장소명이 유효하면 우선 사용
    if place_clean and not looks_like_note(place_clean):
        return place_clean
    # 내용이 장소처럼 보이면 대체 사용
    if content_clean and not looks_like_note(content_clean):
        return content_clean
    # 둘 다 애매하면 남아있는 값 반환
    return place_clean or content_clean

def ensure_data_file() -> None:
    """일정 CSV가 없으면 기본 샘플 데이터로 생성한다."""
    if config.SCHEDULE_PATH.exists():
        return
    
    # 최소 1행의 시드 데이터로 파일을 생성
    seed = pd.DataFrame(
        [
            {"날짜": "3/4 (수)", "시간": "09:20", "구분": "도착", "내용": "후쿠오카 공항 도착", "장소": "", "이동수단": ""},
        ]
    )
    seed.to_csv(config.SCHEDULE_PATH, index=False)

def load_schedule() -> pd.DataFrame:
    """일정 CSV를 로드하고 누락 컬럼을 보정한다."""
    # 파일이 없으면 기본 파일부터 생성
    ensure_data_file()
    try:
        df = pd.read_csv(config.SCHEDULE_PATH, dtype=str).fillna("")
    except Exception:
        # 읽기 실패 시 빈 데이터프레임 반환
        return pd.DataFrame(columns=config.EXPECTED_COLS)
        
    # 컬럼이 빠져있어도 앱이 정상 동작하도록 보정
    for col in config.EXPECTED_COLS:
        if col not in df.columns:
            df[col] = ""
    return df[config.EXPECTED_COLS]

def save_schedule(df: pd.DataFrame) -> None:
    """일정 CSV를 저장하고 이전 버전은 백업한다."""
    # 기존 파일을 백업으로 이동
    if config.SCHEDULE_PATH.exists():
        config.SCHEDULE_PATH.replace(config.BACKUP_PATH)
    # 최신 데이터를 저장
    df.to_csv(config.SCHEDULE_PATH, index=False)

def load_expenses() -> pd.DataFrame:
    """지출 CSV를 로드한다. 파일이 없으면 빈 스키마로 반환."""
    if not config.EXPENSES_PATH.exists():
        return pd.DataFrame(columns=["날짜", "항목", "금액", "결제자", "메모"])
    
    return pd.read_csv(config.EXPENSES_PATH, dtype=str).fillna("")

def save_expenses(df: pd.DataFrame) -> None:
    """지출 CSV를 저장한다."""
    df.to_csv(config.EXPENSES_PATH, index=False)

def ensure_candidates_file() -> None:
    """후보 리스트 CSV가 없으면 표준 헤더로 생성한다."""
    if config.CANDIDATES_PATH.exists():
        return
    pd.DataFrame(columns=CANDIDATE_COLS).to_csv(config.CANDIDATES_PATH, index=False)

def normalize_candidates(df: pd.DataFrame) -> pd.DataFrame:
    """후보 리스트 컬럼을 표준 스키마로 보정한다."""
    for col in CANDIDATE_COLS:
        if col not in df.columns:
            df[col] = ""
    return df[CANDIDATE_COLS]

# 날짜/시간 파싱 헬퍼
def parse_date(raw: str) -> Optional[date]:
    """문자열에서 월/일 정보를 추출하여 date 객체로 변환한다."""
    if not raw:
        return None
    # "3/4 (수)" 형태에서 월/일만 추출
    match = re.search(r"(\d{1,2})\s*/\s*(\d{1,2})", raw)
    if not match:
        return None
    month, day = int(match.group(1)), int(match.group(2))
    try:
        return date(config.TRIP_YEAR, month, day)
    except ValueError:
        return None

def parse_time(raw: str) -> Optional[dt_time]:
    """문자열에서 시각(HH:MM)을 추출하여 time 객체로 변환한다."""
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
    """시간대를 오전/오후/저녁/기타로 구분한다."""
    if not t:
        return "기타"
    if t < dt_time(12, 0):
        return "오전"
    if t < dt_time(18, 0):
        return "오후"
    return "저녁"

def load_candidates() -> pd.DataFrame:
    """후보 리스트 CSV를 로드하고 복구 로직을 적용한다."""
    # 파일이 없으면 빈 헤더로 생성
    ensure_candidates_file()
    try:
        df = pd.read_csv(config.CANDIDATES_PATH, dtype=str).fillna("")
        return normalize_candidates(df)
    except Exception:
        # 원본이 깨졌을 경우 백업 파일로 복구 시도
        if config.CANDIDATES_BACKUP_PATH.exists():
            try:
                df = pd.read_csv(config.CANDIDATES_BACKUP_PATH, dtype=str).fillna("")
                df = normalize_candidates(df)
                df.to_csv(config.CANDIDATES_PATH, index=False)
                return df
            except Exception:
                return pd.DataFrame(columns=CANDIDATE_COLS)
        return pd.DataFrame(columns=CANDIDATE_COLS)

def save_candidates(df: pd.DataFrame) -> None:
    """후보 리스트 CSV를 안전하게 저장한다."""
    # 표준 스키마로 보정하여 저장 순서를 유지
    df = normalize_candidates(df.copy())
    # 기존 파일은 백업하여 복구 가능성을 확보
    if config.CANDIDATES_PATH.exists():
        shutil.copy2(config.CANDIDATES_PATH, config.CANDIDATES_BACKUP_PATH)
    # 임시 파일에 먼저 저장 후 원자적으로 교체(손상 방지)
    tmp_path = config.CANDIDATES_PATH.with_suffix(".tmp")
    df.to_csv(tmp_path, index=False)
    tmp_path.replace(config.CANDIDATES_PATH)
