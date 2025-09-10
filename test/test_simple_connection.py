#!/usr/bin/env python3
"""
Simple test to debug the MCP connection issue.
"""

import asyncio
import json
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_simple_connection():
    """Test simple MCP connection without tool calls."""
    print("Testing simple MCP connection...")
    
    # Set up server parameters with monitoring disabled
    server_params = StdioServerParameters(
        command="/Users/trose/src/locator-mcp/.venv/bin/python",
        args=["-m", "ice_locator_mcp"],
        cwd="/Users/trose/src/locator-mcp",
        env={
            "PYTHONPATH": "/Users/trose/src/locator-mcp/src",
            "ICE_LOCATOR_ANALYTICS_ENABLED": "false",
            "ICE_LOCATOR_MCPCAT_ENABLED": "false",
            "ICE_LOCATOR_PROXY_ENABLED": "false"
        }
    )
    
    try:
        print("Starting MCP server...")
        async with stdio_client(server_params) as (read, write):
            print("MCP server started, creating session...")
            async with ClientSession(read, write) as session:
                print("Session created successfully!")
                
                # Try to get server info
                print("Getting server info...")
                try:
                    server_info = await session.get_server_info()
                    print(f"Server info: {server_info}")
                except Exception as e:
                    print(f"Error getting server info: {e}")
                
                # Try to list tools
                print("Listing tools...")
                try:
                    tools = await session.list_tools()
                    print(f"Tools listed successfully: {len(tools)} tools found")
                    for tool in tools:
                        print(f"  - {tool.name}: {tool.description}")
                except Exception as e:
                    print(f"Error listing tools: {e}")
                    import traceback
                    traceback.print_exc()
                
    except Exception as e:
        print(f"Connection error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_connection())

