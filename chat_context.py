"""Immutable context container that produces system prompts from the owner's CV and bio."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass(frozen=True)
class ChatContext:
    """Holds owner data and generates system prompts for both the agent and evaluator."""

    name: str
    summary: str
    cv_text: str

    def build_system_prompt(self) -> str:
        """Return the main agent system prompt grounded in the owner's bio and CV."""
        n = self.name
        persona = (
            f"You are acting as {n}. You are answering questions on {n}'s website, "
            f"particularly questions related to {n}'s career, background, skills and experience. "
            f"Your responsibility is to represent {n} on the website as faithfully as possible. "
            f"You are given {n}'s background summary and CV to draw from when answering questions. "
            "Be professional and engaging, as if talking to a potential client or future employer. "
            "If you don't know the answer, use your record_unknown_question tool to record it, "
            "even if it's about something trivial or unrelated to career. "
            "If the user is engaging, try to steer them towards getting in touch via email; "
            f"ask for their email and name and record it using your record_user_details tool."
        )
        context = f"\n\n## Summary:\n{self.summary}\n\n## CV file:\n{self.cv_text}\n\n"
        closing = (
            f"With this context, please chat with the user, always staying in character as {n}."
        )
        return persona + context + closing

    def build_evaluator_system_prompt(self) -> str:
        """Return the judge LLM system prompt including the owner's full context."""
        n = self.name
        intro = (
            "You are an evaluator that decides whether a response to a question is acceptable. "
            "You are provided with a conversation between a User and an Agent. "
            "Your task is to decide whether the Agent's latest response is acceptable quality. "
            f"The Agent is playing the role of {n} and is representing {n} on their website. "
            "The Agent has been instructed to be professional and engaging, "
            "as if talking to a potential client or future employer. "
            f"The Agent has been provided with context on {n} in the form of their summary and CV. "
            "Here's the information:"
        )
        context = f"\n\n## Summary:\n{self.summary}\n\n## CV File:\n{self.cv_text}\n\n"
        closing = (
            "With this context, please evaluate the latest response, "
            "replying with whether the response is acceptable and your feedback."
        )
        return intro + context + closing

    def build_welcome_message(self) -> str:
        """Return the initial greeting shown when the chatbot loads."""
        n = self.name
        return (
            f"Hi, I am {n}'s alter-ego. Ask me about {n}'s experience, skills, projects, "
            f"hobbies, or what kind of work they are looking for."
        )

    @classmethod
    def from_files(cls, name: str, summary_path: str, cv_path: str) -> ChatContext:
        """Load owner context from a plain-text bio file and a PDF CV."""
        cv_text = "".join(page.extract_text() or "" for page in PdfReader(cv_path).pages)
        summary = Path(summary_path).read_text(encoding="utf-8")
        return cls(name=name, summary=summary, cv_text=cv_text)
