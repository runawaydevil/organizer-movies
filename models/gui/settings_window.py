"""
Settings window for Movie Organizer configuration
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Callable, Optional
import logging


class SettingsWindow:
    """
    Settings configuration window
    """
    
    def __init__(self, parent, current_settings: Dict[str, Any]):
        """
        Initialize settings window
        
        Args:
            parent: Parent window
            current_settings: Current configuration settings
        """
        self.parent = parent
        self.current_settings = current_settings.copy()
        self.logger = logging.getLogger(__name__)
        
        # Callbacks
        self.on_save_callback: Optional[Callable] = None
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("Settings - Movie Organizer v0.1")
        self.window.geometry("650x750")  # Increased size
        self.window.transient(parent)
        self.window.grab_set()
        
        # Make window resizable
        self.window.resizable(True, True)
        
        # Set minimum size
        self.window.minsize(600, 600)
        
        # Center window on parent
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (650 // 2)
        y = (self.window.winfo_screenheight() // 2) - (750 // 2)
        self.window.geometry(f"650x750+{x}+{y}")
        
        # Create GUI with scroll
        self._create_scrollable_widgets()
        self._load_current_settings()
        
        self.logger.info("Settings window initialized")
    
    def _create_scrollable_widgets(self):
        """Create all widgets with scrollable container"""
        # Create main container with scrollbar
        main_container = ttk.Frame(self.window)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(main_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Now create the actual content in scrollable_frame
        self._create_widgets()
    
    def _create_widgets(self):
        """Create all widgets"""
        # Main container (now inside scrollable_frame)
        main_frame = ttk.Frame(self.scrollable_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # API Key section
        api_frame = ttk.LabelFrame(main_frame, text="OpenAI API Configuration", padding="10")
        api_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(api_frame, text="API Key:").pack(anchor=tk.W)
        
        self.api_key_var = tk.StringVar()
        api_key_entry = ttk.Entry(
            api_frame,
            textvariable=self.api_key_var,
            show="*",
            width=60
        )
        api_key_entry.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Label(api_frame, text="Model:").pack(anchor=tk.W)
        
        self.model_var = tk.StringVar()
        model_combo = ttk.Combobox(
            api_frame,
            textvariable=self.model_var,
            values=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            state="readonly",
            width=20
        )
        model_combo.pack(anchor=tk.W, pady=(5, 0))
        
        # Rate limiting section
        rate_frame = ttk.LabelFrame(main_frame, text="Rate Limiting", padding="10")
        rate_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(rate_frame, text="Delay between API calls (seconds):").pack(anchor=tk.W)
        
        self.rate_delay_var = tk.DoubleVar()
        rate_delay_spin = ttk.Spinbox(
            rate_frame,
            from_=0.1,
            to=10.0,
            increment=0.1,
            textvariable=self.rate_delay_var,
            width=10
        )
        rate_delay_spin.pack(anchor=tk.W, pady=(5, 0))
        
        # Network settings section
        network_frame = ttk.LabelFrame(main_frame, text="Network Operations", padding="10")
        network_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Network retry attempts
        ttk.Label(network_frame, text="Network retry attempts:").pack(anchor=tk.W)
        
        self.network_retries_var = tk.IntVar()
        network_retries_spin = ttk.Spinbox(
            network_frame,
            from_=1,
            to=10,
            increment=1,
            textvariable=self.network_retries_var,
            width=10
        )
        network_retries_spin.pack(anchor=tk.W, pady=(5, 10))
        
        # Network retry delay
        ttk.Label(network_frame, text="Network retry delay (seconds):").pack(anchor=tk.W)
        
        self.network_delay_var = tk.DoubleVar()
        network_delay_spin = ttk.Spinbox(
            network_frame,
            from_=0.1,
            to=10.0,
            increment=0.1,
            textvariable=self.network_delay_var,
            width=10
        )
        network_delay_spin.pack(anchor=tk.W, pady=(5, 10))
        
        # Network timeout
        ttk.Label(network_frame, text="Network timeout (seconds):").pack(anchor=tk.W)
        
        self.network_timeout_var = tk.DoubleVar()
        network_timeout_spin = ttk.Spinbox(
            network_frame,
            from_=5.0,
            to=300.0,
            increment=5.0,
            textvariable=self.network_timeout_var,
            width=10
        )
        network_timeout_spin.pack(anchor=tk.W, pady=(5, 0))
        
        # File naming section
        naming_frame = ttk.LabelFrame(main_frame, text="File Naming", padding="10")
        naming_frame.pack(fill=tk.X, pady=(0, 20))
        
        # File naming pattern
        ttk.Label(naming_frame, text="File naming pattern:").pack(anchor=tk.W)
        
        self.file_pattern_var = tk.StringVar()
        file_pattern_combo = ttk.Combobox(
            naming_frame,
            textvariable=self.file_pattern_var,
            values=[
                "{title} ({year}){extension}",
                "{title} - {year}{extension}",
                "{year} - {title}{extension}",
                "{title}{extension}"
            ],
            width=40
        )
        file_pattern_combo.pack(anchor=tk.W, pady=(5, 10))
        
        # Max filename length
        ttk.Label(naming_frame, text="Maximum filename length:").pack(anchor=tk.W)
        
        self.max_filename_var = tk.IntVar()
        max_filename_spin = ttk.Spinbox(
            naming_frame,
            from_=50,
            to=255,
            increment=10,
            textvariable=self.max_filename_var,
            width=10
        )
        max_filename_spin.pack(anchor=tk.W, pady=(5, 0))
        
        # TMDB section
        tmdb_frame = ttk.LabelFrame(main_frame, text="TMDB Integration", padding="10")
        tmdb_frame.pack(fill=tk.X, pady=(0, 20))
        
        # TMDB enabled checkbox
        self.tmdb_enabled_var = tk.BooleanVar()
        tmdb_enabled_check = ttk.Checkbutton(
            tmdb_frame,
            text="Enable TMDB integration for better movie identification",
            variable=self.tmdb_enabled_var,
            command=self._toggle_tmdb_fields
        )
        tmdb_enabled_check.pack(anchor=tk.W, pady=(0, 10))
        
        # TMDB API Key
        self.tmdb_api_label = ttk.Label(tmdb_frame, text="TMDB API Key:")
        self.tmdb_api_label.pack(anchor=tk.W)
        
        self.tmdb_api_key_var = tk.StringVar()
        self.tmdb_api_entry = ttk.Entry(
            tmdb_frame,
            textvariable=self.tmdb_api_key_var,
            show="*",
            width=60
        )
        self.tmdb_api_entry.pack(fill=tk.X, pady=(5, 10))
        
        # TMDB Bearer Token
        self.tmdb_bearer_label = ttk.Label(tmdb_frame, text="TMDB Bearer Token:")
        self.tmdb_bearer_label.pack(anchor=tk.W)
        
        self.tmdb_bearer_token_var = tk.StringVar()
        self.tmdb_bearer_entry = ttk.Entry(
            tmdb_frame,
            textvariable=self.tmdb_bearer_token_var,
            show="*",
            width=60
        )
        self.tmdb_bearer_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Test connection button
        self.test_tmdb_button = ttk.Button(
            tmdb_frame,
            text="Test TMDB Connection",
            command=self._test_tmdb_connection
        )
        self.test_tmdb_button.pack(anchor=tk.W, pady=(0, 10))
        
        # Connection status label
        self.tmdb_status_var = tk.StringVar()
        self.tmdb_status_label = ttk.Label(
            tmdb_frame,
            textvariable=self.tmdb_status_var,
            foreground="gray"
        )
        self.tmdb_status_label.pack(anchor=tk.W, pady=(0, 10))
        
        # TMDB preferences
        self.tmdb_original_titles_var = tk.BooleanVar()
        tmdb_original_check = ttk.Checkbutton(
            tmdb_frame,
            text="Use original movie titles (recommended for media servers)",
            variable=self.tmdb_original_titles_var
        )
        tmdb_original_check.pack(anchor=tk.W, pady=(0, 5))
        
        # Language selection
        ttk.Label(tmdb_frame, text="TMDB Language:").pack(anchor=tk.W)
        
        self.tmdb_language_var = tk.StringVar()
        tmdb_language_combo = ttk.Combobox(
            tmdb_frame,
            textvariable=self.tmdb_language_var,
            values=["en-US", "pt-BR", "es-ES", "fr-FR", "de-DE", "it-IT", "ja-JP"],
            state="readonly",
            width=15
        )
        tmdb_language_combo.pack(anchor=tk.W, pady=(5, 0))
        
        # Error handling section
        error_frame = ttk.LabelFrame(main_frame, text="Error Handling", padding="10")
        error_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Continue on error
        self.continue_on_error_var = tk.BooleanVar()
        continue_check = ttk.Checkbutton(
            error_frame,
            text="Continue processing after individual file errors",
            variable=self.continue_on_error_var
        )
        continue_check.pack(anchor=tk.W, pady=(0, 5))
        
        # Show error details
        self.show_error_details_var = tk.BooleanVar()
        error_details_check = ttk.Checkbutton(
            error_frame,
            text="Show detailed error information",
            variable=self.show_error_details_var
        )
        error_details_check.pack(anchor=tk.W, pady=(0, 5))
        
        # Log detailed errors
        self.log_detailed_errors_var = tk.BooleanVar()
        log_errors_check = ttk.Checkbutton(
            error_frame,
            text="Log detailed error information",
            variable=self.log_detailed_errors_var
        )
        log_errors_check.pack(anchor=tk.W)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Save and Cancel buttons
        ttk.Button(
            buttons_frame,
            text="Save",
            command=self._save_settings
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(
            buttons_frame,
            text="Cancel",
            command=self._cancel
        ).pack(side=tk.RIGHT)
    
    def _load_current_settings(self):
        """Load current settings into the form"""
        # API settings
        self.api_key_var.set(self.current_settings.get("openai_api_key", ""))
        self.model_var.set(self.current_settings.get("openai_model", "gpt-3.5-turbo"))
        self.rate_delay_var.set(self.current_settings.get("rate_limit_delay", 1.0))
        
        # Network settings
        self.network_retries_var.set(self.current_settings.get("network_retry_attempts", 3))
        self.network_delay_var.set(self.current_settings.get("network_retry_delay", 1.0))
        self.network_timeout_var.set(self.current_settings.get("network_timeout", 30.0))
        
        # File naming settings
        self.file_pattern_var.set(self.current_settings.get("file_naming_pattern", "{title} ({year}){extension}"))
        self.max_filename_var.set(self.current_settings.get("max_filename_length", 200))
        
        # Error handling settings
        self.continue_on_error_var.set(self.current_settings.get("continue_on_error", True))
        self.show_error_details_var.set(self.current_settings.get("show_error_details", True))
        self.log_detailed_errors_var.set(self.current_settings.get("log_detailed_errors", True))
        
        # TMDB settings
        tmdb_config = self.current_settings.get("tmdb_config", {})
        self.tmdb_enabled_var.set(tmdb_config.get("enabled", False))
        self.tmdb_api_key_var.set(tmdb_config.get("api_key", ""))
        self.tmdb_bearer_token_var.set(tmdb_config.get("bearer_token", ""))
        self.tmdb_original_titles_var.set(tmdb_config.get("use_original_titles", True))
        self.tmdb_language_var.set(tmdb_config.get("language", "en-US"))
        
        # Update TMDB field states
        self._toggle_tmdb_fields()
    
    def _save_settings(self):
        """Save settings and close window"""
        # Validate settings
        if not self.api_key_var.get().strip():
            messagebox.showwarning("Invalid Settings", "Please enter an OpenAI API key.")
            return
        
        # Validate network settings
        if self.network_retries_var.get() < 1 or self.network_retries_var.get() > 10:
            messagebox.showwarning("Invalid Settings", "Network retry attempts must be between 1 and 10.")
            return
        
        if self.network_timeout_var.get() < 5 or self.network_timeout_var.get() > 300:
            messagebox.showwarning("Invalid Settings", "Network timeout must be between 5 and 300 seconds.")
            return
        
        if not self.file_pattern_var.get().strip():
            messagebox.showwarning("Invalid Settings", "Please enter a file naming pattern.")
            return
        
        # Validate TMDB settings if enabled
        if self.tmdb_enabled_var.get():
            if not self.tmdb_api_key_var.get().strip():
                messagebox.showwarning("Invalid Settings", "Please enter TMDB API key or disable TMDB integration.")
                return
            
            if not self.tmdb_bearer_token_var.get().strip():
                messagebox.showwarning("Invalid Settings", "Please enter TMDB bearer token or disable TMDB integration.")
                return
        
        # Collect all settings
        settings = {
            # API settings
            "openai_api_key": self.api_key_var.get().strip(),
            "openai_model": self.model_var.get(),
            "rate_limit_delay": self.rate_delay_var.get(),
            
            # Network settings
            "network_retry_attempts": self.network_retries_var.get(),
            "network_retry_delay": self.network_delay_var.get(),
            "network_timeout": self.network_timeout_var.get(),
            
            # File naming settings
            "file_naming_pattern": self.file_pattern_var.get().strip(),
            "max_filename_length": self.max_filename_var.get(),
            
            # Error handling settings
            "continue_on_error": self.continue_on_error_var.get(),
            "show_error_details": self.show_error_details_var.get(),
            "log_detailed_errors": self.log_detailed_errors_var.get(),
            
            # TMDB settings
            "tmdb_config": {
                "enabled": self.tmdb_enabled_var.get(),
                "api_key": self.tmdb_api_key_var.get().strip(),
                "bearer_token": self.tmdb_bearer_token_var.get().strip(),
                "use_original_titles": self.tmdb_original_titles_var.get(),
                "language": self.tmdb_language_var.get(),
                "cache_duration_days": 7,  # Default value
                "rate_limit_delay": 0.25   # Default value
            }
        }
        
        # Call save callback
        if self.on_save_callback:
            self.on_save_callback(settings)
        
        self.window.destroy()
    
    def _cancel(self):
        """Cancel and close window"""
        self.window.destroy()
    
    def _toggle_tmdb_fields(self):
        """Enable/disable TMDB fields based on checkbox"""
        enabled = self.tmdb_enabled_var.get()
        
        # Update field states
        state = tk.NORMAL if enabled else tk.DISABLED
        
        self.tmdb_api_entry.config(state=state)
        self.tmdb_bearer_entry.config(state=state)
        self.test_tmdb_button.config(state=state)
        
        # Update labels color
        color = "black" if enabled else "gray"
        self.tmdb_api_label.config(foreground=color)
        self.tmdb_bearer_label.config(foreground=color)
        
        # Clear status if disabled
        if not enabled:
            self.tmdb_status_var.set("")
    
    def _test_tmdb_connection(self):
        """Test TMDB API connection"""
        api_key = self.tmdb_api_key_var.get().strip()
        bearer_token = self.tmdb_bearer_token_var.get().strip()
        
        if not api_key or not bearer_token:
            self.tmdb_status_var.set("Please enter both API key and bearer token")
            self.tmdb_status_label.config(foreground="red")
            return
        
        # Show testing status
        self.tmdb_status_var.set("Testing connection...")
        self.tmdb_status_label.config(foreground="blue")
        self.window.update()
        
        try:
            # Import here to avoid circular imports
            from services.tmdb_config_manager import TMDBConfigManager
            
            config_manager = TMDBConfigManager()
            is_valid, message = config_manager.validate_api_credentials(api_key, bearer_token)
            
            if is_valid:
                self.tmdb_status_var.set("✓ Connection successful")
                self.tmdb_status_label.config(foreground="green")
            else:
                self.tmdb_status_var.set(f"✗ {message}")
                self.tmdb_status_label.config(foreground="red")
                
        except Exception as e:
            self.tmdb_status_var.set(f"✗ Error: {str(e)}")
            self.tmdb_status_label.config(foreground="red")
    
    def set_save_callback(self, callback: Callable):
        """Set callback for save operation"""
        self.on_save_callback = callback