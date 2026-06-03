from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv(override=True)

gemini = OpenAI(
    api_key=os.environ["GOOGLE_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str


def evaluator_user_prompt(reply, message, history):
    user_prompt = f"Here's the conversation between the User and the Agent: \n\n{history}\n\n"
    user_prompt += f"Here's the latest message from the User: \n\n{message}\n\n"
    user_prompt += f"Here's the latest response from the Agent: \n\n{reply}\n\n"
    user_prompt += "Please evaluate the response, replying with whether it is acceptable and your feedback."
    return user_prompt

def evaluate(reply, message, history, evaluator_system_prompt) -> Evaluation:

    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": evaluator_system_prompt},
        {"role": "user", "content": evaluator_user_prompt(reply, message, history)},
    ]
    response = gemini.beta.chat.completions.parse(model="gemini-2.5-flash", messages=messages, response_format=Evaluation)
    result = response.choices[0].message.parsed
    if result is None:
        raise ValueError("Model failed to return a structured response")
    return result