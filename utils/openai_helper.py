from openai import OpenAI
import config
import base64
import io

def get_client(api_key: str):
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

def translate_text(text: str, source_lang: str, target_lang: str, api_key: str, model: str) -> str:
    client = get_client(api_key)
    if not client:
        raise RuntimeError("OpenAI API 키가 필요합니다.")

    system_prompt = (
        "You are a professional travel interpreter. "
        "Translate accurately, preserve meaning and nuance, and keep it natural. "
        "Return only the translation without extra commentary."
    )
    user_prompt = f"Translate from {source_lang} to {target_lang}.\n\nText:\n{text}"
    
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
    client = get_client(api_key)
    if not client:
        raise RuntimeError("OpenAI API 키가 필요합니다.")
        
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "voice.wav"
    
    kwargs = {"model": model, "file": audio_file}
    if language:
        kwargs["language"] = language
        
    response = client.audio.transcriptions.create(**kwargs)
    return response.text.strip()

def text_to_speech(text: str, api_key: str, model: str, voice: str) -> bytes:
    client = get_client(api_key)
    if not client:
        raise RuntimeError("OpenAI API 키가 필요합니다.")
        
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
    )
    return response.content

def extract_text_from_image(image_bytes: bytes, mime_type: str, api_key: str, model: str) -> str:
    client = get_client(api_key)
    if not client:
        raise RuntimeError("OpenAI API 키가 필요합니다.")
        
    data_url = f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('utf-8')}"
    prompt = (
        "Extract all visible text from this image. "
        "Preserve line breaks. Return only the text. "
        "If no text is visible, return an empty string."
    )
    
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
