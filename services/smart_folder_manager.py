"""
Smart Folder Management System
Handles intelligent folder organization based on movie content
"""
import logging
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

from models.movie_metadata import MovieMetadata


class FolderActionType(Enum):
    """Types of folder actions"""
    NO_ACTION = "no_action"
    RENAME_FOLDER = "rename_folder"
    CREATE_INDIVIDUAL_FOLDERS = "create_individual_folders"


@dataclass
class FolderAction:
    """Action recommended for a folder"""
    action_type: FolderActionType
    target_name: Optional[str] = None
    individual_folders: List[str] = field(default_factory=list)
    reason: str = ""


@dataclass
class FolderAnalysis:
    """Analysis of folder content"""
    folder_path: Path
    movie_files: List[Path]
    movie_count: int
    has_single_movie: bool
    current_folder_name: str
    suggested_action: FolderAction
    
    @property
    def needs_folder_rename(self) -> bool:
        """Check if folder needs to be renamed"""
        return self.has_single_movie and not self.is_already_movie_folder()
    
    def is_already_movie_folder(self) -> bool:
        """Check if folder already follows movie naming convention (Title (Year))"""
        pattern = r'^.+\s\(\d{4}\)$'
        return bool(re.match(pattern, self.current_folder_name))


class SmartFolderManager:
    """
    Manages folders intelligently based on movie content
    """
    
    def __init__(self, video_extensions: Optional[List[str]] = None):
        """
        Initialize Smart Folder Manager
        
        Args:
            video_extensions: List of video file extensions to consider
        """
        self.logger = logging.getLogger(__name__)
        
        # Default video extensions
        self.video_extensions = video_extensions or [
            '.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm',
            '.m4v', '.3gp', '.ogv', '.ts', '.m2ts', '.mts'
        ]
        
        # Convert to lowercase for comparison
        self.video_extensions = [ext.lower() for ext in self.video_extensions]
    
    def analyze_folder_content(self, folder_path: Path) -> FolderAnalysis:
        """
        Analyze folder content and determine recommended action
        
        Args:
            folder_path: Path to folder to analyze
            
        Returns:
            FolderAnalysis: Analysis results with recommended action
        """
        try:
            if not folder_path.exists() or not folder_path.is_dir():
                raise ValueError(f"Invalid folder path: {folder_path}")
            
            # Find all movie files in the folder
            movie_files = self._find_movie_files(folder_path)
            movie_count = len(movie_files)
            
            self.logger.info(f"Analyzing folder '{folder_path.name}': found {movie_count} movie files")
            
            # Determine action based on movie count
            if movie_count == 0:
                action = FolderAction(
                    action_type=FolderActionType.NO_ACTION,
                    reason="No movie files found in folder"
                )
            elif movie_count == 1:
                action = self._analyze_single_movie_folder(folder_path, movie_files[0])
            else:
                action = self._analyze_multiple_movies_folder(folder_path, movie_files)
            
            # Create analysis result
            analysis = FolderAnalysis(
                folder_path=folder_path,
                movie_files=movie_files,
                movie_count=movie_count,
                has_single_movie=(movie_count == 1),
                current_folder_name=folder_path.name,
                suggested_action=action
            )
            
            self.logger.debug(f"Folder analysis complete: {action.action_type.value} - {action.reason}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing folder {folder_path}: {e}")
            
            # Return safe default analysis
            return FolderAnalysis(
                folder_path=folder_path,
                movie_files=[],
                movie_count=0,
                has_single_movie=False,
                current_folder_name=folder_path.name,
                suggested_action=FolderAction(
                    action_type=FolderActionType.NO_ACTION,
                    reason=f"Error analyzing folder: {str(e)}"
                )
            )
    
    def _find_movie_files(self, folder_path: Path) -> List[Path]:
        """
        Find all movie files in a folder (non-recursive)
        
        Args:
            folder_path: Path to search
            
        Returns:
            List[Path]: List of movie files found
        """
        movie_files = []
        
        try:
            for file_path in folder_path.iterdir():
                if file_path.is_file() and self._is_movie_file(file_path):
                    movie_files.append(file_path)
        except Exception as e:
            self.logger.warning(f"Error scanning folder {folder_path}: {e}")
        
        return sorted(movie_files)  # Sort for consistent ordering
    
    def _is_movie_file(self, file_path: Path) -> bool:
        """
        Check if file is a movie file based on extension
        
        Args:
            file_path: Path to check
            
        Returns:
            bool: True if it's a movie file
        """
        return file_path.suffix.lower() in self.video_extensions
    
    def _analyze_single_movie_folder(self, folder_path: Path, movie_file: Path) -> FolderAction:
        """
        Analyze folder with single movie
        
        Args:
            folder_path: Folder containing the movie
            movie_file: The single movie file
            
        Returns:
            FolderAction: Recommended action
        """
        current_name = folder_path.name
        
        # Check if folder already follows movie naming convention
        if re.match(r'^.+\s\(\d{4}\)$', current_name):
            return FolderAction(
                action_type=FolderActionType.NO_ACTION,
                reason=f"Folder '{current_name}' already follows movie naming convention"
            )
        
        # Recommend renaming folder
        return FolderAction(
            action_type=FolderActionType.RENAME_FOLDER,
            reason=f"Single movie in folder - should rename folder to movie title"
        )
    
    def _analyze_multiple_movies_folder(self, folder_path: Path, movie_files: List[Path]) -> FolderAction:
        """
        Analyze folder with multiple movies
        
        Args:
            folder_path: Folder containing movies
            movie_files: List of movie files
            
        Returns:
            FolderAction: Recommended action
        """
        return FolderAction(
            action_type=FolderActionType.CREATE_INDIVIDUAL_FOLDERS,
            reason=f"Multiple movies ({len(movie_files)}) in folder - should create individual folders"
        )
    
    def should_rename_existing_folder(self, folder_path: Path, movie_count: int) -> bool:
        """
        Determine if existing folder should be renamed
        
        Args:
            folder_path: Path to folder
            movie_count: Number of movies in folder
            
        Returns:
            bool: True if folder should be renamed
        """
        if movie_count != 1:
            return False
        
        # Check if already follows naming convention
        current_name = folder_path.name
        return not re.match(r'^.+\s\(\d{4}\)$', current_name)
    
    def rename_existing_folder(self, folder_path: Path, new_name: str) -> bool:
        """
        Rename existing folder
        
        Args:
            folder_path: Current folder path
            new_name: New folder name
            
        Returns:
            bool: True if successful
        """
        try:
            # Sanitize new name for filesystem
            sanitized_name = self._sanitize_folder_name(new_name)
            
            # Create new path
            new_path = folder_path.parent / sanitized_name
            
            # Check if target already exists
            if new_path.exists():
                self.logger.warning(f"Target folder already exists: {new_path}")
                return False
            
            # Rename folder
            folder_path.rename(new_path)
            
            self.logger.info(f"Renamed folder: '{folder_path.name}' -> '{sanitized_name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to rename folder {folder_path} to {new_name}: {e}")
            return False
    
    def create_individual_movie_folders(self, folder_path: Path, movies_metadata: List[MovieMetadata]) -> List[Path]:
        """
        Create individual folders for multiple movies
        
        Args:
            folder_path: Parent folder containing movies
            movies_metadata: List of movie metadata for naming folders
            
        Returns:
            List[Path]: List of created folder paths
        """
        created_folders = []
        
        try:
            for metadata in movies_metadata:
                # Generate folder name
                folder_name = self._generate_movie_folder_name(metadata)
                sanitized_name = self._sanitize_folder_name(folder_name)
                
                # Create folder path
                movie_folder_path = folder_path / sanitized_name
                
                # Create folder if it doesn't exist
                if not movie_folder_path.exists():
                    movie_folder_path.mkdir(parents=True, exist_ok=True)
                    created_folders.append(movie_folder_path)
                    self.logger.info(f"Created movie folder: {sanitized_name}")
                else:
                    self.logger.info(f"Movie folder already exists: {sanitized_name}")
                    created_folders.append(movie_folder_path)
            
            return created_folders
            
        except Exception as e:
            self.logger.error(f"Failed to create individual movie folders in {folder_path}: {e}")
            return []
    
    def move_movie_to_folder(self, movie_file: Path, target_folder: Path) -> bool:
        """
        Move movie file to target folder
        
        Args:
            movie_file: Path to movie file
            target_folder: Target folder path
            
        Returns:
            bool: True if successful
        """
        try:
            # Ensure target folder exists
            target_folder.mkdir(parents=True, exist_ok=True)
            
            # Create target file path
            target_file = target_folder / movie_file.name
            
            # Check if target already exists
            if target_file.exists():
                self.logger.warning(f"Target file already exists: {target_file}")
                return False
            
            # Move file
            movie_file.rename(target_file)
            
            self.logger.info(f"Moved movie: {movie_file.name} -> {target_folder.name}/")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to move {movie_file} to {target_folder}: {e}")
            return False
    
    def _generate_movie_folder_name(self, metadata: MovieMetadata) -> str:
        """
        Generate standardized folder name for movie
        
        Args:
            metadata: Movie metadata
            
        Returns:
            str: Folder name in format "Title (Year)"
        """
        title = metadata.title or "Unknown Movie"
        year = metadata.year
        
        if year:
            return f"{title} ({year})"
        else:
            return title
    
    def _sanitize_folder_name(self, name: str) -> str:
        """
        Sanitize folder name for media server and filesystem compatibility
        
        Args:
            name: Original folder name
            
        Returns:
            str: Sanitized folder name compatible with Plex, Jellyfin, etc.
        """
        if not name:
            return "Movie"
        
        # Start with the original name
        sanitized = name
        
        # Replace problematic characters for media servers and filesystems
        # These characters can cause issues with Plex, Jellyfin, and various filesystems
        char_replacements = {
            '<': '(',
            '>': ')',
            ':': ' -',  # Common in movie titles, replace with dash
            '"': "'",   # Replace double quotes with single quotes
            '/': '-',   # Replace forward slash with dash
            '\\': '-',  # Replace backslash with dash
            '|': '-',   # Replace pipe with dash
            '?': '',    # Remove question marks
            '*': '',    # Remove asterisks
            '\t': ' ',  # Replace tabs with spaces
            '\n': ' ',  # Replace newlines with spaces
            '\r': ' ',  # Replace carriage returns with spaces
        }
        
        for old_char, new_char in char_replacements.items():
            sanitized = sanitized.replace(old_char, new_char)
        
        # Remove multiple consecutive spaces
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Remove leading/trailing spaces and dots (problematic on Windows)
        sanitized = sanitized.strip(' .')
        
        # Handle special cases that media servers don't like
        # Remove trailing periods (Windows issue)
        while sanitized.endswith('.'):
            sanitized = sanitized[:-1].strip()
        
        # Ensure reasonable length (most filesystems support 255, but keep shorter for compatibility)
        if len(sanitized) > 200:
            # Try to cut at a word boundary
            if ' ' in sanitized[:200]:
                last_space = sanitized[:200].rfind(' ')
                sanitized = sanitized[:last_space]
            else:
                sanitized = sanitized[:200]
            sanitized = sanitized.strip()
        
        # Final check - ensure not empty and not just special characters
        if not sanitized or sanitized.isspace():
            sanitized = "Movie"
        
        # Ensure it doesn't end with a space or dot
        sanitized = sanitized.rstrip(' .')
        
        return sanitized
    
    def get_folder_organization_plan(self, folder_path: Path, movies_metadata: List[MovieMetadata]) -> Dict[str, Any]:
        """
        Get a plan for organizing folder without executing it
        
        Args:
            folder_path: Folder to analyze
            movies_metadata: Movie metadata for the files in folder
            
        Returns:
            Dict: Organization plan with details
        """
        analysis = self.analyze_folder_content(folder_path)
        
        plan = {
            'folder_path': str(folder_path),
            'current_name': folder_path.name,
            'movie_count': analysis.movie_count,
            'action_type': analysis.suggested_action.action_type.value,
            'reason': analysis.suggested_action.reason,
            'changes': []
        }
        
        if analysis.suggested_action.action_type == FolderActionType.RENAME_FOLDER:
            if movies_metadata and len(movies_metadata) > 0:
                new_name = self._generate_movie_folder_name(movies_metadata[0])
                plan['changes'].append({
                    'type': 'rename_folder',
                    'from': folder_path.name,
                    'to': new_name
                })
        
        elif analysis.suggested_action.action_type == FolderActionType.CREATE_INDIVIDUAL_FOLDERS:
            for metadata in movies_metadata:
                folder_name = self._generate_movie_folder_name(metadata)
                plan['changes'].append({
                    'type': 'create_folder',
                    'folder_name': folder_name,
                    'movie_file': metadata.original_filename
                })
        
        return plan