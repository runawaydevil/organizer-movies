"""
Setup script for Movie Organizer
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="movie-organizer",
    version="1.0.0",
    author="Movie Organizer Team",
    author_email="your-email@example.com",
    description="AI-Powered Movie File Organizer with TMDB Integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/movie-organizer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "Topic :: System :: Filesystems",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "openai>=1.0.0",
        "reportlab>=4.0.0",
        "pillow>=9.0.0",
        "httpx>=0.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "movie-organizer=main:main",
        ],
    },
    keywords="movie organizer ai tmdb plex jellyfin media server",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/movie-organizer/issues",
        "Source": "https://github.com/yourusername/movie-organizer",
        "Documentation": "https://github.com/yourusername/movie-organizer#readme",
    },
)