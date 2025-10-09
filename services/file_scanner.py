#!/usr/bin/env python3
"""
File scanning service for detecting video files
AI-Powered Movie File Organizer with TMDB Integration

Author: Pablo Murad (runawaydevil)
Version: 0.1
Repository: https://github.com/runawaydevil/organizer-movies.git
"""
import os
from pathlib import Path
from typing import List, Set
import logging


class FileScanner:
    """
    Scans directories for video files
    """
    
    def __init__(self, source_directory: str, video_extensions: List[str], recursive: bool = True):
        """
        Initialize FileScanner
        
        Args:
            source_directory: Directory to scan for video files
            video_extensions: List of valid video file extensions
            recursive: Whether to scan subdirectories (default: True)
        """
        self.source_directory = Path(source_directory)
        self.video_extensions = set(ext.lower() for ext in video_extensions)
        self.recursive = recursive
        self.logger = logging.getLogger(__name__)
        
    def scan_video_files(self) -> List[Path]:
        """
        Scan source directory for video files with network timeout handling
        
        Returns:
            List[Path]: List of video file paths found
        """
        video_files = []
        
        # Check if directory exists with timeout for network paths
        try:
            if not self._check_directory_with_timeout(self.source_directory):
                return video_files
        except Exception as e:
            self.logger.error(f"Error checking directory: {e}")
            return video_files
        
        try:
            if self.recursive:
                # Scan recursively including subdirectories
                video_files = self._scan_recursive(self.source_directory)
            else:
                # Scan only files in the source directory (not subdirectories)
                video_files = self._scan_directory(self.source_directory)
                        
        except PermissionError as e:
            self.logger.error(f"Permission denied accessing directory: {e}")
        except OSError as e:
            if e.errno in [53, 67, 110, 111]:  # Network-related errors
                self.logger.error(f"Network error scanning directory: {e}")
            else:
                self.logger.error(f"OS error scanning directory: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error scanning directory: {e}")
            
        self.logger.info(f"Found {len(video_files)} video files in {self.source_directory}")
        return video_files
    
    def _check_directory_with_timeout(self, directory: Path, timeout: float = 10.0) -> bool:
        """
        Check if directory exists and is accessible with timeout
        
        Args:
            directory: Directory to check
            timeout: Timeout in seconds
            
        Returns:
            bool: True if directory is accessible
        """
        import signal
        import threading
        
        result = [False]  # Use list to allow modification in nested function
        error = [None]
        
        def check_directory():
            try:
                if not directory.exists():
                    self.logger.warning(f"Source directory does not exist: {directory}")
                    return
                    
                if not directory.is_dir():
                    self.logger.warning(f"Source path is not a directory: {directory}")
                    return
                
                # Try to list directory contents to verify access
                list(directory.iterdir())
                result[0] = True
                
            except Exception as e:
                error[0] = e
        
        # Start check in thread with timeout
        thread = threading.Thread(target=check_directory, daemon=True)
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            self.logger.error(f"Directory check timed out after {timeout}s: {directory}")
            return False
        
        if error[0]:
            raise error[0]
        
        return result[0]
    
    def _scan_directory(self, directory: Path) -> List[Path]:
        """
        Scan a single directory for video files with error handling and timeout
        
        Args:
            directory: Directory to scan
            
        Returns:
            List[Path]: List of video files found
        """
        video_files = []
        
        try:
            # Use timeout for directory listing on network paths
            items = self._list_directory_with_timeout(directory, timeout=10.0)
            if items is None:
                self.logger.warning(f"Directory listing timed out: {directory}")
                return video_files
            
            for item in items:
                try:
                    # Quick check to avoid slow operations
                    item_name = item.name.upper()
                    
                    # Skip ORGANIZER directories
                    if "ORGANIZER" in item_name:
                        self.logger.info(f"Skipping ORGANIZER directory: {item}")
                        continue
                    
                    # Check if it's a file and video file (avoid slow is_file() calls on network)
                    if self.is_video_file(item):
                        # Only do expensive checks if it looks like a video file
                        if self._is_accessible_quick(item):
                            video_files.append(item)
                            self.logger.debug(f"Found video file: {item.name}")
                        else:
                            self.logger.warning(f"Video file not accessible: {item.name}")
                
                except Exception as e:
                    self.logger.warning(f"Error checking item {item}: {e}")
                    continue
        
        except OSError as e:
            if e.errno in [53, 67, 110, 111]:  # Network-related errors
                self.logger.error(f"Network error scanning {directory}: {e}")
            else:
                self.logger.error(f"OS error scanning {directory}: {e}")
        except Exception as e:
            self.logger.error(f"Error scanning {directory}: {e}")
        
        return video_files
    
    def _list_directory_with_timeout(self, directory: Path, timeout: float = 10.0):
        """
        List directory contents with timeout
        
        Args:
            directory: Directory to list
            timeout: Timeout in seconds
            
        Returns:
            List of Path objects or None if timeout
        """
        import threading
        
        result = [None]
        error = [None]
        
        def list_directory():
            try:
                result[0] = list(directory.iterdir())
            except Exception as e:
                error[0] = e
        
        thread = threading.Thread(target=list_directory, daemon=True)
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            self.logger.warning(f"Directory listing timed out after {timeout}s: {directory}")
            return None
        
        if error[0]:
            raise error[0]
        
        return result[0]
    
    def _is_accessible_quick(self, file_path: Path) -> bool:
        """
        Quick accessibility check without expensive operations
        
        Args:
            file_path: File to check
            
        Returns:
            bool: True if accessible
        """
        try:
            # Just check if we can get basic info
            file_path.stat()
            return True
        except:
            return False
    
    def _scan_recursive(self, directory: Path) -> List[Path]:
        """
        Recursively scan directory and subdirectories for video files with network handling
        
        Args:
            directory: Directory to scan
            
        Returns:
            List[Path]: List of video file paths found
        """
        video_files = []
        
        # First scan current directory
        video_files.extend(self._scan_directory(directory))
        
        # Then scan subdirectories with timeout
        try:
            # Use timeout for directory listing
            items = self._list_directory_with_timeout(directory, timeout=10.0)
            if items is None:
                self.logger.warning(f"Directory listing timed out for recursive scan: {directory}")
                return video_files
            
            for item in items:
                try:
                    # Quick name check to avoid slow operations
                    item_name = item.name.upper()
                    
                    # Skip ORGANIZER directories
                    if "ORGANIZER" in item_name:
                        self.logger.info(f"Skipping ORGANIZER directory: {item}")
                        continue
                    
                    # Check if it's a directory (this might be slow on network)
                    try:
                        is_dir = item.is_dir()
                    except:
                        # If we can't determine, skip it
                        continue
                    
                    if is_dir:
                        try:
                            # Check if subdirectory is accessible with timeout
                            if self._check_directory_with_timeout(item, timeout=3.0):
                                subdirectory_files = self._scan_recursive(item)
                                video_files.extend(subdirectory_files)
                                if subdirectory_files:
                                    self.logger.debug(f"Found {len(subdirectory_files)} video files in subdirectory: {item}")
                            else:
                                self.logger.warning(f"Skipping inaccessible subdirectory: {item}")
                        except PermissionError:
                            self.logger.warning(f"Permission denied accessing subdirectory: {item}")
                        except Exception as e:
                            self.logger.warning(f"Error scanning subdirectory {item}: {e}")
                
                except Exception as e:
                    self.logger.warning(f"Error processing item {item}: {e}")
                    continue
        
        except OSError as e:
            if e.errno in [53, 67, 110, 111]:  # Network-related errors
                self.logger.error(f"Network error during recursive scan of {directory}: {e}")
            else:
                self.logger.error(f"OS error during recursive scan of {directory}: {e}")
        except Exception as e:
            self.logger.error(f"Error during recursive scan of {directory}: {e}")
        
        return video_files
    
    def is_video_file(self, file_path: Path) -> bool:
        """
        Check if a file is a video file based on extension
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            bool: True if file is a video file
        """
        if not file_path.is_file():
            return False
            
        extension = file_path.suffix.lower()
        return extension in self.video_extensions
    
    def _is_accessible(self, file_path: Path) -> bool:
        """
        Check if a file is accessible for reading
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            bool: True if file is accessible
        """
        try:
            # Check if file exists and is readable
            return file_path.exists() and os.access(file_path, os.R_OK)
        except Exception:
            return False
    
    def filter_valid_files(self, file_paths: List[Path]) -> List[Path]:
        """
        Filter list of files to only include valid, accessible video files
        
        Args:
            file_paths: List of file paths to filter
            
        Returns:
            List[Path]: Filtered list of valid video files
        """
        valid_files = []
        
        for file_path in file_paths:
            if self.is_valid_video_file(file_path):
                valid_files.append(file_path)
            else:
                self.logger.debug(f"Filtered out invalid file: {file_path.name}")
                
        return valid_files
    
    def is_valid_video_file(self, file_path: Path) -> bool:
        """
        Comprehensive validation of video file
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            bool: True if file is a valid, accessible video file
        """
        # Check if it's a video file by extension
        if not self.is_video_file(file_path):
            return False
            
        # Check if file is accessible
        if not self._is_accessible(file_path):
            self.logger.warning(f"Video file not accessible: {file_path.name}")
            return False
            
        # Check minimum file size (avoid empty or corrupted files)
        try:
            if file_path.stat().st_size < 1024:  # Less than 1KB
                self.logger.warning(f"Video file too small: {file_path.name}")
                return False
        except Exception:
            return False
            
        return True
    
    def get_supported_extensions(self) -> Set[str]:
        """
        Get set of supported video extensions
        
        Returns:
            Set[str]: Set of supported extensions
        """
        return self.video_extensions.copy()
    
    def get_file_info(self, file_path: Path) -> dict:
        """
        Get basic information about a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            dict: File information including size, modified time, etc.
        """
        try:
            stat = file_path.stat()
            return {
                'name': file_path.name,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'extension': file_path.suffix.lower(),
                'accessible': self._is_accessible(file_path),
                'is_video': self.is_video_file(file_path),
                'is_valid': self.is_valid_video_file(file_path)
            }
        except Exception as e:
            self.logger.error(f"Error getting file info for {file_path}: {e}")
            return {
                'name': file_path.name,
                'size': 0,
                'modified': 0,
                'extension': file_path.suffix.lower(),
                'accessible': False,
                'is_video': False,
                'is_valid': False
            }