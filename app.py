from __future__ import annotations

import base64
import io
import os
import re
import time
from datetime import date, datetime, time as dt_time
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency at runtime
    OpenAI = None
try:
    from streamlit_mic_recorder import mic_recorder
except Exception:  # pragma: no cover - optional dependency at runtime
    mic_recorder = None

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "schedule.csv"
BACKUP_PATH = BASE_DIR / "data" / "schedule.backup.csv"
SECRETS_PATHS = [
    Path.home() / ".streamlit" / "secrets.toml",
    BASE_DIR / ".streamlit" / "secrets.toml",
]

APP_TITLE = "지민쓰와 떠나는 후쿠오카 찐친 패밀리 투어"
TRIP_YEAR = 2026
AUTO_TRANSLATE_COOLDOWN_SEC = 1.2

EXPECTED_COLS = ["날짜", "시간", "구분", "내용", "장소", "지도검색어", "이동수단"]
NOTE_KEYWORDS = {
    "체험",
    "식사",
    "이동",
    "탑승",
    "복귀",
    "휴식",
    "구경",
    "관람",
    "산책",
    "쇼핑",
    "대기",
    "정리",
    "짐",
    "이용",
    "체크인",
    "체크아웃",
    "자유",
    "환승",
    "셔틀",
    "시간",
}


def load_env() -> None:
    load_dotenv()


def secrets_file_exists() -> bool:
    return any(path.exists() for path in SECRETS_PATHS)


def normalize_model_name(name: str) -> str:
    cleaned = name.strip()
    if not cleaned:
        return cleaned
    return cleaned.lower().replace(" ", "-")


def get_secret(name: str, default: str = "") -> str:
    if secrets_file_exists():
        try:
            if name in st.secrets:
                return str(st.secrets[name]).strip()
        except Exception:
            pass
    return os.getenv(name, default).strip()


def ensure_data_file() -> None:
    if DATA_PATH.exists():
        return
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    seed = pd.DataFrame(
        [
            {"날짜": "3/4 (수)", "시간": "09:20", "구분": "도착", "내용": "후쿠오카 공항 도착", "장소": "", "이동수단": ""},
        ]
    )
    seed.to_csv(DATA_PATH, index=False)


def load_schedule() -> pd.DataFrame:
    ensure_data_file()
    df = pd.read_csv(DATA_PATH, dtype=str).fillna("")
    for col in EXPECTED_COLS:
        if col not in df.columns:
            df[col] = ""
    df = df[EXPECTED_COLS]
    return df


def save_schedule(df: pd.DataFrame) -> None:
    BACKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DATA_PATH.exists():
        DATA_PATH.replace(BACKUP_PATH)
    df.to_csv(DATA_PATH, index=False)


def parse_date(raw: str) -> Optional[date]:
    if not raw:
        return None
    match = re.search(r"(\d{1,2})\s*/\s*(\d{1,2})", raw)
    if not match:
        return None
    month, day = int(match.group(1)), int(match.group(2))
    try:
        return date(TRIP_YEAR, month, day)
    except ValueError:
        return None


def parse_time(raw: str) -> Optional[dt_time]:
    if not raw:
        return None
    match = re.search(r"(\d{1,2}):(\d{2})", raw)
    if not match:
        return None
    hour, minute = int(match.group(1)), int(match.group(2))
    try:
        return dt_time(hour, minute)
    except ValueError:
        return None


def time_bucket(t: Optional[dt_time]) -> str:
    if not t:
        return "기타"
    if t < dt_time(12, 0):
        return "오전"
    if t < dt_time(18, 0):
        return "오후"
    return "저녁"


def build_view_df(df: pd.DataFrame) -> pd.DataFrame:
    view = df.copy()
    view["_date"] = view["날짜"].apply(parse_date)
    view["_time"] = view["시간"].apply(parse_time)
    view["시간대"] = view["_time"].apply(time_bucket)
    view["지도검색어"] = view.get("지도검색어", "")
    view["_map_query"] = view.apply(
        lambda row: choose_map_query(row["내용"], row["장소"], row["지도검색어"]),
        axis=1,
    )
    view["지도표시"] = view["_map_query"]
    view["지도"] = view["_map_query"].apply(make_maps_search_link)
    view = view.sort_values(by=["_date", "_time"], na_position="last")
    return view


def make_maps_search_link(place: str) -> str:
    if not place:
        return ""
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(place)}"


def looks_like_note(text: str) -> bool:
    compact = text.replace(" ", "")
    return any(keyword in compact for keyword in NOTE_KEYWORDS)


