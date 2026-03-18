"""
Factory to create LLM analyzer from config.
Author: Pablo Murad (runawaydevil). 2025-2026.
"""
from typing import Dict, Any

from .base import BaseLLMAnalyzer
from .openai_analyzer import OpenAIAnalyzer
from .ollama_analyzer import OllamaAnalyzer


def create_llm_analyzer(config: Dict[str, Any]) -> BaseLLMAnalyzer:
    """
    Create an LLM analyzer from config dict.
    Supports llm_provider (openai | ollama) with backward compatibility:
    if llm_provider/llm_model missing, use openai and openai_model.
    """
    provider = config.get("llm_provider") or "openai"
    model = config.get("llm_model") or config.get("openai_model") or "gpt-4o-mini"
    if provider == "ollama":
        base_url = config.get("ollama_base_url", "http://localhost:11434")
        return OllamaAnalyzer(model=model, base_url=base_url)
    api_key = config.get("openai_api_key", "")
    return OpenAIAnalyzer(api_key=api_key, model=model)
