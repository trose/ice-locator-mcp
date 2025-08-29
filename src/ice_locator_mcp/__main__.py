#!/usr/bin/env python3
"""
Entry point for running ICE Locator MCP Server as a module.

Usage:
    python -m ice_locator_mcp
"""

import asyncio
from .server import main

if __name__ == "__main__":
    asyncio.run(main())