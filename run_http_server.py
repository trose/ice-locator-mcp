#!/usr/bin/env python3
"""
HTTP Server for ICE Locator MCP

This script runs the ICE Locator MCP server over HTTP instead of stdio,
making it accessible via web requests.
"""

import asyncio
import sys
import os

# Add the src directory to the path so we can import the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ice_locator_mcp.server import ICELocatorServer
from mcp.server.fastmcp import FastMCP
from ice_locator_mcp.core.config import ServerConfig


async def main():
    """Main entry point for the HTTP server."""
    print("Starting ICE Locator MCP Server on HTTP...")
    
    # Create server config
    config = ServerConfig()
    
    # Create the ICE Locator server
    ice_server = ICELocatorServer(config)
    
    # Create FastMCP server
    app = FastMCP(
        name="ice-locator",
        host="127.0.0.1",
        port=8081
    )
    
    # Register tools from the ICE server with FastMCP
    @app.tool(
        name="search_detainee_by_name",
        description="Search for a detainee by name and personal information"
    )
    async def search_detainee_by_name(
        first_name: str,
        last_name: str,
        date_of_birth: str,
        country_of_birth: str,
        middle_name: str = None,
        language: str = "en",
        fuzzy_search: bool = True
    ) -> str:
        """Search for a detainee by name."""
        arguments = {
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": date_of_birth,
            "country_of_birth": country_of_birth,
            "middle_name": middle_name,
            "language": language,
            "fuzzy_search": fuzzy_search
        }
        result = await ice_server.search_tools.search_by_name(**arguments)
        return result
    
    @app.tool(
        name="search_detainee_by_alien_number",
        description="Search for a detainee by their alien registration number"
    )
    async def search_detainee_by_alien_number(
        alien_number: str,
        language: str = "en"
    ) -> str:
        """Search for a detainee by alien number."""
        arguments = {
            "alien_number": alien_number,
            "language": language
        }
        result = await ice_server.search_tools.search_by_alien_number(**arguments)
        return result
    
    @app.tool(
        name="smart_detainee_search",
        description="AI-powered search using natural language queries"
    )
    async def smart_detainee_search(
        query: str,
        context: str = None,
        suggest_corrections: bool = True,
        language: str = "en"
    ) -> str:
        """Perform a smart search."""
        arguments = {
            "query": query,
            "context": context,
            "suggest_corrections": suggest_corrections,
            "language": language
        }
        result = await ice_server.search_tools.smart_search(**arguments)
        return result
    
    @app.tool(
        name="bulk_search_detainees",
        description="Search multiple detainees simultaneously"
    )
    async def bulk_search_detainees(
        search_requests: list,
        max_concurrent: int = 3,
        continue_on_error: bool = True
    ) -> str:
        """Perform bulk searches."""
        arguments = {
            "search_requests": search_requests,
            "max_concurrent": max_concurrent,
            "continue_on_error": continue_on_error
        }
        result = await ice_server.search_tools.bulk_search(**arguments)
        return result
    
    @app.tool(
        name="generate_search_report",
        description="Generate comprehensive reports for legal or advocacy use"
    )
    async def generate_search_report(
        search_criteria: dict,
        results: list,
        report_type: str = "legal",
        format: str = "markdown"
    ) -> str:
        """Generate a search report."""
        arguments = {
            "search_criteria": search_criteria,
            "results": results,
            "report_type": report_type,
            "format": format
        }
        result = await ice_server.search_tools.generate_report(**arguments)
        return result
    
    # Start the ICE server components
    await ice_server.start()
    
    print(f"ICE Locator MCP Server running on http://127.0.0.1:8081")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Run the FastMCP server with HTTP transport
        await app.run_streamable_http_async()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        await ice_server.stop()


if __name__ == "__main__":
    asyncio.run(main())