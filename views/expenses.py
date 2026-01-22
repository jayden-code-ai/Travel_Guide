import streamlit as st
import pandas as pd
from utils import data_manager
import config

def render():
    st.markdown("<div class='section-title'>💰 N빵 정산</div>", unsafe_allow_html=True)
    
    tab_calc, tab_log = st.tabs(["🧮 1/N 계산기", "📝 지출 기록"])
    
    with tab_calc:
        st.subheader("간편 계산기")
        total = st.number_input("총 금액 (엔/원)", min_value=0, step=100)
        people = st.number_input("인원 수", min_value=1, value=5, step=1)
        
        if total > 0:
            per_person = total / people
            st.success(f"한 사람당: **{per_person:,.0f}**")
            
    with tab_log:
        st.subheader("지출 내역")
        df = data_manager.load_expenses()
        
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            key="expenses_editor",
            column_config={
                "금액": st.column_config.NumberColumn("금액", format="%d")
            }
        )
        
        if st.button("저장하기", type="secondary"):
            data_manager.save_expenses(edited_df)
            st.toast("저장되었습니다.")
            
        if not edited_df.empty:
            total_spent = pd.to_numeric(edited_df["금액"], errors='coerce').sum()
            st.metric(label="총 지출 합계", value=f"{total_spent:,.0f}")
