"""
Fast network scanner that avoids hangs on slow network locations
"""
import os
import logging
import threading
import time
from pathlib import Path
from typing import List, Set
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed


class FastNetworkScanner:
    """
    Fast scanner optimized for network locations with timeout handling
    """
    
    def __init__(self, source_directory: str, video_extensions: List[str], recursive: bool = True):
        """
        Initialize FastNetworkScanner
        
        Args:
            source_directory: Directory to scan
            video_extensions: List of video file extensions
            recursive: Whether to scan subdirectories
        """
        self.source_directory = Path(source_directory)
        self.video_extensions = set(ext.lower() for ext in video_extensions)
        self.recursive = recursive
        self.logger = logging.getLogger(__name__)
        
        # Timeouts for different operations (increased for large directories)
        self.dir_check_timeout = 10.0  # Timeout for checking if directory is accessible
        self.scan_timeout = 30.0       # Timeout for scanning a single directory
        self.max_workers = 6           # Maximum concurrent threads
        self.max_files_per_batch = 1000  # Process files in batches
        
    def scan_video_files(self) -> List[Path]:
        """
        Scan for video files with network optimizations
        
        Returns:
            List[Path]: List of video files found
        """
        video_files = []
        
        # Quick check if source directory is accessible
        if not self._is_directory_accessible(self.source_directory):
            self.logger.error(f"Source directory not accessible: {self.source_directory}")
            return video_files
        
        if self.recursive:
            video_files = self._scan_recursive_fast(self.source_directory)
        else:
            video_files = self._scan_directory_fast(self.source_directory)
        
        self.logger.info(f"Found {len(video_files)} video files in {self.source_directory}")
        return video_files
    
    def _is_directory_accessible(self, directory: Path, timeout: float = 3.0) -> bool:
        """
        Check if directory is accessible with timeout
        
        Args:
            directory: Directory to check
            timeout: Timeout in seconds
            
        Returns:
            bool: True if accessible
        """
        result = [False]
        error = [None]
        
        def check():
            try:
                if directory.exists() and directory.is_dir():
                    # Try to list one item to verify access
                    next(directory.iterdir(), None)
                    result[0] = True
            except Exception as e:
                error[0] = e
        
        thread = threading.Thread(target=check, daemon=True)
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            self.logger.warning(f"Directory check timed out: {directory}")
            return False
        
        if error[0]:
            self.logger.warning(f"Directory check failed: {directory} - {error[0]}")
            return False
        
        return result[0]
    
    def _scan_directory_fast(self, directory: Path) -> List[Path]:
        """
        Fast scan of a single directory with timeout
        
        Args:
            directory: Directory to scan
            
        Returns:
            List[Path]: Video files found
        """
        video_files = []
        
        def scan():
            try:
                for item in directory.iterdir():
                    if item.is_file() and self._is_video_file(item):
                        video_files.append(item)
                        self.logger.debug(f"Found video file: {item.name}")
            except Exception as e:
                self.logger.warning(f"Error scanning {directory}: {e}")
        
        # Run scan with timeout
        thread = threading.Thread(target=scan, daemon=True)
        thread.start()
        thread.join(self.scan_timeout)
        
        if thread.is_alive():
            self.logger.warning(f"Directory scan timed out: {directory}")
        
        return video_files
    
    def _scan_recursive_fast(self, root_directory: Path) -> List[Path]:
        """
        Fast recursive scan using thread pool with timeouts
        
        Args:
            root_directory: Root directory to scan
            
        Returns:
            List[Path]: All video files found
        """
        all_video_files = []
        directories_to_scan = [root_directory]
        scanned_directories = set()
        
        # First, collect all accessible directories
        self.logger.info("Collecting accessible directories...")
        
        while directories_to_scan:
            current_batch = directories_to_scan[:10]  # Process in batches
            directories_to_scan = directories_to_scan[10:]
            
            # Use thread pool to check directories in parallel
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_dir = {}
                
                for directory in current_batch:
                    if directory in scanned_directories:
                        continue
                    
                    scanned_directories.add(directory)
                    future = executor.submit(self._scan_directory_with_subdirs, directory)
                    future_to_dir[future] = directory
                
                # Collect results with timeout
                for future in as_completed(future_to_dir, timeout=30):
                    directory = future_to_dir[future]
                    try:
                        video_files, subdirs = future.result(timeout=self.scan_timeout)
                        all_video_files.extend(video_files)
                        
                        # Add new subdirectories to scan
                        for subdir in subdirs:
                            if subdir not in scanned_directories:
                                directories_to_scan.append(subdir)
                        
                        if video_files:
                            self.logger.info(f"Found {len(video_files)} videos in {directory}")
                        
                    except TimeoutError:
                        self.logger.warning(f"Scan timed out for directory: {directory}")
                    except Exception as e:
                        self.logger.warning(f"Error scanning directory {directory}: {e}")
        
        return all_video_files
    
    def _scan_directory_with_subdirs(self, directory: Path) -> tuple[List[Path], List[Path]]:
        """
        Scan directory for videos and return subdirectories
        
        Args:
            directory: Directory to scan
            
        Returns:
            tuple: (video_files, subdirectories)
        """
        video_files = []
        subdirectories = []
        
        try:
            # Quick accessibility check
            if not self._is_directory_accessible(directory, timeout=2.0):
                return video_files, subdirectories
            
            for item in directory.iterdir():
                try:
                    if item.is_file() and self._is_video_file(item):
                        video_files.append(item)
                    elif item.is_dir() and not self._should_skip_directory(item):
                        subdirectories.append(item)
                except OSError as e:
                    # Skip items that cause OS errors (permissions, network issues, etc.)
                    self.logger.debug(f"Skipping inaccessible item {item}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.warning(f"Error scanning directory {directory}: {e}")
        
        return video_files, subdirectories
    
    def _should_skip_directory(self, directory: Path) -> bool:
        """
        Check if directory should be skipped
        
        Args:
            directory: Directory to check
            
        Returns:
            bool: True if should skip
        """
        dir_name = directory.name.upper()
        
        # Skip common system/hidden directories
        skip_patterns = [
            'ORGANIZER',
            '$RECYCLE.BIN',
            'SYSTEM VOLUME INFORMATION',
            '.TRASH',
            '.THUMBNAILS',
            '@EADIR',  # Synology
            '.DS_STORE',  # macOS
        ]
        
        for pattern in skip_patterns:
            if pattern in dir_name:
                return True
        
        # Skip hidden directories
        if dir_name.startswith('.'):
            return True
        
        return False
    
    def _is_video_file(self, file_path: Path) -> bool:
        """
        Check if file is a video file
        
        Args:
            file_path: File to check
            
        Returns:
            bool: True if video file
        """
        return file_path.suffix.lower() in self.video_extensions
    
    def get_file_info(self, file_path: Path) -> dict:
        """
        Get file information with error handling
        
        Args:
            file_path: File to get info for
            
        Returns:
            dict: File information
        """
        try:
            stat = file_path.stat()
            return {
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "accessible": True
            }
        except Exception as e:
            self.logger.warning(f"Could not get file info for {file_path}: {e}")
            return {
                "size": 0,
                "modified": 0,
                "accessible": False
            }