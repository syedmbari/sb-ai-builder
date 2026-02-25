import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class LLMClient:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def chat(self, messages, temperature=0.2, json_mode=False):
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"} if json_mode else None
        ).choices[0].message.content
