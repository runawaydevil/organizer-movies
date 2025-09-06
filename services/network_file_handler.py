"""
Network file handler for network-specific operations with retry logic
"""
import os
import time
import logging
from pathlib import Path
from typing import Callable, Any, Optional
from dataclasses import dataclass


@dataclass
class NetworkOperationResult:
    """Result of network file operation"""
    success: bool
    message: str
    retry_count: int
    final_path: Optional[Path] = None
    error_type: Optional[str] = None  # 'permission', 'network', 'space', 'other'


class NetworkFileHandler:
    """Handles network-specific file operations with retry logic"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        """
        Initialize NetworkFileHandler
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds for exponential backoff
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.logger = logging.getLogger(__name__)
    
    def is_network_path(self, path: Path) -> bool:
        """
        Check if path is on network location
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if path is on network location
        """
        try:
            path_str = str(path.resolve())
            
            # Check for UNC paths (\\server\share)
            if path_str.startswith('\\\\'):
                return True
            
            # Check for mapped network drives on Windows
            if os.name == 'nt':
                drive = path.drive if hasattr(path, 'drive') else path_str[:2]
                if drive and len(drive) == 2 and drive[1] == ':':
                    # Use Windows API to check if drive is network
                    try:
                        import ctypes
                        drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive + '\\')
                        # DRIVE_REMOTE = 4
                        return drive_type == 4
                    except (ImportError, AttributeError, OSError):
                        # Fallback: assume non-C: drives might be network
                        return drive.upper() != 'C:'
            
            # Check for common network mount points on Unix-like systems
            if os.name == 'posix':
                network_prefixes = ['/mnt/', '/media/', '/net/', '/Network/']
                return any(path_str.startswith(prefix) for prefix in network_prefixes)
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Could not determine if path is network: {path}, error: {e}")
            return False
    
    def check_network_connectivity(self, path: Path) -> bool:
        """
        Verify network path is accessible
        
        Args:
            path: Network path to check
            
        Returns:
            bool: True if path is accessible
        """
        try:
            # Try to access the path
            if path.exists():
                # Try to list contents if it's a directory
                if path.is_dir():
                    list(path.iterdir())
                # Try to read file info if it's a file
                elif path.is_file():
                    path.stat()
                return True
            else:
                # Try to access parent directory
                parent = path.parent
                if parent.exists() and parent.is_dir():
                    list(parent.iterdir())
                    return True
                return False
                
        except (OSError, PermissionError, TimeoutError) as e:
            self.logger.warning(f"Network connectivity check failed for {path}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error checking network connectivity for {path}: {e}")
            return False
    
    def execute_with_retry(self, operation: Callable, *args, **kwargs) -> NetworkOperationResult:
        """
        Execute operation with exponential backoff retry
        
        Args:
            operation: Function to execute
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            NetworkOperationResult: Result of the operation with retry information
        """
        last_exception = None
        retry_count = 0
        
        for attempt in range(self.max_retries + 1):
            try:
                # Execute the operation
                result = operation(*args, **kwargs)
                
                # If we get here, operation succeeded
                return NetworkOperationResult(
                    success=True,
                    message="Operation completed successfully",
                    retry_count=retry_count,
                    final_path=result if isinstance(result, Path) else None
                )
                
            except PermissionError as e:
                # Permission errors usually don't benefit from retry
                self.logger.error(f"Permission error on attempt {attempt + 1}: {e}")
                return NetworkOperationResult(
                    success=False,
                    message=f"Permission denied: {e}",
                    retry_count=retry_count,
                    error_type='permission'
                )
                
            except OSError as e:
                last_exception = e
                error_code = getattr(e, 'errno', None)
                
                # Categorize the error
                if error_code in [28, 122]:  # No space left, disk quota exceeded
                    return NetworkOperationResult(
                        success=False,
                        message=f"Insufficient disk space: {e}",
                        retry_count=retry_count,
                        error_type='space'
                    )
                elif error_code in [2, 3, 53, 67, 110, 111, 113]:  # File not found, path not found, network path not found, network name deleted, connection timed out, connection refused, no route to host
                    error_type = 'network'
                else:
                    error_type = 'other'
                
                # Check if we should retry
                if attempt < self.max_retries and self._is_retryable_error(e):
                    retry_count += 1
                    delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                    
                    self.logger.warning(f"Network operation failed on attempt {attempt + 1}, retrying in {delay}s: {e}")
                    time.sleep(delay)
                    continue
                else:
                    # Max retries reached or non-retryable error
                    return NetworkOperationResult(
                        success=False,
                        message=f"Network operation failed after {retry_count} retries: {e}",
                        retry_count=retry_count,
                        error_type=error_type
                    )
                    
            except Exception as e:
                last_exception = e
                
                # For unexpected errors, try once more if we haven't reached max retries
                if attempt < self.max_retries:
                    retry_count += 1
                    delay = self.base_delay * (2 ** attempt)
                    
                    self.logger.warning(f"Unexpected error on attempt {attempt + 1}, retrying in {delay}s: {e}")
                    time.sleep(delay)
                    continue
                else:
                    return NetworkOperationResult(
                        success=False,
                        message=f"Unexpected error after {retry_count} retries: {e}",
                        retry_count=retry_count,
                        error_type='other'
                    )
        
        # This should not be reached, but just in case
        return NetworkOperationResult(
            success=False,
            message=f"Operation failed after maximum retries: {last_exception}",
            retry_count=retry_count,
            error_type='other'
        )
    
    def _is_retryable_error(self, error: OSError) -> bool:
        """
        Determine if an OSError is retryable
        
        Args:
            error: The OSError to check
            
        Returns:
            bool: True if the error might be resolved by retrying
        """
        error_code = getattr(error, 'errno', None)
        
        # Retryable network errors
        retryable_codes = [
            11,   # Resource temporarily unavailable
            32,   # Broken pipe
            53,   # Network path not found (might be temporary)
            64,   # Network is down
            65,   # Network is unreachable
            67,   # Network name deleted
            104,  # Connection reset by peer
            110,  # Connection timed out
            111,  # Connection refused
            113,  # No route to host
        ]
        
        return error_code in retryable_codes
    
    def get_network_info(self, path: Path) -> dict:
        """
        Get information about network path
        
        Args:
            path: Path to analyze
            
        Returns:
            dict: Network information
        """
        info = {
            'is_network': self.is_network_path(path),
            'is_accessible': False,
            'path_type': 'unknown',
            'drive_type': 'unknown'
        }
        
        try:
            if path.exists():
                info['is_accessible'] = True
                info['path_type'] = 'directory' if path.is_dir() else 'file'
            
            # Get drive type on Windows
            if os.name == 'nt' and hasattr(path, 'drive'):
                try:
                    import ctypes
                    drive_type = ctypes.windll.kernel32.GetDriveTypeW(path.drive + '\\')
                    drive_types = {
                        0: 'unknown',
                        1: 'invalid',
                        2: 'removable',
                        3: 'fixed',
                        4: 'remote',
                        5: 'cdrom',
                        6: 'ramdisk'
                    }
                    info['drive_type'] = drive_types.get(drive_type, 'unknown')
                except (ImportError, AttributeError, OSError):
                    pass
            
        except Exception as e:
            self.logger.warning(f"Could not get network info for {path}: {e}")
        
        return info