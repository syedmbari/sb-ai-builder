from __future__ import annotations

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load env deterministically from repo root
load_dotenv(dotenv_path=".env")


class LLMClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("Missing OPENAI_API_KEY in .env")

        self.model = (os.getenv("OPENAI_MODEL") or "gpt-4o-mini").strip()
        self.client = OpenAI(api_key=api_key)

    def chat(self, messages, *, temperature: float = 0.2, json_mode: bool = False) -> str:
        """
        messages: [{"role": "system"|"user"|"assistant", "content": "..."}]
        json_mode: if True, enforce JSON object output.
        Returns: assistant message content as string.
        """
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"} if json_mode else None,
        )
        return resp.choices[0].message.content