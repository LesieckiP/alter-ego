from dataclasses import dataclass

from pypdf import PdfReader


@dataclass(frozen=True)
class ChatContext:
    name: str
    summary: str
    cv_text: str


    def build_system_prompt(self) -> str:
        system_prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, \
                        particularly questions related to {self.name}'s career, background, skills and experience. \
                        Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
                        You are given a summary of {self.name}'s background and CV file which you can use to answer questions. \
                        Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
                        If you don't know the answer, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career.\
                        If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and name and record it using your record_user_details tool."

        system_prompt += (
            f"\n\n## Summary:\n{self.summary}\n\n## CV file:\n{self.cv_text}\n\n"
        )
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt


    def build_evaluator_system_prompt(self) -> str:
        evaluator_system_prompt = f"You are an evaluator that decides whether a response to a question is acceptable. \
                                    You are provided with a conversation between a User and an Agent. Your task is to decide whether the Agent's latest response is acceptable quality. \
                                    The Agent is playing the role of {self.name} and is representing {self.name} on their website. \
                                    The Agent has been instructed to be professional and engaging, as if talking to a potential client or future employer who came across the website. \
                                    The Agent has been provided with context on {self.name} in the form of their summary and CV details. Here's the information:"

        evaluator_system_prompt += (
            f"\n\n## Summary:\n{self.summary}\n\n## CV File:\n{self.cv_text}\n\n"
        )
        evaluator_system_prompt += "With this context, please evaluate the latest response, replying with whether the response is acceptable and your feedback."
        return evaluator_system_prompt


    def build_welcome_message(self) -> str:
        return (
            f"Hi, I am {self.name}'s alter-ego. Ask me about {self.name}'s experience, skills, projects, "
            f"hobbies, or what kind of work they are looking for."
        )
    
    @classmethod
    def from_files(cls, name: str, summary_path: str, cv_path: str) -> "ChatContext":
        cv_text = "".join(page.extract_text() or "" for page in PdfReader(cv_path).pages)
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = f.read()
        return cls(name=name, summary=summary, cv_text=cv_text)
