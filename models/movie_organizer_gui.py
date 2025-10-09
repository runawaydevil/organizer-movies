#!/usr/bin/env python3
"""
Main GUI application controller for Movie Organizer
AI-Powered Movie File Organizer with TMDB Integration

Author: Pablo Murad (runawaydevil)
Version: 0.1
Repository: https://github.com/runawaydevil/organizer-movies.git
"""
import os
import sys
import logging
import threading
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from tkinter import messagebox

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
from gui.settings_window import SettingsWindow
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from version import get_version_string, APP_TITLE, VERSION, AUTHOR

from services.file_scanner import FileScanner
# FastNetworkScanner will be imported when needed
from services.ai_analyzer import AIAnalyzer
from services.folder_creator import FolderCreator
from services.file_mover import FileMover
from services.tmdb_config_manager import TMDBConfigManager
from services.movie_report_generator import MovieReportGenerator
from services.secure_config_manager import SecureConfigManager
from models.config import OrganizerConfig, ProcessResult, OrganizationReport, TMDBConfig
from models.movie_metadata import MovieMetadata


class MovieOrganizerGUI:
    """
    Main GUI application controller
    
    Author: Pablo Murad (runawaydevil)
    Version: 0.1
    """
    
    def __init__(self):
        """Initialize the GUI application"""
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing {get_version_string()}")
        
        # Initialize secure config manager
        self.secure_config = SecureConfigManager()
        
        # Application state - load from secure storage
        self.config = self.secure_config.load_config()
        self.current_files = []
        self.file_scanner = None
        self.ai_analyzer = None  # Will be either AIAnalyzer or HybridAnalyzer based on TMDB config
        self.folder_creator = None
        self.file_mover = FileMover()
        self.processing_thread = None
        self.is_processing = False
        
        # TMDB configuration manager
        self.tmdb_config_manager = TMDBConfigManager()
        
        # Movie report generator
        self.report_generator = MovieReportGenerator()
        
        # Create main window with version information
        self.main_window = MainWindow()
        self.main_window.root.title(APP_TITLE)  # Set window title with version
        self.main_window.set_scan_callback(self.scan_folder)
        self.main_window.set_process_callback(self.process_files)
        self.main_window.set_settings_callback(self.show_settings)
        self.main_window.set_metadata_edit_callback(self.on_metadata_edited)
        self.main_window.set_reanalyze_callback(self.reanalyze_file)
        self.main_window.set_manual_search_callback(self.manual_tmdb_search)
        
        # Update status with version info
        self.main_window.update_status(f"Ready - {get_version_string()}")
        
        # Load TMDB configuration
        self._load_tmdb_config()
        
        self.logger.info("Movie Organizer GUI initialized")
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('movie_organizer.log')
            ]
        )
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration with network support"""
        return {
            # API settings
            "openai_api_key": "",  # Configure your OpenAI API key here
            "openai_model": "gpt-3.5-turbo",
            "rate_limit_delay": 1.0,
            "max_retries": 3,
            
            # Network-specific settings
            "network_retry_attempts": 3,
            "network_retry_delay": 1.0,
            "network_timeout": 30.0,
            "skip_network_verification": False,
            
            # File naming settings  
            "file_naming_pattern": "{title} ({year}){extension}",
            "folder_naming_pattern": "{title} ({year})",
            "handle_duplicates": True,
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
            
            # TMDB configuration (will be loaded from TMDBConfigManager)
            "tmdb_config": {
                "enabled": False,
                "api_key": "",
                "bearer_token": "",
                "use_original_titles": True,
                "language": "en-US",
                "cache_duration_days": 7,
                "rate_limit_delay": 0.25
            },
            
            # Legacy settings for backward compatibility
            "folder_pattern": "{title} - {year}",
            "organize_in_place": True,
            "create_movie_folders": True,
            "rename_files": True,
            "dry_run": False,
            "create_backup": False,
            "skip_duplicates": True,
            "log_level": "INFO",
            "enable_file_logging": True
        }
    
    def scan_folder(self, folder_path: str):
        """Scan folder for movie files with network-aware threading"""
        self.logger.info(f"Scanning folder: {folder_path}")
        
        # Check if APIs are configured before scanning
        if not self.config.get("openai_api_key"):
            self._show_api_configuration_error()
            return
        
        self.main_window.update_status("Scanning for movie files...")
        
        # Check if this is a network path
        from pathlib import Path
        path_obj = Path(folder_path)
        
        # Simple network detection for mapped drives
        is_network = False
        try:
            path_str = str(path_obj.resolve())
            # Check for mapped network drives (X:, Y:, Z: etc, but not C:)
            if len(path_str) >= 2 and path_str[1] == ':' and path_str[0].upper() not in ['C', 'D']:
                is_network = True
            # Check for UNC paths
            elif path_str.startswith('\\\\') or path_str.startswith('//'):
                is_network = True
            
            if is_network:
                self.logger.info(f"Network path detected: {folder_path}")
                self.main_window.update_status("Scanning network location (this may take longer)...")
        except Exception as e:
            self.logger.warning(f"Could not determine if path is network: {e}")
            is_network = False
        
        # Start scanning in a separate thread to avoid blocking the GUI
        def scan_thread():
            try:
                # Use FastNetworkScanner for network paths, regular FileScanner for local
                recursive = self.main_window.recursive_scan_var.get()
                
                if is_network:
                    # Use fast network scanner to avoid GUI freezing
                    try:
                        import sys
                        import os
                        services_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'services')
                        if services_path not in sys.path:
                            sys.path.insert(0, services_path)
                        from fast_network_scanner import FastNetworkScanner
                        
                        self.file_scanner = FastNetworkScanner(
                            source_directory=folder_path,
                            video_extensions=self.config["video_extensions"],
                            recursive=recursive
                        )
                        self.logger.info("Using FastNetworkScanner for network location")
                    except ImportError as e:
                        self.logger.warning(f"Could not import FastNetworkScanner: {e}, using regular scanner")
                        self.file_scanner = FileScanner(
                            source_directory=folder_path,
                            video_extensions=self.config["video_extensions"],
                            recursive=recursive
                        )
                else:
                    # Use regular scanner for local paths
                    self.file_scanner = FileScanner(
                        source_directory=folder_path,
                        video_extensions=self.config["video_extensions"],
                        recursive=recursive
                    )
                
                # Scan for files (this might be slow on network)
                self.main_window.update_status("Scanning files...")
                video_files = self.file_scanner.scan_video_files()
                
                if not video_files:
                    self.main_window.show_info(
                        "No Files Found",
                        "No video files were found in the selected folder."
                    )
                    self.main_window.update_status("No video files found")
                    return
                
                # Prepare file data for display
                self.main_window.update_status("Processing file information...")
                files_data = []
                
                for i, file_path in enumerate(video_files):
                    # Update progress for large directories
                    if len(video_files) > 50 and i % 10 == 0:
                        progress = (i / len(video_files)) * 100
                        self.main_window.update_progress(
                            progress,
                            f"Processing file info {i+1}/{len(video_files)}..."
                        )
                    
                    try:
                        file_info = self.file_scanner.get_file_info(file_path)
                        
                        # Get relative location from source directory
                        try:
                            relative_location = file_path.parent.relative_to(Path(folder_path))
                            location_display = str(relative_location) if str(relative_location) != "." else "Root"
                        except ValueError:
                            location_display = str(file_path.parent)
                        
                        files_data.append({
                            "filename": file_path.name,
                            "path": str(file_path),
                            "location": location_display,
                            "size": self._format_file_size(file_info["size"]),
                            "analysis": "Pending...",
                            "proposed_folder": "Analyzing..."
                        })
                    except Exception as e:
                        self.logger.warning(f"Could not get info for {file_path}: {e}")
                        # Add file anyway with basic info
                        files_data.append({
                            "filename": file_path.name,
                            "path": str(file_path),
                            "location": "Unknown",
                            "size": "Unknown",
                            "analysis": "Pending...",
                            "proposed_folder": "Analyzing..."
                        })
                
                # Update UI on main thread
                self.current_files = files_data
                self.main_window.update_file_list(files_data)
                
                network_info = " (network location)" if is_network else ""
                self.main_window.update_status(f"Found {len(video_files)} video files{network_info}")
                self.main_window.update_progress(0, "")  # Clear progress
                
                # Start analysis in background
                self._start_analysis_thread()
                
            except Exception as e:
                self.logger.error(f"Error scanning folder: {e}")
                self.main_window.show_error("Scan Error", f"Error scanning folder: {str(e)}")
                self.main_window.update_status("Scan failed")
                self.main_window.update_progress(0, "")  # Clear progress
        
        # Start the scan thread
        import threading
        scan_thread_obj = threading.Thread(target=scan_thread, daemon=True)
        scan_thread_obj.start()
    
    def _start_analysis_thread(self):
        """Start background thread for AI analysis"""
        if not self.config.get("openai_api_key"):
            self.main_window.show_error(
                "No API Key",
                "Please configure your OpenAI API key in Settings before analyzing files."
            )
            return
        
        def analyze_files():
            try:
                # Initialize AI analyzer
                self.ai_analyzer = AIAnalyzer(
                    api_key=self.config["openai_api_key"],
                    model=self.config["openai_model"]
                )
                
                total_files = len(self.current_files)
                
                for i, file_data in enumerate(self.current_files):
                    if not self.is_processing:  # Allow cancellation
                        break
                    
                    filename = file_data["filename"]
                    
                    # Update progress
                    progress = (i / total_files) * 100
                    self.main_window.update_progress(
                        progress,
                        f"Analyzing {i+1}/{total_files}: {filename[:30]}..."
                    )
                    
                    # Check if movie was already organized
                    if self.report_generator.is_movie_already_organized(filename):
                        organized_info = self.report_generator.get_organized_movie_info(filename)
                        
                        # Create metadata from organized info
                        from models.movie_metadata import MovieMetadata
                        metadata = MovieMetadata(
                            title=organized_info['title'],
                            year=organized_info['year'],
                            original_filename=filename,
                            confidence_score=organized_info['confidence_score']
                        )
                        
                        # Format analysis result
                        analysis_text = f"{metadata.title}"
                        if metadata.year:
                            analysis_text += f" ({metadata.year})"
                        analysis_text += f" [{metadata.confidence_score:.1%}] ✅ Already Organized"
                        
                        # Get proposed folder name
                        proposed_folder = organized_info['folder_path']
                        
                        # Update UI
                        self.main_window.update_file_analysis(
                            filename,
                            analysis_text,
                            proposed_folder,
                            metadata.confidence_score
                        )
                        
                        # Store metadata
                        file_data["metadata"] = metadata
                        file_data["already_organized"] = True
                        
                        continue  # Skip analysis for already organized movies
                    
                    try:
                        # Show loading indicator for TMDB operations
                        if self._is_tmdb_enabled():
                            self.main_window.update_progress(
                                progress,
                                f"Analyzing with TMDB {i+1}/{total_files}: {filename[:25]}... 🎬"
                            )
                        
                        # Analyze filename using best available analyzer (AI + TMDB if configured)
                        analyzer = self._get_analyzer()
                        metadata = analyzer.analyze_filename(filename)
                        
                        # Format analysis result with source indicator
                        analysis_text = f"{metadata.title}"
                        if metadata.year:
                            analysis_text += f" ({metadata.year})"
                        
                        # Add source indicator
                        source_indicator = self._get_analysis_source_indicator()
                        analysis_text += f" [{metadata.confidence_score:.1%}] {source_indicator}"
                        
                        # Get proposed folder name
                        proposed_folder = self._get_proposed_folder_name(metadata)
                        
                        # Update UI with confidence
                        self.main_window.update_file_analysis(
                            filename,
                            analysis_text,
                            proposed_folder,
                            metadata.confidence_score
                        )
                        
                        # Store metadata
                        file_data["metadata"] = metadata
                        file_data["proposed_folder"] = proposed_folder
                        
                    except Exception as e:
                        self.logger.error(f"Error analyzing {filename}: {e}")
                        self.main_window.update_file_analysis(
                            filename,
                            f"Error: {str(e)}",
                            "Analysis failed",
                            0.0  # Zero confidence for errors
                        )
                    
                    # Rate limiting
                    import time
                    time.sleep(self.config["rate_limit_delay"])
                
                # Analysis complete
                self.main_window.update_progress(100, "Analysis complete")
                self.main_window.update_status("Analysis complete - ready to organize")
                
            except Exception as e:
                self.logger.error(f"Error in analysis thread: {e}")
                self.main_window.show_error("Analysis Error", f"Error during analysis: {str(e)}")
        
        # Start analysis thread
        self.is_processing = True
        analysis_thread = threading.Thread(target=analyze_files, daemon=True)
        analysis_thread.start()
    
    def _get_proposed_folder_name(self, metadata: MovieMetadata) -> str:
        """Get proposed folder name based on metadata and pattern"""
        # Use new pattern, fallback to legacy pattern
        pattern = self.config.get("folder_naming_pattern", self.config.get("folder_pattern", "{title} ({year})"))
        
        # Use the metadata method for consistent formatting, with fallback
        try:
            if hasattr(metadata, 'get_folder_name_with_pattern'):
                return metadata.get_folder_name_with_pattern(pattern)
            else:
                # Fallback to manual formatting
                title = metadata.sanitize_title()
                if metadata.year and "{year}" in pattern:
                    return pattern.format(title=title, year=metadata.year)
                else:
                    pattern_no_year = pattern.replace(" ({year})", "").replace("({year})", "").replace(" - {year}", "")
                    return pattern_no_year.format(title=title)
        except Exception as e:
            self.logger.warning(f"Error formatting folder name: {e}")
            # Ultimate fallback
            if metadata.year:
                return f"{metadata.sanitize_title()} ({metadata.year})"
            return metadata.sanitize_title()
    
    def process_files(self, selected_files: List[str]):
        """Process selected files with enhanced error handling and network support"""
        if not selected_files:
            return
        
        # Check if APIs are configured before processing
        if not self.config.get("openai_api_key"):
            self._show_api_configuration_error()
            return
        
        self.logger.info(f"Starting to process {len(selected_files)} files")
        
        # Confirm processing
        if not messagebox.askyesno(
            "Confirm Organization",
            f"Are you sure you want to organize {len(selected_files)} files?\n\n"
            "This will:\n"
            "• Create movie folders in the same directory as your files\n"
            "• Rename files with clean movie titles\n"
            "• Move files into their respective movie folders\n"
            "• Handle network locations with retry logic"
        ):
            return
        
        # Start processing thread
        def process_files_thread():
            # Import here to avoid circular imports
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from processing_context import ProcessingContext, ErrorHandler
            
            # Initialize processing context and error handler
            context = ProcessingContext(total_files=len(selected_files))
            error_handler = ErrorHandler(continue_on_error=True)
            
            try:
                self.is_processing = True
                self.main_window.update_status("Organizing files...")
                
                # Initialize services with enhanced configuration
                folder_pattern = self.config.get("folder_naming_pattern", "{title} ({year})")
                file_pattern = self.config.get("file_naming_pattern", "{title} ({year}){extension}")
                max_retries = self.config.get("network_retry_attempts", 3)
                base_delay = self.config.get("network_retry_delay", 1.0)
                
                # FolderCreator doesn't need base_directory since we create folders in the same location as source files
                self.folder_creator = FolderCreator(base_directory=".")
                # Create FileMover with backward compatibility
                try:
                    # Try new version with network parameters
                    self.file_mover = FileMover(
                        file_pattern=file_pattern,
                        max_retries=max_retries,
                        base_delay=base_delay
                    )
                except TypeError:
                    # Fallback to old version without network parameters
                    self.logger.warning("Using FileMover without network parameters (old version)")
                    self.file_mover = FileMover(file_pattern=file_pattern)
                
                results = []
                
                for i, filename in enumerate(selected_files):
                    # Check if processing should stop
                    if not self.is_processing:
                        context.add_warning(filename, "Processing cancelled by user")
                        self.logger.info("Processing cancelled by user")
                        break
                    
                    # Update progress with context information
                    progress = context.get_progress_percentage()
                    elapsed = context.get_elapsed_time()
                    eta = context.get_estimated_remaining_time()
                    
                    status_msg = f"Organizing {context.processed_files + 1}/{context.total_files}: {filename[:30]}..."
                    if eta and eta > 1:
                        status_msg += f" (ETA: {eta:.0f}s)"
                    
                    self.main_window.update_progress(progress, status_msg)
                    
                    try:
                        self.logger.info(f"Processing file {i+1}/{len(selected_files)}: {filename}")
                        
                        # Find file data and metadata
                        file_data = None
                        for data in self.current_files:
                            if data.get("filename") == filename:
                                file_data = data
                                break
                        
                        if not file_data or not file_data.get("metadata"):
                            context.add_failure(filename, "No metadata available", "validation")
                            results.append(f"[ERROR] {filename}: No metadata available")
                            continue
                        
                        metadata = file_data["metadata"]
                        source_path = Path(file_data["path"])
                        
                        self.logger.info(f"Source path: {source_path}")
                        self.logger.info(f"Metadata: {metadata.title} ({metadata.year})")
                        
                        # Check if this is a network operation
                        is_network = self.file_mover.is_network_path(source_path)
                        if is_network:
                            context.increment_network_operations()
                            self.logger.info(f"Network operation detected for: {filename}")
                        
                        # Create destination folder in the same directory as the source file
                        # Set the base directory to the source file's parent directory
                        self.folder_creator.base_directory = source_path.parent
                        # Create destination folder
                        destination_folder = self.folder_creator.create_movie_folder(metadata)
                        
                        # Organize file (reduced logging for speed)
                        success, message, final_path = self.file_mover.organize_movie_file_fast(
                            source_path, metadata, destination_folder
                        )
                        
                        if success:
                            context.add_success(filename, message, final_path)
                            folder_name = destination_folder.name if destination_folder else "Unknown"
                            file_name = final_path.name if final_path else filename
                            network_indicator = " [NETWORK]" if is_network else ""
                            results.append(f"[SUCCESS] {filename} → {folder_name}/{file_name}{network_indicator}")
                            
                            # Add to organized movies report
                            source_indicator = self._get_analysis_source_indicator()
                            source = "AI"
                            if "🎬" in source_indicator:
                                source = "TMDB"
                            elif "✏️" in source_indicator:
                                source = "Manual"
                            
                            self.report_generator.add_organized_movie(
                                title=metadata.title,
                                year=metadata.year,
                                original_filename=filename,
                                folder_path=str(destination_folder),
                                source=source,
                                confidence_score=metadata.confidence_score
                            )
                        else:
                            # Use error handler to categorize and handle the error
                            error = Exception(message)
                            should_continue = error_handler.handle_error(error, context, filename)
                            results.append(f"[ERROR] {filename}: {message}")
                            
                            if not should_continue:
                                self.logger.critical("Processing stopped due to critical error")
                                break
                    
                    except Exception as e:
                        # Use error handler for unexpected exceptions
                        should_continue = error_handler.handle_error(e, context, filename)
                        results.append(f"[ERROR] {filename}: {str(e)}")
                        
                        if not should_continue:
                            self.logger.critical("Processing stopped due to critical error")
                            break
                
                # Finish processing
                context.finish_processing()
                self.is_processing = False
                
                # Generate PDF report automatically
                self._generate_pdf_report_automatically()
                
                # Update final progress
                self.main_window.update_progress(100, "Processing complete")
                
                # Get comprehensive report
                report = context.get_summary_report()
                
                # Show enhanced results
                self._show_enhanced_processing_results(report, results)
                
                # Update status with detailed information
                status_parts = [
                    f"Organization complete: {report['successful_moves']} organized, {report['failed_moves']} failed"
                ]
                
                if report['network_operations'] > 0:
                    status_parts.append(f"{report['network_operations']} network operations")
                
                if report['retry_operations'] > 0:
                    status_parts.append(f"{report['retry_operations']} retries")
                
                final_status = " • ".join(status_parts)
                self.main_window.update_status(final_status)
                
            except Exception as e:
                self.logger.error(f"Critical error processing files: {e}")
                self.main_window.show_error("Processing Error", f"Critical error processing files: {str(e)}")
                self.is_processing = False
        
        processing_thread = threading.Thread(target=process_files_thread, daemon=True)
        processing_thread.start()
    
    def show_settings(self):
        """Show settings window"""
        settings_window = SettingsWindow(self.main_window.root, self.config)
        settings_window.set_save_callback(self._save_settings)
    
    def _save_settings(self, new_settings: Dict[str, Any]):
        """Save new settings with secure storage"""
        self.config.update(new_settings)
        self.logger.info("Settings updated")
        
        # Save configuration securely (API keys will be encoded)
        if self.secure_config.save_config(self.config):
            self.logger.info("Configuration saved securely to local storage")
        else:
            self.logger.error("Failed to save configuration securely")
        
        # Handle TMDB configuration changes
        if "tmdb_config" in new_settings:
            tmdb_config = TMDBConfig(**new_settings["tmdb_config"])
            
            # Save TMDB configuration (legacy system)
            if self.tmdb_config_manager.save_tmdb_config(tmdb_config):
                self.logger.info("TMDB configuration saved")
                
                # Reload analyzer to use new TMDB settings
                self.ai_analyzer = None  # Reset current analyzer
                self._load_tmdb_config()  # Reload with new config
                
                if tmdb_config.is_configured():
                    self.main_window.update_status("✅ Settings saved securely - TMDB integration enabled")
                    self.main_window.update_analyzer_status("Hybrid (AI + TMDB)", tmdb_enabled=True)
                else:
                    self.main_window.update_status("✅ Settings saved securely - Using AI-only analysis")
                    self.main_window.update_analyzer_status("AI Only", tmdb_enabled=False)
            else:
                self.logger.error("Failed to save TMDB configuration")
                self.main_window.update_status("⚠️ Settings saved but TMDB configuration failed")
        else:
            self.main_window.update_status("✅ Settings saved securely")
        
        # Update logging level if changed
        if "log_level" in new_settings:
            logging.getLogger().setLevel(getattr(logging, new_settings["log_level"]))
    
    def on_metadata_edited(self, filename: str, new_metadata, reanalyze: bool = False):
        """Handle metadata edit from GUI"""
        self.logger.info(f"Metadata manually edited for {filename}: {new_metadata.title} ({new_metadata.year}) - Reanalyze: {reanalyze}")
        
        # Update the file data
        for file_data in self.current_files:
            if file_data.get("filename") == filename:
                file_data["metadata"] = new_metadata
                file_data["proposed_folder"] = self._get_proposed_folder_name(new_metadata)
                break
        
        # Re-analyze with AI if requested
        if reanalyze:
            self._reanalyze_with_manual_context(filename, new_metadata)
    
    def reanalyze_file(self, filename: str):
        """Re-analyze a single file with AI"""
        if not self.ai_analyzer:
            self.main_window.show_error(
                "No AI Analyzer",
                "Please scan files first to initialize the AI analyzer."
            )
            return
        
        self.logger.info(f"Re-analyzing file: {filename}")
        
        # Show appropriate loading status
        if self._is_tmdb_enabled():
            self.main_window.update_status(f"Re-analyzing with TMDB: {filename}... 🎬")
            self.main_window.show_tmdb_loading(True)
        else:
            self.main_window.update_status(f"Re-analyzing: {filename}...")
        
        def reanalyze_thread():
            try:
                # Analyze filename using best available analyzer (AI + TMDB if configured)
                analyzer = self._get_analyzer()
                metadata = analyzer.analyze_filename(filename)
                
                # Format analysis result with source indicator
                analysis_text = f"{metadata.title}"
                if metadata.year:
                    analysis_text += f" ({metadata.year})"
                
                # Add source indicator
                source_indicator = self._get_analysis_source_indicator()
                analysis_text += f" [{metadata.confidence_score:.1%}] {source_indicator}"
                
                # Get proposed folder name
                proposed_folder = self._get_proposed_folder_name(metadata)
                
                # Update UI
                self.main_window.update_file_analysis(
                    filename,
                    analysis_text,
                    proposed_folder
                )
                
                # Update file data
                for file_data in self.current_files:
                    if file_data.get("filename") == filename:
                        file_data["metadata"] = metadata
                        file_data["proposed_folder"] = proposed_folder
                        break
                
                # Hide loading indicator
                if self._is_tmdb_enabled():
                    self.main_window.show_tmdb_loading(False)
                
                self.main_window.update_status(f"Re-analysis complete for {filename}")
                
            except Exception as e:
                self.logger.error(f"Error re-analyzing {filename}: {e}")
                self.main_window.show_error("Re-analysis Error", f"Error re-analyzing file: {str(e)}")
                self.main_window.update_status("Re-analysis failed")
        
        # Start re-analysis thread
        import threading
        reanalysis_thread = threading.Thread(target=reanalyze_thread, daemon=True)
        reanalysis_thread.start()
    
    def _reanalyze_with_manual_context(self, filename: str, manual_metadata):
        """Re-analyze file with manual context to get better AI results"""
        if not self.ai_analyzer:
            return
        
        def reanalyze_with_context():
            try:
                # Create enhanced prompt with manual context
                enhanced_prompt = f"""
