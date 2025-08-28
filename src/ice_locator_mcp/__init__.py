# ICE Locator MCP Server

"""
Model Context Protocol server for ICE detainee location services.

This package provides a standardized MCP interface to the U.S. Immigration 
and Customs Enforcement (ICE) Online Detainee Locator System (ODLS).
"""

from .server import ICELocatorServer

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = ["ICELocatorServer"]