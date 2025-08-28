"""
Internationalization and multilingual support for ICE Locator MCP Server.

This module provides comprehensive Spanish language support including:
- Natural language processing in Spanish
- Interface translation and localization
- Cultural name matching and processing
- Localized legal resources and guidance
"""

from .processor import LanguageProcessor, MultiLanguageInterface, TranslationEntry

__all__ = [
    "LanguageProcessor",
    "MultiLanguageInterface", 
    "TranslationEntry"
]