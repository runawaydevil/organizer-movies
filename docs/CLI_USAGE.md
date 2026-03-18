# CLI Usage

Movie Organizer CLI: organize movie files by folder using LLM (OpenAI or Ollama) and optional TMDB.  
Author: Pablo Murad (runawaydevil). 2025-2026.

## Run

From project root:

```bash
python cli.py <source_folder> [options]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `source_folder` | Folder to scan for video files (local or network path). |
| `--output-dir`, `-o` | Destination directory for organized folders. If omitted, organizes in-place. |
| `--network` | Treat source and output as network paths; use network scanner and timeouts. |
| `--dry-run` | Show what would be done without moving files. |
| `--recursive` | Scan subfolders (default when not specified may depend on version). |
| `--llm-provider` | Override: `openai` or `ollama`. |
| `--llm-model` | Override model name. |
| `--ollama-url` | Ollama base URL (default: http://localhost:11434). |
| `--config` | Run interactive config setup. |
| `--report` | Generate PDF report. |
| `--version` | Show version. |

API overrides: `--openai-key`, `--tmdb-key`, `--tmdb-token`, `--model` (OpenAI model).

## Network paths

Supported: UNC (`\\server\share`), mapped drives (Windows), `/mnt/`, `/net/`, `/media/` (Linux). Use `--network` to force network scanner and retry/timeout settings.

## Examples

```bash
# In-place organization
python cli.py /path/to/movies --dry-run

# Output to a different directory
python cli.py /path/to/movies -o /path/to/organized

# Network share
python cli.py "\\server\movies" -o "\\server\organized" --network

# Use Ollama
python cli.py /path/to/movies --llm-provider ollama --llm-model llama3.2
```

## Config

Configure API keys in the GUI (File → Settings) or run `python cli.py --config`. Config is stored in the user config directory; see `config/config.example.json` for structure.
