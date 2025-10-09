"""
TMDB Cache System for storing and retrieving TMDB API results
"""
import json
import logging
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from services.tmdb_service import TMDBMovieResult


@dataclass
class TMDBCacheEntry:
    """Cache entry for TMDB results"""
    search_key: str
    result_data: Dict[str, Any]
    cached_at: str  # ISO format datetime
    expires_at: str  # ISO format datetime
    
    def is_valid(self) -> bool:
        """Check if cache entry is still valid"""
        try:
            expires = datetime.fromisoformat(self.expires_at)
            return datetime.now() < expires
        except (ValueError, TypeError):
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TMDBCacheEntry':
        """Create from dictionary"""
        return cls(**data)
    
    def get_tmdb_result(self) -> Optional[TMDBMovieResult]:
        """Convert cached data back to TMDBMovieResult"""
        try:
            return TMDBMovieResult(**self.result_data)
        except (TypeError, ValueError) as e:
            logging.getLogger(__name__).warning(f"Failed to deserialize cached TMDB result: {e}")
            return None


class TMDBCache:
    """
    Cache system for TMDB API results
    """
    
    def __init__(self, cache_duration_days: int = 7, cache_file: str = "tmdb_cache.json"):
        """
        Initialize TMDB cache
        
        Args:
            cache_duration_days: How many days to keep cache entries
            cache_file: Path to cache file
        """
        self.cache_duration_days = cache_duration_days
        self.cache_file = Path(cache_file)
        self.logger = logging.getLogger(__name__)
        self._cache_data: Dict[str, TMDBCacheEntry] = {}
        
        # Load existing cache
        self._load_cache()
        
        # Clean expired entries on startup
        self._clean_expired_cache()
    
    def _generate_cache_key(self, title: str, year: Optional[int] = None) -> str:
        """
        Generate a unique cache key for a movie search
        
        Args:
            title: Movie title
            year: Movie year (optional)
            
        Returns:
            str: Unique cache key
        """
        # Normalize title for consistent caching
        normalized_title = title.lower().strip()
        
        # Create key string
        key_string = f"{normalized_title}|{year if year else 'no_year'}"
        
        # Generate hash for consistent key length
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
    
    def get_cached_result(self, title: str, year: Optional[int] = None) -> Optional[TMDBMovieResult]:
        """
        Get cached TMDB result
        
        Args:
            title: Movie title to search for
            year: Movie year (optional)
            
        Returns:
            TMDBMovieResult: Cached result or None if not found/expired
        """
        cache_key = self._generate_cache_key(title, year)
        
        if cache_key not in self._cache_data:
            self.logger.debug(f"No cache entry found for: {title} ({year})")
            return None
        
        entry = self._cache_data[cache_key]
        
        if not entry.is_valid():
            self.logger.debug(f"Cache entry expired for: {title} ({year})")
            # Remove expired entry
            del self._cache_data[cache_key]
            self._save_cache()
            return None
        
        result = entry.get_tmdb_result()
        if result:
            self.logger.info(f"Cache hit for: {title} ({year}) -> {result.title}")
        else:
            self.logger.warning(f"Failed to deserialize cached result for: {title} ({year})")
            # Remove corrupted entry
            del self._cache_data[cache_key]
            self._save_cache()
        
        return result
    
    def cache_result(self, title: str, year: Optional[int], result: TMDBMovieResult) -> None:
        """
        Cache a TMDB result
        
        Args:
            title: Original search title
            year: Original search year
            result: TMDB result to cache
        """
        try:
            cache_key = self._generate_cache_key(title, year)
            
            # Create cache entry
            now = datetime.now()
            expires_at = now + timedelta(days=self.cache_duration_days)
            
            entry = TMDBCacheEntry(
                search_key=cache_key,
                result_data=asdict(result),
                cached_at=now.isoformat(),
                expires_at=expires_at.isoformat()
            )
            
            # Store in memory cache
            self._cache_data[cache_key] = entry
            
            # Save to disk
            self._save_cache()
            
            self.logger.info(f"Cached TMDB result: {title} ({year}) -> {result.title}")
            
        except Exception as e:
            self.logger.error(f"Failed to cache TMDB result for {title} ({year}): {e}")
    
    def is_cache_valid(self, title: str, year: Optional[int] = None) -> bool:
        """
        Check if cache entry exists and is valid
        
        Args:
            title: Movie title
            year: Movie year (optional)
            
        Returns:
            bool: True if valid cache entry exists
        """
        cache_key = self._generate_cache_key(title, year)
        
        if cache_key not in self._cache_data:
            return False
        
        return self._cache_data[cache_key].is_valid()
    
    def clear_expired_cache(self) -> int:
        """
        Remove expired cache entries
        
        Returns:
            int: Number of entries removed
        """
        return self._clean_expired_cache()
    
    def clear_all_cache(self) -> bool:
        """
        Clear all cache entries
        
        Returns:
            bool: True if successful
        """
        try:
            self._cache_data.clear()
            self._save_cache()
            self.logger.info("All cache entries cleared")
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dict: Cache statistics
        """
        total_entries = len(self._cache_data)
        valid_entries = sum(1 for entry in self._cache_data.values() if entry.is_valid())
        expired_entries = total_entries - valid_entries
        
        # Calculate cache size
        cache_size = 0
        if self.cache_file.exists():
            cache_size = self.cache_file.stat().st_size
        
        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'cache_file_size_bytes': cache_size,
            'cache_file_size_mb': round(cache_size / (1024 * 1024), 2),
            'cache_duration_days': self.cache_duration_days
        }
    
    def _load_cache(self) -> None:
        """Load cache from disk"""
        try:
            if not self.cache_file.exists():
                self.logger.info("No cache file found, starting with empty cache")
                return
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Convert to cache entries
            for key, entry_data in cache_data.items():
                try:
                    entry = TMDBCacheEntry.from_dict(entry_data)
                    self._cache_data[key] = entry
                except Exception as e:
                    self.logger.warning(f"Failed to load cache entry {key}: {e}")
            
            self.logger.info(f"Loaded {len(self._cache_data)} cache entries from {self.cache_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to load cache from {self.cache_file}: {e}")
            self._cache_data = {}
    
    def _save_cache(self) -> None:
        """Save cache to disk"""
        try:
            # Convert cache entries to serializable format
            cache_data = {}
            for key, entry in self._cache_data.items():
                cache_data[key] = entry.to_dict()
            
            # Write to file
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Cache saved to {self.cache_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save cache to {self.cache_file}: {e}")
    
    def _clean_expired_cache(self) -> int:
        """
        Remove expired cache entries
        
        Returns:
            int: Number of entries removed
        """
        expired_keys = []
        
        for key, entry in self._cache_data.items():
            if not entry.is_valid():
                expired_keys.append(key)
        
        # Remove expired entries
        for key in expired_keys:
            del self._cache_data[key]
        
        if expired_keys:
            self._save_cache()
            self.logger.info(f"Removed {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def optimize_memory_usage(self) -> Dict[str, int]:
        """
        Optimize cache memory usage by removing less useful entries
        
        Returns:
            Dict: Statistics about optimization
        """
        original_count = len(self._cache_data)
        
        if original_count == 0:
            return {'original_entries': 0, 'removed_entries': 0, 'final_entries': 0}
        
        # Remove expired entries first
        expired_removed = self._clean_expired_cache()
        
        # If still too many entries, remove oldest ones
        max_entries = 500  # Reasonable limit for memory usage
        oldest_removed = 0
        
        if len(self._cache_data) > max_entries:
            oldest_removed = self.optimize_cache(max_entries)
        
        final_count = len(self._cache_data)
        
        stats = {
            'original_entries': original_count,
            'expired_removed': expired_removed,
            'oldest_removed': oldest_removed,
            'removed_entries': expired_removed + oldest_removed,
            'final_entries': final_count
        }
        
        if stats['removed_entries'] > 0:
            self.logger.info(f"Cache optimized: {stats['removed_entries']} entries removed, {final_count} remaining")
        
        return stats
    
    def optimize_cache(self, max_entries: int = 1000) -> int:
        """
        Optimize cache by removing oldest entries if over limit
        
        Args:
            max_entries: Maximum number of entries to keep
            
        Returns:
            int: Number of entries removed
        """
        if len(self._cache_data) <= max_entries:
            return 0
        
        try:
            # Sort entries by cached_at date (oldest first)
            sorted_entries = sorted(
                self._cache_data.items(),
                key=lambda x: x[1].cached_at
            )
            
            # Keep only the most recent entries
            entries_to_keep = sorted_entries[-max_entries:]
            entries_to_remove = len(self._cache_data) - max_entries
            
            # Rebuild cache with only recent entries
            self._cache_data = dict(entries_to_keep)
            self._save_cache()
            
            self.logger.info(f"Cache optimized: removed {entries_to_remove} oldest entries")
            return entries_to_remove
            
        except Exception as e:
            self.logger.error(f"Failed to optimize cache: {e}")
            return 0