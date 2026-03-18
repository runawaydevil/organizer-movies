#!/usr/bin/env python3
"""
CLI Organizer - Command line interface for movie organization
AI-Powered Movie File Organizer with TMDB Integration

Author: Pablo Murad (runawaydevil)
Version: 0.1
Repository: https://github.com/runawaydevil/organizer-movies.git
"""
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

from core.version import get_version_string, get_startup_banner, VERSION, AUTHOR
from services.file_scanner import FileScanner
from services.fast_network_scanner import FastNetworkScanner
from services.llm.factory import create_llm_analyzer
from services.hybrid_analyzer import HybridAnalyzer
from services.folder_creator import FolderCreator
from services.file_mover import FileMover
from services.movie_report_generator import MovieReportGenerator


class CLIOrganizer:
    """
    Command line organizer for movies
    
    Author: Pablo Murad (runawaydevil)
    Version: 0.1
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize CLI organizer
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Display version information
        print(get_startup_banner().strip())
        print("=" * 60)
        
        # Initialize services
        self._init_services()
    
    def _init_services(self):
        """Initialize all required services"""
        provider = self.config.get("llm_provider") or "openai"
        if provider == "openai" and not self.config.get("openai_api_key"):
            print("ERROR: OpenAI API key not configured.")
            print("Use --openai-key, run --config, or use --llm-provider ollama.")
            raise ValueError("OpenAI API key required when llm_provider=openai")

        try:
            self.analyzer = create_llm_analyzer(self.config)
            provider_label = self.config.get("llm_provider") or "openai"
            model = self.config.get("llm_model") or self.config.get("openai_model") or "gpt-4o-mini"
            print(f"LLM: {provider_label} ({model})")

            if (self.config.get("tmdb_enabled") and
                self.config.get("tmdb_api_key") and
                self.config.get("tmdb_bearer_token")):
                print("Initializing Hybrid Analyzer (LLM + TMDB)...")
                self.analyzer = HybridAnalyzer(
                    llm_analyzer=self.analyzer,
                    tmdb_api_key=self.config["tmdb_api_key"],
                    tmdb_bearer_token=self.config["tmdb_bearer_token"],
                    cache_duration_days=self.config.get("tmdb_cache_duration_days", 7),
                )
                print("Hybrid analyzer ready (LLM + TMDB)")
            else:
                print("LLM-only analyzer ready (configure TMDB in GUI for better accuracy)")
        except Exception as e:
            print(f"❌ ERROR: Failed to initialize analyzer: {e}")
            print()
            print("POSSIBLE CAUSES:")
            print("• Invalid OpenAI API key")
            print("• No internet connection")
            print("• Insufficient OpenAI credits")
            print("• Invalid TMDB credentials (if configured)")
            print()
            print("SOLUTIONS:")
            print("• Check API key in GUI settings")
            print("• Verify internet connection")
            print("• Check OpenAI account credits")
            print("• See API_SETUP.md for help")
            raise
        
        # File scanner and folder creator are created per run in organize_folder
        self.file_mover = FileMover(
            file_pattern=self.config.get('file_naming_pattern', '{title} ({year}){extension}'),
            max_retries=self.config.get('network_retry_attempts', 3),
            base_delay=self.config.get('network_retry_delay', 1.0)
        )
        self.report_generator = MovieReportGenerator()

    @staticmethod
    def _is_network_path(path) -> bool:
        """Return True if path is a network path (UNC, mapped drive, or Linux network prefix)."""
        s = str(path).strip()
        if not s:
            return False
        if s.startswith("\\\\") or s.startswith("//"):
            return True
        if len(s) >= 2 and s[1] == ":" and os.name == "nt":
            try:
                import ctypes
                drive = s[:2].upper()
                if ctypes.windll.kernel32.GetDriveTypeW(drive + "\\") == 4:
                    return True
            except Exception:
                pass
        if s.startswith("/mnt/") or s.startswith("/net/") or s.startswith("/media/"):
            return True
        return False
    
    def organize_folder(self, source_folder: Path, dry_run: bool = False, recursive: bool = True,
                        output_dir: Path = None, use_network: bool = False) -> bool:
        """
        Organize movies in a folder
        
        Args:
            source_folder: Source folder to organize
            dry_run: If True, show what would be done without doing it
            recursive: If True, scan subfolders
            
        Returns:
            bool: True if successful
        """
        try:
            output_base = output_dir if output_dir is not None else source_folder
            use_network_scanner = use_network or self._is_network_path(source_folder) or (
                output_dir is not None and self._is_network_path(output_dir)
            )
            video_extensions = self.config.get('video_extensions', [
                '.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.ogv', '.ts', '.m2ts', '.mts'
            ])

            if use_network_scanner:
                scanner = FastNetworkScanner(str(source_folder), video_extensions, recursive)
            else:
                scanner = FileScanner(str(source_folder), video_extensions, recursive)
            folder_creator = FolderCreator(str(output_base))

            print(f"Scanning folder: {source_folder}")
            movie_files = scanner.scan_video_files()
            
            if not movie_files:
                print("   No movie files found.")
                return True
            
            print(f"   Found {len(movie_files)} movie files")
            
            if dry_run:
                print("\n🔍 DRY RUN - Showing what would be done:")
                print("=" * 50)
            else:
                print(f"\n🎬 Analyzing and organizing {len(movie_files)} movies...")
                print("=" * 50)
            
            organized_count = 0
            failed_count = 0
            
            for i, file_path in enumerate(movie_files, 1):
                try:
                    print(f"\n[{i}/{len(movie_files)}] Processing: {file_path.name}")
                    
                    # Check if already organized
                    if self.report_generator.is_movie_already_organized(file_path.name):
                        print("   ✅ Already organized (skipping)")
                        continue
                    
                    # Analyze movie
                    print("   🔍 Analyzing with AI...")
                    metadata = self.analyzer.analyze_filename(file_path.name)
                    
                    if not metadata or not metadata.is_valid():
                        print("   ❌ Failed to analyze movie")
                        failed_count += 1
                        continue
                    
                    print(f"   📝 Identified: {metadata.title} ({metadata.year}) [{metadata.confidence_score:.1%}]")
                    
                    # Generate folder name
                    folder_name = f"{metadata.title} ({metadata.year})" if metadata.year else metadata.title
                    target_folder = file_path.parent / folder_name
                    
                    print(f"   Target folder: {folder_name}")
                    
                    if dry_run:
                        print(f"   Would move: {file_path.name} -> {folder_name}/")
                        organized_count += 1
                    else:
                        # Create folder under output_base and move file
                        destination_folder = folder_creator.create_movie_folder(metadata)
                        
                        # Move file
                        success, message, final_path = self.file_mover.organize_movie_file(
                            file_path, metadata, destination_folder
                        )
                        
                        if success:
                            print(f"   ✅ Organized: {final_path.name if final_path else 'unknown'}")
                            organized_count += 1
                            
                            # Add to report
                            source_type = "TMDB" if hasattr(self.analyzer, 'tmdb_service') else "AI"
                            self.report_generator.add_organized_movie(
                                title=metadata.title,
                                year=metadata.year,
                                original_filename=file_path.name,
                                folder_path=str(destination_folder),
                                source=source_type,
                                confidence_score=metadata.confidence_score
                            )
                        else:
                            print(f"   ❌ Failed: {message}")
                            failed_count += 1
                
                except Exception as e:
                    print(f"   ❌ Error processing {file_path.name}: {e}")
                    failed_count += 1
                    continue
            
            # Summary
            print("\n" + "=" * 60)
            print("📊 ORGANIZATION SUMMARY")
            print("=" * 60)
            print(f"✅ Successfully organized: {organized_count} movies")
            print(f"❌ Failed: {failed_count} movies")
            print(f"📈 Success rate: {(organized_count / len(movie_files) * 100):.1f}%")
            print(f"🎬 {get_version_string()}")
            
            if not dry_run and organized_count > 0:
                # Generate PDF report
                print("\n📄 Generating PDF report...")
                if self.report_generator.generate_pdf_report():
                    print("✅ PDF report generated successfully!")
                else:
                    print("⚠️  Failed to generate PDF report")
            
            return True
            
        except Exception as e:
            print(f"❌ Error organizing folder: {e}")
            return False

def setup_logging():
    """Setup logging for CLI"""
    logging.basicConfig(
        level=logging.WARNING,  # Less verbose for CLI
        format=f'%(levelname)s [{VERSION}]: %(message)s'
    )

def show_help():
    """Show CLI help information"""
    help_text = f"""
{get_startup_banner().strip()}

USAGE:
    python -m services.cli_organizer

DESCRIPTION:
    Command line interface for organizing movie files using AI and TMDB.
    
FEATURES:
    • AI-powered movie identification using OpenAI GPT
    • Optional TMDB integration for enhanced accuracy
    • Automatic folder creation and file organization
    • PDF report generation
    • Dry-run mode for preview
    
REQUIREMENTS:
    • OpenAI API Key (required)
    • TMDB API Key & Bearer Token (optional, recommended)
    
For GUI interface, run: python main.py

Author: {AUTHOR}
Version: {VERSION}
Repository: https://github.com/runawaydevil/organizer-movies.git
"""
    print(help_text)

if __name__ == "__main__":
    setup_logging()
    show_help()