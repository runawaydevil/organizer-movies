"""
Configuration Manager - Handles persistent storage of API keys and settings
"""
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
import base64


class ConfigManager:
    """
    Manages persistent configuration including API keys
    Stores sensitive data encrypted locally
    """
    
    def __init__(self, config_file: str = "user_config.json"):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to configuration file (will be in .gitignore)
        """
        self.logger = logging.getLogger(__name__)
        self.config_file = Path(config_file)
        self.key_file = Path(".config_key")
        
        # Initialize encryption
        self._init_encryption()
        
        # Default configuration
        self.default_config = {
            "version": "0.01",
            "author": "Pablo Murad (runawaydevil)",
            "openai_api_key": "",
            "openai_model": "gpt-3.5-turbo",
            "tmdb_api_key": "",
            "tmdb_bearer_token": "",
            "tmdb_enabled": False,
            "tmdb_use_original_titles": True,
            "tmdb_language": "en-US",
            "rate_limit_delay": 1.0,
            "max_retries": 3,
            "network_retry_attempts": 3,
            "network_retry_delay": 1.0,
            "network_timeout": 30.0,
            "file_naming_pattern": "{title} ({year}){extension}",
            "folder_naming_pattern": "{title} ({year})",
            "max_filename_length": 200,
            "continue_on_error": True,
            "log_detailed_errors": True,
            "show_error_details": True,
            "video_extensions": [
                ".mkv", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm",
                ".m4v", ".3gp", ".ogv", ".ts", ".m2ts", ".mts"
            ]
        }
    
    def _init_encryption(self):
        """Initialize encryption for sensitive data"""
        try:
            if self.key_file.exists():
                # Load existing key
                with open(self.key_file, 'rb') as f:
                    key = f.read()
            else:
                # Generate new key
                key = Fernet.generate_key()
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                
                # Make key file hidden on Windows
                if os.name == 'nt':
                    try:
                        import ctypes
                        ctypes.windll.kernel32.SetFileAttributesW(str(self.key_file), 2)
                    except:
                        pass
            
            self.cipher = Fernet(key)
            self.logger.debug("Encryption initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize encryption: {e}")
            # Fallback to no encryption
            self.cipher = None
    
    def _encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data like API keys"""
        if not self.cipher or not data:
            return data
        
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            self.logger.warning(f"Failed to encrypt data: {e}")
            return data
    
    def _decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not self.cipher or not encrypted_data:
            return encrypted_data
        
        try:
            decoded = base64.b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            self.logger.warning(f"Failed to decrypt data: {e}")
            return encrypted_data
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file
        
        Returns:
            Dict: Configuration dictionary
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Decrypt sensitive fields
                sensitive_fields = ['openai_api_key', 'tmdb_api_key', 'tmdb_bearer_token']
                for field in sensitive_fields:
                    if field in config and config[field]:
                        config[field] = self._decrypt_sensitive_data(config[field])
                
                # Merge with defaults for any missing keys
                merged_config = self.default_config.copy()
                merged_config.update(config)
                
                self.logger.info("Configuration loaded successfully")
                return merged_config
            else:
                self.logger.info("No configuration file found, using defaults")
                return self.default_config.copy()
                
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save configuration to file
        
        Args:
            config: Configuration dictionary to save
            
        Returns:
            bool: True if successful
        """
        try:
            # Create a copy for encryption
            config_to_save = config.copy()
            
            # Encrypt sensitive fields
            sensitive_fields = ['openai_api_key', 'tmdb_api_key', 'tmdb_bearer_token']
            for field in sensitive_fields:
                if field in config_to_save and config_to_save[field]:
                    config_to_save[field] = self._encrypt_sensitive_data(config_to_save[field])
            
            # Save to file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Configuration saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False
    
    def get_openai_config(self) -> Dict[str, str]:
        """Get OpenAI configuration"""
        config = self.load_config()
        return {
            'api_key': config.get('openai_api_key', ''),
            'model': config.get('openai_model', 'gpt-3.5-turbo')
        }
    
    def get_tmdb_config(self) -> Dict[str, Any]:
        """Get TMDB configuration"""
        config = self.load_config()
        return {
            'api_key': config.get('tmdb_api_key', ''),
            'bearer_token': config.get('tmdb_bearer_token', ''),
            'enabled': config.get('tmdb_enabled', False),
            'use_original_titles': config.get('tmdb_use_original_titles', True),
            'language': config.get('tmdb_language', 'en-US')
        }
    
    def save_openai_config(self, api_key: str, model: str = "gpt-3.5-turbo") -> bool:
        """Save OpenAI configuration"""
        config = self.load_config()
        config['openai_api_key'] = api_key
        config['openai_model'] = model
        return self.save_config(config)
    
    def save_tmdb_config(self, api_key: str, bearer_token: str, enabled: bool = True) -> bool:
        """Save TMDB configuration"""
        config = self.load_config()
        config['tmdb_api_key'] = api_key
        config['tmdb_bearer_token'] = bearer_token
        config['tmdb_enabled'] = enabled
        return self.save_config(config)
    
    def is_configured(self) -> Dict[str, bool]:
        """Check what services are configured"""
        config = self.load_config()
        
        return {
            'openai': bool(config.get('openai_api_key', '')),
            'tmdb': bool(config.get('tmdb_api_key', '') and config.get('tmdb_bearer_token', '')),
            'tmdb_enabled': config.get('tmdb_enabled', False)
        }
    
    def get_app_info(self) -> Dict[str, str]:
        """Get application information"""
        return {
            'name': 'Movie Organizer',
            'version': '0.01',
            'author': 'Pablo Murad (runawaydevil)',
            'description': 'AI-Powered Movie File Organizer with TMDB Integration'
        }
    
    def clear_sensitive_data(self) -> bool:
        """Clear all sensitive data (API keys)"""
        try:
            config = self.load_config()
            config['openai_api_key'] = ''
            config['tmdb_api_key'] = ''
            config['tmdb_bearer_token'] = ''
            config['tmdb_enabled'] = False
            
            return self.save_config(config)
            
        except Exception as e:
            self.logger.error(f"Error clearing sensitive data: {e}")
            return False