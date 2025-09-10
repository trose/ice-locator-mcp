#!/usr/bin/env python3
"""
Minimal MCP server test to verify basic functionality.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence

import mcp.types as types
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from mcp.server import Server

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MinimalMCPServer:
    """Minimal MCP server for testing."""
    
    def __init__(self):
        """Initialize the minimal server."""
        self.server = Server("minimal-test")
        self._register_handlers()
        
    def _register_handlers(self) -> None:
        """Register minimal handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools."""
            return [
                types.Tool(
                    name="test_search",
                    description="Test search function",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name to search for"
                            }
                        },
                        "required": ["name"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> list[types.TextContent]:
            """Handle tool calls."""
            if name == "test_search":
                search_name = arguments.get("name", "Unknown")
                result = {
                    "status": "found",
                    "message": f"Test search for {search_name} completed",
                    "results": []
                }
                return [types.TextContent(type="text", text=json.dumps(result))]
            else:
                raise ValueError(f"Unknown tool: {name}")

async def main() -> None:
    """Main entry point."""
    logger.info("Starting minimal MCP server...")
    
    server = MinimalMCPServer()
    
    try:
        # Run server with stdio transport
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="minimal-test",
                    server_version="0.1.0",
                    capabilities=server.server.get_capabilities()
                )
            )
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

