#!/usr/bin/env python3
"""
Movie Organizer - Command Line Interface
AI-Powered Movie File Organizer with TMDB Integration
Version: 0.1
Author: Pablo Murad (runawaydevil)
"""
import sys
import os
import argparse
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

def main():
    """Command line interface for Movie Organizer"""
    parser = argparse.ArgumentParser(
        description="Movie Organizer - AI-Powered Movie File Organizer with TMDB Integration",
        epilog="Author: Pablo Murad (runawaydevil) | Version: 0.1"
    )
    
    parser.add_argument(
        "source_folder",
        help="Source folder containing movie files to organize"
    )
    
    parser.add_argument(
        "--openai-key",
        help="OpenAI API key for movie analysis"
    )
    
    parser.add_argument(
        "--tmdb-key",
        help="TMDB API key for enhanced movie identification"
    )
    
    parser.add_argument(
        "--tmdb-token",
        help="TMDB Bearer token for API access"
    )
    
    parser.add_argument(
        "--model",
        default="gpt-3.5-turbo",
        help="OpenAI model to use (default: gpt-3.5-turbo)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually moving files"
    )
    
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Scan subfolders recursively"
    )
    
    parser.add_argument(
        "--config",
        action="store_true",
        help="Configure API keys interactively"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate PDF report of organized movies"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Movie Organizer v0.1 by Pablo Murad (runawaydevil)"
    )
    
    args = parser.parse_args()
    
    try:
        from services.config_manager import ConfigManager
        from services.cli_organizer import CLIOrganizer
        
        config_manager = ConfigManager()
        
        # Handle configuration setup
        if args.config:
            setup_configuration(config_manager)
            return 0
        
        # Handle report generation
        if args.report:
            generate_report()
            return 0
        
        # Validate source folder
        source_path = Path(args.source_folder)
        if not source_path.exists():
            print(f"❌ Error: Source folder does not exist: {source_path}")
            return 1
        
        if not source_path.is_dir():
            print(f"❌ Error: Source path is not a directory: {source_path}")
            return 1
        
        # Load configuration
        config = config_manager.load_config()
        
        # Override with command line arguments
        if args.openai_key:
            config['openai_api_key'] = args.openai_key
        
        if args.tmdb_key:
            config['tmdb_api_key'] = args.tmdb_key
        
        if args.tmdb_token:
            config['tmdb_bearer_token'] = args.tmdb_token
            config['tmdb_enabled'] = True
        
        config['openai_model'] = args.model
        
        # Validate required configuration
        if not config.get('openai_api_key'):
            print("❌ Error: OpenAI API key is required.")
            print("   Use --openai-key or run --config to set it up.")
            return 1
        
        # Initialize CLI organizer
        cli_organizer = CLIOrganizer(config)
        
        # Run organization
        success = cli_organizer.organize_folder(
            source_path,
            dry_run=args.dry_run,
            recursive=args.recursive
        )
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user")
        return 0
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1

def setup_configuration(config_manager):
    """Interactive configuration setup"""
    print("🔧 Movie Organizer Configuration Setup")
    print("=" * 50)
    
    config = config_manager.load_config()
    
    # OpenAI API Key
    print("\n📝 OpenAI Configuration:")
    current_openai = "***configured***" if config.get('openai_api_key') else "not configured"
    print(f"   Current status: {current_openai}")
    
    openai_key = input("   Enter OpenAI API key (or press Enter to keep current): ").strip()
    if openai_key:
        config['openai_api_key'] = openai_key
        print("   ✅ OpenAI API key updated")
    
    # OpenAI Model
    model = input(f"   Enter OpenAI model (current: {config.get('openai_model', 'gpt-3.5-turbo')}): ").strip()
    if model:
        config['openai_model'] = model
    
    # TMDB Configuration
    print("\n🎬 TMDB Configuration (optional):")
    current_tmdb = "***configured***" if config.get('tmdb_api_key') else "not configured"
    print(f"   Current status: {current_tmdb}")
    
    tmdb_key = input("   Enter TMDB API key (or press Enter to skip): ").strip()
    if tmdb_key:
        config['tmdb_api_key'] = tmdb_key
        
        tmdb_token = input("   Enter TMDB Bearer token: ").strip()
        if tmdb_token:
            config['tmdb_bearer_token'] = tmdb_token
            config['tmdb_enabled'] = True
            print("   ✅ TMDB configuration updated")
        else:
            print("   ⚠️  TMDB Bearer token required for TMDB integration")
    
    # Save configuration
    if config_manager.save_config(config):
        print("\n✅ Configuration saved successfully!")
        print("   Your API keys are encrypted and stored locally.")
        print("   They will not be included in version control.")
    else:
        print("\n❌ Failed to save configuration")
        return False
    
    return True

def generate_report():
    """Generate PDF report"""
    try:
        from services.movie_report_generator import MovieReportGenerator
        
        print("📊 Generating Movie Organization Report...")
        
        generator = MovieReportGenerator()
        success = generator.generate_pdf_report()
        
        if success:
            print("✅ PDF report generated successfully!")
            print(f"   Location: {Path.cwd() / 'organized_movies_report.pdf'}")
            
            # Show statistics
            stats = generator.get_statistics_summary()
            print(f"\n{stats}")
        else:
            print("❌ Failed to generate PDF report")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return False

if __name__ == "__main__":
    sys.exit(main())