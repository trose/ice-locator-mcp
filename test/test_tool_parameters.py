#!/usr/bin/env python3
"""
Test MCP tool parameters to fix the "Invalid request parameters" error.
"""

import asyncio
import json
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_tool_parameters():
    """Test different parameter formats for MCP tools."""
    print("Testing MCP tool parameters...")
    
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
                print("Session created, listing tools...")
                
                # List available tools
                tools = await session.list_tools()
                print(f"Available tools: {[tool.name for tool in tools]}")
                
                # Test 1: Try to call search_detainee_by_name with minimal parameters
                print("\n--- Test 1: Minimal parameters ---")
                try:
                    result = await session.call_tool(
                        name="search_detainee_by_name",
                        arguments={
                            "first_name": "JOSE",
                            "last_name": "GARCIA",
                            "date_of_birth": "1980-01-01",
                            "country_of_birth": "Mexico"
                        }
                    )
                    print(f"✅ Success: {result}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                
                # Test 2: Try with all optional parameters
                print("\n--- Test 2: All parameters ---")
                try:
                    result = await session.call_tool(
                        name="search_detainee_by_name",
                        arguments={
                            "first_name": "JOSE",
                            "last_name": "GARCIA",
                            "date_of_birth": "1980-01-01",
                            "country_of_birth": "Mexico",
                            "middle_name": None,
                            "language": "en",
                            "fuzzy_search": True
                        }
                    )
                    print(f"✅ Success: {result}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                
                # Test 3: Try with string parameters only
                print("\n--- Test 3: String parameters only ---")
                try:
                    result = await session.call_tool(
                        name="search_detainee_by_name",
                        arguments={
                            "first_name": "JOSE",
                            "last_name": "GARCIA",
                            "date_of_birth": "1980-01-01",
                            "country_of_birth": "Mexico",
                            "language": "en",
                            "fuzzy_search": "true"
                        }
                    )
                    print(f"✅ Success: {result}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tool_parameters())

