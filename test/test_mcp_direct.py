#!/usr/bin/env python3
"""
Direct test of the MCP server to diagnose connection issues.
"""

import asyncio
import json
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_connection():
    """Test direct connection to MCP server."""
    print("Testing MCP server connection...")
    
    # Set up server parameters
    server_params = StdioServerParameters(
        command="/Users/trose/src/locator-mcp/.venv/bin/python",
        args=["-m", "ice_locator_mcp"],
        cwd="/Users/trose/src/locator-mcp",
        env={
            "PYTHONPATH": "/Users/trose/src/locator-mcp/src"
        }
    )
    
    try:
        print("Starting MCP server...")
        async with stdio_client(server_params) as (read, write):
            print("MCP server started, creating session...")
            async with ClientSession(read, write) as session:
                print("Session created, listing tools...")
                
                # List available tools
                tools = await session.list_tools()
                print(f"Available tools: {[tool.name for tool in tools]}")
                
                # Test a simple search
                print("Testing search_detainee_by_name tool...")
                result = await session.call_tool(
                    name="search_detainee_by_name",
                    arguments={
                        "first_name": "JOSE",
                        "last_name": "GARCIA", 
                        "date_of_birth": "1980-01-01",
                        "country_of_birth": "Mexico",
                        "fuzzy_search": True
                    }
                )
                
                print(f"Search result: {result}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_connection())

