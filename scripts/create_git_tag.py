#!/usr/bin/env python3
"""
Create Git Tag - Movie Organizer v0.1
Creates annotated Git tag for release

Author: Pablo Murad (runawaydevil)
Repository: https://github.com/runawaydevil/organizer-movies.git
"""
import subprocess
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.version import VERSION, get_version_string

def create_git_tag():
    """Create annotated Git tag for release"""
    tag_name = f"v{VERSION}"
    
    print(f"🏷️  Creating Git tag: {tag_name}")
    print(f"📝 Version: {get_version_string()}")
    
    # Check if tag already exists
    try:
        result = subprocess.run(
            ["git", "tag", "-l", tag_name],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout.strip():
            print(f"⚠️  Tag {tag_name} already exists!")
            response = input("Do you want to delete and recreate it? (y/N): ")
            if response.lower() != 'y':
                print("❌ Tag creation cancelled")
                return False
            
            # Delete existing tag
            subprocess.run(["git", "tag", "-d", tag_name], check=True)
            print(f"🗑️  Deleted existing tag {tag_name}")
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking existing tags: {e}")
        return False
    
    # Create tag message
    tag_message = f"""Movie Organizer v{VERSION} - First Official Release

🎬 AI-Powered Movie File Organizer with TMDB Integration

✨ Features:
• AI-powered movie identification using OpenAI GPT
• TMDB integration for enhanced accuracy
• Smart folder management and organization
• Network drive support
• PDF report generation
• Secure API key storage
• Cross-platform compatibility

🔒 Security:
• AES-256 encryption for API keys
• Local processing only
• No telemetry or data collection

📦 Distribution:
• Windows executable with installer
• Portable mode available
• Complete documentation included

Author: Pablo Murad (runawaydevil)
Repository: https://github.com/runawaydevil/organizer-movies.git"""
    
    try:
        # Create annotated tag
        subprocess.run([
            "git", "tag", "-a", tag_name, 
            "-m", tag_message
        ], check=True)
        
        print(f"✅ Created annotated tag: {tag_name}")
        
        # Show tag info
        result = subprocess.run([
            "git", "show", tag_name, "--no-patch"
        ], capture_output=True, text=True, check=True)
        
        print("\n📋 Tag Information:")
        print(result.stdout)
        
        # Ask if user wants to push tag
        response = input(f"\nDo you want to push tag {tag_name} to origin? (y/N): ")
        if response.lower() == 'y':
            subprocess.run(["git", "push", "origin", tag_name], check=True)
            print(f"🚀 Pushed tag {tag_name} to origin")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating tag: {e}")
        return False

def list_existing_tags():
    """List existing Git tags"""
    try:
        result = subprocess.run(
            ["git", "tag", "-l", "--sort=-version:refname"],
            capture_output=True,
            text=True,
            check=True
        )
        
        tags = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        if tags:
            print("📋 Existing tags:")
            for tag in tags[:10]:  # Show last 10 tags
                print(f"   • {tag}")
            if len(tags) > 10:
                print(f"   ... and {len(tags) - 10} more")
        else:
            print("📋 No existing tags found")
        
        return tags
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error listing tags: {e}")
        return []

def main():
    """Main function"""
    print("🏷️  Git Tag Creator - Movie Organizer")
    print("=" * 50)
    print()
    
    # Check if we're in a git repository
    try:
        subprocess.run(["git", "status"], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ Not in a Git repository!")
        return 1
    
    # Check for uncommitted changes
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout.strip():
            print("⚠️  You have uncommitted changes:")
            print(result.stdout)
            response = input("Do you want to continue anyway? (y/N): ")
            if response.lower() != 'y':
                print("❌ Tag creation cancelled")
                return 1
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking git status: {e}")
        return 1
    
    # List existing tags
    list_existing_tags()
    print()
    
    # Create new tag
    if create_git_tag():
        print("\n🎉 Tag created successfully!")
        print(f"📝 Use 'git push origin v{VERSION}' to push to remote")
        print(f"🚀 Ready to create GitHub release for v{VERSION}")
        return 0
    else:
        print("\n❌ Tag creation failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())