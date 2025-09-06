"""
TMDB Configuration Manager
"""
import logging
import json
from pathlib import Path
from typing import Optional
from models.config import TMDBConfig
from services.tmdb_service import TMDBService


class TMDBConfigManager:
    """
    Manages TMDB-specific configuration and validation
    """
    
    def __init__(self):
        """Initialize TMDB configuration manager"""
        self.logger = logging.getLogger(__name__)
        self.config_file = Path("tmdb_config.json")
    
    def validate_api_credentials(self, api_key: str, bearer_token: str) -> tuple[bool, str]:
        """
        Validate TMDB API credentials by testing connection
        
        Args:
            api_key: TMDB API key
            bearer_token: TMDB bearer token
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        try:
            if not api_key or len(api_key) < 10:
                return False, "API key is too short or empty"
            
            if not bearer_token or len(bearer_token) < 10:
                return False, "Bearer token is too short or empty"
            
            # Test connection with provided credentials
            tmdb_service = TMDBService(api_key, bearer_token, cache_duration_days=1)  # Short cache for testing
            
            if tmdb_service.test_connection():
                self.logger.info("TMDB API credentials validated successfully")
                return True, "Connection successful"
            else:
                return False, "Failed to connect to TMDB API - check your credentials"
                
        except Exception as e:
            self.logger.error(f"Error validating TMDB credentials: {e}")
            return False, f"Validation error: {str(e)}"
    
    def save_tmdb_config(self, config: TMDBConfig) -> bool:
        """
        Save TMDB configuration to file
        
        Args:
            config: TMDB configuration to save
            
        Returns:
            bool: True if saved successfully
        """
        try:
            config_data = {
                'api_key': config.api_key,
                'bearer_token': config.bearer_token,
                'enabled': config.enabled,
                'cache_duration_days': config.cache_duration_days,
                'use_original_titles': config.use_original_titles,
                'language': config.language,
                'rate_limit_delay': config.rate_limit_delay
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
            
            self.logger.info(f"TMDB configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving TMDB configuration: {e}")
            return False
    
    def load_tmdb_config(self) -> Optional[TMDBConfig]:
        """
        Load TMDB configuration from file
        
        Returns:
            TMDBConfig: Loaded configuration or None if not found
        """
        try:
            if not self.config_file.exists():
                self.logger.info("No TMDB configuration file found, using defaults")
                return TMDBConfig()
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            config = TMDBConfig(
                api_key=config_data.get('api_key', ''),
                bearer_token=config_data.get('bearer_token', ''),
                enabled=config_data.get('enabled', False),
                cache_duration_days=config_data.get('cache_duration_days', 7),
                use_original_titles=config_data.get('use_original_titles', True),
                language=config_data.get('language', 'en-US'),
                rate_limit_delay=config_data.get('rate_limit_delay', 0.25)
            )
            
            self.logger.info("TMDB configuration loaded successfully")
            return config
            
        except Exception as e:
            self.logger.error(f"Error loading TMDB configuration: {e}")
            return TMDBConfig()  # Return default config on error
    
    def is_tmdb_enabled(self) -> bool:
        """
        Check if TMDB is enabled and properly configured
        
        Returns:
            bool: True if TMDB is enabled and configured
        """
        config = self.load_tmdb_config()
        return config is not None and config.is_configured()
    
    def get_tmdb_service(self) -> Optional[TMDBService]:
        """
        Get configured TMDB service instance
        
        Returns:
            TMDBService: Configured service or None if not available
        """
        config = self.load_tmdb_config()
        
        if config and config.is_configured():
            try:
                return TMDBService(
                    config.api_key, 
                    config.bearer_token,
                    cache_duration_days=config.cache_duration_days
                )
            except Exception as e:
                self.logger.error(f"Error creating TMDB service: {e}")
                return None
        
        return None
    
    def test_current_config(self) -> tuple[bool, str]:
        """
        Test the currently saved TMDB configuration
        
        Returns:
            tuple[bool, str]: (is_working, status_message)
        """
        config = self.load_tmdb_config()
        
        if not config or not config.is_configured():
            return False, "TMDB is not configured"
        
        return self.validate_api_credentials(config.api_key, config.bearer_token)
    
    def disable_tmdb(self) -> bool:
        """
        Disable TMDB integration
        
        Returns:
            bool: True if disabled successfully
        """
        try:
            config = self.load_tmdb_config()
            if config:
                config.enabled = False
                return self.save_tmdb_config(config)
            return True
            
        except Exception as e:
            self.logger.error(f"Error disabling TMDB: {e}")
            return False
    
    def enable_tmdb(self) -> tuple[bool, str]:
        """
        Enable TMDB integration if properly configured
        
        Returns:
            tuple[bool, str]: (enabled_successfully, message)
        """
        try:
            config = self.load_tmdb_config()
            
            if not config or not config.api_key or not config.bearer_token:
                return False, "TMDB credentials not configured"
            
            # Test credentials before enabling
            is_valid, message = self.validate_api_credentials(config.api_key, config.bearer_token)
            
            if is_valid:
                config.enabled = True
                if self.save_tmdb_config(config):
                    return True, "TMDB enabled successfully"
                else:
                    return False, "Failed to save configuration"
            else:
                return False, f"Cannot enable TMDB: {message}"
                
        except Exception as e:
            self.logger.error(f"Error enabling TMDB: {e}")
            return False, f"Error enabling TMDB: {str(e)}"