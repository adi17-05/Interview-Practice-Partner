from __future__ import annotations

from collections import Counter
from typing import Dict, List, Any


def aggregate_weak_spots(sessions: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Aggregate weak-spot topics across all stored sessions.

    Each session is expected to have a `weak_spot_topics` list.
    """
    counter: Counter[str] = Counter()
    for session in sessions:
        for topic in session.get("weak_spot_topics", []):
            if topic:
                counter[topic] += 1
    return dict(counter)
