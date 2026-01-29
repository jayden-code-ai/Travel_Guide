"""추억 앨범 화면: 사진 업로드 및 갤러리 표시."""

import streamlit as st
import os
from PIL import Image
import config

def render():
    """사진 업로드와 갤러리 표시를 담당한다."""
    st.markdown("<div class='section-title'>📸 추억 앨범</div>", unsafe_allow_html=True)
    
    # 다중 파일 업로드 입력
    uploaded_files = st.file_uploader(
        "사진 추가하기", 
        type=['png', 'jpg', 'jpeg'], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button(f"{len(uploaded_files)}장 업로드"):
            # 업로드된 파일을 로컬 사진 디렉터리에 저장
            for up_file in uploaded_files:
                save_path = config.PHOTOS_DIR / up_file.name
                with open(save_path, "wb") as f:
                    f.write(up_file.getbuffer())
            st.success("사진이 저장되었습니다!")
            st.rerun()
            
    # 저장된 사진 목록 로드
    photos = [f for f in os.listdir(config.PHOTOS_DIR) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
    
    if not photos:
        st.info("아직 사진이 없어요. 첫 번째 사진을 올려보세요!")
        return
        
    # 간단한 3열 갤러리 그리드
    cols = st.columns(3)
    for idx, photo_name in enumerate(photos):
        col = cols[idx % 3]
        img_path = config.PHOTOS_DIR / photo_name
        try:
            # 이미지 로드 후 해당 컬럼에 표시
            image = Image.open(img_path)
            with col:
                st.image(image, use_column_width=True, caption=photo_name)
        except Exception:
            # 손상된 파일은 조용히 무시
            pass
