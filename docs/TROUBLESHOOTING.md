# Troubleshooting

Common issues and fixes. Author: Pablo Murad (runawaydevil). 2025-2026.

## Installation

**Missing tkinter**
- Linux: `sudo apt-get install python3-tk` (or equivalent).
- macOS: `brew install python-tk`.

**Missing cryptography**
- `pip install cryptography`. On Linux if build fails: install `build-essential libssl-dev libffi-dev python3-dev`, then retry.

**Permission denied**
- Use a venv: `python -m venv venv`, activate, then `pip install -r requirements.txt`.

## LLM / API

**OpenAI: Invalid API key**
- Key should start with `sk-`. Copy from [OpenAI API Keys](https://platform.openai.com/api-keys). No extra spaces.

**OpenAI: Rate limit / no credits**
- Add credits at [OpenAI Billing](https://platform.openai.com/account/billing). Or switch to Ollama (Settings → Provider: Ollama).

**Ollama: Connection refused**
- Start Ollama: run `ollama serve` or launch Ollama app. Default URL: http://localhost:11434. Check Settings → Ollama Base URL.

**TMDB: Invalid credentials**
- You need both API Key and Bearer Token from [TMDB API](https://www.themoviedb.org/settings/api). Re-copy both.

## Network paths

**Slow or hanging on network folders**
- Use CLI with `--network`. In GUI, network paths use a slower scanner with timeouts; ensure the share is reachable and not overloaded.

**Permission denied on network**
- Check share permissions and that the process can write to the destination.

## Build / run

**Import errors when running**
- Run from project root: `python main.py` or `python cli.py <folder>`. Ensure `core`, `models`, `services` are on the path (e.g. no `cd` into a subfolder that breaks imports).

**PyInstaller build fails**
- Use the project’s build script: `cd scripts && python build_release.py`. See [RELEASE_INSTRUCTIONS.md](RELEASE_INSTRUCTIONS.md).

## macOS: API keys not persisting

If you have to re-enter API keys every time you run the app:

- **Config location:** `~/.config/movie-organizer/`. Ensure this directory exists and is writable (e.g. `mkdir -p ~/.config/movie-organizer`).
- **After an update:** If keys still don’t persist, re-enter them once in Settings and save. New installs use a stable encryption key; older configs may have been encrypted with a key that depended on how the app was launched.
- **Terminal vs Finder:** Running from Terminal vs double-clicking can use a different environment (e.g. `HOME`). Prefer running from the same context, or re-enter keys once after the fix so they are stored with the new key.
