#!/usr/bin/env python3
"""
Movie metadata data model
AI-Powered Movie File Organizer with TMDB Integration

Author: Pablo Murad (runawaydevil)
Version: 0.1
Repository: https://github.com/runawaydevil/organizer-movies.git
"""
from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class MovieMetadata:
    """
    Represents metadata extracted from a movie filename
    """
    title: str
    year: Optional[int]
    original_filename: str
    confidence_score: float
    
    def get_folder_name(self) -> str:
        """
        Generate standardized folder name based on metadata
        
        Returns:
            str: Folder name in format "Title - Year" or just "Title"
        """
        if self.year:
            return f"{self.title} - {self.year}"
        return self.title
    
    def is_valid(self) -> bool:
        """
        Validate metadata integrity
        
        Returns:
            bool: True if metadata is valid
        """
        if not self.title or not self.title.strip():
            return False
        
        if self.year is not None and (self.year < 1800 or self.year > 2030):
            return False
            
        if not (0.0 <= self.confidence_score <= 1.0):
            return False
            
        return True
    
    def sanitize_title(self) -> str:
        """
        Sanitize title for filesystem compatibility
        
        Returns:
            str: Sanitized title safe for folder names
        """
        if not self.title:
            return "Unknown Movie"
        
        # Remove invalid characters for Windows/cross-platform compatibility
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, '', self.title)
        
        # Remove control characters (ASCII 0-31)
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32)
        
        # Remove extra whitespace and dots at the end
        sanitized = sanitized.strip().rstrip('.')
        
        # Replace multiple spaces with single space
        sanitized = ' '.join(sanitized.split())
        
        # Limit length to avoid filesystem issues
        if len(sanitized) > 100:
            sanitized = sanitized[:100].strip()
            
        return sanitized if sanitized else "Unknown Movie"
    
    def get_clean_filename(self, pattern: str = "{title} ({year}){extension}", extension: str = "") -> str:
        """
        Generate clean filename based on pattern and metadata
        
        Args:
            pattern: Naming pattern with placeholders {title}, {year}, {extension}
            extension: File extension (including dot, e.g., ".mp4")
            
        Returns:
            str: Clean filename safe for filesystem use
        """
        # Get sanitized title
        safe_title = self.sanitize_title()
        
        # Handle different patterns
        if pattern == "{title} ({year}){extension}":
            # Default pattern
            if self.year:
                result = f"{safe_title} ({self.year}){extension}"
            else:
                result = f"{safe_title}{extension}"
        elif pattern == "{year} - {title}{extension}":
            # Year-first pattern
            if self.year:
                result = f"{self.year} - {safe_title}{extension}"
            else:
                result = f"{safe_title}{extension}"
        elif pattern == "{title}{extension}":
            # Title-only pattern
            result = f"{safe_title}{extension}"
        else:
            # Generic pattern handling using format
            try:
                replacements = {
                    'title': safe_title,
                    'year': str(self.year) if self.year else '',
                    'extension': extension
                }
                
                # Handle year-less patterns
                if not self.year and '{year}' in pattern:
                    pattern = pattern.replace(' ({year})', '').replace('({year})', '')
                    pattern = pattern.replace('{year} - ', '').replace(' - {year}', '')
                    pattern = pattern.replace('{year}', '')
                
                result = pattern.format(**replacements)
            except (KeyError, ValueError):
                # Fallback
                if self.year:
                    result = f"{safe_title} ({self.year}){extension}"
                else:
                    result = f"{safe_title}{extension}"
        
        # Clean up formatting
        result = result.replace('  ', ' ').replace('()', '').replace(' .', '.').strip()
        
        return result if result else f"Unknown Movie{extension}"
    
