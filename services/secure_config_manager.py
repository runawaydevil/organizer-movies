#!/usr/bin/env python3
"""
Secure Configuration Manager - Movie Organizer v0.1
Handles secure storage and retrieval of API keys and user configuration

Author: Pablo Murad (runawaydevil)
Repository: https://github.com/runawaydevil/organizer-movies.git
"""
import json
import logging
import os
import secrets
from pathlib import Path
from typing import Dict, Any, Optional
import base64

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

class SecureConfigManager:
    """
    Manages secure storage of API keys and configuration
    Uses AES encryption when available, falls back to base64 encoding
    Keys are stored locally and never go to GitHub
    """
    
    def __init__(self):
        """Initialize secure configuration manager"""
        self.logger = logging.getLogger(__name__)
        
        # Create config directory in user's system
        if os.name == 'nt':  # Windows
            base_dir = Path.home() / "AppData" / "Local" / "MovieOrganizer"
        else:  # Linux/Mac
            base_dir = Path.home() / ".config" / "movie-organizer"
        
        self.config_dir = base_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Set proper permissions (readable only by user)
        try:
            os.chmod(self.config_dir, 0o700)
        except Exception as e:
            self.logger.warning(f"Could not set directory permissions: {e}")
        
        # Configuration files
        self.config_file = self.config_dir / "config.json"
        self.key_file = self.config_dir / ".key"
        
        # Initialize encryption
        self.use_encryption = CRYPTO_AVAILABLE
        if not self.use_encryption:
            self.logger.warning("Cryptography library not available, using base64 encoding")
        
        self.logger.info(f"Secure config manager initialized: {self.config_dir}")
        self.logger.info(f"Encryption enabled: {self.use_encryption}")
    
    def _get_encryption_key(self) -> bytes:
        """Get or create encryption key"""
        if not self.use_encryption:
            return b"fallback_key"
        
        try:
            if self.key_file.exists():
                # Load existing key
                with open(self.key_file, 'rb') as f:
                    salt = f.read(16)
                    if len(salt) != 16:
                        raise ValueError("Invalid salt length")
            else:
                # Generate new salt
                salt = secrets.token_bytes(16)
                with open(self.key_file, 'wb') as f:
                    f.write(salt)
                # Set file permissions (readable only by user)
                try:
                    os.chmod(self.key_file, 0o600)
                except Exception as e:
                    self.logger.warning(f"Could not set key file permissions: {e}")
            
            # Derive key from machine-specific information + salt
            machine_info = f"{os.name}-{Path.home()}-MovieOrganizer".encode()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(machine_info))
            return key
            
        except Exception as e:
            self.logger.error(f"Error with encryption key: {e}")
            # Fallback to a deterministic key
            return base64.urlsafe_b64encode(b"fallback_key_movie_organizer_v01"[:32].ljust(32, b'0'))
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not data:
            return ""
        
        if not self.use_encryption:
            # Fallback to base64 encoding
            return base64.b64encode(data.encode()).decode()
        
        try:
            key = self._get_encryption_key()
            fernet = Fernet(key)
            encrypted = fernet.encrypt(data.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            # Fallback to base64
            return base64.b64encode(data.encode()).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not encrypted_data:
            return ""
        
        try:
            if not self.use_encryption:
                # Fallback base64 decoding
                return base64.b64decode(encrypted_data.encode()).decode()
            
            key = self._get_encryption_key()
            fernet = Fernet(key)
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            # Try fallback base64 decoding
            try:
                return base64.b64decode(encrypted_data.encode()).decode()
            except Exception:
                self.logger.error(f"Decryption failed: {e}")
                return ""
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save configuration with API keys encoded
        
        Args:
            config: Configuration dictionary
            
        Returns:
            bool: True if saved successfully
        """
        try:
            # Create a copy to avoid modifying original
            safe_config = config.copy()
            
            # Encode sensitive data
            if "openai_api_key" in safe_config and safe_config["openai_api_key"]:
                safe_config["openai_api_key"] = self._encode_key(safe_config["openai_api_key"])
            
            if "tmdb_config" in safe_config and isinstance(safe_config["tmdb_config"], dict):
                tmdb_config = safe_config["tmdb_config"].copy()
                if "api_key" in tmdb_config and tmdb_config["api_key"]:
                    tmdb_config["api_key"] = self._encode_key(tmdb_config["api_key"])
                if "bearer_token" in tmdb_config and tmdb_config["bearer_token"]:
                    tmdb_config["bearer_token"] = self._encode_key(tmdb_config["bearer_token"])
                safe_config["tmdb_config"] = tmdb_config
            
            # Add metadata
            safe_config["_metadata"] = {
                "version": "0.1",
                "author": "Pablo Murad (runawaydevil)",
                "encoded": True
            }
            
            # Save to file
            with open(self.config_file, 'w') as f:
                json.dump(safe_config, f, indent=2)
            
            self.logger.info("Configuration saved securely")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            return False
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration with API keys decoded
        
        Returns:
            Dict: Configuration with decoded API keys
        """
        try:
            if not self.config_file.exists():
                return self._get_default_config()
            
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Check if config is encoded
            if config.get("_metadata", {}).get("encoded", False):
                # Decode sensitive data
                if "openai_api_key" in config:
                    config["openai_api_key"] = self._decode_key(config["openai_api_key"])
                
                if "tmdb_config" in config and isinstance(config["tmdb_config"], dict):
                    tmdb_config = config["tmdb_config"]
                    if "api_key" in tmdb_config:
                        tmdb_config["api_key"] = self._decode_key(tmdb_config["api_key"])
                    if "bearer_token" in tmdb_config:
                        tmdb_config["bearer_token"] = self._decode_key(tmdb_config["bearer_token"])
            
            # Remove metadata before returning
            config.pop("_metadata", None)
            
            # Merge with defaults to ensure all keys exist
            default_config = self._get_default_config()
            default_config.update(config)
            
            self.logger.info("Configuration loaded successfully")
            return default_config
            
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            # API settings
            "openai_api_key": "",
            "openai_model": "gpt-3.5-turbo",
            "rate_limit_delay": 1.0,
            "max_retries": 3,
            
            # Network settings
            "network_retry_attempts": 3,
            "network_retry_delay": 1.0,
            "network_timeout": 30.0,
            
            # File naming settings  
            "file_naming_pattern": "{title} ({year}){extension}",
            "folder_naming_pattern": "{title} ({year})",
            "max_filename_length": 200,
            
            # Error handling
            "continue_on_error": True,
            "log_detailed_errors": True,
            "show_error_details": True,
            
            # Video file extensions
            "video_extensions": [
                ".mkv", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm",
                ".m4v", ".3gp", ".ogv", ".ts", ".m2ts", ".mts"
            ],
            
            # TMDB configuration
            "tmdb_config": {
                "enabled": False,
                "api_key": "",
                "bearer_token": "",
                "use_original_titles": True,
                "language": "en-US",
                "cache_duration_days": 7,
                "rate_limit_delay": 0.25
            }
        }
    
    def clear_config(self) -> bool:
        """Clear all configuration"""
        try:
            if self.config_file.exists():
                self.config_file.unlink()
            self.logger.info("Configuration cleared")
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear config: {e}")
            return False
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get information about configuration status"""
        return {
            "config_directory": str(self.config_dir),
            "config_file_exists": self.config_file.exists(),
            "openai_configured": bool(self.load_config().get("openai_api_key")),
            "tmdb_configured": bool(self.load_config().get("tmdb_config", {}).get("api_key")),
            "version": "0.1",
            "author": "Pablo Murad (runawaydevil)"
        }