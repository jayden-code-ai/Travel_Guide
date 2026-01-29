"""지도 탭 UI: 일정 장소 지도와 후보 장소 저장소를 제공한다."""

import streamlit as st
import pandas as pd
from urllib.parse import quote_plus
from utils import data_manager
import config

def render():
    """지도 화면을 렌더링한다(일정 장소/후보 장소 탭)."""
    st.markdown("<div class='section-title'>🗺️ 지도 탐색</div>", unsafe_allow_html=True)
    
    # 일정 장소 탭과 후보 리스트 탭을 분리하여 UX를 단순화
    tab_schedule, tab_candidate = st.tabs(["📅 일정 장소", "🤔 요기오때?"])
    
    # --- 일정에 포함된 장소 보기 ---
    with tab_schedule:
        st.caption("일정에 포함된 장소를 지도에서 확인하세요.")
        
        # 일정 데이터에서 지도 검색어 후보를 추출
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
        
        # 좌측: 장소 선택, 우측: 지도 표시
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
                # 선택한 장소를 Google Maps 검색 링크로 제공
                map_link = f"https://www.google.com/maps/search/?api=1&query={quote_plus(place)}"
                st.markdown(f"📍 **{place}** ([Google 지도에서 열기]({map_link}))")

                # API 키가 있으면 Embed 지도까지 표시
                if config.GOOGLE_MAPS_API_KEY:
                    embed_url = (
                        "https://www.google.com/maps/embed/v1/place"
                        f"?key={config.GOOGLE_MAPS_API_KEY}&q={quote_plus(place)}"
                    )
                    st.components.v1.iframe(embed_url, height=450)
                else:
                    st.warning("Google Maps API 키가 설정되지 않아 지도를 표시할 수 없습니다.")

    # --- 후보 장소 저장소(요기오때?) ---
    with tab_candidate:
        st.subheader("가볼까 고민되는 장소 저장소")
        st.caption("지도 링크를 넣어두면 나중에 보기 편해요!")
        
        # 후보 리스트 로드
        candidates_df = data_manager.load_candidates()
        
        # 신규 후보 입력 폼
        with st.form("add_candidate_form", clear_on_submit=True):
            col_in1, col_in2, col_btn = st.columns([2, 3, 1])
            with col_in1:
                new_place = st.text_input("장소명", placeholder="예: 다이소 키체인")
            with col_in2:
                new_link = st.text_input("지도 링크 (URL)", placeholder="구글맵 링크 붙여넣기")
            with col_btn:
                submitted = st.form_submit_button("추가")
                
            if submitted and new_place:
                # 신규 후보를 추가하고 저장
                new_row = pd.DataFrame([{"장소명": new_place, "지도링크": new_link}])
                updated_df = pd.concat([candidates_df, new_row], ignore_index=True)
                data_manager.save_candidates(updated_df)
                st.rerun()

        st.divider()
        
        # 후보 리스트 표시
        if candidates_df.empty:
            st.info("아직 저장된 장소가 없어요. 위에 추가해보세요!")
        else:
            # 저장 직후 최신 데이터 반영을 위해 재로드
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
                        
                    # 삭제 버튼(행 단위로 제거)
                    if st.button("삭제", key=f"del_{idx}"):
                        candidates_df = candidates_df.drop(idx)
                        data_manager.save_candidates(candidates_df)
                        st.rerun()
                    
                    # 장소명이 있으면 Embed 지도로 미리보기 표시
                    query_for_map = c_place
                    if config.GOOGLE_MAPS_API_KEY:
                         embed_url = (
                            "https://www.google.com/maps/embed/v1/place"
                            f"?key={config.GOOGLE_MAPS_API_KEY}&q={quote_plus(query_for_map)}"
                        )
                         st.components.v1.iframe(embed_url, height=300)
