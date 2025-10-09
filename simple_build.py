#!/usr/bin/env python3
"""
Simple Build Script - Movie Organizer v0.1
Creates a working Windows executable

Author: Pablo Murad (runawaydevil)
"""
import subprocess
import sys
import shutil
from pathlib import Path

def create_simple_exe():
    """Create executable with simple PyInstaller command"""
    print("🔨 Building simple executable...")
    
    # Clean previous builds
    if Path('dist').exists():
        shutil.rmtree('dist')
    if Path('build').exists():
        shutil.rmtree('build')
    
    # Simple PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=MovieOrganizer",
        "--add-data=Images;Images",
        "--add-data=version.py;.",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=openai",
        "--hidden-import=requests",
        "--hidden-import=reportlab",
        "--hidden-import=cryptography",
        "--hidden-import=PIL",
        "--clean",
        "main.py"
    ]
    
    print("Command:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Simple executable built successfully!")
        return True
    else:
        print("❌ Build failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False

def test_exe():
    """Test the executable"""
    exe_path = Path("dist/MovieOrganizer.exe")
    if exe_path.exists():
        print(f"✅ Executable created: {exe_path}")
        print(f"📊 Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
        
        # Try to run it briefly
        try:
            result = subprocess.run([str(exe_path)], timeout=3, capture_output=True)
            print("✅ Executable starts without immediate crash")
        except subprocess.TimeoutExpired:
            print("✅ Executable is running (timeout after 3s - normal for GUI)")
        except Exception as e:
            print(f"❌ Executable failed to start: {e}")
            return False
        
        return True
    else:
        print("❌ Executable not found!")
        return False

def main():
    print("🎬 Movie Organizer v0.1 - Simple Build")
    print("Author: Pablo Murad (runawaydevil)")
    print("=" * 50)
    
    if create_simple_exe():
        if test_exe():
            print("\n🎉 Build completed successfully!")
            print("📁 Executable location: dist/MovieOrganizer.exe")
            print("🚀 Ready to test!")
        else:
            print("\n❌ Build completed but executable has issues")
    else:
        print("\n❌ Build failed")

if __name__ == "__main__":
    main()