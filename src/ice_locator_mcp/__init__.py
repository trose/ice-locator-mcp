# ICE Locator MCP Server

"""
Advanced Model Context Protocol server for ICE detainee location services.

This package provides comprehensive MCP interface to the U.S. Immigration 
and Customs Enforcement (ICE) Online Detainee Locator System (ODLS) with
advanced anti-detection capabilities, bilingual support, and privacy-first design.
"""

from .server import ICELocatorServer
from .core.config import ServerConfig

__version__ = "1.0.0"
__author__ = "trose"
__email__ = "contact@ice-locator-mcp.org"
__license__ = "MIT"
__description__ = "Advanced MCP server for ICE detainee location services"
__url__ = "https://github.com/trose/ice-locator-mcp"

__all__ = ["ICELocatorServer", "Config"]