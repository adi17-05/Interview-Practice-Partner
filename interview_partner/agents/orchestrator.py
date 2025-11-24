from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from interview_partner.config import settings
from interview_partner.agents.interviewer import InterviewerAgent
from interview_partner.agents.critic import CriticAgent
from interview_partner.agents.memory_agent import MemoryAgent


@dataclass
class Orchestrator:
    """
    Coordinates Interviewer, Critic, and Memory agents for a single user session.
    """

    user_id: str
    role: str
    mode: str = "normal"  # "normal" | "drill"
    tone: str = "neutral"
    max_questions: int = field(
        default_factory=lambda: settings.MAX_QUESTIONS
    )

    interviewer: InterviewerAgent = field(init=False)
    critic: CriticAgent = field(init=False)
    memory: MemoryAgent = field(init=False)

    current_question: Optional[str] = field(default=None, init=False)
    evaluations: List[Dict[str, Any]] = field(default_factory=list, init=False)
    num_questions_asked: int = field(default=0, init=False)
    finished: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        self.memory = MemoryAgent(user_id=self.user_id)
        weak_topics: List[str] = []
        if self.mode == "drill":
            weak_topics = self.memory.get_weak_spots(top_k=5)

        self.interviewer = InterviewerAgent(
            role=self.role,
            tone=self.tone,
            mode=self.mode,
            topics=weak_topics or None,
        )
        self.critic = CriticAgent()

    # Public Orchestrator API ---------------------------------------------- #
    def start_interview(self) -> str:
        """
        Start the interview and return the first question text.
        """
        if self.current_question is not None:
            return self.current_question

        self.current_question = self.interviewer.get_next_question(last_answer=None)
        self.num_questions_asked = 1
        return self.current_question

    def submit_answer(self, answer: str) -> str:
        """
        Submit a candidate answer.

        - Evaluates the answer with CriticAgent.
        - Decides whether to continue or end.
        - Returns the next question or an end-of-interview message.
        """
        if self.finished:
            return "This interview session is already complete. Please start a new session."

        if not self.current_question:
            # If for some reason start_interview() wasn't called.
            self.current_question = self.interviewer.get_next_question(last_answer=None)

        question = self.current_question
        evaluation = self.critic.evaluate_answer(
            question=question,
            answer=answer,
            role=self.role,
        )
        self.evaluations.append(evaluation)

        # Decide whether to continue.
        if self.num_questions_asked >= self.max_questions:
            self.finished = True
            return "Thank you, that concludes this mock interview."

        # Ask the interviewer for the next question.
        next_q = self.interviewer.get_next_question(last_answer=answer)
        self.current_question = next_q
        self.num_questions_asked += 1
        return next_q

    def finalize_session(self) -> Dict[str, Any]:
        """
        Produce a session summary, update long-term memory, and return the summary.
        """
        summary_core = self.critic.summarize_session(
            evaluations=self.evaluations,
            role=self.role,
        )

        summary_record: Dict[str, Any] = {
            "user_id": self.user_id,
            "role": self.role,
            "summary_text": summary_core["summary_text"],
            "weak_spot_topics": summary_core.get("weak_spot_topics", []),
            "strength_topics": summary_core.get("strength_topics", []),
            "evaluations": self.evaluations,
        }

        self.memory.add_session_summary(summary_record)
        return summary_record

    def get_weak_spot_topics(self) -> List[str]:
        return self.memory.get_weak_spots()

    def get_latest_session(self) -> Optional[Dict[str, Any]]:
        return self.memory.get_latest_session()
