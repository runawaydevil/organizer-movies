"""
OpenAI implementation of BaseLLMAnalyzer.
Author: Pablo Murad (runawaydevil). 2025-2026.
"""
from openai import OpenAI

from .base import BaseLLMAnalyzer


class OpenAIAnalyzer(BaseLLMAnalyzer):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key)
        self.logger.info("OpenAI client initialized")

    def _get_analysis_response(self, filename: str) -> str:
        prompt = self.ANALYSIS_PROMPT.format(filename=filename)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a movie filename analyzer. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            temperature=0.1,
        )
        if not response.choices or not response.choices[0].message.content:
            raise RuntimeError("Empty response from OpenAI")
        return response.choices[0].message.content.strip()

    def complete_chat(self, system: str, user_content: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_content},
            ],
            max_tokens=300,
            temperature=0.2,
        )
        if not response.choices or not response.choices[0].message.content:
            return ""
        return response.choices[0].message.content.strip()
