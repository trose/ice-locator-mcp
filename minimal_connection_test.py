#!/usr/bin/env python3
"""
Minimal test to check if we can connect to the ICE Locator MCP Server.
"""

import asyncio
import os
import sys

# Add the src directory to the path so we can import the MCP components
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_connection():
    """Test basic connection to the MCP server."""
    print("Testing connection to ICE Locator MCP Server...")
    
    # Start the MCP server using stdio transport
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "ice_locator_mcp"],
        cwd=os.path.join(os.path.dirname(__file__)),
        env={
            **os.environ,
            "ICE_LOCATOR_ANALYTICS_ENABLED": "false"
        }
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            print("Stdio client created successfully")
            async with ClientSession(read, write) as session:
                print("Client session created successfully")
                print("Connection test completed")
                return True
    except Exception as e:
        print(f"Error connecting to MCP server: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_connection())
    print(f"Connection test result: {'SUCCESS' if result else 'FAILED'}")