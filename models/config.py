#!/usr/bin/env python3
"""
Configuration and result data models
AI-Powered Movie File Organizer with TMDB Integration

Author: Pablo Murad (runawaydevil)
Version: 0.1
Repository: https://github.com/runawaydevil/organizer-movies.git
"""
from dataclasses import dataclass, field
from typing import Optional, List, Literal

try:
    from .movie_metadata import MovieMetadata
except ImportError:
    from movie_metadata import MovieMetadata


@dataclass
class LLMConfig:
    """LLM provider configuration (OpenAI or Ollama)."""
    provider: Literal["openai", "ollama"] = "openai"
    model: str = "gpt-4o-mini"
    openai_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"


@dataclass
class TMDBConfig:
    """
    TMDB-specific configuration
    """
    api_key: str = ""
    bearer_token: str = ""
    enabled: bool = False
    cache_duration_days: int = 7
    use_original_titles: bool = True
    language: str = "en-US"
    rate_limit_delay: float = 0.25
    
    def is_configured(self) -> bool:
        """Check if TMDB is properly configured"""
        return bool(self.api_key and self.bearer_token and self.enabled)


@dataclass
class OrganizerConfig:
    """
    Configuration for the Movie Organizer
    """
    source_directory: str
    organizer_directory: str
    openai_api_key: str
    video_extensions: List[str] = field(default_factory=lambda: [
        '.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', 
        '.m4v', '.3gp', '.ogv', '.ts', '.m2ts', '.mts'
    ])
    openai_model: str = "gpt-3.5-turbo"
    rate_limit_delay: float = 1.0
    max_retries: int = 3
    
    # TMDB configuration
    tmdb_config: TMDBConfig = field(default_factory=TMDBConfig)
    
    # Network-specific settings
    network_retry_attempts: int = 3
    network_retry_delay: float = 1.0
    network_timeout: float = 30.0
    skip_network_verification: bool = False
    
    # File naming settings  
    file_naming_pattern: str = "{title} ({year}){extension}"
    folder_naming_pattern: str = "{title} - {year}"
    handle_duplicates: bool = True
    max_filename_length: int = 200
    
    # Error handling
    continue_on_error: bool = True
    log_detailed_errors: bool = True
    show_error_details: bool = True
    
    def validate(self) -> bool:
        """
        Validate configuration parameters
        
        Returns:
            bool: True if configuration is valid
        """
        if not self.source_directory or not self.organizer_directory:
            return False
            
        if not self.openai_api_key or len(self.openai_api_key) < 10:
            return False
            
        if self.rate_limit_delay < 0 or self.max_retries < 0:
            return False
        
        # Validate network settings
        if self.network_retry_attempts < 0 or self.network_retry_attempts > 10:
            return False
            
        if self.network_retry_delay < 0 or self.network_retry_delay > 60:
            return False
            
        if self.network_timeout < 1 or self.network_timeout > 300:
            return False
        
        # Validate file naming settings
        if not self.file_naming_pattern or not self.folder_naming_pattern:
            return False
            
        if self.max_filename_length < 50 or self.max_filename_length > 255:
            return False
        
        # Validate TMDB settings if enabled
        if self.tmdb_config.enabled:
            if not self.tmdb_config.api_key or len(self.tmdb_config.api_key) < 10:
                return False
            if not self.tmdb_config.bearer_token or len(self.tmdb_config.bearer_token) < 10:
                return False
            if self.tmdb_config.cache_duration_days < 1 or self.tmdb_config.cache_duration_days > 30:
                return False
            if self.tmdb_config.rate_limit_delay < 0.1 or self.tmdb_config.rate_limit_delay > 5.0:
                return False
            
        return True


@dataclass
class ProcessResult:
    """
    Result of processing a single movie file
    """
    filename: str
    success: bool
    metadata: Optional[MovieMetadata] = None
    error_message: Optional[str] = None
    folder_created: Optional[str] = None
    original_path: Optional[str] = None
    new_path: Optional[str] = None
    
    def __str__(self) -> str:
        if self.success:
            return f"✓ {self.filename} -> {self.folder_created}"
        else:
            return f"✗ {self.filename}: {self.error_message}"


@dataclass
class OrganizationReport:
    """
    Final report of the organization process
    """
    total_files: int = 0
    processed_files: int = 0
    successful_moves: int = 0
    failed_moves: int = 0
    folders_created: int = 0
    results: List[ProcessResult] = field(default_factory=list)
    
    def add_result(self, result: ProcessResult):
        """Add a process result to the report"""
        self.results.append(result)
        self.processed_files += 1
        
        if result.success:
            self.successful_moves += 1
            if result.folder_created:
                self.folders_created += 1
        else:
            self.failed_moves += 1
    
    def get_success_rate(self) -> float:
        """Calculate success rate as percentage"""
        if self.processed_files == 0:
            return 0.0
        return (self.successful_moves / self.processed_files) * 100
    
    def get_summary(self) -> str:
        """Generate a summary string of the organization process"""
        summary = f"""
=== Movie Organization Report ===
Total files found: {self.total_files}
Files processed: {self.processed_files}
Successful moves: {self.successful_moves}
Failed moves: {self.failed_moves}
Folders created: {self.folders_created}
Success rate: {self.get_success_rate():.1f}%

"""
        
        if self.failed_moves > 0:
            summary += "Failed files:\n"
            for result in self.results:
                if not result.success:
                    summary += f"  - {result.filename}: {result.error_message}\n"
        
        return summary