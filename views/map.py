import streamlit as st
import pandas as pd
from urllib.parse import quote_plus
from utils import data_manager
import config

def render():
    st.markdown("<div class='section-title'>🗺️ 지도 탐색</div>", unsafe_allow_html=True)
    
    tab_schedule, tab_candidate = st.tabs(["📅 일정 장소", "🤔 요기오때?"])
    
    # --- Schedule Places ---
    with tab_schedule:
        st.caption("일정에 포함된 장소를 지도에서 확인하세요.")
        
        df = data_manager.load_schedule()
        unique_places = sorted({
            q for q in df.apply(
                lambda row: data_manager.choose_map_query(
                    row.get("내용", ""), 
                    row.get("장소", ""), 
                    row.get("지도검색어", "")
                ),
                axis=1
            ) if q.strip()
        })
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            choice = st.radio("장소 선택", ["직접 입력"] + unique_places, key="map_choice_schedule")
            
            if choice == "직접 입력":
                place = st.text_input("장소 검색", placeholder="예: 하카타역", key="map_input_schedule")
            else:
                place = choice
                
        with col2:
            if not place:
                st.info("장소를 선택하면 지도가 표시됩니다.")
            else:
                map_link = f"https://www.google.com/maps/search/?api=1&query={quote_plus(place)}"
                st.markdown(f"📍 **{place}** ([Google 지도에서 열기]({map_link}))")

                if config.GOOGLE_MAPS_API_KEY:
                    embed_url = (
                        "https://www.google.com/maps/embed/v1/place"
                        f"?key={config.GOOGLE_MAPS_API_KEY}&q={quote_plus(place)}"
                    )
                    st.components.v1.iframe(embed_url, height=450)
                else:
                    st.warning("Google Maps API 키가 설정되지 않아 지도를 표시할 수 없습니다.")

    # --- Candidate Places (How about here?) ---
    with tab_candidate:
        st.subheader("가볼까 고민되는 장소 저장소")
        st.caption("지도 링크를 넣어두면 나중에 보기 편해요!")
        
        # Load Data
        candidates_df = data_manager.load_candidates()
        
        # Input Form
        with st.form("add_candidate_form", clear_on_submit=True):
            col_in1, col_in2, col_btn = st.columns([2, 3, 1])
            with col_in1:
                new_place = st.text_input("장소명", placeholder="예: 다이소 키체인")
            with col_in2:
                new_link = st.text_input("지도 링크 (URL)", placeholder="구글맵 링크 붙여넣기")
            with col_btn:
                submitted = st.form_submit_button("추가")
                
            if submitted and new_place:
                new_row = pd.DataFrame([{"장소명": new_place, "지도링크": new_link}])
                updated_df = pd.concat([candidates_df, new_row], ignore_index=True)
                data_manager.save_candidates(updated_df)
                st.rerun()

        st.divider()
        
        # Display List
        if candidates_df.empty:
            st.info("아직 저장된 장소가 없어요. 위에 추가해보세요!")
        else:
            # Re-load to ensure fresh data
            candidates_df = data_manager.load_candidates()
            
            st.markdown("##### 📌 후보 리스트")
            for idx, row in candidates_df.iterrows():
                c_place = row["장소명"]
                c_link = row["지도링크"]
                
                with st.expander(f"📍 {c_place}", expanded=False):
                    if c_link:
                         st.markdown(f"🔗 [지도 바로가기]({c_link})")
                    else:
                        st.caption("링크 없음")
                        
                    # Delete Button (Simple implementation)
                    if st.button("삭제", key=f"del_{idx}"):
                        candidates_df = candidates_df.drop(idx)
                        data_manager.save_candidates(candidates_df)
                        st.rerun()
                    
                    # Embed Map if link or name exists
                    query_for_map = c_place
                    if config.GOOGLE_MAPS_API_KEY:
                         embed_url = (
                            "https://www.google.com/maps/embed/v1/place"
                            f"?key={config.GOOGLE_MAPS_API_KEY}&q={quote_plus(query_for_map)}"
                        )
                         st.components.v1.iframe(embed_url, height=300)
