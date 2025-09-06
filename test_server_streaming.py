#!/usr/bin/env python3
"""
Test script for ICE Locator MCP Server with proper streaming handling
"""

import asyncio
import json
import httpx


async def test_server():
    """Test the ICE Locator MCP server with proper streaming handling."""
    url = "http://127.0.0.1:8081/mcp"
    
    async with httpx.AsyncClient() as client:
        # First, let's try to get the tools list with proper streaming
        try:
            response = await client.post(
                url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {}
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream"
                }
            )
            
            # Handle streaming response
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: " prefix
                    try:
                        json_data = json.loads(data)
                        print(f"Received data: {json_data}")
                        if "result" in json_data:
                            print(f"Tools: {json_data['result']}")
                            break
                    except json.JSONDecodeError:
                        print(f"Non-JSON data: {data}")
                        
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_server())