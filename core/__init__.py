#!/usr/bin/env python3
"""
Core module - Movie Organizer
Version, processing context and shared utilities.

Author: Pablo Murad (runawaydevil)
Version: 0.1
"""
from core.version import (
    VERSION,
    AUTHOR,
    APP_TITLE,
    COPYRIGHT,
    REPOSITORY_URL,
    get_version_string,
    get_version_info,
    get_startup_banner,
)
from core.processing_context import ProcessingContext, ErrorHandler

__all__ = [
    "VERSION",
    "AUTHOR",
    "APP_TITLE",
    "COPYRIGHT",
    "REPOSITORY_URL",
    "get_version_string",
    "get_version_info",
    "get_startup_banner",
    "ProcessingContext",
    "ErrorHandler",
]
