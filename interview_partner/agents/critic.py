from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List

from interview_partner.config import settings
from interview_partner.core import llm, prompts


DEFAULT_SCORE = 6  # fallback mid-range score for robustness


@dataclass
class CriticAgent:
    """LLM-as-a-Judge for per-answer evaluation and session summaries."""

    model: str = settings.CRITIC_MODEL

    def evaluate_answer(self, question: str, answer: str, role: str) -> Dict[str, Any]:
        """
        Evaluate a single answer and return a structured dict:

        {
          "question": str,
          "answer": str,
          "scores": {...},
          "weak_spots": [...],
          "strengths": [...],
          "comments": str
        }
        """
        system_prompt = prompts.critic_system_prompt()
        user_prompt = prompts.critic_user_prompt(question=question, answer=answer, role=role)

        try:
            raw = llm.chat_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=self.model,
                temperature=0.3,
                max_output_tokens=512,  # Increased from 256 to allow full JSON response
                json_mode=True,
            )
        except Exception as e:
            # If API fails completely, return a fallback evaluation
            print(f"Critic evaluation failed: {e}. Using fallback scores.")
            return {
                "question": question,
                "answer": answer,
                "scores": {
                    "clarity": DEFAULT_SCORE,
                    "technical_or_role_fit": DEFAULT_SCORE,
                    "structure_STAR": DEFAULT_SCORE,
                    "confidence": DEFAULT_SCORE,
                    "brevity": DEFAULT_SCORE,
                },
                "weak_spots": ["Unable to evaluate - API error"],
                "strengths": ["Answer recorded"],
                "comments": "Evaluation temporarily unavailable. Your answer has been recorded.",
            }

        try:
            data = json.loads(raw)
        except Exception:
            # Fallback if the model returns invalid JSON.
            data = {}

        scores = data.get("scores") or {}
        normalized_scores = {
            "clarity": int(scores.get("clarity", DEFAULT_SCORE)),
            "technical_or_role_fit": int(scores.get("technical_or_role_fit", DEFAULT_SCORE)),
            "structure_STAR": int(scores.get("structure_STAR", DEFAULT_SCORE)),
            "confidence": int(scores.get("confidence", DEFAULT_SCORE)),
            "brevity": int(scores.get("brevity", DEFAULT_SCORE)),
        }

        return {
            "question": question,
            "answer": answer,
            "scores": normalized_scores,
            "weak_spots": data.get("weak_spots", []),
            "strengths": data.get("strengths", []),
            "comments": data.get("comments", ""),
        }

    def summarize_session(self, evaluations: List[Dict[str, Any]], role: str) -> Dict[str, Any]:
        """
        Aggregate per-answer evaluations into a session summary.

        Returns:
        {
          "summary_text": str,
          "weak_spot_topics": [...],
          "strength_topics": [...]
        }
        """
        evaluations_json = json.dumps(
            [
                {
                    "question": e["question"],
                    "answer": e["answer"],
                    "scores": e["scores"],
                    "weak_spots": e.get("weak_spots", []),
                    "strengths": e.get("strengths", []),
                    "comments": e.get("comments", ""),
                }
                for e in evaluations
            ],
            ensure_ascii=False,
        )

        system_prompt = prompts.session_summary_system_prompt()
        user_prompt = prompts.session_summary_user_prompt(
            role=role, evaluations_json=evaluations_json
        )

        try:
            raw = llm.chat_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=self.model,
                temperature=0.4,
                max_output_tokens=512,
                json_mode=True,
            )
            data = json.loads(raw)
        except Exception as e:
            # Fallback if API fails
            print(f"Session summary generation failed: {e}. Using fallback summary.")
            
            # Extract weak spots and strengths from evaluations
            all_weak_spots = []
            all_strengths = []
            for e in evaluations:
                all_weak_spots.extend(e.get("weak_spots", []))
                all_strengths.extend(e.get("strengths", []))
            
            # Calculate average scores
            avg_scores = {}
            score_keys = ["clarity", "technical_or_role_fit", "structure_STAR", "confidence", "brevity"]
            for key in score_keys:
                scores = [e["scores"].get(key, DEFAULT_SCORE) for e in evaluations]
                avg_scores[key] = sum(scores) / len(scores) if scores else DEFAULT_SCORE
            
            # Generate fallback summary
            num_questions = len(evaluations)
            avg_overall = sum(avg_scores.values()) / len(avg_scores) if avg_scores else DEFAULT_SCORE
            
            summary_text = (
                f"You completed a {num_questions}-question interview practice session for the {role} role. "
                f"Your overall performance averaged {avg_overall:.1f}/10 across all criteria. "
                f"Continue practicing to improve your interview skills, focusing on providing specific examples "
                f"and structuring your answers using the STAR method (Situation, Task, Action, Result)."
            )
            
            data = {
                "summary_text": summary_text,
                "weak_spot_topics": list(set(all_weak_spots[:5])),  # Top 5 unique weak spots
                "strength_topics": list(set(all_strengths[:5])),  # Top 5 unique strengths
            }

        return {
            "summary_text": data.get(
                "summary_text",
                "This was a useful practice session. Keep refining your answers and focus on "
                "clarity, structure, and concrete examples.",
            ),
            "weak_spot_topics": data.get("weak_spot_topics", []),
            "strength_topics": data.get("strength_topics", []),
        }
