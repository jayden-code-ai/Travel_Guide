import streamlit as st
import time
from utils import openai_helper
try:
    from streamlit_mic_recorder import mic_recorder
except ImportError:
    mic_recorder = None
import config

def render():
    st.markdown("<div class='section-title'>🗣️ AI 통역사</div>", unsafe_allow_html=True)
    st.caption("한국어 ↔ 일본어 실시간 번역")

    if not config.OPENAI_API_KEY:
        st.error("OpenAI API 키가 필요합니다.")
        return

    # Layout
    col_opt, col_blank = st.columns([1, 2])
    with col_opt:
        direction = st.radio("번역 방향", ["한국어 → 일본어", "일본어 → 한국어"], horizontal=True)

    source_lang = "Korean" if direction.startswith("한국어") else "Japanese"
    target_lang = "Japanese" if direction.startswith("한국어") else "Korean"

    tab_text, tab_photo = st.tabs(["💬 텍스트/음성", "📷 사진 번역"])

    # --- TEXT/VOICE ---
    with tab_text:
        # Voice Input
        st.markdown("##### 🎙️ 음성 입력")
        if mic_recorder:
            col_mic, col_status = st.columns([1, 4])
            with col_mic:
                audio = mic_recorder(
                    start_prompt="● 녹음",
                    stop_prompt="■ 정지",
                    just_once=True,
                    key="mic_recorder",
                )
            
            if audio and audio.get("bytes"):
                # Check if this is new audio
                if audio["bytes"] != st.session_state.get("last_mic_audio"):
                    st.session_state["last_mic_audio"] = audio["bytes"]
                    st.audio(audio["bytes"], format="audio/wav")
                    
                    # Auto Transcribe
                    lang_code = "ko" if source_lang == "Korean" else "ja"
                    with st.spinner("음성을 텍스트로 변환 중..."):
                        transcript = openai_helper.transcribe_audio(
                            audio["bytes"], 
                            config.OPENAI_API_KEY, 
                            config.OPENAI_STT_MODEL, 
                            lang_code
                        )
                        st.session_state["source_text_input"] = transcript
                        st.rerun()

        st.divider()

        # Text Input & Result
        col1, col2 = st.columns(2)
        with col1:
             # Widget will pick up value from st.session_state["source_text_input"]
            source_text = st.text_area("입력", height=150, key="source_text_input", placeholder="번역할 내용을 입력하세요.")
        with col2:
            st.text_area(
                "결과", 
                height=150, 
                value=st.session_state.get("trans_result", ""),
                disabled=True
            )

        col_act1, col_act2 = st.columns([1, 3])
        with col_act1:
            if st.button("번역하기", type="primary", use_container_width=True):
                if source_text:
                    with st.spinner("번역 중..."):
                        res = openai_helper.translate_text(
                            source_text, source_lang, target_lang, 
                            config.OPENAI_API_KEY, config.OPENAI_TRANSLATE_MODEL
                        )
                        st.session_state["trans_result"] = res
                        st.rerun()

        with col_act2:
            if st.button("🔊 결과 듣기"):
                target_text = st.session_state.get("trans_result", "")
                if target_text:
                    audio_data = openai_helper.text_to_speech(
                        target_text, config.OPENAI_API_KEY, 
                        config.OPENAI_TTS_MODEL, config.OPENAI_TTS_VOICE
                    )
                    st.audio(audio_data, format="audio/mp3", autoplay=True)

    # --- PHOTO ---
    with tab_photo:
        img_file = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg"])
        if img_file:
            st.image(img_file, width=300)
            if st.button("이미지에서 텍스트 추출 및 번역"):
                with st.spinner("분석 중..."):
                    extracted = openai_helper.extract_text_from_image(
                        img_file.getvalue(), img_file.type, 
                        config.OPENAI_API_KEY, config.OPENAI_OCR_MODEL
                    )
                    if extracted:
                        translated = openai_helper.translate_text(
                            extracted, "Any", "Korean", # Always translate to Korean for understanding
                            config.OPENAI_API_KEY, config.OPENAI_TRANSLATE_MODEL
                        )
                        st.session_state["ocr_extracted"] = extracted
                        st.session_state["ocr_translated"] = translated
                        st.rerun()
        
        if st.session_state.get("ocr_extracted"):
            c1, c2 = st.columns(2)
            c1.text_area("추출된 텍스트", st.session_state["ocr_extracted"], height=200)
            c2.text_area("번역 결과 (한국어)", st.session_state["ocr_translated"], height=200)
