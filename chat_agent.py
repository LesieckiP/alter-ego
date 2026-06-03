from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr
import chat_context
import evaluation
from tool_specs import tools
from tool_executor import ToolExecutor

class ChatAgent:

    def __init__(self, context: chat_context.ChatContext, client: OpenAI):
        self.context = context
        self.client = client
        self.system_prompt = context.build_system_prompt()
        self.welcome_message = context.build_welcome_message()
        self.tools = tools
        self.tool_executor = ToolExecutor()


    def _rerun(self, reply, message, history, feedback):
        updated_system_prompt = self.system_prompt + "\n\n## Previous answer rejected\nYou just tried to reply, but the quality control rejected your reply\n"
        updated_system_prompt += f"## Your attempted answer:\n{reply}\n\n"
        updated_system_prompt += f"## Reason for rejection:\n{feedback}\n\n"
        messages = [{"role": "system", "content": updated_system_prompt}] + history + [{"role": "user", "content": message}]
        response = self.client.chat.completions.create(model="gpt-4o-mini", messages=messages)
        return response.choices[0].message.content


    def chat(self, message, history):
        user_message = message
        system = self.system_prompt
        messages = [{"role": "system", "content": system}] + history + [{"role": "user", "content": message}]
        done = False
        while not done:
            response = self.client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=self.tools) # pyright: ignore[reportArgumentType]
            finish_reasion = response.choices[0].finish_reason
            if finish_reasion == "tool_calls":
                assistant_message = response.choices[0].message
                tool_calls = assistant_message.tool_calls
                results = self.handle_tool_calls(tool_calls)
                messages.append(assistant_message)
                messages.extend(results)
            else:
                done = True
        reply = response.choices[0].message.content

        evaluation_result = evaluation.evaluate(reply, user_message, history, evaluator_system_prompt=self.context.build_evaluator_system_prompt())

        if evaluation_result.is_acceptable:
            print("Passed evaluation - returning reply")
        else:
            print("Failed evaluation - retrying")
            print(evaluation_result.feedback)
            reply = self._rerun(reply, user_message, history, evaluation_result.feedback)
        return reply

    def handle_tool_calls(self, tool_calls):
        return self.tool_executor.execute(tool_calls)

def main():
    load_dotenv(override=True)
    client = OpenAI()
    agent = ChatAgent(
        context=chat_context.ChatContext.from_files(
            name="Piotr Lesiecki",
            summary_path="me/summary.txt",
            cv_path="me/CV_Piotr_Lesiecki_2026.pdf"
        ),
        client=client
    )

    chatbot = gr.Chatbot(value=[{"role": "assistant", "content": agent.welcome_message}])

    with gr.Blocks() as demo:
        gr.ChatInterface(agent.chat, chatbot=chatbot)

    demo.launch(
        footer_links=[],
        server_name="127.0.0.1",
        server_port=7860,
        root_path="/alter-ego",
        share=False,
    )

if __name__ == "__main__":
    main()
