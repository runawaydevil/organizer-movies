# Movie Organizer

AI-powered movie file organizer. Analyzes filenames via OpenAI or local Ollama, optionally enriches with TMDB, and organizes files into `Title (Year)` folders. Runs on Windows, Linux, and macOS (from source).

**Author:** Pablo Murad (runawaydevil) · 2025–2026

## Requirements

- Python 3.8+
- **LLM:** OpenAI API key **or** [Ollama](https://ollama.ai) (local)
- **Optional:** TMDB API key + bearer token for better matching

## Install

```bash
git clone https://github.com/runawaydevil/organizer-movies.git
cd organizer-movies
pip install -r requirements.txt
```

First run: configure API keys in GUI (File → Settings) or via config (see `config/config.example.json`).

## Running on Linux and macOS

From the project root (same as Windows):

```bash
python main.py          # GUI
python cli.py <folder>  # CLI
```

- **Linux:** Install tkinter if needed: `sudo apt-get install python3-tk` (Debian/Ubuntu) or equivalent. Use a venv if you prefer: `python3 -m venv venv && source venv/bin/activate` then `pip install -r requirements.txt`.
- **macOS:** Install tkinter if needed: `brew install python-tk` (when using Homebrew Python). Config is stored under `~/.config/movie-organizer/`.

## Usage

**GUI:**
```bash
python main.py
```

**CLI:**
```bash
python cli.py <source_folder> [options]
```

Options: `--output-dir DIR`, `--dry-run`, `--recursive`, `--network`, `--llm-provider`, `--llm-model`, `--ollama-url`. See [docs/CLI_USAGE.md](docs/CLI_USAGE.md).

Network paths (UNC, mapped drives, `/mnt/`, `/net/`) are supported; use `--network` for explicit network mode.

## Config

Config is stored in the user config directory. Examples: `config/config.example.json`, `config/tmdb_config.example.json`. Keys (OpenAI) are encrypted locally.

## Project layout

```
core/          # version, processing context
config/        # example configs
models/        # data models, GUI
services/      # LLM (OpenAI/Ollama), TMDB, file scan/move, CLI
scripts/       # build, release, tagging
docs/          # documentation
```

## Build

```bash
cd scripts && python build_release.py
```

Dev deps: `pip install -e ".[dev]"` or use `requirements-dev.txt`.

## Security

- API keys encrypted (AES-256) in local storage.
- No telemetry. Only movie-related data sent to configured APIs.

