"""
Fallback parser for movie filenames using regex patterns
"""
import re
import logging
from typing import Optional, Dict, Any
from models.movie_metadata import MovieMetadata


class FallbackParser:
    """
    Regex-based fallback parser for movie filenames
    """
    
    def __init__(self):
        """Initialize FallbackParser with common patterns"""
        self.logger = logging.getLogger(__name__)
        
        # Common movie filename patterns
        self.patterns = [
            # Pattern: Movie.Title.Year.Quality.Source.mkv
            r'^(.+?)\.(\d{4})\..*$',
            
            # Pattern: Movie Title (Year) [Quality].ext
            r'^(.+?)\s*\((\d{4})\).*$',
            
            # Pattern: Movie.Title.Year.ext
            r'^(.+?)\.(\d{4})\.[^.]*$',
            
            # Pattern: Movie Title Year Quality.ext
            r'^(.+?)\s+(\d{4})\s+.*$',
            
            # Pattern: Movie_Title_Year_Quality.ext
            r'^(.+?)_(\d{4})_.*$',
            
            # Pattern: Movie-Title-Year-Quality.ext
            r'^(.+?)-(\d{4})-.*$',
            
            # Pattern: Year.Movie.Title.Quality.ext
            r'^(\d{4})\.(.+?)\..*$',
            
            # Pattern: [Year] Movie Title [Quality].ext
            r'^\[(\d{4})\]\s*(.+?)\s*\[.*$',
            
            # Pattern: Movie.Title.YY.Quality.ext (2-digit year)
            r'^(.+?)\.(\d{2})\..*$',
            
            # Pattern: Just movie title with no year
            r'^(.+?)\.(?:BD|DVD|HD|720p|1080p|x264|x265).*$',
        ]
        
        # Compile patterns for better performance
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.patterns]
        
        # Common technical terms to remove from titles
        self.technical_terms = [
            'BD720p', 'BD1080p', 'DVDRip', 'TrialBD', 'HD1080p', 'TetraBD',
            'MemoriadaTV', 'Mini', 'HDTV', 'WEB-DL', 'BluRay', 'x264', 'x265',
            'HEVC', 'AAC', 'DTS', 'AC3', '5.1', '7.1', 'REMUX', 'REPACK',
            'PROPER', 'EXTENDED', 'UNRATED', 'DIRECTORS', 'CUT'
        ]
    
    def parse_filename(self, filename: str) -> MovieMetadata:
        """
        Parse movie filename using regex patterns
        
        Args:
            filename: Movie filename to parse
            
        Returns:
            MovieMetadata: Extracted metadata with low confidence score
        """
        if not filename or not filename.strip():
            return self._create_default_metadata(filename)
        
        # Remove file extension
        name_without_ext = self._remove_extension(filename)
        
        # Try each pattern
        for i, pattern in enumerate(self.compiled_patterns):
            match = pattern.match(name_without_ext)
            if match:
                self.logger.debug(f"Pattern {i} matched for '{filename}'")
                return self._extract_from_match(match, filename, i)
        
        # No pattern matched, return basic metadata
        self.logger.debug(f"No pattern matched for '{filename}', using basic extraction")
        return self._extract_basic_info(filename)
    
    def _remove_extension(self, filename: str) -> str:
        """Remove file extension from filename"""
        if '.' in filename:
            return filename.rsplit('.', 1)[0]
        return filename
    
    def _extract_from_match(self, match: re.Match, original_filename: str, pattern_index: int) -> MovieMetadata:
        """
        Extract metadata from regex match
        
        Args:
            match: Regex match object
            original_filename: Original filename
            pattern_index: Index of the pattern that matched
            
        Returns:
            MovieMetadata: Extracted metadata
        """
        groups = match.groups()
        
        if pattern_index == 6:  # Year.Movie.Title pattern
            year_str, title = groups[0], groups[1]
        elif pattern_index == 7:  # [Year] Movie Title pattern
            year_str, title = groups[0], groups[1]
        elif pattern_index == 8:  # 2-digit year pattern
            title, year_str = groups[0], groups[1]
            # Convert 2-digit year to 4-digit (assume 1900s for old movies, 2000s for recent)
            year_int = int(year_str)
            if year_int > 30:  # Assume 1931-1999
                year_str = f"19{year_str}"
            else:  # Assume 2000-2030
                year_str = f"20{year_str}"
        else:  # Most common patterns: Title.Year
            title, year_str = groups[0], groups[1]
        
        # Clean and validate title
        cleaned_title = self._clean_title(title)
        
        # Validate and convert year
        year = self._validate_year(year_str)
        
        # Calculate confidence based on pattern quality
        confidence = self._calculate_confidence(pattern_index, cleaned_title, year)
        
        return MovieMetadata(
            title=cleaned_title,
            year=year,
            original_filename=original_filename,
            confidence_score=confidence
        )
    
    def _extract_basic_info(self, filename: str) -> MovieMetadata:
        """
        Extract basic info when no pattern matches
        
        Args:
            filename: Original filename
            
        Returns:
            MovieMetadata: Basic metadata
        """
        # Remove extension and clean up
        name_without_ext = self._remove_extension(filename)
        cleaned_title = self._clean_title(name_without_ext)
        
        # Try to find a year anywhere in the filename (4-digit or 2-digit)
        year_match = re.search(r'\b(19\d{2}|20[0-3]\d)\b', filename)  # 4-digit year
        if not year_match:
            # Try 2-digit year
            two_digit_match = re.search(r'\.(\d{2})\.', filename)
            if two_digit_match:
                two_digit = int(two_digit_match.group(1))
                # Convert 2-digit to 4-digit (assume 1930-2030)
                if two_digit >= 30:
                    year = 1900 + two_digit
                else:
                    year = 2000 + two_digit
            else:
                year = None
        else:
            year = int(year_match.group(1))
        
        return MovieMetadata(
            title=cleaned_title if cleaned_title else filename,
            year=year,
            original_filename=filename,
            confidence_score=0.2 if year else 0.1
        )
    
    def _clean_title(self, title: str) -> str:
        """
        Clean movie title by removing technical terms and formatting
        
        Args:
            title: Raw title string
            
        Returns:
            str: Cleaned title
        """
        if not title:
            return ""
        
        # Replace dots, underscores, and dashes with spaces
        cleaned = re.sub(r'[._-]', ' ', title)
        
        # Remove technical terms
        for term in self.technical_terms:
            cleaned = re.sub(rf'\b{re.escape(term)}\b', '', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        cleaned = ' '.join(cleaned.split())
        
        # Capitalize properly
        cleaned = cleaned.title()
        
        return cleaned.strip()
    
    def _validate_year(self, year_str: str) -> Optional[int]:
        """
        Validate and convert year string to integer
        
        Args:
            year_str: Year string from regex match
            
        Returns:
            Optional[int]: Valid year or None
        """
        try:
            year = int(year_str)
            if 1800 <= year <= 2030:
                return year
        except (ValueError, TypeError):
            pass
        return None
    
    def _calculate_confidence(self, pattern_index: int, title: str, year: Optional[int]) -> float:
        """
        Calculate confidence score based on extraction quality
        
        Args:
            pattern_index: Index of matched pattern
            title: Extracted title
            year: Extracted year
            
        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        base_confidence = 0.3  # Base confidence for regex parsing
        
        # Adjust based on pattern quality
        pattern_quality = {
            0: 0.8,  # Movie.Title.Year.Quality - very reliable
            1: 0.7,  # Movie Title (Year) - reliable
            2: 0.6,  # Movie.Title.Year - good
            3: 0.5,  # Movie Title Year - okay
            4: 0.4,  # Movie_Title_Year - okay
            5: 0.4,  # Movie-Title-Year - okay
            6: 0.3,  # Year.Movie.Title - less reliable
            7: 0.5,  # [Year] Movie Title - okay
            8: 0.2,  # 2-digit year - unreliable
            9: 0.1,  # No year pattern - very unreliable
        }
        
        confidence = pattern_quality.get(pattern_index, base_confidence)
        
        # Boost confidence if we have both title and year
        if title and year:
            confidence += 0.1
        
        # Reduce confidence if title seems too short or generic
        if title and len(title.strip()) < 3:
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _create_default_metadata(self, filename: str) -> MovieMetadata:
        """
        Create default metadata for unparseable filenames
        
        Args:
            filename: Original filename
            
        Returns:
            MovieMetadata: Default metadata
        """
        return MovieMetadata(
            title=filename if filename else "Unknown Movie",
            year=None,
            original_filename=filename,
            confidence_score=0.0
        )