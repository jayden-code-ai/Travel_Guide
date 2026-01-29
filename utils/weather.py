"""Open-Meteo API를 사용해 후쿠오카 날씨 데이터를 가져오는 유틸리티."""

import requests
from datetime import datetime, timedelta

# 후쿠오카 좌표(고정)
LAT = 33.5902
LON = 130.4017

def get_weather_forecast():
    """Open-Meteo API에서 후쿠오카 7일 예보를 가져온다."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LAT,
        "longitude": LON,
        # 필요한 일별 지표만 요청(코드/최저·최고기온/강수확률)
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "precipitation_probability_max"],
        "timezone": "Asia/Tokyo",
        "forecast_days": 7
    }
    
    try:
        # 타임아웃을 두어 네트워크 지연으로 인한 멈춤 방지
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        # daily 키에 날짜별 리스트가 담겨 있음
        return data.get("daily", {})
    except Exception as e:
        # API 호출 실패 시 None 반환(상위에서 안내 메시지 표시)
        print(f"Weather API Error: {e}")
        return None

def get_weather_icon(code: int) -> str:
    """WMO 날씨 코드를 이모지 아이콘으로 매핑한다."""
    if code == 0: return "☀️"
    if code in [1, 2, 3]: return "⛅"
    if code in [45, 48]: return "🌫️"
    if code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: return "🌧️"
    if code in [71, 73, 75, 77, 85, 86]: return "🌨️"
    if code in [95, 96, 99]: return "⛈️"
    return "❓"

def get_weather_msg(code: int) -> str:
    """WMO 날씨 코드를 간단한 한국어 설명으로 변환한다."""
    if code == 0: return "맑음"
    if code in [1, 2, 3]: return "구름 조금"
    if code in [45, 48]: return "안개"
    if code in [51, 53, 55]: return "이슬비"
    if code in [61, 63, 65]: return "비"
    if code in [80, 81, 82]: return "소나기"
    if code in [95, 96, 99]: return "뇌우"
    return "흐림"
