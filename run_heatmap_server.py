#!/usr/bin/env python3
"""
Heatmap API Server for ICE Locator MCP

This script runs the heatmap API server over HTTP, making heatmap data 
accessible via web requests for the web and mobile apps.
"""

import asyncio
import sys
import os
import uvicorn

# Add the src directory to the path so we can import the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ice_locator_mcp.api import app


def main():
    """Main entry point for the heatmap API server."""
    print("Starting ICE Locator Heatmap API Server...")
    
    # Run the FastAPI server with uvicorn
    uvicorn.run(
        "ice_locator_mcp.api:app",
        host="127.0.0.1",
        port=8082,
        reload=True,
        root_path=os.path.join(os.path.dirname(__file__), 'src'),
        app_dir=os.path.join(os.path.dirname(__file__), 'src')
    )


if __name__ == "__main__":
    main()