Analise o seguinte nome de arquivo de filme, considerando que o usuário indicou informações:

Filename: {filename}
Título sugerido pelo usuário: {manual_metadata.title}
Ano sugerido pelo usuário: {manual_metadata.year or "não informado"}

IMPORTANTE: Sempre retorne o título ORIGINAL do filme (em inglês ou idioma original), não traduções.
Se o usuário forneceu um título em português/outro idioma, encontre o título original correspondente.

Com base nessas informações, confirme ou refine os dados e retorne um JSON com:
- title: título ORIGINAL do filme (em inglês ou idioma original)
- year: ano do filme (confirme se está correto)
- confidence: nível de confiança (0.0 a 1.0)

Exemplos:
- Se usuário disse "Cidade de Deus" → retorne "City of God"
- Se usuário disse "O Poderoso Chefão" → retorne "The Godfather"
- Se usuário disse "Duro de Matar" → retorne "Die Hard"

Resposta JSON:"""
                
                # Make API call with enhanced context
                response = self.ai_analyzer.client.chat.completions.create(
                    model=self.config["openai_model"],
                    messages=[
                        {"role": "system", "content": "You are a movie filename analyzer. Return only valid JSON."},
                        {"role": "user", "content": enhanced_prompt}
                    ],
                    max_tokens=150,
                    temperature=0.1
                )
                
                if response.choices and response.choices[0].message.content:
                    # Parse the enhanced response
                    api_response = {"content": response.choices[0].message.content.strip()}
                    enhanced_metadata = self.ai_analyzer._parse_ai_response(api_response, filename)
                    
                    # Merge with manual data (prioritize manual input)
                    final_metadata = MovieMetadata(
                        title=manual_metadata.title,  # Keep manual title
                        year=enhanced_metadata.year if enhanced_metadata.year else manual_metadata.year,
                        original_filename=filename,
                        confidence_score=min(enhanced_metadata.confidence_score + 0.2, 1.0)  # Boost confidence
                    )
                    
                    # Update UI with enhanced results
                    analysis_text = f"{final_metadata.title}"
                    if final_metadata.year:
                        analysis_text += f" ({final_metadata.year})"
                    
                    # Add enhanced indicator
                    source_indicator = self._get_analysis_source_indicator()
                    analysis_text += f" [Enhanced: {final_metadata.confidence_score:.1%}] {source_indicator}"
                    
                    proposed_folder = self._get_proposed_folder_name(final_metadata)
                    
                    self.main_window.update_file_analysis(
                        filename,
                        analysis_text,
                        proposed_folder,
                        final_metadata.confidence_score
                    )
                    
                    # Update file data
                    for file_data in self.current_files:
                        if file_data.get("filename") == filename:
                            file_data["metadata"] = final_metadata
                            file_data["proposed_folder"] = proposed_folder
                            break
                    
                    self.main_window.update_status(f"Enhanced analysis complete for {filename}")
                    
            except Exception as e:
                self.logger.error(f"Error in enhanced re-analysis for {filename}: {e}")
                self.main_window.update_status(f"Enhanced analysis failed for {filename}")
        
        # Start enhanced analysis thread
        import threading
        enhanced_thread = threading.Thread(target=reanalyze_with_context, daemon=True)
        enhanced_thread.start()
    
    def _show_processing_results(self, successful: int, failed: int, results: list):
        """Show processing results in a dialog"""
        import tkinter as tk
        from tkinter import ttk
        
        # Create results window
        results_window = tk.Toplevel(self.main_window.root)
        results_window.title("Processing Results")
        results_window.geometry("600x500")
        results_window.transient(self.main_window.root)
        
        # Main frame
        main_frame = ttk.Frame(results_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Summary
        summary_text = f"Processing Complete!\n\n✅ Successfully moved: {successful} files\n❌ Failed: {failed} files"
        summary_label = ttk.Label(main_frame, text=summary_text, font=("Arial", 12))
        summary_label.pack(pady=(0, 20))
        
        # Results list
        ttk.Label(main_frame, text="Detailed Results:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 20))
        
        results_text = tk.Text(text_frame, wrap=tk.WORD, height=15)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=results_text.yview)
        results_text.configure(yscrollcommand=scrollbar.set)
        
        # Add results
        for result in results:
            results_text.insert(tk.END, result + "\n")
        
        results_text.config(state=tk.DISABLED)  # Make read-only
        
        results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=results_window.destroy).pack()
        
        # Center window
        results_window.update_idletasks()
        x = (results_window.winfo_screenwidth() - results_window.winfo_reqwidth()) // 2
        y = (results_window.winfo_screenheight() - results_window.winfo_reqheight()) // 2
        results_window.geometry(f"+{x}+{y}")
    
    def _show_enhanced_processing_results(self, report: dict, results: list):
        """Show enhanced processing results with network and error information"""
        import tkinter as tk
        from tkinter import ttk
        
        # Create results window
        results_window = tk.Toplevel(self.main_window.root)
        results_window.title("Processing Results - Enhanced")
        results_window.geometry("700x600")
        results_window.transient(self.main_window.root)
        
        # Main frame with notebook for tabs
        main_frame = ttk.Frame(results_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Summary tab
        summary_frame = ttk.Frame(notebook, padding="20")
        notebook.add(summary_frame, text="Summary")
        
        # Summary statistics
        summary_text = f"""Processing Complete!

