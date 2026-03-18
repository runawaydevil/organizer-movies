#!/usr/bin/env python3
"""
Hybrid analyzer that combines OpenAI and TMDB for better movie identification
AI-Powered Movie File Organizer with TMDB Integration

Author: Pablo Murad (runawaydevil)
Version: 0.1
Repository: https://github.com/runawaydevil/organizer-movies.git
"""
import logging
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

from .tmdb_service import TMDBService, TMDBMovieResult
from models.movie_metadata import MovieMetadata

try:
    from .llm.base import BaseLLMAnalyzer
except ImportError:
    BaseLLMAnalyzer = None


class HybridAnalyzer:
    """
    Combines LLM (OpenAI or Ollama) and TMDB for enhanced movie identification.
    Accepts any BaseLLMAnalyzer by injection.
    """
    
    def __init__(self, llm_analyzer: "BaseLLMAnalyzer", tmdb_api_key: str, tmdb_bearer_token: str,
                 cache_duration_days: int = 7):
        """
        Initialize hybrid analyzer.
        
        Args:
            llm_analyzer: LLM analyzer (OpenAI or Ollama)
            tmdb_api_key: TMDB API key
            tmdb_bearer_token: TMDB bearer token
            cache_duration_days: TMDB cache duration
        """
        self.logger = logging.getLogger(__name__)
        self.ai_analyzer = llm_analyzer
        self.tmdb_service = TMDBService(tmdb_api_key, tmdb_bearer_token, cache_duration_days=cache_duration_days)
        self._test_services()
    
    def _test_services(self):
        """Test that both services are working"""
        try:
            # Test TMDB connection
            if self.tmdb_service.test_connection():
                self.logger.info("TMDB service initialized successfully")
            else:
                self.logger.warning("TMDB service connection failed")
        except Exception as e:
            self.logger.error(f"Error testing TMDB service: {e}")
    
    def analyze_filename(self, filename: str) -> MovieMetadata:
        """
        Analyze filename using hybrid approach (AI + TMDB)
        
        Args:
            filename: Movie filename to analyze
            
        Returns:
            MovieMetadata: Enhanced metadata with TMDB information
        """
        self.logger.info(f"Analyzing with hybrid approach: {filename}")
        
        # Step 1: Use AI to get initial analysis
        ai_metadata = self.ai_analyzer.analyze_filename(filename)
        
        if not ai_metadata or not ai_metadata.title:
            self.logger.warning(f"AI analysis failed for {filename}")
            return ai_metadata
        
        # Step 2: Use TMDB to get accurate information
        tmdb_result = self._enhance_with_tmdb(ai_metadata)
        
        if tmdb_result:
            # Create enhanced metadata with TMDB information
            # Use original title for better media server compatibility
            enhanced_metadata = MovieMetadata(
                title=tmdb_result.get_display_title(),  # Uses original title when available
                year=tmdb_result.year,
                original_filename=filename,
                confidence_score=min(ai_metadata.confidence_score + 0.2, 1.0)  # Boost confidence with TMDB
            )
            
            self.logger.info(f"Enhanced with TMDB: {filename} -> {enhanced_metadata.title} ({enhanced_metadata.year})")
            return enhanced_metadata
        else:
            # Fallback to AI-only result
            self.logger.info(f"TMDB enhancement failed, using AI result: {ai_metadata.title} ({ai_metadata.year})")
            return ai_metadata
    
    def _enhance_with_tmdb(self, ai_metadata: MovieMetadata) -> Optional[TMDBMovieResult]:
        """
        Enhance AI metadata with TMDB information
        
        Args:
            ai_metadata: Metadata from AI analysis
            
        Returns:
            TMDBMovieResult: TMDB result or None
        """
        try:
            # Search TMDB with AI-provided title and year
            tmdb_result = self.tmdb_service.get_best_match(ai_metadata.title, ai_metadata.year)
            
            if tmdb_result:
                # Validate that the match makes sense
                if self._is_good_match(ai_metadata, tmdb_result):
                    return tmdb_result
                else:
                    self.logger.warning(f"TMDB match rejected for {ai_metadata.title}: {tmdb_result.title}")
                    return None
            else:
                self.logger.info(f"No TMDB match found for: {ai_metadata.title}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error enhancing with TMDB: {e}")
            return None
    
    def _is_good_match(self, ai_metadata: MovieMetadata, tmdb_result: TMDBMovieResult) -> bool:
        """
        Validate that TMDB result is a good match for AI metadata
        
        Args:
            ai_metadata: Original AI metadata
            tmdb_result: TMDB search result
            
        Returns:
            bool: True if it's a good match
        """
        # Check year match (allow 1 year difference)
        if ai_metadata.year and tmdb_result.year:
            year_diff = abs(ai_metadata.year - tmdb_result.year)
            if year_diff > 1:
                self.logger.debug(f"Year mismatch: AI={ai_metadata.year}, TMDB={tmdb_result.year}")
                return False
        
        # Check title similarity (basic check)
        ai_title_clean = ai_metadata.title.lower().replace(' ', '').replace('-', '').replace(':', '')
        tmdb_title_clean = tmdb_result.title.lower().replace(' ', '').replace('-', '').replace(':', '')
        tmdb_original_clean = tmdb_result.original_title.lower().replace(' ', '').replace('-', '').replace(':', '')
        
        # Check if titles have some similarity
        if (ai_title_clean in tmdb_title_clean or tmdb_title_clean in ai_title_clean or
            ai_title_clean in tmdb_original_clean or tmdb_original_clean in ai_title_clean):
            return True
        
        # Check if first few characters match (for abbreviated titles)
        if len(ai_title_clean) >= 3 and len(tmdb_title_clean) >= 3:
            if ai_title_clean[:3] == tmdb_title_clean[:3]:
                return True
        
        self.logger.debug(f"Title mismatch: AI='{ai_metadata.title}', TMDB='{tmdb_result.title}'")
        return False
    
    def analyze_with_manual_hint(self, filename: str, manual_title: str, manual_year: Optional[int] = None) -> MovieMetadata:
        """
        Analyze filename with manual hint for better TMDB matching
        
        Args:
            filename: Original filename
            manual_title: User-provided title hint
            manual_year: User-provided year hint
            
        Returns:
            MovieMetadata: Enhanced metadata
        """
        self.logger.info(f"Analyzing with manual hint: {filename} -> '{manual_title}' ({manual_year})")
        
        # Search TMDB directly with manual hint
        tmdb_result = self.tmdb_service.get_best_match(manual_title, manual_year)
        
        if tmdb_result:
            # Create metadata with TMDB information
            enhanced_metadata = MovieMetadata(
                title=tmdb_result.get_display_title(),
                year=tmdb_result.year,
                original_filename=filename,
                confidence_score=0.95  # High confidence with manual hint + TMDB
            )
            
            self.logger.info(f"Manual hint enhanced with TMDB: {enhanced_metadata.title} ({enhanced_metadata.year})")
            return enhanced_metadata
        else:
            # Fallback to manual input
            fallback_metadata = MovieMetadata(
                title=manual_title,
                year=manual_year,
                original_filename=filename,
                confidence_score=0.8  # Good confidence with manual input
            )
            
            self.logger.info(f"Using manual hint (no TMDB match): {fallback_metadata.title} ({fallback_metadata.year})")
            return fallback_metadata
    
    def get_tmdb_info(self, title: str, year: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Get additional TMDB information for a movie
        
        Args:
            title: Movie title
            year: Movie year
            
        Returns:
            Dict: Additional TMDB information or None
        """
        try:
            tmdb_result = self.tmdb_service.get_best_match(title, year)
            
            if tmdb_result:
                # Get detailed information
                details = self.tmdb_service.get_movie_details(tmdb_result.id)
                
                return {
                    'tmdb_id': tmdb_result.id,
                    'title': tmdb_result.title,
                    'original_title': tmdb_result.original_title,
                    'year': tmdb_result.year,
                    'overview': tmdb_result.overview,
                    'vote_average': tmdb_result.vote_average,
                    'popularity': tmdb_result.popularity,
                    'original_language': tmdb_result.original_language,
                    'details': details
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting TMDB info: {e}")
            return None