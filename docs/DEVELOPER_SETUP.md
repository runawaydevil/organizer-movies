# Developer Setup

Movie Organizer – dev environment.  
Author: Pablo Murad (runawaydevil). 2025-2026.

## Prerequisites

- Python 3.8+
- Git

## Setup

```bash
git clone https://github.com/runawaydevil/organizer-movies.git
cd organizer-movies
pip install -r requirements.txt
```

Optional dev deps: `pip install -r requirements-dev.txt` or `pip install -e ".[dev]"`.

## Config

Do not commit real API keys. Use example configs:

- `config/config.example.json` – main config (LLM, network, naming).
- `config/tmdb_config.example.json` – TMDB.

Configure via GUI (File → Settings) or by copying examples to the app config directory and editing.

## Run

From the project root:

```bash
python main.py          # GUI
python cli.py <folder>  # CLI
```

**Linux:** Install tkinter if missing (e.g. `sudo apt-get install python3-tk`). Prefer a venv: `python3 -m venv venv`, `source venv/bin/activate`, then `pip install -r requirements.txt`.

**macOS:** Install tkinter if missing (e.g. `brew install python-tk` with Homebrew Python). Config directory: `~/.config/movie-organizer/`.

## Build

```bash
cd scripts && python build_release.py
```

See [RELEASE_INSTRUCTIONS.md](RELEASE_INSTRUCTIONS.md) for release steps.

## Project layout

- `core/` – version, processing context  
- `config/` – example configs  
- `models/` – data models, GUI  
- `services/` – LLM (OpenAI/Ollama), TMDB, file scan/move, CLI  
- `scripts/` – build, release, tagging  
- `docs/` – documentation  
