# 🔧 Troubleshooting Guide

**Movie Organizer v0.1 - Common Issues and Solutions**  
*Author: Pablo Murad (runawaydevil)*

This guide covers common issues you might encounter while using Movie Organizer and their solutions.

## 🚨 Installation Issues

### Python and Dependencies

**"No module named 'tkinter'"**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL/Fedora
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk

# macOS (with Homebrew)
brew install python-tk
```

**"No module named 'cryptography'"**
```bash
# Install cryptography
pip install cryptography

# If compilation fails on Linux
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev

# On older systems
pip install --upgrade pip setuptools wheel
pip install cryptography
```

**"Permission denied" during installation**
```bash
# Use user installation
pip install --user -r requirements.txt

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## 🔑 API Configuration Issues

### OpenAI API Problems

**"Invalid API Key"**
- ✅ **Check key format**: Should start with `sk-` and be 51 characters long
- ✅ **Copy correctly**: No extra spaces or characters
- ✅ **Verify in dashboard**: Check [OpenAI API Keys](https://platform.openai.com/api-keys)
- ✅ **Check account status**: Ensure account is active and not suspended

**"Insufficient credits" / "Rate limit exceeded"**
- 💰 **Add credits**: Visit [OpenAI Billing](https://platform.openai.com/account/billing)
- ⏱️ **Wait and retry**: Rate limits reset after time
- 🔄 **Reduce batch size**: Process fewer files at once
- 📊 **Check usage**: Monitor usage in OpenAI dashboard

**"API request failed"**
- 🌐 **Check internet**: Verify network connection
- 🔥 **Firewall**: Ensure Movie Organizer can access internet
- 🚫 **Proxy**: Configure proxy settings if needed
- 📡 **OpenAI status**: Check [OpenAI Status](https://status.openai.com)

### TMDB API Problems

**"TMDB API Error" / "Invalid credentials"**
- 🔑 **Check both keys**: Need both API Key AND Bearer Token
- 📝 **Verify format**: 
  - API Key: 32 characters (letters and numbers)
  - Bearer Token: Long string starting with `eyJ`
- 🌐 **Test connection**: Use "Test Connection" button in settings
- 📋 **Account status**: Check [TMDB Account](https://www.themoviedb.org/settings/api)

**"TMDB rate limit exceeded"**
- ⏱️ **Automatic handling**: Movie Organizer handles this automatically
- 🔧 **Increase delay**: Adjust rate limit delay in settings
- 📊 **Check usage**: TMDB allows 40 requests per 10 seconds

## 🖥️ Application Issues

### GUI Problems

**"Application won't start"**
```bash
# Check Python version
python --version  # Should be 3.8+

# Run with error output
python main.py

# Check for missing dependencies
pip check
```

**"GUI appears but is blank/frozen"**
- 🖥️ **Display issues**: Try different display scaling
- 🔄 **Restart**: Close and restart application
- 🧹 **Clear config**: Delete config files and reconfigure
- 💻 **Virtual machine**: GUI may have issues in some VMs

**"Settings won't save"**
- 📁 **Permissions**: Check write permissions to config directory
- 💾 **Disk space**: Ensure sufficient disk space
- 🔒 **Admin rights**: Try running as administrator (Windows)
- 🛡️ **Antivirus**: Check if antivirus is blocking file writes

### File Processing Issues

**"No movie files found"**
- 📂 **Check extensions**: Ensure files have supported extensions
- 🔍 **Recursive scan**: Enable recursive scanning for subfolders
- 📁 **Folder permissions**: Ensure read access to movie folders
- 🌐 **Network drives**: Network paths may need special handling

**"Analysis failed" / "Low confidence scores"**
- 📝 **Filename quality**: Use descriptive filenames
- 📅 **Include year**: Add year to filename for better results
- 🏷️ **Remove tags**: Remove quality tags (1080p, x264, etc.)
- 🎬 **Manual search**: Use manual TMDB search for difficult movies

**"File move failed" / "Permission denied"**
- 🔒 **File permissions**: Check read/write permissions
- 📁 **Destination space**: Ensure sufficient disk space
- 🔄 **File in use**: Close media players or other applications
- 🌐 **Network issues**: Network drives may have connectivity issues

## 🌐 Network and Performance Issues

### Network Drive Problems

**"Network path not accessible"**
- 🔗 **Check connection**: Verify network drive is connected
- 🔑 **Credentials**: Ensure proper network credentials
- ⏱️ **Timeout**: Increase network timeout in settings
- 🔄 **Retry logic**: Enable network retry attempts

**"Slow processing on network drives"**
- 📊 **Expected behavior**: Network operations are slower
- 🔄 **Increase timeouts**: Adjust network timeout settings
- 💾 **Local processing**: Consider copying files locally first
- 🌐 **Network speed**: Check network connection speed

### Performance Issues

**"Application is slow"**
- 🧠 **Memory usage**: Close other applications
- 💻 **System resources**: Check CPU and memory usage
- 📊 **Large collections**: Process in smaller batches
- 🔄 **Cache**: TMDB cache improves performance over time

**"High API costs"**
- 🎯 **Use GPT-3.5**: Switch from GPT-4 to GPT-3.5-turbo
- 📊 **Monitor usage**: Check OpenAI usage dashboard
- 🎬 **Enable TMDB**: Use free TMDB to reduce OpenAI calls
- 📝 **Better filenames**: Cleaner names need fewer retries

## 🔒 Security and Privacy Issues

### Configuration Security

**"API keys not saving"**
- 🔐 **Encryption**: Check if cryptography library is installed
- 📁 **Config location**: Verify config directory permissions
- 🛡️ **Antivirus**: Check if security software is interfering
- 🔄 **Fallback mode**: App uses base64 if encryption fails

**"Suspicious activity warnings"**
- ✅ **False positive**: Movie Organizer is safe
- 🛡️ **Antivirus exception**: Add to antivirus whitelist
- 🔍 **Code signing**: Future versions will be code-signed
- 📊 **Open source**: All code is publicly available

### Privacy Concerns

**"What data is sent to APIs?"**
- 📝 **OpenAI**: Only movie filenames (no personal data)
- 🎬 **TMDB**: Only movie titles for metadata lookup
- 🚫 **No telemetry**: No usage data collected
- 💻 **Local processing**: All analysis done locally

## 🐛 Specific Error Messages

### Common Error Codes

**"Error 401: Unauthorized"**
- 🔑 **API key issue**: Check and re-enter API keys
- 📊 **Account status**: Verify account is active
- 💰 **Billing**: Check if payment method is valid

**"Error 429: Too Many Requests"**
- ⏱️ **Rate limiting**: Wait and retry automatically
- 🔧 **Adjust settings**: Increase rate limit delays
- 📊 **Usage limits**: Check API usage quotas

**"Error 500: Internal Server Error"**
- 🌐 **API issue**: Problem with OpenAI/TMDB servers
- 🔄 **Retry**: Try again later
- 📡 **Status pages**: Check API status pages

### File System Errors

**"Path too long"**
- 📏 **Windows limitation**: Path exceeds 260 characters
- 📁 **Shorter names**: Use shorter folder/file names
- 🔧 **Enable long paths**: Enable long path support in Windows
- 📂 **Move closer**: Move files closer to drive root

**"Invalid characters in filename"**
- 🚫 **Special characters**: Remove `< > : " | ? * \`
- 🔧 **Auto-sanitization**: Movie Organizer cleans names automatically
- 📝 **Manual edit**: Edit metadata to fix names

## 🔧 Advanced Troubleshooting

### Debug Mode

**Enable detailed logging:**
```bash
# Run with debug output
python main.py --debug

# Check log file
tail -f movie_organizer.log

# Windows
type movie_organizer.log
```

### Configuration Reset

**Reset all settings:**
```bash
# Find config directory
python -c "from services.secure_config_manager import SecureConfigManager; print(SecureConfigManager().config_dir)"

# Delete config files (backup first!)
# Windows: %LOCALAPPDATA%\MovieOrganizer\
# Linux: ~/.config/movie-organizer/
```

### System Information

**Gather system info for support:**
```bash
# Python version
python --version

# Installed packages
pip list

# System info
python -c "import platform; print(platform.platform())"

# Movie Organizer version
python -c "from version import VERSION; print(VERSION)"
```

## 📞 Getting Help

### Before Asking for Help

1. ✅ **Check this guide** - Most issues are covered here
2. 🔍 **Search existing issues** - Someone may have had the same problem
3. 📊 **Gather information** - Version, OS, error messages, logs
4. 🧪 **Test with simple case** - Try with a single, well-named movie file

### How to Report Issues

1. **Create GitHub Issue**: [Movie Organizer Issues](https://github.com/runawaydevil/organizer-movies/issues)
2. **Include information**:
   - Operating system and version
   - Python version
   - Movie Organizer version
   - Complete error message
   - Steps to reproduce
   - Log files (remove API keys!)

### Community Support

- 💬 **GitHub Discussions**: [Project Discussions](https://github.com/runawaydevil/organizer-movies/discussions)
- 📖 **Documentation**: Check all files in `docs/` folder
- 🔍 **Search Issues**: Look for similar problems

## 🚀 Performance Optimization

### Speed Up Processing

1. **Use GPT-3.5-turbo** instead of GPT-4
2. **Enable TMDB** for better caching
3. **Process in batches** for large collections
4. **Use SSD** for better file I/O performance
5. **Close other applications** to free resources

### Reduce API Costs

1. **Clean filenames** before processing
2. **Use TMDB** to reduce OpenAI calls
3. **Monitor usage** regularly
4. **Process incrementally** instead of all at once

---

**Movie Organizer v0.1**  
**Made with ❤️ by Pablo Murad (runawaydevil)**  
*Having issues? We're here to help! 🛠️*