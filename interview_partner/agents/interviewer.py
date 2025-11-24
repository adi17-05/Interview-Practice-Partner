from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from interview_partner.core import llm
from interview_partner.core import prompts
from interview_partner.data.qbank import Question, get_questions_for_role


@dataclass
class InterviewerAgent:
    """
    Handles visible interview behavior:
    - Pulls questions from a role-specific bank.
    - Generates follow-up questions via LLM when needed.
    """

    role: str
    tone: str = "neutral"  # friendly | neutral | grilling
    mode: str = "normal"  # normal | drill
    topics: Optional[List[str]] = None

    _scripted_questions: List[Question] = field(init=False)
    _index: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        questions = get_questions_for_role(self.role)

        if self.mode == "drill" and self.topics:
            # Prioritize questions whose tags overlap weak-spot topics.
            prioritized: List[Question] = []
            others: List[Question] = []
            topic_set = {t.lower() for t in self.topics}
            for q in questions:
                if any(tag.lower() in topic_set for tag in q.tags):
                    prioritized.append(q)
                else:
                    others.append(q)
            questions = prioritized + others

        self._scripted_questions = questions

    def has_more_scripted(self) -> bool:
        return self._index < len(self._scripted_questions)

    def _next_scripted_question(self) -> Optional[str]:
        if not self.has_more_scripted():
            return None
        q = self._scripted_questions[self._index]
        self._index += 1
        return q.text

    def get_next_question(self, last_answer: Optional[str] = None) -> str:
        """
        Return the next interview question.

        If we still have scripted questions, use them.
        Otherwise, generate a contextual follow-up / new question with the LLM.
        """
        # First question: just use the scripted bank.
        if last_answer is None:
            scripted = self._next_scripted_question()
            if scripted:
                return scripted

        # If there are still scripted questions, we can continue to use them
        # for most of the session and rely on the LLM mainly for follow-ups.
        if self.has_more_scripted() and (not last_answer or len(last_answer.split()) > 60):
            scripted = self._next_scripted_question()
            if scripted:
                return scripted

        # Otherwise ask the LLM for a follow-up or next question.
        system_prompt = prompts.interviewer_system_prompt(
            role=self.role, tone=self.tone, mode=self.mode, topics=self.topics or []
        )

        # If we don't have a previous question, just ask for a new one.
        current_question = (
            self._scripted_questions[self._index - 1].text
            if self._index > 0 and self._scripted_questions
            else "Start the interview with a strong opening question."
        )

        user_prompt = prompts.interviewer_followup_prompt(
            role=self.role,
            current_question=current_question,
            last_answer=last_answer or "",
            tone=self.tone,
        )

        try:
            next_q = llm.chat_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
                max_output_tokens=256,  # Increased from 128
            )
            # Guardrail: avoid empty responses.
            if next_q.strip():
                return next_q.strip()
        except Exception as e:
            print(f"Failed to generate follow-up question: {e}. Using scripted question.")
        
        # Fallback to scripted question or current question
        fallback = self._next_scripted_question()
        if fallback:
            return fallback
        
        # Last resort: return a generic follow-up
        return "Can you tell me more about your experience with that? Please provide specific examples."
