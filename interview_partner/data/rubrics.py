from __future__ import annotations

from typing import Dict

RUBRIC_DESCRIPTIONS: Dict[str, str] = {
    "clarity": "How clearly and logically the candidate expresses their thoughts.",
    "technical_or_role_fit": (
        "How well the answer demonstrates the required technical or role-specific skills."
    ),
    "structure_STAR": (
        "How well the candidate structures their answer using STAR "
        "(Situation, Task, Action, Result) or a similar framework."
    ),
    "confidence": "Perceived confidence, ownership, and decisiveness (without arrogance).",
    "brevity": "How concise yet complete the answer is (no rambling, no missing key points).",
}

RUBRIC_TITLES: Dict[str, str] = {
    "clarity": "Communication Clarity",
    "technical_or_role_fit": "Technical & Role Fit",
    "structure_STAR": "Structural Integrity (STAR)",
    "confidence": "Professional Confidence",
    "brevity": "Conciseness",
}


def get_rubric_description(key: str) -> str:
    return RUBRIC_DESCRIPTIONS.get(key, "")
