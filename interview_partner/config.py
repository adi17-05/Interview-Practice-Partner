from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    # Optional: make local development easier by loading a .env file if present
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover - dotenv is optional
    load_dotenv = None  # type: ignore


BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR  # alias


def _load_env() -> None:
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists() and load_dotenv is not None:
        load_dotenv(env_path)


_load_env()


@dataclass(frozen=True)
class Settings:
    """Global configuration for the Interview Practice Partner project."""

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    # Fast, cost-effective default text model
    DEFAULT_MODEL: str = os.getenv("GEMINI_MODEL_TEXT", "gemini-2.5-flash")
    CRITIC_MODEL: str = os.getenv("GEMINI_MODEL_CRITIC", "gemini-2.5-flash")
    STT_MODEL: str = os.getenv("GEMINI_MODEL_STT", "gemini-2.5-flash")
    # TTS model with native audio output
    TTS_MODEL: str = os.getenv("GEMINI_MODEL_TTS", "gemini-2.5-flash-preview-tts")

    # Where we store per-user memory JSON
    DATA_DIR: Path = PROJECT_ROOT / "storage"

    # Max questions per interview session
    MIN_QUESTIONS: int = 5
    MAX_QUESTIONS: int = 8


settings = Settings()
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
