"""후쿠오카 날씨 예보 화면을 렌더링하는 뷰."""

import streamlit as st
import pandas as pd
from datetime import datetime
from utils import weather

def render():
    """Open-Meteo API 데이터를 카드 형태로 보여준다."""
    st.markdown("<div class='section-title'>⛅ 후쿠오카 날씨</div>", unsafe_allow_html=True)
    
    # 로딩 스피너와 함께 API 호출
    with st.spinner("날씨 정보를 가져오는 중..."):
        data = weather.get_weather_forecast()
    
    if not data:
        st.error("날씨 정보를 불러올 수 없습니다.")
        return

    # 일별 예보 데이터 추출
    dates = data.get("time", [])
    codes = data.get("weather_code", [])
    max_temps = data.get("temperature_2m_max", [])
    min_temps = data.get("temperature_2m_min", [])
    rain_probs = data.get("precipitation_probability_max", [])
    
    # 카드 UI로 표시(최대 4개 컬럼)
    cols = st.columns(len(dates)) if len(dates) <= 4 else st.columns(4)
    
    for i, date_str in enumerate(dates):
        # UI 가독성을 위해 최대 4일만 표시
        if i >= 4: break 
        
        col = cols[i]
        # 코드 → 아이콘/텍스트 매핑
        w_code = codes[i]
        icon = weather.get_weather_icon(w_code)
        desc = weather.get_weather_msg(w_code)
        
        # 날짜 표시용 포맷 변환
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        display_date = f"{dt.month}/{dt.day} ({dt.strftime('%a')})"
        
        with col:
            st.markdown(
                f"""
                <div style="background: white; border-radius: 12px; padding: 15px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">{display_date}</div>
                    <div style="font-size: 2.5rem; margin-bottom: 5px;">{icon}</div>
                    <div style="font-weight: bold; margin-bottom: 8px;">{desc}</div>
                    <div style="font-size: 0.9rem;">
                        <span style="color: #e74c3c;">{max_temps[i]}°</span> / 
                        <span style="color: #3498db;">{min_temps[i]}°</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #888; margin-top: 5px;">☔ {rain_probs[i]}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
    # 데이터 출처 안내
    st.caption("제공: Open-Meteo API (후쿠오카 기준)")
