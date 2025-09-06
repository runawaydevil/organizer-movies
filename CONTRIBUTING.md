# Contributing to Movie Organizer

Thank you for your interest in contributing to Movie Organizer! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- OpenAI API key for testing
- TMDB API credentials (optional)

### Development Setup

1. **Fork and clone the repository**
```bash
git clone https://github.com/yourusername/movie-organizer.git
cd movie-organizer
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API keys**
   - Copy your OpenAI API key
   - Run the application and configure in Settings

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python test_integration.py
python test_tmdb_cache.py
python test_file_mover.py
```

### Test Coverage
- Unit tests for all core components
- Integration tests for complete workflows
- Network operation tests
- GUI component tests

## 📝 Code Style

### Python Style Guide
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Add docstrings to all classes and methods
- Keep functions focused and small

### Example Code Style
```python
def analyze_movie_file(self, filename: str, use_tmdb: bool = True) -> Optional[MovieMetadata]:
    """
    Analyze movie file and return metadata
    
    Args:
        filename: Name of the movie file
        use_tmdb: Whether to use TMDB for enhanced accuracy
        
    Returns:
        MovieMetadata: Analyzed movie metadata or None if failed
    """
    try:
        # Implementation here
        pass
    except Exception as e:
        self.logger.error(f"Error analyzing {filename}: {e}")
        return None
```

## 🐛 Bug Reports

### Before Submitting
- Check existing issues to avoid duplicates
- Test with the latest version
- Gather relevant information (logs, screenshots, system info)

### Bug Report Template
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. Windows 10, Ubuntu 20.04]
- Python version: [e.g. 3.9.0]
- Movie Organizer version: [e.g. 1.0.0]

**Additional context**
Add any other context about the problem here.
```

## 💡 Feature Requests

### Feature Request Template
```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request.
```

## 🔄 Pull Requests

### Before Submitting
- Create an issue to discuss major changes
- Fork the repository and create a feature branch
- Write tests for new functionality
- Update documentation as needed
- Test your changes thoroughly

### Pull Request Process
1. **Create a feature branch**
```bash
git checkout -b feature/amazing-feature
```

2. **Make your changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation

3. **Test your changes**
```bash
python -m pytest tests/ -v
python test_integration.py
```

4. **Commit your changes**
```bash
git commit -m "Add amazing feature"
```

5. **Push to your fork**
```bash
git push origin feature/amazing-feature
```

6. **Create a Pull Request**
   - Use a clear title and description
   - Reference related issues
   - Include screenshots if applicable

### Pull Request Template
```markdown
**Description**
Brief description of changes made.

**Type of Change**
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

**Testing**
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

**Checklist**
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings or errors introduced
```

## 🏷️ Versioning

We use [Semantic Versioning](http://semver.org/) for versioning:
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

## 📞 Questions?

- Create an issue for questions about the codebase
- Check existing documentation and issues first
- Be specific and provide context

Thank you for contributing to Movie Organizer! 🎬