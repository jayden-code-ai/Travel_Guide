"""앱 엔트리 포인트: 사이드바 메뉴와 각 뷰 렌더링을 연결한다."""

import streamlit as st
from streamlit_option_menu import option_menu

import config
from utils import style
from views import schedule, map, translate, weather, expenses, gallery

def main():
    """Streamlit 페이지 기본 설정과 탭 렌더링을 수행한다."""
    # 페이지 메타(제목/아이콘/레이아웃) 설정
    st.set_page_config(
        page_title=config.APP_TITLE,
        page_icon="🧳",
        layout="wide"
    )
    
    # 공통 스타일(CSS/JS)을 주입하여 UI 톤을 통일
    style.inject_response_css()

    # 사이드바 메뉴 구성 및 여행 정보 표시
    with st.sidebar:
        st.markdown(f"### {config.APP_TITLE}")
        
        # 메뉴 선택에 따라 메인 뷰를 전환
        selected = option_menu(
            "메뉴",
            ["일정 View", "지도 View", "AI 통역사", "날씨 예보", "지출 기록", "추억 앨범"],
            icons=["calendar-check", "map", "translate", "cloud-sun", "receipt", "images"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "5!important", "background-color": "var(--sidebar-bg)"},
                "icon": {"color": "var(--title-color)", "font-size": "25px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "var(--pill-bg)", "color": "var(--text-color)"},
                "nav-link-selected": {"background-color": "var(--pill-bg)", "color": "var(--pill-text)"},
            }
        )
        
        st.divider()
        st.markdown("#### ℹ️ 여행 정보")
        # 고정된 여행 정보 요약 패널
        st.info(
            f"**기간**: {config.TRIP_DATES}\n\n"
            f"**인원**: {config.TRIP_MEMBERS}\n\n"
            f"**숙소**: {config.HOTEL_NAME}"
        )

    # 메인 콘텐츠(상단 타이틀)
    st.title(config.APP_TITLE)
    
    # 메뉴 선택 결과에 따라 각 화면 렌더링
    if selected == "일정 View":
        schedule.render()
    elif selected == "지도 View":
        map.render()
    elif selected == "AI 통역사":
        translate.render()
    elif selected == "날씨 예보":
        weather.render()
    elif selected == "지출 기록":
        expenses.render()
    elif selected == "추억 앨범":
        gallery.render()

if __name__ == "__main__":
    # 직접 실행 시 main() 호출
    main()
