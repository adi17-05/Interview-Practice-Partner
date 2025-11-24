from __future__ import annotations

from typing import Optional

import io
import wave

from google.genai import types  # type: ignore

from interview_partner.config import settings
from interview_partner.core.llm import get_client


def transcribe_audio_bytes(audio_bytes: bytes, mime_type: str = "audio/wav") -> str:
    """
    Use Gemini audio understanding to transcribe user speech to text.

    This uses a text+audio prompt: we ask Gemini to transcribe exactly and
    return just the transcript as plain text.
    """
    client = get_client()

    # Build an audio Part from raw bytes
    audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)

    response = client.models.generate_content(
        model=settings.STT_MODEL,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        "Transcribe the spoken audio to plain text. "
                        "Return ONLY the raw transcript, no extra commentary."
                    ),
                    audio_part,
                ],
            )
        ],
    )

    # Validate response
    if response is None:
        raise RuntimeError("STT: Gemini API returned None response")

    if not hasattr(response, "text") or response.text is None:
        error_msg = "STT: No text in response"
        if hasattr(response, "prompt_feedback"):
            error_msg += f". Prompt feedback: {response.prompt_feedback}"
        raise RuntimeError(error_msg)

    return response.text.strip()


def text_to_speech_bytes(text: str) -> Optional[bytes]:
    """
    Convert text to spoken audio using Gemini TTS.

    Returns raw WAV bytes suitable for `st.audio(...)`.
    If TTS is not available or fails, returns None.
    """
    if not text.strip():
        return None

    client = get_client()

    try:
        response = client.models.generate_content(
            model=settings.TTS_MODEL,
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Kore"  # you can change this voice if you want
                        )
                    )
                ),
            ),
        )
    except Exception as e:
        # Fail gracefully; caller can fall back to text-only behavior.
        print(f"TTS generation failed: {e}")
        return None

    # Validate response structure
    if response is None:
        print("TTS: Response is None")
        return None

    if not hasattr(response, "candidates") or not response.candidates:
        print("TTS: No candidates in response")
        return None

    candidate = response.candidates[0]
    if not hasattr(candidate, "content") or candidate.content is None:
        print("TTS: No content in candidate")
        return None

    if not hasattr(candidate.content, "parts") or not candidate.content.parts:
        print("TTS: No parts in content")
        return None

    # Extract audio data from the first part that has inline_data
    for part in candidate.content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            data = part.inline_data.data

            # Wrap the PCM bytes in a WAV container so Streamlit can play it easily.
            buf = io.BytesIO()
            with wave.open(buf, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(24000)
                wf.writeframes(data)

            return buf.getvalue()

    print("TTS: No inline_data found in parts")
    return None
