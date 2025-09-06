#!/usr/bin/env python3
"""
Simple MCP client to test connection to ICE Locator MCP Server.
"""

import asyncio
import json
import os
import sys

# Add the src directory to the path so we can import the MCP components
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_connection():
    """Test connection to the MCP server."""
    print("Testing connection to ICE Locator MCP Server...")
    
    # Start the MCP server using stdio transport with configuration
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
            async with ClientSession(read, write) as session:
                # List available tools
                try:
                    tools = await session.list_tools()
                    print(f"Successfully connected to MCP server!")
                    print(f"Available tools: {[tool.name for tool in tools]}")
                    
                    # Test a simple tool call
                    for tool in tools:
                        print(f"\nTool: {tool.name}")
                        print(f"Description: {tool.description}")
                        if tool.inputSchema:
                            print(f"Input schema: {json.dumps(tool.inputSchema, indent=2)}")
                            
                except Exception as e:
                    print(f"Error listing tools: {e}")
                    return
                    
    except Exception as e:
        print(f"Error connecting to MCP server: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_connection())