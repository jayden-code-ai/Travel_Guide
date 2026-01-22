import streamlit as st
from urllib.parse import quote_plus
from utils import data_manager
import config

def render():
    st.markdown("<div class='section-title'>🗺️ 지도 탐색</div>", unsafe_allow_html=True)
    st.caption("일정에 포함된 장소를 지도에서 확인하세요.")

    df = data_manager.load_schedule()
    unique_places = sorted({p for p in df["장소"].dropna().tolist() if p.strip()})
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        choice = st.radio("장소 선택", ["직접 입력"] + unique_places)
        
        if choice == "직접 입력":
            place = st.text_input("장소 검색", placeholder="예: 하카타역")
        else:
            place = choice
            
    with col2:
        if not place:
            st.info("장소를 선택하면 지도가 표시됩니다.")
            return

        map_link = f"https://www.google.com/maps/search/?api=1&query={quote_plus(place)}"
        st.markdown(f"📍 **{place}** ([Google 지도에서 열기]({map_link}))")

        if not config.GOOGLE_MAPS_API_KEY:
            st.warning("Google Maps API 키가 설정되지 않아 지도를 표시할 수 없습니다.")
            return

        embed_url = (
            "https://www.google.com/maps/embed/v1/place"
            f"?key={config.GOOGLE_MAPS_API_KEY}&q={quote_plus(place)}"
        )
        st.components.v1.iframe(embed_url, height=450)
