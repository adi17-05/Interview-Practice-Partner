from __future__ import annotations

import time
from typing import Any, Optional

from google import genai  # type: ignore
from google.genai import types  # type: ignore

from interview_partner.config import settings

_client: Optional[genai.Client] = None


def get_client() -> genai.Client:
    """
    Return a singleton Gemini GenAI client configured with GEMINI_API_KEY.
    """
    global _client
    if _client is None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. "
                "Create a .env file with GEMINI_API_KEY=your_key_here."
            )
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def chat_completion(
    *,
    system_prompt: str = "",
    user_prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.4,
    max_output_tokens: int = 512,
    json_mode: bool = False,
    max_retries: int = 3,
) -> str:
    """
    Lightweight wrapper around Gemini `generate_content` with retry logic.

    - `system_prompt` is inlined before the `user_prompt`.
    - When `json_mode=True`, we set `response_mime_type="application/json"`
      so the model returns a JSON *string*, which the caller can parse.
    - Retries up to `max_retries` times with exponential backoff on failures.
    """
    client = get_client()

    if system_prompt:
        prompt = f"{system_prompt.strip()}\n\nUser:\n{user_prompt.strip()}"
    else:
        prompt = user_prompt

    config_kwargs: dict[str, Any] = {
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
    }
    if json_mode:
        # Ask Gemini explicitly for JSON output
        config_kwargs["response_mime_type"] = "application/json"

    gen_config = types.GenerateContentConfig(**config_kwargs)

    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model or settings.DEFAULT_MODEL,
                contents=[
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)],
                    )
                ],
                config=gen_config,
            )

            if response is None:
                raise RuntimeError("Gemini API returned None response. Check your API key and quota.")

            # --- Try to extract text robustly ---------------------------------------
            text: Optional[str] = getattr(response, "text", None)

            # Some SDK / modality combos don't populate response.text,
            # but the text is in candidates[*].content.parts[*].text
            if not text:
                candidates = getattr(response, "candidates", None)
                if candidates:
                    for cand in candidates:
                        content = getattr(cand, "content", None)
                        if not content:
                            continue
                        parts = getattr(content, "parts", None) or []
                        collected: list[str] = []
                        for part in parts:
                            part_text = getattr(part, "text", None)
                            if part_text:
                                collected.append(part_text)
                        if collected:
                            text = "".join(collected)
                            break

            if not text:
                # Check for safety/content filtering
                error_msg = "Gemini API response has no text content."
                if hasattr(response, "prompt_feedback"):
                    feedback = response.prompt_feedback
                    error_msg += f" Prompt feedback: {feedback}"
                    # If blocked by safety, don't retry
                    if hasattr(feedback, "block_reason") and feedback.block_reason:
                        raise RuntimeError(f"{error_msg} - Content blocked by safety filters.")
                
                # If it's attempt < max_retries, we'll retry
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    print(f"Empty response on attempt {attempt + 1}/{max_retries}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise RuntimeError(error_msg)

            return text.strip()
            
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"API error on attempt {attempt + 1}/{max_retries}: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise

    # Should not reach here, but just in case
    if last_error:
        raise last_error
    raise RuntimeError("Failed to get response from Gemini API after retries.")
