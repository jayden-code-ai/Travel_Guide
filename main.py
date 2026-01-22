import streamlit as st
from streamlit_option_menu import option_menu

import config
from utils import style
from views import schedule, map, translate, weather, expenses, gallery

def main():
    # Page Config
    st.set_page_config(
        page_title=config.APP_TITLE,
        page_icon="🧳",
        layout="wide"
    )
    
    # Inject CSS
    style.inject_response_css()

    # Sidebar / Navigation
    with st.sidebar:
        st.markdown(f"### {config.APP_TITLE}")
        
        selected = option_menu(
            "메뉴",
            ["일정 View", "지도 View", "AI 통역사", "날씨 예보", "N빵 정산", "추억 앨범"],
            icons=["calendar-check", "map", "translate", "cloud-sun", "calculator", "images"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "5!important", "background-color": "#fffbf7"},
                "icon": {"color": "#d35400", "font-size": "25px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#ffe4c7", "color": "#d35400"},
            }
        )
        
        st.divider()
        st.markdown("#### ℹ️ 여행 정보")
        st.info(
            f"**기간**: {config.TRIP_DATES}\n\n"
            f"**인원**: {config.TRIP_MEMBERS}\n\n"
            f"**숙소**: {config.HOTEL_NAME}"
        )

    # Main Content
    st.title(config.APP_TITLE)
    
    if selected == "일정 View":
        schedule.render()
    elif selected == "지도 View":
        map.render()
    elif selected == "AI 통역사":
        translate.render()
    elif selected == "날씨 예보":
        weather.render()
    elif selected == "N빵 정산":
        expenses.render()
    elif selected == "추억 앨범":
        gallery.render()

if __name__ == "__main__":
    main()
