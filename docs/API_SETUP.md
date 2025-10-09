# 🔑 API Setup Guide

**Movie Organizer v0.1 - API Configuration Guide**  
*Author: Pablo Murad (runawaydevil)*

This guide provides detailed instructions for setting up the required and optional API keys for Movie Organizer.

## 📋 Overview

Movie Organizer uses two APIs to provide the best movie identification experience:

- **🤖 OpenAI API** (Required) - For AI-powered movie identification
- **🎬 TMDB API** (Optional, Recommended) - For enhanced accuracy and metadata

## 🚨 Required: OpenAI API Key

### Why is OpenAI Required?

The OpenAI API is the core of Movie Organizer's intelligence. It analyzes movie filenames and identifies movies using advanced AI models.

### Step-by-Step Setup

1. **Create OpenAI Account**
   - Visit [OpenAI Platform](https://platform.openai.com)
   - Sign up for a new account or log in to existing account

2. **Navigate to API Keys**
   - Go to [API Keys page](https://platform.openai.com/api-keys)
   - Click "Create new secret key"

3. **Generate API Key**
   - Give your key a descriptive name (e.g., "Movie Organizer")
   - Copy the generated key immediately (you won't see it again!)
   - Store it securely

4. **Add Credits to Account**
   - Visit [Billing page](https://platform.openai.com/account/billing)
   - Add payment method and credits
   - **Minimum recommended**: $5-10 for processing hundreds of movies

5. **Configure in Movie Organizer**
   - Open Movie Organizer
   - Go to Settings (File → Settings or Ctrl+,)
   - Paste your API key in "OpenAI API Key" field
   - Select your preferred model (GPT-3.5-turbo recommended for cost)
   - Click "Save"

### Model Selection

| Model | Speed | Accuracy | Cost | Recommendation |
|-------|-------|----------|------|----------------|
| **gpt-3.5-turbo** | ⚡ Fast | ✅ Good | 💰 Low | **Recommended** |
| **gpt-4** | 🐌 Slower | ⭐ Excellent | 💰💰 High | For difficult files |
| **gpt-4-turbo** | ⚡ Fast | ⭐ Excellent | 💰💰 Medium | Best balance |

### Cost Estimation

- **GPT-3.5-turbo**: ~$0.001 per movie (~1000 movies per $1)
- **GPT-4**: ~$0.01 per movie (~100 movies per $1)
- **Average collection (500 movies)**: $0.50 - $5.00

## 🎬 Optional: TMDB API (Recommended)

### Why Use TMDB?

TMDB (The Movie Database) provides:
- ✅ **Higher accuracy** - Cross-references AI results
- ✅ **Rich metadata** - Posters, cast, ratings, genres
- ✅ **Multiple languages** - International movie support
- ✅ **Free to use** - No cost for API calls

### Step-by-Step Setup

1. **Create TMDB Account**
   - Visit [TMDB](https://www.themoviedb.org)
   - Sign up for a free account

2. **Request API Access**
   - Go to [API Settings](https://www.themoviedb.org/settings/api)
   - Click "Request an API Key"
   - Choose "Developer" option
   - Fill out the application form:
     - **Application Name**: "Movie Organizer"
     - **Application URL**: "Personal Use" or your website
     - **Application Summary**: "Personal movie collection organization"

3. **Get Your Credentials**
   After approval (usually instant), you'll get:
   - **API Key (v3 auth)** - 32-character string
   - **API Read Access Token (v4 auth)** - Long Bearer token

4. **Configure in Movie Organizer**
   - Open Movie Organizer Settings
   - Enter both credentials in TMDB section:
     - **TMDB API Key**: Your v3 API key
     - **TMDB Bearer Token**: Your v4 access token
   - Configure language preferences
   - Click "Test Connection" to verify
   - Click "Save"

### TMDB Configuration Options

| Setting | Description | Recommendation |
|---------|-------------|----------------|
| **Language** | Metadata language | en-US (or your preference) |
| **Original Titles** | Use original vs localized titles | ✅ Enabled |
| **Cache Duration** | How long to cache results | 7 days |
| **Rate Limit Delay** | Delay between API calls | 0.25 seconds |

## 🔧 Configuration in Movie Organizer

### GUI Configuration

1. **Open Settings**
   ```
   File → Settings
   OR
   Ctrl + , (Comma)
   ```

2. **OpenAI Section**
   - Enter your OpenAI API key
   - Select model (gpt-3.5-turbo recommended)
   - Test connection

3. **TMDB Section** (Optional)
   - Enter API Key and Bearer Token
   - Configure language and preferences
   - Test connection

4. **Save Configuration**
   - Keys are encrypted and stored locally
   - Never transmitted except to respective APIs

### CLI Configuration

For CLI usage, configure through GUI first, then use:

```bash
# CLI will use saved configuration
python services/cli_organizer.py
```

## 🔒 Security & Privacy

### API Key Storage
- **Encrypted locally** using AES-256 encryption
- **Never transmitted** except to OpenAI/TMDB
- **Stored securely** in OS-specific locations:
  - Windows: `%LOCALAPPDATA%\\MovieOrganizer\\config\\`
  - Linux: `~/.config/movie-organizer/config/`

### Data Privacy
- **Only movie titles** sent to APIs for identification
- **No personal data** transmitted
- **No telemetry** or usage tracking
- **Local processing** only

## 🚨 Troubleshooting

### OpenAI API Issues

**"Invalid API Key"**
- Verify key is copied correctly (no extra spaces)
- Check if key is active in OpenAI dashboard
- Ensure account has sufficient credits

**"Rate limit exceeded"**
- You're making too many requests
- Wait a few minutes and try again
- Consider upgrading OpenAI plan

**"Insufficient credits"**
- Add more credits to your OpenAI account
- Check billing page for current balance

### TMDB API Issues

**"Invalid API Key"**
- Verify both API Key and Bearer Token are correct
- Check TMDB account status
- Ensure API access is approved

**"Rate limit exceeded"**
- TMDB allows 40 requests per 10 seconds
- Movie Organizer automatically handles rate limiting
- If issues persist, increase rate limit delay in settings

**"Movie not found"**
- Some movies may not be in TMDB database
- AI-only identification will be used as fallback
- Consider manual search for difficult movies

### General Issues

**"No internet connection"**
- Check your internet connection
- Verify firewall isn't blocking the application
- Try testing with a simple movie first

**"Settings not saving"**
- Check file permissions in config directory
- Run as administrator (Windows) if needed
- Verify disk space is available

## 💡 Tips for Best Results

### OpenAI Tips
1. **Use descriptive filenames** - Better results with clear movie names
2. **Include year when possible** - Helps distinguish remakes
3. **Remove excessive tags** - Clean filenames work better
4. **Monitor usage** - Check OpenAI usage dashboard regularly

### TMDB Tips
1. **Enable original titles** - Better for international movies
2. **Set correct language** - Matches your collection language
3. **Use cache** - Reduces API calls for repeated operations
4. **Manual search** - Use for difficult or obscure movies

### General Tips
1. **Start small** - Test with a few movies first
2. **Review results** - Check AI confidence scores
3. **Manual corrections** - Edit metadata when needed
4. **Backup first** - Always backup your collection before organizing

## 📞 Support

If you encounter issues with API setup:

1. **Check this guide** - Most issues are covered here
2. **Test with simple movies** - Verify basic functionality
3. **Check API status pages**:
   - [OpenAI Status](https://status.openai.com)
   - [TMDB Status](https://status.themoviedb.org)
4. **Create an issue** - [GitHub Issues](https://github.com/runawaydevil/organizer-movies/issues)

---

**Movie Organizer v0.1**  
**Made with ❤️ by Pablo Murad (runawaydevil)**  
*Get your APIs configured and start organizing! 🎬*