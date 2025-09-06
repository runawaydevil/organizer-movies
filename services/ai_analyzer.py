#!/usr/bin/env python3
"""
AI-powered movie filename analyzer using OpenAI API
AI-Powered Movie File Organizer with TMDB Integration

Author: Pablo Murad (runawaydevil)
Version: 0.01
Repository: https://github.com/runawaydevil/organizer-movies.git
"""
import json
import logging
import time
from typing import Optional, Dict, Any
from openai import OpenAI
from models.movie_metadata import MovieMetadata
from .fallback_parser import FallbackParser


class AIAnalyzer:
    """
    Analyzes movie filenames using OpenAI API
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initialize AIAnalyzer
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use for analysis
        """
        self.api_key = api_key
        self.model = model
        self.client = None
        self.logger = logging.getLogger(__name__)
        self.fallback_parser = FallbackParser()
        
        # Initialize OpenAI client
        self._initialize_client()
        
        # Analysis prompt template
        self.analysis_prompt = """
Analise o seguinte nome de arquivo de filme e extraia as informações:
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
- "MNMil.86.Trial" → {{"title": "Mille Miglia", "year": 1986, "confidence": 0.7}}
- "Cidade.de.Deus.2002" → {{"title": "City of God", "year": 2002, "confidence": 0.95}}
- "Memories.Murder.03" → {{"title": "Memories of Murder", "year": 2003, "confidence": 0.8}}

Resposta JSON:"""
    
    def _initialize_client(self):
        """Initialize OpenAI client with API key"""
        try:
            self.client = OpenAI(api_key=self.api_key)
            self.logger.info("OpenAI client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    
    def analyze_filename(self, filename: str) -> MovieMetadata:
        """
        Analyze movie filename and extract metadata
        
        Args:
            filename: Movie filename to analyze
            
        Returns:
            MovieMetadata: Extracted movie metadata
        """
        if not filename or not filename.strip():
            return self._create_fallback_metadata(filename, "Empty filename")
        
        try:
            # Call OpenAI API
            api_response = self._call_openai_api(filename)
            
            # Parse response
            metadata = self._parse_ai_response(api_response, filename)
            
            self.logger.info(f"Successfully analyzed: {filename} -> {metadata.title} ({metadata.year})")
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error analyzing filename '{filename}': {e}")
            return self._use_fallback_parser(filename, str(e))
    
    def _call_openai_api(self, filename: str) -> Dict[str, Any]:
        """
        Make API call to OpenAI
        
        Args:
            filename: Filename to analyze
            
        Returns:
            Dict: API response
        """
        if not self.client:
            raise Exception("OpenAI client not initialized")
        
        prompt = self.analysis_prompt.format(filename=filename)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a movie filename analyzer. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.1
            )
            
            if not response.choices or not response.choices[0].message.content:
                raise Exception("Empty response from OpenAI API")
            
            content = response.choices[0].message.content.strip()
            self.logger.debug(f"OpenAI response for '{filename}': {content}")
            
            return {"content": content, "usage": response.usage}
            
        except Exception as e:
            self.logger.error(f"OpenAI API call failed: {e}")
            raise
    
    def _parse_ai_response(self, response: Dict[str, Any], original_filename: str) -> MovieMetadata:
        """
        Parse OpenAI API response into MovieMetadata
        
        Args:
            response: API response dictionary
            original_filename: Original filename for fallback
            
        Returns:
            MovieMetadata: Parsed metadata
        """
        try:
            content = response.get("content", "")
            
            # Clean up response content (remove markdown formatting if present)
            content = self._clean_response_content(content)
            
            # Try to parse JSON from response
            parsed_data = json.loads(content)
            
            # Validate required fields
            if not self._validate_ai_response(parsed_data):
                raise ValueError("Invalid response structure")
            
            # Extract and validate data
            title = self._extract_and_clean_title(parsed_data.get("title", ""))
            year = self._extract_and_validate_year(parsed_data.get("year"))
            confidence = self._extract_and_validate_confidence(parsed_data.get("confidence", 0.0))
            
            # Use original filename as title if AI didn't provide one
            if not title:
                title = original_filename
                confidence = 0.1
            
            metadata = MovieMetadata(
                title=title,
                year=year,
                original_filename=original_filename,
                confidence_score=confidence
            )
            
            # Final validation of metadata
            if not metadata.is_valid():
                self.logger.warning(f"Generated metadata is invalid: {metadata}")
                return self._create_fallback_metadata(original_filename, "Invalid metadata generated")
            
            return metadata
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            self.logger.warning(f"Failed to parse AI response: {e}")
            return self._create_fallback_metadata(original_filename, f"Parse error: {e}")
    
    def _clean_response_content(self, content: str) -> str:
        """
        Clean response content to extract JSON
        
        Args:
            content: Raw response content
            
        Returns:
            str: Cleaned JSON string
        """
        # Remove markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        return content.strip()
    
    def _extract_and_clean_title(self, title: Any) -> str:
        """
        Extract and clean movie title
        
        Args:
            title: Title from AI response
            
        Returns:
            str: Cleaned title
        """
        if not title or not isinstance(title, str):
            return ""
        
        # Clean up title
        title = title.strip()
        
        # Remove common technical terms that might leak through
        technical_terms = [
            'BD720p', 'BD1080p', 'DVDRip', 'TrialBD', 'HD1080p', 'TetraBD',
            'MemoriadaTV', 'Mini', 'HDTV', 'WEB-DL', 'BluRay', 'x264', 'x265'
        ]
        
        for term in technical_terms:
            title = title.replace(term, '').strip()
        
        # Clean up extra spaces and dots
        title = ' '.join(title.split())
        title = title.replace('..', '.').strip('.')
        
        return title
    
    def _extract_and_validate_year(self, year: Any) -> Optional[int]:
        """
        Extract and validate year
        
        Args:
            year: Year from AI response
            
        Returns:
            Optional[int]: Validated year or None
        """
        if year is None:
            return None
        
        try:
            if isinstance(year, str):
                # Extract digits from string
                year_str = ''.join(filter(str.isdigit, year))
                if len(year_str) == 4:
                    year = int(year_str)
                else:
                    return None
            else:
                year = int(year)
            
            # Validate year range
            if 1800 <= year <= 2030:
                return year
            else:
                return None
                
        except (ValueError, TypeError):
            return None
    
    def _extract_and_validate_confidence(self, confidence: Any) -> float:
        """
        Extract and validate confidence score
        
        Args:
            confidence: Confidence from AI response
            
        Returns:
            float: Validated confidence score between 0.0 and 1.0
        """
        try:
            confidence = float(confidence)
            return max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            return 0.0
    
    def _validate_ai_response(self, response: Dict[str, Any]) -> bool:
        """
        Validate AI response structure
        
        Args:
            response: Parsed JSON response
            
        Returns:
            bool: True if response is valid
        """
        required_fields = ['title', 'year', 'confidence']
        return all(field in response for field in required_fields)
    
    def _use_fallback_parser(self, filename: str, error_reason: str) -> MovieMetadata:
        """
        Use fallback parser when AI analysis fails
        
        Args:
            filename: Original filename
            error_reason: Reason for fallback
            
        Returns:
            MovieMetadata: Fallback metadata from regex parsing
        """
        self.logger.info(f"Using fallback parser for '{filename}': {error_reason}")
        
        try:
            return self.fallback_parser.parse_filename(filename)
        except Exception as fallback_error:
            self.logger.error(f"Fallback parser also failed for '{filename}': {fallback_error}")
            return self._create_emergency_metadata(filename)
    
    def _create_emergency_metadata(self, filename: str) -> MovieMetadata:
        """
        Create emergency metadata when both AI and fallback fail
        
        Args:
            filename: Original filename
            
        Returns:
            MovieMetadata: Emergency metadata
        """
        return MovieMetadata(
            title=filename,
            year=None,
            original_filename=filename,
            confidence_score=0.0
        )