File Statistics:
[SUCCESS] Successfully organized: {report['successful_moves']} files
[ERROR] Failed: {report['failed_moves']} files
Success rate: {report['success_rate']:.1f}%

Performance:
Total time: {report['elapsed_time']:.1f} seconds
Network operations: {report['network_operations']}
Retry operations: {report['retry_operations']}

Issues:
Errors: {report['error_count']}
Warnings: {report['warning_count']}"""
        
        summary_label = ttk.Label(summary_frame, text=summary_text, font=("Consolas", 10), justify=tk.LEFT)
        summary_label.pack(anchor=tk.W)
        
        # Results tab
        results_frame = ttk.Frame(notebook, padding="20")
        notebook.add(results_frame, text="Detailed Results")
        
        # Results list
        ttk.Label(results_frame, text="File Operations:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # Text widget with scrollbar for results
        results_text_frame = ttk.Frame(results_frame)
        results_text_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        results_text = tk.Text(results_text_frame, wrap=tk.WORD, font=("Consolas", 9))
        results_scrollbar = ttk.Scrollbar(results_text_frame, orient=tk.VERTICAL, command=results_text.yview)
        results_text.configure(yscrollcommand=results_scrollbar.set)
        
        # Add results
        for result in results:
            results_text.insert(tk.END, result + "\n")
        
        results_text.config(state=tk.DISABLED)  # Make read-only
        
        results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Errors tab (if there are errors)
        if report['error_count'] > 0:
            errors_frame = ttk.Frame(notebook, padding="20")
            notebook.add(errors_frame, text=f"Errors ({report['error_count']})")
            
            ttk.Label(errors_frame, text="Error Details:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
            
            # Text widget for errors
            errors_text_frame = ttk.Frame(errors_frame)
            errors_text_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
            
            errors_text = tk.Text(errors_text_frame, wrap=tk.WORD, font=("Consolas", 9))
            errors_scrollbar = ttk.Scrollbar(errors_text_frame, orient=tk.VERTICAL, command=errors_text.yview)
            errors_text.configure(yscrollcommand=errors_scrollbar.set)
            
            # Add errors
            for error in report['errors']:
                errors_text.insert(tk.END, error + "\n")
            
            errors_text.config(state=tk.DISABLED)
            
            errors_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            errors_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Warnings tab (if there are warnings)
        if report['warning_count'] > 0:
            warnings_frame = ttk.Frame(notebook, padding="20")
            notebook.add(warnings_frame, text=f"Warnings ({report['warning_count']})")
            
            ttk.Label(warnings_frame, text="Warning Details:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
            
            # Text widget for warnings
            warnings_text_frame = ttk.Frame(warnings_frame)
            warnings_text_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
            
            warnings_text = tk.Text(warnings_text_frame, wrap=tk.WORD, font=("Consolas", 9))
            warnings_scrollbar = ttk.Scrollbar(warnings_text_frame, orient=tk.VERTICAL, command=warnings_text.yview)
            warnings_text.configure(yscrollcommand=warnings_scrollbar.set)
            
            # Add warnings
            for warning in report['warnings']:
                warnings_text.insert(tk.END, warning + "\n")
            
            warnings_text.config(state=tk.DISABLED)
            
            warnings_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            warnings_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=results_window.destroy).pack()
        
        # Center window
        results_window.update_idletasks()
        x = (results_window.winfo_screenwidth() - results_window.winfo_reqwidth()) // 2
        y = (results_window.winfo_screenheight() - results_window.winfo_reqheight()) // 2
        results_window.geometry(f"+{x}+{y}")
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def _load_tmdb_config(self):
        """Load TMDB configuration and initialize analyzer"""
        tmdb_config = self.tmdb_config_manager.load_tmdb_config()
        
        # Always try to use hybrid analyzer if TMDB is configured
        if tmdb_config and tmdb_config.is_configured():
            try:
                # Import here to avoid circular imports
                from services.hybrid_analyzer import HybridAnalyzer
                
                self.ai_analyzer = HybridAnalyzer(
                    openai_api_key=self.config["openai_api_key"],
                    tmdb_api_key=tmdb_config.api_key,
                    tmdb_bearer_token=tmdb_config.bearer_token,
                    openai_model=self.config.get("openai_model", "gpt-3.5-turbo")
                )
                
                self.logger.info("Hybrid analyzer (AI + TMDB) initialized - will use best results from both sources")
                
                # Update GUI status
                self.main_window.update_analyzer_status("Hybrid (AI + TMDB)", tmdb_enabled=True)
                
            except Exception as e:
                self.logger.error(f"Failed to initialize hybrid analyzer, falling back to AI-only: {e}")
                self._initialize_ai_only_analyzer()
        else:
            self.logger.info("TMDB not configured, using AI-only analysis")
            self._initialize_ai_only_analyzer()
            
            # Update GUI status
            self.main_window.update_analyzer_status("AI Only", tmdb_enabled=False)
    
    def _initialize_ai_only_analyzer(self):
        """Initialize AI-only analyzer as fallback"""
        try:
            # Check if OpenAI API key is configured
            if not self.config.get("openai_api_key"):
                self.logger.error("OpenAI API key not configured")
                self.main_window.update_status("❌ OpenAI API key required - Please configure in Settings")
                return False
            
            from services.ai_analyzer import AIAnalyzer
            
            self.ai_analyzer = AIAnalyzer(
                api_key=self.config["openai_api_key"],
                model=self.config.get("openai_model", "gpt-3.5-turbo")
            )
            
            # Update GUI status
            self.main_window.update_analyzer_status("AI Only", tmdb_enabled=False)
            self.main_window.update_status("✅ AI analyzer ready - TMDB optional for better accuracy")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI analyzer: {e}")
            self.main_window.update_status(f"❌ AI analyzer failed: {str(e)}")
            return False
    
    def _get_analyzer(self):
        """Get the current analyzer (always returns the best available analyzer)"""
        if not self.ai_analyzer:
            # Check if OpenAI API key is configured
            if not self.config.get("openai_api_key"):
                self._show_api_configuration_error()
                return None
            
            self._load_tmdb_config()
        
        return self.ai_analyzer
    
    def _show_api_configuration_error(self):
        """Show helpful error message when APIs are not configured"""
        error_message = f"""
