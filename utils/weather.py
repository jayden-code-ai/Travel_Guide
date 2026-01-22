import requests
from datetime import datetime, timedelta

# Fukuoka Coordinates
LAT = 33.5902
LON = 130.4017

def get_weather_forecast():
    """Fetch 7-day weather forecast for Fukuoka from Open-Meteo API."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LAT,
        "longitude": LON,
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "precipitation_probability_max"],
        "timezone": "Asia/Tokyo",
        "forecast_days": 7
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("daily", {})
    except Exception as e:
        print(f"Weather API Error: {e}")
        return None

def get_weather_icon(code: int) -> str:
    """Map WMO weather code to emoji."""
    if code == 0: return "☀️"
    if code in [1, 2, 3]: return "⛅"
    if code in [45, 48]: return "🌫️"
    if code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: return "🌧️"
    if code in [71, 73, 75, 77, 85, 86]: return "🌨️"
    if code in [95, 96, 99]: return "⛈️"
    return "❓"

def get_weather_msg(code: int) -> str:
    if code == 0: return "맑음"
    if code in [1, 2, 3]: return "구름 조금"
    if code in [45, 48]: return "안개"
    if code in [51, 53, 55]: return "이슬비"
    if code in [61, 63, 65]: return "비"
    if code in [80, 81, 82]: return "소나기"
    if code in [95, 96, 99]: return "뇌우"
    return "흐림"
