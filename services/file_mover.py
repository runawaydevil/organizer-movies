#!/usr/bin/env python3
"""
File movement service for organizing movies
AI-Powered Movie File Organizer with TMDB Integration

Author: Pablo Murad (runawaydevil)
Version: 0.01
Repository: https://github.com/runawaydevil/organizer-movies.git
"""
import os
import shutil
import logging
from pathlib import Path
from typing import Optional, Tuple
import hashlib

from .network_file_handler import NetworkFileHandler
from .smart_folder_manager import SmartFolderManager


class FileMover:
    """
    Safely moves movie files to organized folders
    """
    
    def __init__(self, file_pattern: str = "{title} ({year}){extension}", 
                 max_retries: int = 3, base_delay: float = 1.0):
        """
        Initialize FileMover with configurable file naming pattern and network handling
        
        Args:
            file_pattern: Pattern for naming files (default: "{title} ({year}){extension}")
            max_retries: Maximum number of retry attempts for network operations
            base_delay: Base delay in seconds for exponential backoff
        """
        self.logger = logging.getLogger(__name__)
        self.file_pattern = file_pattern
        self.network_handler = NetworkFileHandler(max_retries=max_retries, base_delay=base_delay)
        self.smart_folder_manager = SmartFolderManager()
    
    def organize_movie_file(self, source_path: Path, metadata, target_folder: Path, file_pattern: str = None) -> Tuple[bool, str, Optional[Path]]:
        """
        Rename and move movie file to organized location
        
        Args:
            source_path: Original file path
            metadata: Movie metadata for naming
            target_folder: Destination folder
            file_pattern: Optional naming pattern (overrides default)
            
        Returns:
            Tuple[bool, str, Optional[Path]]: (success, message, final_path)
        """
        try:
            # Import here to avoid circular imports
            from models.movie_metadata import MovieMetadata
            
            # Validate inputs
            if not source_path.exists():
                return False, f"Source file does not exist: {source_path}", None
            
            if not source_path.is_file():
                return False, f"Source is not a file: {source_path}", None
            
            if not isinstance(metadata, MovieMetadata):
                return False, "Invalid metadata provided", None
            
            if not metadata.is_valid():
                return False, f"Invalid metadata for file: {source_path.name}", None
            
            # Create target folder if it doesn't exist
            try:
                target_folder.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return False, f"Failed to create target folder {target_folder}: {e}", None
            
            # Generate new filename based on metadata
            pattern = file_pattern or self.file_pattern
            new_filename = self._generate_filename(metadata, source_path.suffix, pattern)
            
            if not new_filename:
                return False, "Failed to generate valid filename", None
            
            # Create destination path
            destination_path = target_folder / new_filename
            
            # Handle file name conflicts
            destination_path = self._handle_file_conflicts(destination_path)
            
            # Check if we're dealing with network paths
            is_source_network = self.network_handler.is_network_path(source_path)
            is_dest_network = self.network_handler.is_network_path(destination_path)
            
            # Check network connectivity if needed
            if is_source_network and not self.network_handler.check_network_connectivity(source_path):
                return False, f"Source network path is not accessible: {source_path}", None
            
            if is_dest_network and not self.network_handler.check_network_connectivity(destination_path.parent):
                return False, f"Destination network path is not accessible: {destination_path.parent}", None
            
            # Check disk space
            if not self._check_disk_space(source_path, destination_path.parent):
                return False, "Insufficient disk space", None
            
            # Calculate source hash for verification
            source_hash = self._calculate_file_hash(source_path)
            
            # Log the move operation
            self.logger.info(f"Moving file: {source_path} -> {destination_path}")
            
            # Perform the move operation
            try:
                if is_source_network or is_dest_network:
                    self.logger.info(f"Network operation detected - using simple move")
                else:
                    self.logger.info(f"Local operation - using standard move")
                
                # Use simple shutil.move for all operations
                # This is more reliable than complex network handling
                self.logger.info(f"Moving: {source_path} -> {destination_path}")
                shutil.move(str(source_path), str(destination_path))
                self.logger.info(f"Move completed successfully")
                
            except Exception as e:
                self.logger.error(f"Move operation failed: {e}")
                return False, f"Failed to move file: {e}", None
            
            # Verify the move was successful
            if not self.verify_move_success(source_path, destination_path, source_hash):
                # Try to rollback
                self.rollback_move(source_path, destination_path)
                return False, "File verification failed after move", destination_path
            
            # Prepare success message with network info
            success_msg = f"Successfully organized: {source_path.name} -> {destination_path.name}"
            if is_source_network or is_dest_network:
                success_msg += " (network operation)"
            
            self.logger.info(success_msg)
            return True, success_msg, destination_path
            
        except PermissionError as e:
            error_msg = f"Permission denied: {e}"
            self.logger.error(error_msg)
            return False, error_msg, None
            
        except OSError as e:
            error_msg = f"OS error during organization: {e}"
            self.logger.error(error_msg)
            return False, error_msg, None
            
        except Exception as e:
            error_msg = f"Unexpected error during organization: {e}"
            self.logger.error(error_msg)
            return False, error_msg, None
    
    def _generate_filename(self, metadata, extension: str, pattern: str) -> str:
        """
        Generate filename based on metadata and pattern
        
        Args:
            metadata: Movie metadata
            extension: File extension
            pattern: Naming pattern
            
        Returns:
            str: Generated filename or empty string if failed
        """
        try:
            # Sanitize title for filename use
            safe_title = self._sanitize_filename(metadata.title)
            
            # Prepare replacement values
            replacements = {
                'title': safe_title,
                'year': str(metadata.year) if metadata.year else '',
                'extension': extension
            }
            
            # Generate filename from pattern
            filename = pattern.format(**replacements)
            
            # Clean up any double spaces or empty parentheses
            filename = filename.replace('  ', ' ').replace('()', '').replace(' .', '.').strip()
            
            # Ensure filename is not too long (Windows limit is 255 chars)
            if len(filename) > 200:  # Leave some buffer
                # Truncate title and regenerate
                max_title_length = 200 - len(pattern) + len('{title}')
                safe_title = safe_title[:max_title_length].strip()
                replacements['title'] = safe_title
                filename = pattern.format(**replacements)
                filename = filename.replace('  ', ' ').replace('()', '').strip()
            
            return filename if filename else None
            
        except Exception as e:
            self.logger.error(f"Error generating filename: {e}")
            return ""
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for filesystem compatibility
        
        Args:
            filename: Original filename
            
        Returns:
            str: Sanitized filename
        """
        if not filename:
            return "Unknown"
        
        # Remove invalid characters for Windows/cross-platform compatibility
        invalid_chars = r'[<>:"/\\|?*]'
        import re
        sanitized = re.sub(invalid_chars, '', filename)
        
        # Remove control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32)
        
        # Remove extra whitespace and dots at the end
        sanitized = sanitized.strip().rstrip('.')
        
        # Replace multiple spaces with single space
        sanitized = ' '.join(sanitized.split())
        
        return sanitized if sanitized else "Unknown"
    
    def move_file(self, source: Path, destination_folder: Path) -> Tuple[bool, Optional[str], Optional[Path]]:
        """
        Move file to destination folder
        
        Args:
            source: Source file path
            destination_folder: Destination folder path
            
        Returns:
            Tuple[bool, Optional[str], Optional[Path]]: (success, error_message, final_path)
        """
        try:
            # Validate source file
            if not source.exists():
                return False, f"Source file does not exist: {source}", None
            
            if not source.is_file():
                return False, f"Source is not a file: {source}", None
            
            # Create destination folder if it doesn't exist
            destination_folder.mkdir(parents=True, exist_ok=True)
            
            # Determine destination file path
            destination_file = destination_folder / source.name
            
            # Handle file name conflicts
            destination_file = self._handle_file_conflicts(destination_file)
            
            # Verify we have enough space
            if not self._check_disk_space(source, destination_file.parent):
                return False, "Insufficient disk space", None
            
            # Create backup of file hash for verification
            source_hash = self._calculate_file_hash(source)
            
            # Move the file
            shutil.move(str(source), str(destination_file))
            
            # Verify the move was successful
            if not self.verify_move_success(source, destination_file, source_hash):
                return False, "File verification failed after move", destination_file
            
            self.logger.info(f"Successfully moved: {source} -> {destination_file}")
            return True, None, destination_file
            
        except PermissionError as e:
            error_msg = f"Permission denied: {e}"
            self.logger.error(error_msg)
            return False, error_msg, None
            
        except OSError as e:
            error_msg = f"OS error during move: {e}"
            self.logger.error(error_msg)
            return False, error_msg, None
            
        except Exception as e:
            error_msg = f"Unexpected error during move: {e}"
            self.logger.error(error_msg)
            return False, error_msg, None
    
    def verify_move_success(self, original_source: Path, destination: Path, original_hash: Optional[str] = None) -> bool:
        """
        Verify that file was moved successfully
        
        Args:
            original_source: Original source path (should not exist)
            destination: Destination path (should exist)
            original_hash: Original file hash for verification
            
        Returns:
            bool: True if move was successful
        """
        try:
            # Check that source no longer exists
            if original_source.exists():
                self.logger.warning(f"Source file still exists after move: {original_source}")
                return False
            
            # Check that destination exists
            if not destination.exists():
                self.logger.error(f"Destination file does not exist after move: {destination}")
                return False
            
            # Verify file hash if provided
            if original_hash:
                destination_hash = self._calculate_file_hash(destination)
                if original_hash != destination_hash:
                    self.logger.error(f"File hash mismatch after move: {destination}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error verifying move: {e}")
            return False
    
    def rollback_move(self, source: Path, destination: Path) -> bool:
        """
        Rollback a file move operation
        
        Args:
            source: Original source path
            destination: Current destination path
            
        Returns:
            bool: True if rollback was successful
        """
        try:
            if destination.exists() and not source.exists():
                shutil.move(str(destination), str(source))
                self.logger.info(f"Rollback successful: {destination} -> {source}")
                return True
            else:
                self.logger.warning(f"Cannot rollback: source exists={source.exists()}, dest exists={destination.exists()}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during rollback: {e}")
            return False
    
    def _handle_file_conflicts(self, destination_file: Path) -> Path:
        """
        Handle file name conflicts by adding numbers
        
        Args:
            destination_file: Proposed destination file path
            
        Returns:
            Path: Unique destination file path
        """
        if not destination_file.exists():
            return destination_file
        
        base_name = destination_file.stem
        extension = destination_file.suffix
        parent = destination_file.parent
        counter = 1
        
        while True:
            new_name = f"{base_name} ({counter}){extension}"
            new_path = parent / new_name
            
            if not new_path.exists():
                self.logger.info(f"Resolved file conflict: {destination_file.name} -> {new_name}")
                return new_path
            
            counter += 1
            
            # Safety check
            if counter > 100:
                import time
                timestamp = int(time.time())
                new_name = f"{base_name}_{timestamp}{extension}"
                return parent / new_name
    
    def _check_disk_space(self, source: Path, destination_parent: Path) -> bool:
        """
        Check if there's enough disk space for the move
        
        Args:
            source: Source file
            destination_parent: Destination parent directory
            
        Returns:
            bool: True if there's enough space
        """
        try:
            source_size = source.stat().st_size
            
            # Get available space on destination drive
            if hasattr(shutil, 'disk_usage'):
                _, _, free_space = shutil.disk_usage(destination_parent)
                # Add 10% buffer
                required_space = int(source_size * 1.1)
                return free_space > required_space
            else:
                # Fallback - assume there's space
                return True
                
        except Exception as e:
            self.logger.warning(f"Could not check disk space: {e}")
            return True  # Assume there's space if we can't check
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate MD5 hash of file for verification
        
        Args:
            file_path: Path to file
            
        Returns:
            str: MD5 hash of file
        """
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                # Read in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
            
        except Exception as e:
            self.logger.warning(f"Could not calculate hash for {file_path}: {e}")
            return ""
    
    def is_file_locked(self, file_path: Path) -> bool:
        """
        Check if file is locked/in use
        
        Args:
            file_path: Path to file
            
        Returns:
            bool: True if file is locked
        """
        try:
            # Try to open file in exclusive mode
            with open(file_path, 'r+b') as f:
                pass
            return False
        except (IOError, OSError):
            return True    

    def get_network_info(self, path: Path) -> dict:
        """
        Get network information for a path
        
        Args:
            path: Path to analyze
            
        Returns:
            dict: Network information
        """
        return self.network_handler.get_network_info(path)
    
    def is_network_path(self, path: Path) -> bool:
        """
        Check if path is on network location
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if path is on network location
        """
        return self.network_handler.is_network_path(path)
    
    def check_network_connectivity(self, path: Path) -> bool:
        """
        Check network connectivity for a path
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if path is accessible
        """
        return self.network_handler.check_network_connectivity(path)
    
    def organize_folder_intelligently(self, folder_path: Path, movies_metadata: list) -> Tuple[bool, str, dict]:
        """
        Organize folder intelligently based on movie content
        
        Args:
            folder_path: Folder to organize
            movies_metadata: List of movie metadata for files in folder
            
        Returns:
            Tuple[bool, str, dict]: (success, message, organization_details)
        """
        try:
            # Analyze folder content
            analysis = self.smart_folder_manager.analyze_folder_content(folder_path)
            
            organization_details = {
                'folder_path': str(folder_path),
                'original_name': folder_path.name,
                'movie_count': analysis.movie_count,
                'action_taken': analysis.suggested_action.action_type.value,
                'changes': []
            }
            
            if analysis.suggested_action.action_type.value == "no_action":
                return True, analysis.suggested_action.reason, organization_details
            
            elif analysis.suggested_action.action_type.value == "rename_folder":
                # Single movie - rename folder
                if movies_metadata and len(movies_metadata) > 0:
                    metadata = movies_metadata[0]
                    new_folder_name = self.smart_folder_manager._generate_movie_folder_name(metadata)
                    
                    success = self.smart_folder_manager.rename_existing_folder(folder_path, new_folder_name)
                    
                    if success:
                        organization_details['changes'].append({
                            'type': 'folder_renamed',
                            'from': folder_path.name,
                            'to': new_folder_name
                        })
                        return True, f"Renamed folder to '{new_folder_name}'", organization_details
                    else:
                        return False, f"Failed to rename folder to '{new_folder_name}'", organization_details
                else:
                    return False, "No metadata available for folder renaming", organization_details
            
            elif analysis.suggested_action.action_type.value == "create_individual_folders":
                # Multiple movies - create individual folders
                if len(movies_metadata) != analysis.movie_count:
                    return False, f"Metadata count ({len(movies_metadata)}) doesn't match movie count ({analysis.movie_count})", organization_details
                
                # Create individual folders
                created_folders = self.smart_folder_manager.create_individual_movie_folders(folder_path, movies_metadata)
                
                if not created_folders:
                    return False, "Failed to create individual movie folders", organization_details
                
                # Move each movie to its folder
                moved_files = 0
                for i, (movie_file, metadata) in enumerate(zip(analysis.movie_files, movies_metadata)):
                    if i < len(created_folders):
                        target_folder = created_folders[i]
                        
                        # Move movie file to its folder
                        success = self.smart_folder_manager.move_movie_to_folder(movie_file, target_folder)
                        
                        if success:
                            moved_files += 1
                            organization_details['changes'].append({
                                'type': 'movie_moved',
                                'file': movie_file.name,
                                'to_folder': target_folder.name
                            })
                        else:
                            self.logger.warning(f"Failed to move {movie_file.name} to {target_folder.name}")
                
                if moved_files > 0:
                    return True, f"Created {len(created_folders)} folders and moved {moved_files} movies", organization_details
                else:
                    return False, "Failed to move any movies to individual folders", organization_details
            
            return False, f"Unknown action type: {analysis.suggested_action.action_type.value}", organization_details
            
        except Exception as e:
            self.logger.error(f"Error organizing folder {folder_path}: {e}")
            return False, f"Error organizing folder: {str(e)}", {}
    
    def get_folder_organization_plan(self, folder_path: Path, movies_metadata: list) -> dict:
        """
        Get organization plan without executing it
        
        Args:
            folder_path: Folder to analyze
            movies_metadata: Movie metadata for files in folder
            
        Returns:
            dict: Organization plan details
        """
        return self.smart_folder_manager.get_folder_organization_plan(folder_path, movies_metadata)