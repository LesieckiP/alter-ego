"""LLM-as-judge quality gate: evaluates ChatAgent replies using Google Gemini."""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from openai import OpenAI
from pydantic import BaseModel

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletionMessageParam

_MODEL = "gemini-2.5-flash"
_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


class Evaluation(BaseModel):
    """Structured pass/fail result returned by the judge LLM."""

    is_acceptable: bool
    feedback: str


class Evaluator:
    """Wraps a Gemini judge LLM that scores agent responses before they reach the user."""

    def __init__(self, client: OpenAI | None = None) -> None:
        self.client = client or OpenAI(
            api_key=os.environ["GOOGLE_API_KEY"],
            base_url=_BASE_URL,
        )

    def evaluator_user_prompt(self, reply: str, message: str, history: list) -> str:
        """Build the user-turn prompt sent to the judge LLM."""
        user_prompt = f"Here's the conversation between the User and the Agent:\n\n{history}\n\n"
        user_prompt += f"Here's the latest message from the User:\n\n{message}\n\n"
        user_prompt += f"Here's the latest response from the Agent:\n\n{reply}\n\n"
        user_prompt += "Please evaluate the response: is it acceptable? Provide your feedback."
        return user_prompt

    def evaluate(
        self, reply: str, message: str, history: list, evaluator_system_prompt: str
    ) -> Evaluation:
        """Evaluate a reply; returns structured pass/fail with feedback."""
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": evaluator_system_prompt},
            {"role": "user", "content": self.evaluator_user_prompt(reply, message, history)},
        ]
        response = self.client.beta.chat.completions.parse(
            model=_MODEL, messages=messages, response_format=Evaluation
        )
        result = response.choices[0].message.parsed
        if result is None:
            raise ValueError("Model failed to return a structured response")
        return result
