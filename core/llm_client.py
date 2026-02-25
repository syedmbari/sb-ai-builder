import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=".env")

class LLMClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is missing. Create a .env file in the repo root and set OPENAI_API_KEY."
            )
        if " " in api_key:
            raise RuntimeError("OPENAI_API_KEY contains spaces. Re-copy it without spaces/newlines.")

        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = OpenAI(api_key=api_key)