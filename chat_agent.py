"""Gradio chatbot that acts as an AI alter-ego, with LLM-as-judge quality evaluation."""
from __future__ import annotations

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

import chat_context
from config import Config
from evaluation import Evaluator
from tool_executor import ToolExecutor
from tool_specs import tools

_MODEL = "gpt-4o-mini"


class ChatAgent:
    """Orchestrates the conversation loop, tool execution, and quality evaluation."""

    def __init__(self, context: chat_context.ChatContext, client: OpenAI) -> None:
        self.context = context
        self.client = client
        self.system_prompt = context.build_system_prompt()
        self.welcome_message = context.build_welcome_message()
        self.tools = tools
        self.tool_executor = ToolExecutor()
        self.evaluator = Evaluator()

    def _rerun(self, reply: str, message: str, history: list, feedback: str) -> str | None:
        updated_system_prompt = (
            self.system_prompt
            + "\n\n## Previous answer rejected\n"
            "You just tried to reply, but the quality control rejected your reply\n"
            f"\n## Your attempted answer:\n{reply}\n\n"
            f"## Reason for rejection:\n{feedback}\n\n"
        )
        messages = [
            {"role": "system", "content": updated_system_prompt},
            *history,
            {"role": "user", "content": message},
        ]
        response = self.client.chat.completions.create(model=_MODEL, messages=messages)
        return response.choices[0].message.content

    def chat(self, message: str, history: list) -> str | None:
        """Handle one chat turn: run the agent loop, evaluate quality, retry once if needed."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            *history,
            {"role": "user", "content": message},
        ]
        done = False
        while not done:
            response = self.client.chat.completions.create(
                model=_MODEL,
                messages=messages,
                tools=self.tools,  # pyright: ignore[reportArgumentType]
            )
            finish_reason = response.choices[0].finish_reason
            if finish_reason == "tool_calls":
                assistant_message = response.choices[0].message
                if tool_calls := assistant_message.tool_calls:
                    results = self.handle_tool_calls(tool_calls)
                else:
                    results = []
                messages.append(assistant_message)
                messages.extend(results)
            else:
                done = True

        reply = response.choices[0].message.content or ""
        evaluation_result = self.evaluator.evaluate(
            reply,
            message,
            history,
            evaluator_system_prompt=self.context.build_evaluator_system_prompt(),
        )

        if evaluation_result.is_acceptable:
            print("Passed evaluation - returning reply")
        else:
            print("Failed evaluation - retrying")
            print(evaluation_result.feedback)
            reply = self._rerun(reply, message, history, evaluation_result.feedback)

        return reply

    def handle_tool_calls(self, tool_calls: list) -> list:
        """Delegate tool call dispatch to the ToolExecutor."""
        return self.tool_executor.execute(tool_calls)


def main() -> None:
    """Entry point: load config, build the agent, and launch the Gradio UI."""
    load_dotenv(override=True)
    client = OpenAI()
    agent = ChatAgent(
        context=chat_context.ChatContext.from_files(
            name="Piotr Lesiecki",
            summary_path="me/summary.txt",
            cv_path="me/CV_Piotr_Lesiecki_2026.pdf",
        ),
        client=client,
    )

    chatbot = gr.Chatbot(value=[{"role": "assistant", "content": agent.welcome_message}])

    with gr.Blocks() as demo:
        gr.ChatInterface(agent.chat, chatbot=chatbot)

    demo.launch(
        footer_links=[],
        server_name=Config.GRADIO_SERVER_NAME,
        server_port=Config.GRADIO_SERVER_PORT,
        root_path="/alter-ego",
        share=Config.GRADIO_SHARE,
    )


if __name__ == "__main__":
    main()