def strip_note_parentheses(text: str) -> str:
    if not text:
        return ""

    def _replace(match: re.Match[str]) -> str:
        inner = match.group(1)
        return "" if looks_like_note(inner) else match.group(0)

    cleaned = re.sub(r"\(([^()]*)\)", _replace, text)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip(" -")
    return cleaned.strip()


def choose_map_query(content: str, place: str, override: str) -> str:
    if override:
        return override.strip()
    place_clean = strip_note_parentheses(place)
    content_clean = strip_note_parentheses(content)
    if place_clean and not looks_like_note(place_clean):
        return place_clean
    if content_clean and not looks_like_note(content_clean):
        return content_clean
    return place_clean or content_clean


def translate_text(text: str, source_lang: str, target_lang: str, api_key: str, model: str) -> str:
    if not OpenAI:
        raise RuntimeError("openai 패키지가 설치되어 있지 않습니다.")
    client = OpenAI(api_key=api_key)
    system_prompt = (
        "You are a professional travel interpreter. "
        "Translate accurately, preserve meaning and nuance, and keep it natural. "
        "Return only the translation without extra commentary."
    )
    user_prompt = (
        f"Translate from {source_lang} to {target_lang}.\n\n"
        f"Text:\n{text}"
    )
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_output_tokens=400,
        temperature=0.2,
    )
    return response.output_text.strip()


def transcribe_audio(
    audio_bytes: bytes, api_key: str, model: str, language: Optional[str]
) -> str:
    if not OpenAI:
        raise RuntimeError("openai 패키지가 설치되어 있지 않습니다.")
    client = OpenAI(api_key=api_key)
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "voice.wav"
    kwargs = {"model": model, "file": audio_file}
    if language:
        kwargs["language"] = language
    response = client.audio.transcriptions.create(**kwargs)
    return response.text.strip()


def text_to_speech(text: str, api_key: str, model: str, voice: str) -> bytes:
    if not OpenAI:
        raise RuntimeError("openai 패키지가 설치되어 있지 않습니다.")
    client = OpenAI(api_key=api_key)
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
    )
    return response.content


def extract_text_from_image(
    image_bytes: bytes, mime_type: str, api_key: str, model: str
) -> str:
    if not OpenAI:
        raise RuntimeError("openai 패키지가 설치되어 있지 않습니다.")
    client = OpenAI(api_key=api_key)
    data_url = f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('utf-8')}"
    prompt = (
        "Extract all visible text from this image. "
        "Preserve line breaks. Return only the text. "
        "If no text is visible, return an empty string."
    )
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": data_url},
                ],
            }
        ],
        max_output_tokens=400,
        temperature=0,
    )
    return response.output_text.strip()


