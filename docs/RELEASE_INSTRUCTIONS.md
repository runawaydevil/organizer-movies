# Release Instructions

Build and release steps. Author: Pablo Murad (runawaydevil). 2025-2026.

## Build (Windows)

From project root:

```cmd
cd scripts
python build_release.py
```

Output goes to a `release/` folder (or as configured in the script): executable, launchers, README, docs, LICENSE.

## Prerequisites

- Python 3.8+
- Dependencies: `pip install -r requirements.txt`
- PyInstaller (usually installed by the build script)

## Distribution

- **Installed**: run the installer batch as admin; program and config paths are set by the installer.
- **Portable**: run the portable batch from the release folder; no install, config in user profile or local.

## Version and tag

- Set version in `core/version.py` (VERSION, COPYRIGHT).
- Create a Git tag: `python scripts/create_git_tag.py` (if available).

## Platforms

- Windows: primary target for the scripted build.
- Linux/macOS: run from source (`python main.py`, `python cli.py`).
