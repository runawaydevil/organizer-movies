#!/usr/bin/env python3
"""
TMDB (The Movie Database) service for movie metadata
AI-Powered Movie File Organizer with TMDB Integration

Author: Pablo Murad (runawaydevil)
Version: 0.1
Repository: https://github.com/runawaydevil/organizer-movies.git
"""
import requests
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import time


@dataclass
class TMDBMovieResult:
    """TMDB movie search result"""
    id: int
    title: str
    original_title: str
    year: Optional[int]
    overview: str
    poster_path: Optional[str]
    backdrop_path: Optional[str]
    vote_average: float
    vote_count: int
    popularity: float
    adult: bool
    original_language: str
    genre_ids: List[int]
    
    def get_display_title(self) -> str:
        """Get the best title for display (original if different from title)"""
        if self.original_title and self.original_title != self.title:
            return self.original_title
        return self.title
    
    def get_folder_name(self) -> str:
        """Get standardized folder name for media servers"""
        title = self.get_display_title()
        if self.year:
            return f"{title} ({self.year})"
        return title


class TMDBService:
    """Service for interacting with TMDB API"""
    
    def __init__(self, api_key: str, bearer_token: str, cache_duration_days: int = 7):
        """
        Initialize TMDB service
        
        Args:
            api_key: TMDB API key
            bearer_token: TMDB bearer token for API v4
            cache_duration_days: How many days to cache results
        """
        self.api_key = api_key
        self.bearer_token = bearer_token
        self.base_url = "https://api.themoviedb.org/3"
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.25  # 4 requests per second max
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json;charset=utf-8'
        })
        
        # Initialize cache
        from services.tmdb_cache import TMDBCache
        self.cache = TMDBCache(cache_duration_days=cache_duration_days)
        
        # Cache optimization counter
        self._cache_operations = 0
        self._optimization_interval = 50  # Optimize cache every 50 operations
    
    def _rate_limit(self):
        """Enforce rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def search_movie(self, title: str, year: Optional[int] = None, language: str = "en-US") -> List[TMDBMovieResult]:
        """
        Search for movies by title
        
        Args:
            title: Movie title to search for
            year: Optional year to filter results
            language: Language for results (default: en-US)
            
        Returns:
            List[TMDBMovieResult]: List of movie results
        """
        self._rate_limit()
        
        try:
            # Clean up title for search
            search_title = self._clean_title_for_search(title)
            
            params = {
                'query': search_title,
                'language': language,
                'include_adult': 'false',
                'page': 1
            }
            
            if year:
                params['year'] = year
                params['primary_release_year'] = year
            
            self.logger.debug(f"Searching TMDB for: '{search_title}' ({year})")
            
            response = self.session.get(f"{self.base_url}/search/movie", params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for movie_data in data.get('results', []):
                try:
                    # Parse release date for year
                    release_date = movie_data.get('release_date', '')
                    movie_year = None
                    if release_date:
                        movie_year = int(release_date.split('-')[0])
                    
                    result = TMDBMovieResult(
                        id=movie_data['id'],
                        title=movie_data['title'],
                        original_title=movie_data['original_title'],
                        year=movie_year,
                        overview=movie_data.get('overview', ''),
                        poster_path=movie_data.get('poster_path'),
                        backdrop_path=movie_data.get('backdrop_path'),
                        vote_average=movie_data.get('vote_average', 0.0),
                        vote_count=movie_data.get('vote_count', 0),
                        popularity=movie_data.get('popularity', 0.0),
                        adult=movie_data.get('adult', False),
                        original_language=movie_data.get('original_language', ''),
                        genre_ids=movie_data.get('genre_ids', [])
                    )
                    
                    results.append(result)
                    
                except (KeyError, ValueError) as e:
                    self.logger.warning(f"Error parsing movie result: {e}")
                    continue
            
            self.logger.info(f"Found {len(results)} TMDB results for '{search_title}'")
            return results
            
        except requests.RequestException as e:
            self.logger.error(f"TMDB API request failed: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error searching TMDB: {e}")
            return []
    
    def get_best_match(self, title: str, year: Optional[int] = None) -> Optional[TMDBMovieResult]:
        """
        Get the best matching movie from TMDB with caching
        
        Args:
            title: Movie title to search for
            year: Optional year to help with matching
            
        Returns:
            TMDBMovieResult: Best matching movie or None
        """
        # Check cache first
        cached_result = self.cache.get_cached_result(title, year)
        if cached_result:
            self.logger.debug(f"Using cached result for '{title}' ({year})")
            return cached_result
        
        # Search TMDB API
        results = self.search_movie(title, year)
        
        if not results:
            return None
        
        # If we have a year, prioritize exact year matches
        if year:
            exact_year_matches = [r for r in results if r.year == year]
            if exact_year_matches:
                # Sort by popularity and vote average
                exact_year_matches.sort(key=lambda x: (x.popularity, x.vote_average), reverse=True)
                best_match = exact_year_matches[0]
            else:
                # Sort all results by relevance (popularity, vote count, vote average)
                results.sort(key=lambda x: (x.popularity, x.vote_count, x.vote_average), reverse=True)
                best_match = results[0]
        else:
            # Sort all results by relevance (popularity, vote count, vote average)
            results.sort(key=lambda x: (x.popularity, x.vote_count, x.vote_average), reverse=True)
            best_match = results[0]
        
        # Cache the result
        self.cache.cache_result(title, year, best_match)
        
        # Periodic cache optimization for memory management
        self._cache_operations += 1
        if self._cache_operations % self._optimization_interval == 0:
            self._optimize_cache_if_needed()
        
        self.logger.info(f"Best TMDB match for '{title}': '{best_match.get_display_title()}' ({best_match.year})")
        return best_match
    
    def _optimize_cache_if_needed(self):
        """Optimize cache if it's getting too large"""
        try:
            stats = self.cache.get_cache_stats()
            
            # Optimize if cache has more than 300 entries
            if stats['total_entries'] > 300:
                optimization_stats = self.cache.optimize_memory_usage()
                self.logger.debug(f"Cache optimization: {optimization_stats}")
                
        except Exception as e:
            self.logger.warning(f"Cache optimization failed: {e}")
    
    def _clean_title_for_search(self, title: str) -> str:
        """
        Clean title for better TMDB search results
        
        Args:
            title: Original title
            
        Returns:
            str: Cleaned title
        """
        if not title:
            return ""
        
        # Remove common video quality indicators
        quality_indicators = [
            '1080p', '720p', '480p', '4k', 'uhd', 'hd', 'bluray', 'blu-ray', 'brrip', 'webrip', 
            'web-dl', 'dvdrip', 'hdtv', 'hdcam', 'cam', 'ts', 'tc', 'dvdscr', 'screener',
            'r5', 'r6', 'ac3', 'dts', 'aac', 'mp3', 'x264', 'x265', 'h264', 'h265', 'hevc',
            'xvid', 'divx', 'mpeg', 'avi', 'mkv', 'mp4', 'mov', 'wmv', 'flv', 'webm'
        ]
        
        # Remove release group indicators
        release_groups = [
            'yify', 'rarbg', 'etrg', 'shaanig', 'ganool', 'ozlem', 'juggs', 'sparks',
            'amiable', 'blow', 'rovers', 'psychd', 'geckos', 'dimension', 'killers'
        ]
        
        # Convert to lowercase for processing
        cleaned = title.lower()
        
        # Remove quality indicators
        for indicator in quality_indicators:
            cleaned = cleaned.replace(indicator, ' ')
        
        # Remove release groups
        for group in release_groups:
            cleaned = cleaned.replace(group, ' ')
        
        # Remove common separators and clean up
        cleaned = cleaned.replace('.', ' ').replace('_', ' ').replace('-', ' ')
        cleaned = cleaned.replace('[', ' ').replace(']', ' ').replace('(', ' ').replace(')', ' ')
        
        # Remove extra whitespace
        cleaned = ' '.join(cleaned.split())
        
        # Capitalize properly
        cleaned = cleaned.title()
        
        return cleaned.strip()
    
    def test_connection(self) -> bool:
        """
        Test TMDB API connection
        
        Returns:
            bool: True if connection is working
        """
        try:
            self._rate_limit()
            response = self.session.get(f"{self.base_url}/configuration")
            response.raise_for_status()
            
            self.logger.info("TMDB API connection test successful")
            return True
            
        except Exception as e:
            self.logger.error(f"TMDB API connection test failed: {e}")
            return False
    
    def get_movie_details(self, movie_id: int, language: str = "en-US") -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific movie
        
        Args:
            movie_id: TMDB movie ID
            language: Language for results
            
        Returns:
            Dict: Movie details or None
        """
        self._rate_limit()
        
        try:
            params = {'language': language}
            response = self.session.get(f"{self.base_url}/movie/{movie_id}", params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Error getting movie details for ID {movie_id}: {e}")
            return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dict: Cache statistics
        """
        return self.cache.get_cache_stats()
    
    def clear_cache(self) -> bool:
        """
        Clear all cached TMDB results
        
        Returns:
            bool: True if successful
        """
        return self.cache.clear_all_cache()
    
    def clear_expired_cache(self) -> int:
        """
        Remove expired cache entries
        
        Returns:
            int: Number of entries removed
        """
        return self.cache.clear_expired_cache()
    
    def optimize_cache(self, max_entries: int = 1000) -> int:
        """
        Optimize cache by removing oldest entries if over limit
        
        Args:
            max_entries: Maximum number of entries to keep
            
        Returns:
            int: Number of entries removed
        """
        return self.cache.optimize_cache(max_entries)