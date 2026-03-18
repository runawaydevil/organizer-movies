#!/usr/bin/env python3
"""
Simple Build Script - Movie Organizer v0.1
Creates a working Windows executable.
Run from project root: python scripts/simple_build.py

Author: Pablo Murad (runawaydevil)
"""
import subprocess
import sys
import shutil
from pathlib import Path

# Ensure we run from project root (parent of scripts/)
ROOT = Path(__file__).resolve().parent.parent
if Path.cwd() != ROOT:
    import os
    os.chdir(ROOT)

def create_simple_exe():
    """Create executable with simple PyInstaller command"""
    print("Building simple executable...")

    # Clean previous builds
    if Path('dist').exists():
        shutil.rmtree('dist')
    if Path('build').exists():
        shutil.rmtree('build')

    # PyInstaller: bundle core/ so that core.version and core.processing_context are available
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=MovieOrganizer",
        "--add-data=Images;Images",
        "--add-data=core;core",
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
        print("Simple executable built successfully!")
        return True
    else:
        print("Build failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False

def test_exe():
    """Test the executable"""
    exe_path = Path("dist/MovieOrganizer.exe")
    if exe_path.exists():
        print(f"Executable created: {exe_path}")
        print(f"Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")

        try:
            result = subprocess.run([str(exe_path)], timeout=3, capture_output=True)
            print("Executable starts without immediate crash")
        except subprocess.TimeoutExpired:
            print("Executable is running (timeout after 3s - normal for GUI)")
        except Exception as e:
            print(f"Executable failed to start: {e}")
            return False

        return True
    else:
        print("Executable not found!")
        return False

def main():
    print("Movie Organizer v0.1 - Simple Build")
    print("Author: Pablo Murad (runawaydevil)")
    print("=" * 50)

    if create_simple_exe():
        if test_exe():
            print("\nBuild completed successfully!")
            print("Executable location: dist/MovieOrganizer.exe")
        else:
            print("\nBuild completed but executable has issues")
    else:
        print("\nBuild failed")

if __name__ == "__main__":
    main()
