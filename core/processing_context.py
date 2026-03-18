#!/usr/bin/env python3
"""
Processing context and error handling for Movie Organizer
AI-Powered Movie File Organizer with TMDB Integration

Author: Pablo Murad (runawaydevil)
Version: 0.1
Repository: https://github.com/runawaydevil/organizer-movies.git
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import logging
import time
from pathlib import Path


@dataclass
class ProcessingContext:
    """Context for tracking processing state and progress"""

    total_files: int
    processed_files: int = 0
    successful_moves: int = 0
    failed_moves: int = 0
    current_file: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    skipped_files: int = 0
    start_time: float = field(default_factory=time.time)
    network_operations: int = 0
    retry_operations: int = 0

    def add_success(self, filename: str, message: str = "", final_path: Optional[str] = None):
        """Record successful operation"""
        self.processed_files += 1
        self.successful_moves += 1
        if message:
            self.logger.info(f"[SUCCESS] {filename}: {message}")

    def add_failure(self, filename: str, error: str, error_type: str = "other"):
        """Record failed operation"""
        self.processed_files += 1
        self.failed_moves += 1
        self.errors.append(f"{filename}: {error}")
        self.logger.error(f"[ERROR] {filename}: {error}")

    def add_warning(self, filename: str, warning: str):
        """Record warning"""
        self.warnings.append(f"{filename}: {warning}")
        self.logger.warning(f"[WARNING] {filename}: {warning}")

    def add_skipped(self, filename: str, reason: str):
        """Record skipped file"""
        self.skipped_files += 1
        self.logger.info(f"[SKIPPED] {filename}: {reason}")

    def set_current_file(self, filename: str):
        """Set current file being processed"""
        self.current_file = filename

    def increment_network_operations(self):
        """Increment network operations counter"""
        self.network_operations += 1

    def increment_retry_operations(self):
        """Increment retry operations counter"""
        self.retry_operations += 1

    def get_progress_percentage(self) -> float:
        """Get processing progress as percentage"""
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100

    def get_elapsed_time(self) -> float:
        """Get elapsed time since processing started"""
        return time.time() - self.start_time

    def get_estimated_remaining_time(self) -> float:
        """Get estimated remaining time based on current progress"""
        if self.processed_files == 0:
            return 0.0

        elapsed = self.get_elapsed_time()
        avg_time_per_file = elapsed / self.processed_files
        remaining_files = self.total_files - self.processed_files

        return avg_time_per_file * remaining_files

    def finish_processing(self):
        """Mark processing as finished"""
        self.current_file = None
        self.logger.info(f"Processing finished: {self.successful_moves} successful, {self.failed_moves} failed, {self.skipped_files} skipped")

    def get_summary_report(self) -> Dict[str, Any]:
        """Get comprehensive processing summary"""
        return {
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "successful_moves": self.successful_moves,
            "failed_moves": self.failed_moves,
            "skipped_files": self.skipped_files,
            "network_operations": self.network_operations,
            "retry_operations": self.retry_operations,
            "success_rate": (self.successful_moves / self.total_files * 100) if self.total_files > 0 else 0,
            "elapsed_time": self.get_elapsed_time(),
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
            "current_file": self.current_file
        }

    @property
    def logger(self):
        """Get logger instance"""
        return logging.getLogger(__name__)


class ErrorHandler:
    """Handles errors during processing with categorization and recovery"""

    def __init__(self, continue_on_error: bool = True, max_errors: int = 10):
        self.continue_on_error = continue_on_error
        self.max_errors = max_errors
        self.error_count = 0
        self.critical_errors = 0
        self.logger = logging.getLogger(__name__)

    def handle_error(self, error: Exception, context: ProcessingContext, filename: str) -> bool:
        """
        Handle error and determine if processing should continue

        Args:
            error: The exception that occurred
            context: Processing context for tracking
            filename: Name of file being processed

        Returns:
            bool: True if processing should continue, False if should stop
        """
        self.error_count += 1
        error_str = str(error)

        # Categorize error
        error_type = self._categorize_error(error)

        # Log error with category
        self.logger.error(f"Error in {filename} ({error_type}): {error_str}")

        # Add to context
        context.add_failure(filename, f"{error_type}: {error_str}")

        # Determine if this is a critical error
        is_critical = self._is_critical_error(error, error_type)

        if is_critical:
            self.critical_errors += 1
            self.logger.critical(f"Critical error #{self.critical_errors}: {error_str}")

        # Check if we should continue
        should_continue = self._should_continue_processing(error_type, is_critical)

        if not should_continue:
            self.logger.critical(f"Stopping processing due to error limit or critical error")

        return should_continue

    def _categorize_error(self, error: Exception) -> str:
        """Categorize error type for better handling"""
        error_str = str(error).lower()

        # Network-related errors
        if any(keyword in error_str for keyword in ['network', 'connection', 'timeout', 'unreachable', 'host']):
            return "network"

        # Permission errors
        if any(keyword in error_str for keyword in ['permission', 'access denied', 'unauthorized', 'forbidden']):
            return "permission"

        # File system errors
        if any(keyword in error_str for keyword in ['disk full', 'no space', 'path too long', 'invalid character']):
            return "filesystem"

        # File conflicts
        if any(keyword in error_str for keyword in ['already exists', 'file in use', 'locked', 'conflict']):
            return "conflict"

        # API errors
        if any(keyword in error_str for keyword in ['api', 'rate limit', 'quota', 'authentication']):
            return "api"

        # Default category
        return "other"

    def _is_critical_error(self, error: Exception, error_type: str) -> bool:
        """Determine if error is critical and should stop processing"""
        error_str = str(error).lower()

        # Critical error conditions
        critical_conditions = [
            'disk full',
            'no space',
            'access denied',
            'permission denied',
            'authentication failed',
            'api key invalid'
        ]

        return any(condition in error_str for condition in critical_conditions)

    def _should_continue_processing(self, error_type: str, is_critical: bool) -> bool:
        """Determine if processing should continue based on error"""

        # Don't continue if we've hit the error limit
        if self.error_count >= self.max_errors:
            return False

        # Don't continue if we have too many critical errors
        if self.critical_errors >= 3:
            return False

        # Don't continue if user disabled continue-on-error
        if not self.continue_on_error:
            return False

        # Don't continue for critical errors
        if is_critical:
            return False

        # Continue for non-critical errors
        return True

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors encountered"""
        return {
            "total_errors": self.error_count,
            "critical_errors": self.critical_errors,
            "continue_on_error": self.continue_on_error,
            "max_errors": self.max_errors,
            "can_continue": self.error_count < self.max_errors and self.critical_errors < 3
        }
