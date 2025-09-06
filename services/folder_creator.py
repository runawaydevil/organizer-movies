#!/usr/bin/env python3
"""
Folder creation service for organizing movies
AI-Powered Movie File Organizer with TMDB Integration

Author: Pablo Murad (runawaydevil)
Version: 0.01
Repository: https://github.com/runawaydevil/organizer-movies.git
"""
import os
import re
import logging
from pathlib import Path
from typing import Optional
from models.movie_metadata import MovieMetadata


class FolderCreator:
    """
    Creates and manages movie folders
    """
    
    def __init__(self, base_directory: str):
        """
        Initialize FolderCreator
        
        Args:
            base_directory: Base directory where folders will be created
        """
        self.base_directory = Path(base_directory)
        self.logger = logging.getLogger(__name__)
    
    def create_movie_folder(self, metadata: MovieMetadata) -> Path:
        """
        Create folder for movie based on metadata
        
        Args:
            metadata: Movie metadata
            
        Returns:
            Path: Path to created folder
        """
        folder_name = self.sanitize_folder_name(metadata.get_folder_name())
        folder_path = self.base_directory / folder_name
        
        # Handle duplicates
        folder_path = self.handle_duplicate_folders(folder_path)
        
        try:
            folder_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created folder: {folder_path}")
            return folder_path
            
        except Exception as e:
            self.logger.error(f"Error creating folder {folder_path}: {e}")
            raise
    
    def sanitize_folder_name(self, name: str) -> str:
        """
        Sanitize folder name for filesystem compatibility
        
        Args:
            name: Original folder name
            
        Returns:
            str: Sanitized folder name
        """
        if not name or not name.strip():
            return "Unknown Movie"
        
        # Remove invalid characters for Windows/cross-platform compatibility
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, '', name)
        
        # Remove control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32)
        
        # Remove extra whitespace and dots at the end
        sanitized = sanitized.strip().rstrip('.')
        
        # Replace multiple spaces with single space
        sanitized = ' '.join(sanitized.split())
        
        # Limit length to avoid filesystem issues
        if len(sanitized) > 100:
            sanitized = sanitized[:100].strip()
        
        # Ensure we have a valid name
        if not sanitized:
            sanitized = "Unknown Movie"
        
        return sanitized
    
    def handle_duplicate_folders(self, folder_path: Path) -> Path:
        """
        Handle duplicate folder names by adding numbers
        
        Args:
            folder_path: Original folder path
            
        Returns:
            Path: Unique folder path
        """
        if not folder_path.exists():
            return folder_path
        
        base_name = folder_path.name
        parent = folder_path.parent
        counter = 1
        
        while True:
            new_name = f"{base_name} ({counter})"
            new_path = parent / new_name
            
            if not new_path.exists():
                self.logger.info(f"Resolved duplicate: {folder_path} -> {new_path}")
                return new_path
            
            counter += 1
            
            # Safety check to avoid infinite loop
            if counter > 100:
                self.logger.warning(f"Too many duplicates for {base_name}, using timestamp")
                import time
                timestamp = int(time.time())
                new_name = f"{base_name} ({timestamp})"
                return parent / new_name
    
    def folder_exists(self, metadata: MovieMetadata) -> bool:
        """
        Check if folder already exists for this movie
        
        Args:
            metadata: Movie metadata
            
        Returns:
            bool: True if folder exists
        """
        folder_name = self.sanitize_folder_name(metadata.get_folder_name())
        folder_path = self.base_directory / folder_name
        return folder_path.exists()
    
    def get_folder_path(self, metadata: MovieMetadata) -> Path:
        """
        Get the path where folder would be created (without creating it)
        
        Args:
            metadata: Movie metadata
            
        Returns:
            Path: Proposed folder path
        """
        folder_name = self.sanitize_folder_name(metadata.get_folder_name())
        folder_path = self.base_directory / folder_name
        return self.handle_duplicate_folders(folder_path)