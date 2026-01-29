"""OpenAI API 호출을 캡슐화하는 헬퍼 함수 모음."""

from openai import OpenAI
import config
import base64
import io

def get_client(api_key: str):
    """API 키 유무에 따라 OpenAI 클라이언트를 생성한다."""
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

def translate_text(text: str, source_lang: str, target_lang: str, api_key: str, model: str) -> str:
    """텍스트를 지정한 언어 쌍으로 번역한다."""
    client = get_client(api_key)
    if not client:
        raise RuntimeError("OpenAI API 키가 필요합니다.")

    # 시스템 프롬프트: 여행 통역 맥락에서 자연스러운 번역을 유도
    system_prompt = (
        "You are a professional travel interpreter. "
        "Translate accurately, preserve meaning and nuance, and keep it natural. "
        "Return only the translation without extra commentary."
    )
    # 사용자 프롬프트: 번역 방향과 원문 전달
    user_prompt = f"Translate from {source_lang} to {target_lang}.\n\nText:\n{text}"
    
    # 채팅 완성 API 호출
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=400,
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()

def transcribe_audio(audio_bytes: bytes, api_key: str, model: str, language: str = None) -> str:
    """음성 파일 바이트를 받아 텍스트로 전사한다."""
    client = get_client(api_key)
    if not client:
        raise RuntimeError("OpenAI API 키가 필요합니다.")
        
    # OpenAI API는 파일 객체를 요구하므로 메모리 파일로 감싼다
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "voice.wav"
    
    kwargs = {"model": model, "file": audio_file}
    # 언어 힌트를 제공하면 전사 정확도를 높일 수 있음
    if language:
        kwargs["language"] = language
        
    # 음성 인식(Transcription) 호출
    response = client.audio.transcriptions.create(**kwargs)
    return response.text.strip()

def text_to_speech(text: str, api_key: str, model: str, voice: str) -> bytes:
    """텍스트를 음성으로 변환해 MP3 바이트를 반환한다."""
    client = get_client(api_key)
    if not client:
        raise RuntimeError("OpenAI API 키가 필요합니다.")
        
    # TTS(Speech) 생성 요청
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
    )
    return response.content

def extract_text_from_image(image_bytes: bytes, mime_type: str, api_key: str, model: str) -> str:
    """이미지에서 텍스트를 추출(OCR)하여 반환한다."""
    client = get_client(api_key)
    if not client:
        raise RuntimeError("OpenAI API 키가 필요합니다.")
        
    # 멀티모달 입력을 위해 Data URL 포맷으로 변환
    data_url = f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('utf-8')}"
    # OCR 프롬프트: 줄바꿈 유지, 텍스트만 반환
    prompt = (
        "Extract all visible text from this image. "
        "Preserve line breaks. Return only the text. "
        "If no text is visible, return an empty string."
    )
    
    # 이미지 + 텍스트 입력으로 비전 모델 호출
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
        max_tokens=400,
        temperature=0,
    )
    return response.choices[0].message.content.strip()
