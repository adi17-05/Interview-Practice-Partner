from __future__ import annotations

from typing import List


def extract_topics_from_resume(resume_text: str, job_description: str | None = None) -> List[str]:
    """
    Stub for future Resume RAG integration.

    For now, returns an empty list to keep the wiring simple. In a future version,
    this can:
    - chunk the resume and job description,
    - run them through a retrieval model,
    - and infer skill / topic gaps to feed into the InterviewerAgent.
    """
    _ = (resume_text, job_description)  # unused
    return []
