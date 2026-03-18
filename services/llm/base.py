"""
Base LLM analyzer: protocol and shared prompt/parsing logic.
Author: Pablo Murad (runawaydevil). 2025-2026.
"""
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from models.movie_metadata import MovieMetadata
from services.fallback_parser import FallbackParser


class BaseLLMAnalyzer(ABC):
    """
    Protocol for LLM-based movie filename analysis.
    Implementations must provide _get_analysis_response() and may override complete_chat().
    """

    ANALYSIS_PROMPT = """
Analyse o seguinte nome de arquivo de filme e extraia as informações:
Filename: {filename}

REGRAS IMPORTANTES:
1. Sempre retorne o título ORIGINAL do filme (em inglês ou idioma original), não traduções
2. Seja CONSERVADOR - se não tiver certeza do filme, use confidence baixa (0.1-0.4)
3. NÃO "adivinhe" filmes baseado em similaridades vagas
4. Se o nome for muito abreviado ou unclear, mantenha o título próximo ao original
5. SEMPRE tente extrair o ano, mesmo que seja de 2 dígitos (ex: 86 = 1986)

Retorne APENAS um JSON válido com:
- title: título ORIGINAL do filme (se incerto, use uma versão limpa do filename)
- year: ano do filme (SEMPRE tente extrair, mesmo de 2 dígitos. Ex: 86=1986, 03=2003)
- confidence: nível de confiança REAL (0.0-1.0) - seja honesto sobre incerteza

Exemplos:
- "MNMil.86.Trial" -> {{"title": "Mille Miglia", "year": 1986, "confidence": 0.7}}
- "Cidade.de.Deus.2002" -> {{"title": "City of God", "year": 2002, "confidence": 0.95}}
- "Memories.Murder.03" -> {{"title": "Memories of Murder", "year": 2003, "confidence": 0.8}}

Resposta JSON:"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.fallback_parser = FallbackParser()

    def analyze_filename(self, filename: str) -> MovieMetadata:
        if not filename or not filename.strip():
            return self._create_fallback_metadata(filename, "Empty filename")
        try:
            content = self._get_analysis_response(filename)
            metadata = self._parse_ai_response(content, filename)
            self.logger.info(f"Analyzed: {filename} -> {metadata.title} ({metadata.year})")
            return metadata
        except Exception as e:
            self.logger.error(f"Error analyzing '{filename}': {e}")
            return self._use_fallback_parser(filename, str(e))

    @abstractmethod
    def _get_analysis_response(self, filename: str) -> str:
        """Call LLM with analysis prompt and return raw response content string."""

    def complete_chat(self, system: str, user_content: str) -> str:
        """Optional: for manual-search 'improve with AI' flow. Default returns empty."""
        return ""

    def _parse_ai_response(self, content: str, original_filename: str) -> MovieMetadata:
        try:
            content = self._clean_response_content(content)
            parsed = json.loads(content)
            if not self._validate_ai_response(parsed):
                raise ValueError("Invalid response structure")
            title = self._extract_and_clean_title(parsed.get("title", ""))
            year = self._extract_and_validate_year(parsed.get("year"))
            confidence = self._extract_and_validate_confidence(parsed.get("confidence", 0.0))
            if not title:
                title = original_filename
                confidence = 0.1
            metadata = MovieMetadata(
                title=title,
                year=year,
                original_filename=original_filename,
                confidence_score=confidence,
            )
            if not metadata.is_valid():
                return self._create_fallback_metadata(original_filename, "Invalid metadata generated")
            return metadata
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            self.logger.warning(f"Parse error: {e}")
            return self._create_fallback_metadata(original_filename, f"Parse error: {e}")

    def _clean_response_content(self, content: str) -> str:
        if not content:
            return ""
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        return content.strip()

    def _extract_and_clean_title(self, title: Any) -> str:
        if not title or not isinstance(title, str):
            return ""
        title = title.strip()
        terms = [
            "BD720p", "BD1080p", "DVDRip", "TrialBD", "HD1080p", "TetraBD",
            "MemoriadaTV", "Mini", "HDTV", "WEB-DL", "BluRay", "x264", "x265",
        ]
        for term in terms:
            title = title.replace(term, "").strip()
        title = " ".join(title.split()).replace("..", ".").strip(".")
        return title

    def _extract_and_validate_year(self, year: Any) -> Optional[int]:
        if year is None:
            return None
        try:
            if isinstance(year, str):
                year_str = "".join(filter(str.isdigit, year))
                year = int(year_str) if len(year_str) == 4 else None
            else:
                year = int(year)
            return year if year and 1800 <= year <= 2030 else None
        except (ValueError, TypeError):
            return None

    def _extract_and_validate_confidence(self, confidence: Any) -> float:
        try:
            return max(0.0, min(1.0, float(confidence)))
        except (ValueError, TypeError):
            return 0.0

    def _validate_ai_response(self, response: Dict[str, Any]) -> bool:
        return all(k in response for k in ("title", "year", "confidence"))

    def _use_fallback_parser(self, filename: str, error_reason: str) -> MovieMetadata:
        self.logger.info(f"Using fallback parser for '{filename}': {error_reason}")
        try:
            return self.fallback_parser.parse_filename(filename)
        except Exception as e:
            self.logger.error(f"Fallback parser failed: {e}")
            return self._create_emergency_metadata(filename)

    def _create_fallback_metadata(self, filename: str, reason: str) -> MovieMetadata:
        self.logger.debug(f"Fallback metadata for '{filename}': {reason}")
        return self._create_emergency_metadata(filename)

    def _create_emergency_metadata(self, filename: str) -> MovieMetadata:
        return MovieMetadata(
            title=filename,
            year=None,
            original_filename=filename,
            confidence_score=0.0,
        )
