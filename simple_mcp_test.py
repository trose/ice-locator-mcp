#!/usr/bin/env python3
"""
Simple test to verify MCP server is working correctly
"""

import asyncio
import json
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_server():
    """Test the MCP server connectivity."""
    print("Testing MCP server connectivity...")
    
    # Start the MCP server using stdio transport
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "ice_locator_mcp"],
        cwd=os.path.join(os.path.dirname(__file__))
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("Connected to MCP server")
                
                # Try to list tools
                try:
                    tools = await session.list_tools()
                    print(f"Available tools: {[tool.name for tool in tools]}")
                except Exception as e:
                    print(f"Error listing tools: {e}")
                    import traceback
                    traceback.print_exc()
                    
                # Try to call a simple tool
                try:
                    print("Attempting to call search_detainee_by_name...")
                    response = await session.call_tool(
                        name="search_detainee_by_name",
                        arguments={
                            "first_name": "JOSE",
                            "last_name": "GARCIA",
                            "date_of_birth": "1980-01-01",
                            "country_of_birth": "Mexico"
                        }
                    )
                    print(f"Response: {response}")
                    if response and response.content:
                        for content_item in response.content:
                            if hasattr(content_item, 'text'):
                                print(f"Result: {content_item.text}")
                except Exception as e:
                    print(f"Error calling tool: {e}")
                    import traceback
                    traceback.print_exc()
                    
    except Exception as e:
        print(f"Error connecting to MCP server: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mcp_server())