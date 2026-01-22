import streamlit as st
import os
from PIL import Image
import config

def render():
    st.markdown("<div class='section-title'>📸 추억 앨범</div>", unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "사진 추가하기", 
        type=['png', 'jpg', 'jpeg'], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button(f"{len(uploaded_files)}장 업로드"):
            for up_file in uploaded_files:
                save_path = config.PHOTOS_DIR / up_file.name
                with open(save_path, "wb") as f:
                    f.write(up_file.getbuffer())
            st.success("사진이 저장되었습니다!")
            st.rerun()
            
    # Load photos
    photos = [f for f in os.listdir(config.PHOTOS_DIR) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
    
    if not photos:
        st.info("아직 사진이 없어요. 첫 번째 사진을 올려보세요!")
        return
        
    # Simple Masonry-like Grid
    cols = st.columns(3)
    for idx, photo_name in enumerate(photos):
        col = cols[idx % 3]
        img_path = config.PHOTOS_DIR / photo_name
        try:
            image = Image.open(img_path)
            with col:
                st.image(image, use_column_width=True, caption=photo_name)
        except Exception:
            pass
