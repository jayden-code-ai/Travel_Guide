"""지출 기록 및 간단 환율 계산 화면을 제공하는 뷰."""

import streamlit as st
import pandas as pd
from utils import data_manager
import config

def render():
    """지출 기록 화면(환율 계산기 + 지출 내역)을 렌더링한다."""
    st.markdown("<div class='section-title'>💰 지출 기록</div>", unsafe_allow_html=True)
    
    # 환율 계산기 탭과 지출 내역 탭을 분리
    tab_calc, tab_log = st.tabs(["💱 환율 계산기", "📝 지출 내역"])
    
    with tab_calc:
        st.subheader("엔화(JPY) ↔ 원화(KRW) 간편 계산")
        st.caption("고정 환율: 100엔 = 900원 (대략적 계산용)")
        
        # 단순 계산용 고정 환율(1 JPY = 9 KRW)
        EXCHANGE_RATE = 9.0  # 100 JPY = 900 KRW -> 1 JPY = 9 KRW
        
        col1, col2 = st.columns(2)
        with col1:
            # 엔화를 입력하면 원화로 환산
            jpy = st.number_input("엔화 (¥)", min_value=0, step=100, value=1000)
            krw_converted = jpy * EXCHANGE_RATE
            st.metric("원화 환산 (약)", f"{krw_converted:,.0f}원")
            
        with col2:
            # 원화를 입력하면 엔화로 환산
            krw = st.number_input("원화 (₩)", min_value=0, step=1000, value=10000)
            jpy_converted = krw / EXCHANGE_RATE
            st.metric("엔화 환산 (약)", f"{jpy_converted:,.0f}엔")
            
    with tab_log:
        st.subheader("지출 내역")
        # 저장된 지출 데이터를 불러와 편집 테이블로 표시
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
        
        # 저장 버튼 클릭 시 CSV에 반영
        if st.button("저장하기", type="secondary"):
            data_manager.save_expenses(edited_df)
            st.toast("저장되었습니다.")
            
        if not edited_df.empty:
            # 금액 합계를 계산해 요약 표시
            total_spent = pd.to_numeric(edited_df["금액"], errors='coerce').sum()
            st.metric(label="총 지출 합계", value=f"{total_spent:,.0f}")
