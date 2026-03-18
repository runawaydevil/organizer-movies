# API Setup

Configure LLM and optional TMDB for Movie Organizer.  
Author: Pablo Murad (runawaydevil). 2025-2026.

## LLM (required: one of)

### OpenAI

1. Get an API key: [OpenAI API Keys](https://platform.openai.com/api-keys).
2. In Movie Organizer: Settings → Provider **OpenAI** → enter API Key, choose Model (e.g. gpt-4o-mini).
3. Keys are stored encrypted locally.

Supported models: gpt-4o-mini (default), gpt-4o, gpt-4-turbo, gpt-4, gpt-3.5-turbo.

### Ollama (local)

1. Install [Ollama](https://ollama.ai) and run it (e.g. `ollama serve`).
2. Pull a model: `ollama pull llama3.2` (or mistral, gemma2, etc.).
3. In Movie Organizer: Settings → Provider **Ollama** → Base URL (default http://localhost:11434), Model (e.g. llama3.2).

No API key required. All processing is local.

## TMDB (optional)

Improves matching and metadata.

1. Create account: [TMDB](https://www.themoviedb.org).
2. [API Settings](https://www.themoviedb.org/settings/api): Request API Key, create app, copy **API Key** and **Bearer Token**.
3. In Movie Organizer: Settings → enable TMDB, enter API Key and Bearer Token.

## Config file

Example: `config/config.example.json`. User config is stored in the app config directory (not in the repo). Do not commit real keys.
