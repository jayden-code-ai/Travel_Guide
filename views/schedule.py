import streamlit as st
import pandas as pd
from datetime import datetime, date
from urllib.parse import quote_plus

from utils import data_manager
import config

def make_maps_search_link(place: str) -> str:
    if not place:
        return ""
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(place)}"

def render_schedule(view: pd.DataFrame):
     # Sorting and basic processing
    view["_date"] = view["날짜"].apply(data_manager.parse_date)
    view["_time"] = view["시간"].apply(data_manager.parse_time)
    view["시간대"] = view["_time"].apply(data_manager.time_bucket)
    
    # Map Link Logic
    def make_link(row):
        query = data_manager.choose_map_query(
            row.get("내용", ""), 
            row.get("장소", ""), 
            row.get("지도검색어", "")
        )
        if query:
            return make_maps_search_link(query)
        return ""
        
    view["지도"] = view.apply(make_link, axis=1)
    view = view.sort_values(by=["_date", "_time"], na_position="last")
    
    date_options = [d for d in view["날짜"].dropna().unique().tolist() if d]
    date_options = sorted(date_options, key=lambda v: data_manager.parse_date(v) or date.max)

    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        if date_options:
            selected_dates = st.multiselect("날짜 선택", date_options, default=date_options)
        else:
            st.info("데이터가 없습니다.")
            selected_dates = []
            
    with col2:
        keyword = st.text_input("키워드 검색", placeholder="장소/내용/구분")
        
    with col3:
        view_mode = st.selectbox("보기 방식", ["카드", "표"], index=0)

    filtered = view.copy()
    if selected_dates:
        filtered = filtered[filtered["날짜"].isin(selected_dates)]
        
    if keyword:
        mask = (
            filtered["내용"].str.contains(keyword, case=False, na=False)
            | filtered["장소"].str.contains(keyword, case=False, na=False)
            | filtered["구분"].str.contains(keyword, case=False, na=False)
            | filtered["지도검색어"].str.contains(keyword, case=False, na=False)
        )
        filtered = filtered[mask]

    if filtered.empty:
        st.info("조건에 맞는 일정이 없어요. 날짜/키워드를 조정해보세요.")
        return

    if view_mode == "표":
        # Table View
        table = filtered[["날짜", "시간", "구분", "내용", "장소", "이동수단", "지도"]].copy()
        st.dataframe(
            table,
            use_container_width=True,
            column_config={
                "지도": st.column_config.LinkColumn("지도", display_text="지도 열기"),
            },
            hide_index=True,
        )
    else:
        # Card View
        for day, group in filtered.groupby("날짜"):
            st.subheader(day)
            for _, row in group.iterrows():
                place = row["장소"].strip()
                map_link = row["지도"].strip()
                
                st.markdown("<div class='schedule-card'>", unsafe_allow_html=True)
                st.markdown(
                    f"<span class='pill'>{row['시간대']}</span>"
                    f"<strong>{row['시간']} · {row['구분']}</strong>",
                    unsafe_allow_html=True,
                )
                st.write(row["내용"])
                
                if place:
                    if map_link:
                         st.markdown(f"📍 [{place}]({map_link})")
                    else:
                         st.markdown(f"📍 {place}")
                         
                if row["이동수단"]:
                    st.markdown(f"<span class='muted'>🚗 이동: {row['이동수단']}</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

def render_editor(df: pd.DataFrame):
    st.divider()
    st.markdown("<div class='section-title'>✍️ 일정 수정</div>", unsafe_allow_html=True)
    st.caption("수정 후 자동 저장됩니다.")

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_order=config.EXPECTED_COLS,
        key="schedule_editor"
    )

    if st.button("💾 변경사항 저장하기", type="primary"):
        data_manager.save_schedule(edited_df)
        st.toast("일정이 저장되었습니다! ✅")
        st.success("저장 완료!")

def render():
    st.markdown("<div class='section-title'>🗓️ 여행 일정</div>", unsafe_allow_html=True)
    
    df = data_manager.load_schedule()
    
    tab1, tab2 = st.tabs(["보기", "편집"])
    
    with tab1:
        render_schedule(df)
        
    with tab2:
        render_editor(df)