🚨 API Configuration Required

{get_version_string()} requires API keys to function.

REQUIRED:
✅ OpenAI API Key - For AI movie identification

OPTIONAL (Recommended):
🎬 TMDB API Key & Bearer Token - For enhanced accuracy

HOW TO GET API KEYS:

1. OpenAI API Key (Required):
   • Visit: https://platform.openai.com/api-keys
   • Create account and generate API key
   • Add billing credits ($5-10 recommended)

2. TMDB API Keys (Optional):
   • Visit: https://www.themoviedb.org/settings/api
   • Create free account and request API access
   • Get both API Key and Bearer Token

SETUP:
• Go to File → Settings (or Ctrl+,)
• Enter your API keys
• Keys are encrypted and stored securely

Need help? Check API_SETUP.md for detailed instructions.
        """.strip()
        
        messagebox.showerror("API Configuration Required", error_message)
        
        # Offer to open settings
        if messagebox.askyesno("Open Settings?", "Would you like to open Settings to configure your API keys now?"):
            self.show_settings()
    
    def manual_tmdb_search(self, filename: str):
        """
        Open manual TMDB search dialog for a specific file
        
        Args:
            filename: Name of file to search for
        """
        try:
            # Check if TMDB is available
            if not self._is_tmdb_enabled():
                messagebox.showwarning(
                    "TMDB Not Available", 
                    "TMDB integration is not configured. Please configure TMDB in Settings to use manual search."
                )
                return
            
            # Get TMDB service
            tmdb_service = None
            if hasattr(self.ai_analyzer, 'tmdb_service'):
                tmdb_service = self.ai_analyzer.tmdb_service
            
            if not tmdb_service:
                messagebox.showerror("TMDB Error", "TMDB service is not available.")
                return
            
            # Import and show manual search dialog
            from models.gui.manual_search_dialog import ManualSearchDialog
            
            dialog = ManualSearchDialog(self.main_window.root, filename, tmdb_service)
            tmdb_result, manual_title, manual_year = dialog.show_dialog()
            
            if tmdb_result:
                # User selected a TMDB result
                self._apply_tmdb_result(filename, tmdb_result)
                self.logger.info(f"Applied TMDB result for {filename}: {tmdb_result.title} ({tmdb_result.year})")
                
            elif manual_title:
                # User entered manual data
                self._apply_manual_data(filename, manual_title, manual_year)
                self.logger.info(f"Applied manual data for {filename}: {manual_title} ({manual_year})")
                
            else:
                # User cancelled
                self.logger.info(f"Manual search cancelled for {filename}")
                
        except Exception as e:
            self.logger.error(f"Error in manual TMDB search for {filename}: {e}")
            messagebox.showerror("Search Error", f"Failed to perform manual search: {str(e)}")
    
    def _apply_tmdb_result(self, filename: str, tmdb_result):
        """Apply TMDB result to file metadata"""
        from models.movie_metadata import MovieMetadata
        
        # Create metadata from TMDB result
        metadata = MovieMetadata(
            title=tmdb_result.get_display_title(),
            year=tmdb_result.year,
            original_filename=filename,
            confidence_score=0.95  # High confidence for manual selection
        )
        
        # Update file data
        for file_data in self.current_files:
            if file_data.get("filename") == filename:
                file_data["metadata"] = metadata
                break
        
        # Update UI
        self._update_file_in_ui(filename, metadata, "🎬 TMDB")
        self.main_window.update_status(f"Applied TMDB result for {filename}")
    
    def _apply_manual_data(self, filename: str, title: str, year: int = None):
        """Apply manual data to file metadata"""
        from models.movie_metadata import MovieMetadata
        
        # Create metadata from manual input
        metadata = MovieMetadata(
            title=title,
            year=year,
            original_filename=filename,
            confidence_score=0.9  # High confidence for manual input
        )
        
        # Update file data
        for file_data in self.current_files:
            if file_data.get("filename") == filename:
                file_data["metadata"] = metadata
                break
        
        # Update UI
        self._update_file_in_ui(filename, metadata, "✏️ Manual")
        self.main_window.update_status(f"Applied manual data for {filename}")
    
    def _update_file_in_ui(self, filename: str, metadata, source_indicator: str):
        """Update file display in UI"""
        # Format analysis text
        analysis_text = f"{metadata.title}"
        if metadata.year:
            analysis_text += f" ({metadata.year})"
        analysis_text += f" [{metadata.confidence_score:.1%}] {source_indicator}"
        
        # Get proposed folder name
        proposed_folder = self._get_proposed_folder_name(metadata)
        
        # Update tree item
        for item in self.main_window.file_tree.get_children():
            if self.main_window.file_tree.set(item, "filename") == filename:
                self.main_window.file_tree.set(item, "analysis", analysis_text)
                self.main_window.file_tree.set(item, "proposed_folder", proposed_folder)
                
                # Update confidence tag
                confidence_tag = self._get_confidence_tag(metadata.confidence_score)
                self.main_window.file_tree.set(item, tags=(confidence_tag,))
                break
    
    def _get_analysis_source_indicator(self) -> str:
        """
        Get indicator showing the source of analysis
        
        Returns:
            str: Source indicator (🤖 for AI-only, 🎬 for Hybrid)
        """
        if not self.ai_analyzer:
            return "🤖"  # Default to AI-only if not initialized
            
        if hasattr(self.ai_analyzer, 'tmdb_service'):
            # This is a HybridAnalyzer
            return "🎬"
        else:
            # This is AI-only
            return "🤖"
    
    def _is_tmdb_enabled(self) -> bool:
        """
        Check if TMDB is currently enabled
        
        Returns:
            bool: True if TMDB is enabled
        """
        return hasattr(self.ai_analyzer, 'tmdb_service')
    
    def _generate_pdf_report_automatically(self):
        """Generate PDF report automatically after processing"""
        try:
            self.main_window.update_status("Generating PDF report...")
            
            # Generate PDF report
            success = self.report_generator.generate_pdf_report()
            
            if success:
                self.logger.info("PDF report generated automatically")
                self.main_window.update_status("PDF report generated successfully")
                
                # Show statistics in status
                stats = self.report_generator.get_statistics_summary()
                self.logger.info(f"Report statistics:\n{stats}")
                
            else:
                self.logger.warning("Failed to generate PDF report")
                self.main_window.update_status("Failed to generate PDF report")
                
        except Exception as e:
            self.logger.error(f"Error generating automatic PDF report: {e}")
            self.main_window.update_status("Error generating PDF report")
    
    def run(self):
        """Start the GUI application with proper shutdown handling"""
        try:
            self.main_window.run()
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise
        finally:
            # Ensure all processing is stopped
            self.is_processing = False
            
            # Stop any background threads
            self._stop_all_threads()
            
            # Clean up resources
            self._cleanup_application_resources()
            
            self.logger.info("Application shutting down")
    
    def _stop_all_threads(self):
        """Stop all background threads"""
        try:
            self.logger.info("Stopping all background threads")
            self.is_processing = False
            
            # Wait a moment for threads to finish gracefully
            import time
            time.sleep(0.5)
            
        except Exception as e:
            self.logger.error(f"Error stopping threads: {e}")
    
    def _cleanup_application_resources(self):
        """Clean up application resources"""
        try:
            # Clear file scanner
            if self.file_scanner:
                self.file_scanner = None
            
            # Clear AI analyzer
            if self.ai_analyzer:
                self.ai_analyzer = None
            
            # Clear folder creator
            if self.folder_creator:
                self.folder_creator = None
            
            # Clear file mover
            if self.file_mover:
                self.file_mover = None
            
            # Clear current files
            self.current_files = []
            
            self.logger.info("Application resources cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up application resources: {e}")


def main():
    """Main entry point"""
    try:
        app = MovieOrganizerGUI()
        app.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())