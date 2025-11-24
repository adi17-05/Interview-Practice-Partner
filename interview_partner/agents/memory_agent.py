from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from interview_partner.config import settings
from interview_partner.services.weak_spots import aggregate_weak_spots


@dataclass
class MemoryAgent:
    """
    Lightweight per-user memory / personalization layer.

    Stores:
    - session summaries
    - aggregated weak-spot frequencies
    """

    user_id: str
    storage_dir: Path = field(default=settings.DATA_DIR)

    def __post_init__(self) -> None:
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._path = self.storage_dir / f"{self.user_id}_memory.json"

    # Internal helpers ----------------------------------------------------- #
    def _load(self) -> Dict[str, Any]:
        if not self._path.exists():
            return {"user_id": self.user_id, "sessions": [], "weak_spots": {}}
        try:
            with self._path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"user_id": self.user_id, "sessions": [], "weak_spots": {}}

    def _save(self, data: Dict[str, Any]) -> None:
        with self._path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # Public API ----------------------------------------------------------- #
    def add_session_summary(self, summary: Dict[str, Any]) -> None:
        data = self._load()
        sessions: List[Dict[str, Any]] = data.get("sessions", [])
        timestamp = datetime.utcnow().isoformat() + "Z"

        session_record = {
            "timestamp": timestamp,
            **summary,
        }
        sessions.append(session_record)
        data["sessions"] = sessions

        # Recompute weak-spot aggregates over all sessions.
        data["weak_spots"] = aggregate_weak_spots(sessions)
        self._save(data)

    def get_weak_spots(self, top_k: int = 6) -> List[str]:
        data = self._load()
        weak_spots_map: Dict[str, int] = data.get("weak_spots", {})
        # Sort by frequency descending.
        sorted_topics = sorted(
            weak_spots_map.items(), key=lambda kv: kv[1], reverse=True
        )
        return [topic for topic, _ in sorted_topics[:top_k]]

    def get_latest_session(self) -> Optional[Dict[str, Any]]:
        data = self._load()
        sessions: List[Dict[str, Any]] = data.get("sessions", [])
        if not sessions:
            return None
        return sessions[-1]
