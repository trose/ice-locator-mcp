#!/usr/bin/env python3
"""
Test script for ICE Locator MCP Server with proper session handling
"""

import asyncio
import json
import httpx


async def test_server():
    """Test the ICE Locator MCP server with proper session handling."""
    url = "http://127.0.0.1:8081/mcp"
    
    async with httpx.AsyncClient() as client:
        # First, let's try to get the tools list
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
                    "Accept": "application/json, text/event-stream"
                }
            )
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            print(f"Response body: {response.text}")
            
            # Check if we got a session ID
            session_id = response.headers.get('mcp-session-id')
            if session_id:
                print(f"Session ID: {session_id}")
                
                # Try to use the session ID in a subsequent request
                response2 = await client.post(
                    url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/list",
                        "params": {}
                    },
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream",
                        "mcp-session-id": session_id
                    }
                )
                print(f"Second request status: {response2.status_code}")
                print(f"Second request body: {response2.text}")
            else:
                print("No session ID found in response")
                
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_server())