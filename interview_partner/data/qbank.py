from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Question:
    text: str
    topic: str
    tags: List[str]


# A small but easily extensible role-based question bank.
QUESTION_BANK: Dict[str, List[Question]] = {
    "Software Engineer": [
        Question(
            text="Tell me about a time you debugged a particularly hard production issue.",
            topic="behavioral",
            tags=["STAR_method", "debugging", "ownership"],
        ),
        Question(
            text="Describe how you would design a rate limiter for an HTTP API.",
            topic="system_design",
            tags=["system_design", "scalability"],
        ),
        Question(
            text="Walk me through a piece of code you wrote that you're proud of.",
            topic="technical_experience",
            tags=["coding", "communication"],
        ),
        Question(
            text="How do you ensure code quality and reliability in your projects?",
            topic="process",
            tags=["testing", "code_review"],
        ),
    ],
    "Sales": [
        Question(
            text="Describe a time you turned around a difficult customer situation.",
            topic="behavioral",
            tags=["relationship_building", "objection_handling"],
        ),
        Question(
            text="How do you qualify and prioritize leads in your pipeline?",
            topic="sales_process",
            tags=["qualification", "prioritization"],
        ),
        Question(
            text="Walk me through your discovery process for a new prospect.",
            topic="discovery",
            tags=["questioning", "listening"],
        ),
    ],
    "Customer Support": [
        Question(
            text="Tell me about a time you handled an escalated, frustrated customer.",
            topic="behavioral",
            tags=["de_escalation", "empathy"],
        ),
        Question(
            text="How do you balance speed and quality when handling support tickets?",
            topic="prioritization",
            tags=["time_management", "quality"],
        ),
        Question(
            text="Describe your approach to documenting and sharing recurring issues.",
            topic="process",
            tags=["documentation", "collaboration"],
        ),
    ],
}


def get_questions_for_role(role: str) -> List[Question]:
    """Return a copy of the questions for the given role (or a generic set)."""
    if role in QUESTION_BANK:
        return list(QUESTION_BANK[role])

    # Fallback generic questions if an unknown role is requested.
    return [
        Question(
            text="Tell me about a time you faced a major challenge at work and how you handled it.",
            topic="behavioral",
            tags=["STAR_method"],
        ),
        Question(
            text="What do you consider your strongest professional skill, and why?",
            topic="self_assessment",
            tags=["self_awareness"],
        ),
        Question(
            text="Describe a situation where you had to collaborate with a difficult teammate.",
            topic="collaboration",
            tags=["communication", "teamwork"],
        ),
    ]
