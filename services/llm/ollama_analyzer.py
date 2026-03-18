"""
Ollama implementation of BaseLLMAnalyzer (local LLM).
Uses HTTP API so no extra package required beyond requests.
Author: Pablo Murad (runawaydevil). 2025-2026.
"""
import logging

import requests

from .base import BaseLLMAnalyzer


class OllamaAnalyzer(BaseLLMAnalyzer):
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        super().__init__()
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = 120

    def _get_analysis_response(self, filename: str) -> str:
        prompt = self.ANALYSIS_PROMPT.format(filename=filename)
        messages = [
            {"role": "system", "content": "You are a movie filename analyzer. Return only valid JSON."},
            {"role": "user", "content": prompt},
        ]
        r = requests.post(
            f"{self.base_url}/api/chat",
            json={"model": self.model, "messages": messages, "stream": False},
            timeout=self.timeout,
        )
        r.raise_for_status()
        data = r.json()
        msg = data.get("message") or {}
        content = msg.get("content", "")
        if not content:
            raise RuntimeError("Empty response from Ollama")
        return content.strip()

    def complete_chat(self, system: str, user_content: str) -> str:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ]
        r = requests.post(
            f"{self.base_url}/api/chat",
            json={"model": self.model, "messages": messages, "stream": False},
            timeout=self.timeout,
        )
        r.raise_for_status()
        data = r.json()
        msg = data.get("message") or {}
        return (msg.get("content", "") or "").strip()