def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Jua&display=swap');
        html, body, [class*="css"]  {
            font-family: 'Gowun Dodum', sans-serif;
        }
        .main {
            background: linear-gradient(180deg, #fff8f0 0%, #f7f8ff 60%, #fff 100%);
        }
        .hero {
            background: #fff2e9;
            border: 2px dashed #ffb4a2;
            padding: 16px 20px;
            border-radius: 16px;
            margin-bottom: 18px;
        }
        .pill {
            display: inline-block;
            background: #ffe4c7;
            padding: 4px 10px;
            border-radius: 999px;
            margin-right: 6px;
            font-size: 0.85rem;
        }
        .section-title {
            font-family: 'Jua', sans-serif;
            font-size: 1.4rem;
            margin-top: 10px;
        }
        .schedule-card {
            background: #ffffff;
            border: 1px solid #f1d4c9;
            padding: 12px 14px;
            border-radius: 14px;
            margin-bottom: 10px;
            box-shadow: 0 6px 16px rgba(255, 180, 162, 0.15);
        }
        .muted {
            color: #666;
            font-size: 0.9rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_schedule_section(df: pd.DataFrame, maps_api_key: str) -> None:
    st.markdown("<div class='section-title'>🗓️ 일정</div>", unsafe_allow_html=True)
    view = build_view_df(df)

    date_options = [d for d in view["날짜"].dropna().unique().tolist() if d]
    date_options = sorted(date_options, key=lambda v: parse_date(v) or date.max)

    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        selected_dates = st.multiselect("날짜 선택", date_options, default=date_options)
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
        table = filtered[
            ["날짜", "시간", "구분", "내용", "지도표시", "이동수단", "지도"]
        ].copy()
        table = table.rename(columns={"지도표시": "장소(지도)"})
        st.dataframe(
            table,
            use_container_width=True,
            column_config={
                "지도": st.column_config.LinkColumn("지도", display_text="지도 열기"),
            },
            hide_index=True,
        )
    else:
        for day, group in filtered.groupby("날짜"):
            st.subheader(day)
            for _, row in group.iterrows():
                place = row.get("지도표시", "").strip()
                map_link = row["지도"].strip()
                st.markdown("<div class='schedule-card'>", unsafe_allow_html=True)
                st.markdown(
                    f"<span class='pill'>{row['시간대']}</span>"
                    f"<strong>{row['시간']} · {row['구분']}</strong>",
                    unsafe_allow_html=True,
                )
                st.write(row["내용"])
                if place and map_link:
                    st.markdown(f"📍 [{place}]({map_link})")
                if row["이동수단"]:
                    st.markdown(f"<span class='muted'>이동수단: {row['이동수단']}</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("<div class='section-title'>✍️ 일정 수정</div>", unsafe_allow_html=True)
    st.caption("수정 후 저장하면 다음 실행에도 그대로 유지돼요.")

    auto_save = st.toggle("자동 저장", value=True, help="수정할 때마다 파일에 바로 저장됩니다.")

    def _auto_save() -> None:
        edited = st.session_state.get("schedule_editor")
        if isinstance(edited, pd.DataFrame):
            save_schedule(edited)
            st.session_state["last_saved"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    editor_kwargs = {
        "num_rows": "dynamic",
        "use_container_width": True,
        "hide_index": True,
        "column_order": EXPECTED_COLS,
        "column_config": {
            "날짜": st.column_config.TextColumn("날짜", help="예: 3/4 (수)"),
            "시간": st.column_config.TextColumn("시간", help="예: 09:20"),
            "지도검색어": st.column_config.TextColumn("지도검색어", help="지도에 찍힐 정확한 장소 (선택)"),
        },
        "key": "schedule_editor",
    }

    if auto_save:
        st.data_editor(df, on_change=_auto_save, **editor_kwargs)
    else:
        edited_df = st.data_editor(df, **editor_kwargs)
        if st.button("저장하기", type="primary"):
            save_schedule(edited_df)
            st.success("저장 완료!")

    if st.session_state.get("last_saved"):
        st.caption(f"마지막 저장: {st.session_state['last_saved']}")

    if maps_api_key:
        st.caption("장소 링크 클릭 시 Google 지도에서 바로 열립니다.")
    else:
        st.caption("Google Maps API 키를 넣으면 지도 화면도 표시할 수 있어요.")


def render_map_section(maps_api_key: str, df: pd.DataFrame) -> None:
    st.markdown("<div class='section-title'>🗺️ 지도</div>", unsafe_allow_html=True)
    st.caption("일정에 있는 장소를 지도에서 확인해요.")

    view = build_view_df(df)
    places = sorted({p for p in view["지도표시"].dropna().tolist() if p.strip()})
    choice = st.selectbox("장소 선택", ["직접 입력"] + places)
    if choice == "직접 입력":
        place = st.text_input("장소 입력", placeholder="예: 하카타역")
    else:
        place = choice

    if not place:
        return

    map_link = make_maps_search_link(place)
    st.markdown(f"📍 [Google 지도에서 열기]({map_link})")

    if not maps_api_key:
        st.info("Google Maps API 키를 설정하면 지도 화면이 바로 표시됩니다.")
        return

    embed_url = (
        "https://www.google.com/maps/embed/v1/place"
        f"?key={maps_api_key}&q={quote_plus(place)}"
    )
    st.components.v1.iframe(embed_url, height=420)


def render_translate_section(
    api_key: str,
    model: str,
    stt_model: str,
    tts_model: str,
    tts_voice: str,
    translate_model: str,
    ocr_model: str,
) -> None:
    st.markdown("<div class='section-title'>🗣️ 번역</div>", unsafe_allow_html=True)
    st.caption("한국어 ↔ 일본어 전용 번역기")

    direction = st.radio("번역 방향", ["한국어 → 일본어", "일본어 → 한국어"], horizontal=True)

    def _do_translate(text: str) -> Optional[str]:
        if not api_key:
            st.error("OpenAI API 키가 필요합니다. .env 또는 Secrets를 확인해주세요.")
            return None
        if not translate_model:
            st.error("번역 모델이 비어있어요. OPENAI_TRANSLATE_MODEL을 설정해주세요.")
            return None
        source_lang = "Korean" if direction.startswith("한국어") else "Japanese"
        target_lang = "Japanese" if direction.startswith("한국어") else "Korean"
        cache = st.session_state.setdefault("translation_cache", {})
        cache_key = f"{source_lang}->{target_lang}:{text}"
        if cache_key in cache:
            return cache[cache_key]
        with st.spinner("번역 중..."):
            try:
                translated = translate_text(text, source_lang, target_lang, api_key, translate_model)
            except Exception as exc:  # pragma: no cover - network
                st.error(f"번역 실패: {exc}")
                return None
        cache[cache_key] = translated
        return translated

    tab_text, tab_photo = st.tabs(["💬 텍스트 번역", "📷 사진 번역"])

    with tab_text:
        st.markdown("**🎙️ 음성 입력 (선택)**")
        st.caption("마이크로 입력한 내용을 자동으로 텍스트로 변환해요.")

        if mic_recorder is None:
            st.info("음성 입력을 사용하려면 `pip install streamlit-mic-recorder`가 필요합니다.")
        else:
            audio = mic_recorder(
                start_prompt="🎙️ 녹음 시작",
                stop_prompt="⏹️ 녹음 종료",
                just_once=True,
                key="mic_recorder",
            )
            if audio and audio.get("bytes"):
                st.session_state["mic_audio"] = audio["bytes"]
                st.audio(audio["bytes"], format="audio/wav")
            if st.button("음성 → 텍스트 변환"):
                if not api_key:
                    st.error("OpenAI API 키가 필요합니다. .env를 확인해주세요.")
                elif not stt_model:
                    st.error("STT 모델이 비어있어요. OPENAI_STT_MODEL을 설정해주세요.")
                elif not st.session_state.get("mic_audio"):
                    st.warning("먼저 음성을 녹음해주세요.")
                else:
                    language = "ko" if direction.startswith("한국어") else "ja"
                    with st.spinner("음성 인식 중..."):
                        try:
                            transcript = transcribe_audio(
                                st.session_state["mic_audio"], api_key, stt_model, language
                            )
                        except Exception as exc:  # pragma: no cover - network
                            st.error(f"음성 인식 실패: {exc}")
                        else:
                            st.session_state["source_text"] = transcript

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            source_text = st.text_area(
                "원문",
                height=180,
                key="source_text",
                placeholder="여기에 입력",
            )
        with col2:
            result_text = st.text_area(
                "번역 결과",
                height=180,
                value=st.session_state.get("translation_result", ""),
                disabled=True,
            )

        auto_translate = st.toggle(
            "자동 번역 (입력 변경 시)",
            value=False,
            help="입력할 때마다 자동으로 번역합니다. 속도/비용이 늘 수 있어요.",
        )

        if st.button("번역하기", type="primary"):
            if not source_text.strip():
                st.warning("번역할 문장을 입력해주세요.")
                return
            translated = _do_translate(source_text.strip())
            if translated is not None:
                st.session_state["translation_result"] = translated

        if auto_translate and source_text.strip():
            last_text = st.session_state.get("last_auto_translate_text", "")
            last_time = st.session_state.get("last_auto_translate_time", 0.0)
            now = time.time()
            if source_text.strip() != last_text and now - last_time >= AUTO_TRANSLATE_COOLDOWN_SEC:
                translated = _do_translate(source_text.strip())
                if translated is not None:
                    st.session_state["translation_result"] = translated
                    st.session_state["last_auto_translate_text"] = source_text.strip()
                    st.session_state["last_auto_translate_time"] = now

        st.divider()
        st.markdown("**🔊 번역 결과 음성 (선택)**")
        voice_options = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        default_voice_index = (
            voice_options.index(tts_voice) if tts_voice in voice_options else 0
        )
        voice = st.selectbox(
            "음성 선택",
            voice_options,
            index=default_voice_index,
            help="OpenAI TTS 보이스 선택",
        )
        if st.button("번역 결과 듣기"):
            translated_text = st.session_state.get("translation_result", "").strip()
            if not translated_text:
                st.warning("먼저 번역을 완료해주세요.")
                return
            if not api_key:
                st.error("OpenAI API 키가 필요합니다. .env를 확인해주세요.")
                return
            if not tts_model:
                st.error("TTS 모델이 비어있어요. OPENAI_TTS_MODEL을 설정해주세요.")
                return
            if tts_model == "gpt-5-mini-tts":
                st.error("gpt-5-mini-tts는 지원되지 않습니다. gpt-4o-mini-tts 또는 tts-1/tts-1-hd를 사용하세요.")
                return
            with st.spinner("음성 생성 중..."):
                try:
                    audio_bytes = text_to_speech(translated_text, api_key, tts_model, voice)
                except Exception as exc:  # pragma: no cover - network
                    st.error(f"음성 생성 실패: {exc}")
                    return
            st.audio(audio_bytes, format="audio/mp3")

    with tab_photo:
        st.markdown("**📷 사진 번역 (수동)**")
        st.caption("카메라 촬영 또는 이미지 업로드 후 버튼을 눌러 번역하세요.")

        input_mode = st.radio(
            "사진 입력 방식",
            ["선택 안 함", "카메라 촬영", "이미지 업로드"],
            horizontal=True,
        )

        camera_image = None
        upload_image = None
        if input_mode == "카메라 촬영":
            camera_image = st.camera_input("카메라 촬영")
        elif input_mode == "이미지 업로드":
            upload_image = st.file_uploader(
                "이미지 업로드",
                type=["png", "jpg", "jpeg", "webp"],
                accept_multiple_files=False,
            )

        image_file = camera_image or upload_image
        if image_file is not None:
            st.image(image_file, use_column_width=True)

        if st.button("사진에서 번역하기"):
            if not api_key:
                st.error("OpenAI API 키가 필요합니다. .env 또는 Secrets를 확인해주세요.")
            elif not ocr_model:
                st.error("OCR 모델이 비어있어요. OPENAI_OCR_MODEL을 설정해주세요.")
            elif image_file is None:
                st.warning("먼저 카메라 촬영 또는 이미지 업로드를 해주세요.")
            else:
                with st.spinner("이미지 텍스트 추출 중..."):
                    try:
                        image_bytes = image_file.getvalue()
                        mime_type = getattr(image_file, "type", None) or "image/jpeg"
                        ocr_text = extract_text_from_image(image_bytes, mime_type, api_key, ocr_model)
                    except Exception as exc:  # pragma: no cover - network
                        st.error(f"OCR 실패: {exc}")
                        ocr_text = ""
                if not ocr_text.strip():
                    st.warning("이미지에서 텍스트를 찾지 못했어요. 다른 사진을 시도해보세요.")
                else:
                    st.session_state["photo_source_text"] = ocr_text
                    translated = _do_translate(ocr_text.strip())
                    if translated is not None:
                        st.session_state["photo_translation_result"] = translated

        st.divider()
        colp1, colp2 = st.columns(2)
        with colp1:
            st.text_area(
                "사진에서 추출된 텍스트",
                height=180,
                value=st.session_state.get("photo_source_text", ""),
                disabled=True,
            )
        with colp2:
            st.text_area(
                "사진 번역 결과",
                height=180,
                value=st.session_state.get("photo_translation_result", ""),
                disabled=True,
            )


def render_sidebar() -> str:
    st.sidebar.markdown("### 메뉴")
    section = st.sidebar.radio("탭", ["일정", "지도", "번역"], index=0)
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🔎 구글 빠른 검색 (외부 링크)**")
    quick_query = st.sidebar.text_input("검색어", placeholder="예: 후쿠오카 맛집")
    if quick_query:
        search_link = f"https://www.google.com/search?q={quote_plus(quick_query)}"
        st.sidebar.markdown(f"[구글에서 검색하기]({search_link})")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**빠른 정보**")
    st.sidebar.write("- 여행: 2026.03.04 ~ 03.07")
    st.sidebar.write("- 인원: 5명")
    st.sidebar.write("- 호텔: APA Hotel Hakata Eki Chikushiguchi")
    return section


def main() -> None:
    load_env()
    st.set_page_config(page_title=APP_TITLE, page_icon="🧳", layout="wide")
    inject_css()

    st.markdown(
        """
        <div class="hero">
            <h2>🧳 지민쓰와 함께하는 기념 여행</h2>
            <div>가족이지만 친구처럼! 웃음 가득한 후쿠오카 3박 4일 🎉</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.title(APP_TITLE)

    api_key = get_secret("OPENAI_API_KEY")
    model = normalize_model_name(get_secret("OPENAI_MODEL", "gpt-4o-mini"))
    translate_model = normalize_model_name(get_secret("OPENAI_TRANSLATE_MODEL", "gpt-4o-mini"))
    stt_model = normalize_model_name(get_secret("OPENAI_STT_MODEL", "whisper-1"))
    ocr_model = normalize_model_name(get_secret("OPENAI_OCR_MODEL", "gpt-4o-mini"))
    tts_model = normalize_model_name(get_secret("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"))
    tts_voice = get_secret("OPENAI_TTS_VOICE", "alloy")
    maps_api_key = get_secret("GOOGLE_MAPS_API_KEY")

    section = render_sidebar()

    df = load_schedule()

    if section == "일정":
        render_schedule_section(df, maps_api_key)
    elif section == "지도":
        render_map_section(maps_api_key, df)
    elif section == "번역":
        render_translate_section(
            api_key,
            model,
            stt_model,
            tts_model,
            tts_voice,
            translate_model,
            ocr_model,
        )


if __name__ == "__main__":
    main()
