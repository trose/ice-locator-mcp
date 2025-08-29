#!/usr/bin/env python3
"""
ICE Locator MCP Server

Main server implementation that provides MCP tools for accessing ICE detainee information.
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

import mcp.types as types
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
import structlog

from .core.config import ServerConfig
from .core.search_engine import SearchEngine
from .anti_detection.proxy_manager import ProxyManager
from .tools.search_tools import SearchTools
from .utils.logging import setup_logging
from .monitoring.comprehensive_monitor import ComprehensiveMonitor


class ICELocatorServer:
    """Main MCP server for ICE detainee location services."""
    
    def __init__(self, config: Optional[ServerConfig] = None):
        """Initialize the ICE Locator MCP Server."""
        self.config = config or ServerConfig()
        self.logger = structlog.get_logger(__name__)
        
        # Initialize comprehensive monitoring system
        self.comprehensive_monitor = None
        
        if self.config.monitoring_config.mcpcat_enabled:
            try:
                # Initialize comprehensive monitoring system
                self.comprehensive_monitor = ComprehensiveMonitor(
                    self.config.monitoring_config,
                    storage_path=None  # Use default storage path
                )
                
                self.logger.info(
                    "Comprehensive monitoring initialized with privacy-first design",
                    mcpcat_enabled=True,
                    redaction_level=self.config.monitoring_config.redaction_level,
                    components=["mcpcat", "telemetry", "analytics", "session_replay", "system_monitor"]
                )
            except Exception as e:
                self.logger.warning(
                    "Failed to initialize comprehensive monitoring - continuing without analytics",
                    error=str(e)
                )
        
        # Initialize core components
        self.proxy_manager = ProxyManager(self.config.proxy_config)
        self.search_engine = SearchEngine(
            proxy_manager=self.proxy_manager,
            config=self.config.search_config
        )
        self.search_tools = SearchTools(self.search_engine)
        
        # Initialize MCP server
        self.server = Server("ice-locator")
        self._register_handlers()
        
        # Set up MCPcat tracking after tools are registered
        if self.comprehensive_monitor and hasattr(self.comprehensive_monitor, 'mcpcat_monitor'):
            if self.comprehensive_monitor.mcpcat_monitor:
                self.comprehensive_monitor.mcpcat_monitor.setup_tracking(self.server)
        
    def _register_handlers(self) -> None:
        """Register all MCP handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List all available tools."""
            return [
                types.Tool(
                    name="search_detainee_by_name",
                    description="Search for a detainee by name and personal information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "first_name": {
                                "type": "string",
                                "description": "First name of the detainee"
                            },
                            "last_name": {
                                "type": "string", 
                                "description": "Last name of the detainee"
                            },
                            "date_of_birth": {
                                "type": "string",
                                "description": "Date of birth in YYYY-MM-DD format"
                            },
                            "country_of_birth": {
                                "type": "string",
                                "description": "Country of birth"
                            },
                            "middle_name": {
                                "type": "string",
                                "description": "Middle name (optional)"
                            },
                            "language": {
                                "type": "string",
                                "description": "Response language (default: en)",
                                "default": "en"
                            },
                            "fuzzy_search": {
                                "type": "boolean", 
                                "description": "Enable fuzzy name matching (default: true)",
                                "default": True
                            }
                        },
                        "required": ["first_name", "last_name", "date_of_birth", "country_of_birth"]
                    }
                ),
                types.Tool(
                    name="search_detainee_by_alien_number", 
                    description="Search for a detainee by their alien registration number",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "alien_number": {
                                "type": "string",
                                "description": "Alien registration number (A-number)"
                            },
                            "language": {
                                "type": "string",
                                "description": "Response language (default: en)",
                                "default": "en"
                            }
                        },
                        "required": ["alien_number"]
                    }
                ),
                types.Tool(
                    name="smart_detainee_search",
                    description="AI-powered search using natural language queries",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language search query"
                            },
                            "context": {
                                "type": "string",
                                "description": "Additional context for the search"
                            },
                            "suggest_corrections": {
                                "type": "boolean",
                                "description": "Enable auto-correction suggestions (default: true)",
                                "default": True
                            },
                            "language": {
                                "type": "string", 
                                "description": "Response language (default: en)",
                                "default": "en"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="bulk_search_detainees",
                    description="Search multiple detainees simultaneously",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "search_requests": {
                                "type": "array",
                                "description": "List of search requests",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "first_name": {"type": "string"},
                                        "last_name": {"type": "string"},
                                        "date_of_birth": {"type": "string"},
                                        "country_of_birth": {"type": "string"},
                                        "alien_number": {"type": "string"}
                                    }
                                }
                            },
                            "max_concurrent": {
                                "type": "integer",
                                "description": "Maximum concurrent searches (default: 3)",
                                "default": 3,
                                "minimum": 1,
                                "maximum": 5
                            },
                            "continue_on_error": {
                                "type": "boolean",
                                "description": "Continue processing if some searches fail (default: true)",
                                "default": True
                            }
                        },
                        "required": ["search_requests"]
                    }
                ),
                types.Tool(
                    name="generate_search_report",
                    description="Generate comprehensive reports for legal or advocacy use",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "search_criteria": {
                                "type": "object",
                                "description": "Original search parameters"
                            },
                            "results": {
                                "type": "array",
                                "description": "Search results to include in report"
                            },
                            "report_type": {
                                "type": "string",
                                "description": "Type of report (legal, advocacy, family)",
                                "enum": ["legal", "advocacy", "family"],
                                "default": "legal"
                            },
                            "format": {
                                "type": "string",
                                "description": "Output format (markdown, json)",
                                "enum": ["markdown", "json"],
                                "default": "markdown"
                            }
                        },
                        "required": ["search_criteria", "results"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
            """Handle tool calls with telemetry instrumentation."""
            
            # Track tool call with comprehensive monitoring (privacy-preserving)
            if self.comprehensive_monitor:
                await self.comprehensive_monitor.track_tool_call(
                    session_id="default",  # Use default session or implement session management
                    tool_name=name,
                    arguments=arguments
                )
            
            try:
                self.logger.info("Tool called", tool_name=name, arguments=arguments)
                
                if name == "search_detainee_by_name":
                    result = await self.search_tools.search_by_name(**arguments)
                elif name == "search_detainee_by_alien_number":
                    result = await self.search_tools.search_by_alien_number(**arguments)
                elif name == "smart_detainee_search":
                    result = await self.search_tools.smart_search(**arguments)
                elif name == "bulk_search_detainees":
                    result = await self.search_tools.bulk_search(**arguments)
                elif name == "generate_search_report":
                    result = await self.search_tools.generate_report(**arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                # Track successful tool completion
                if self.comprehensive_monitor:
                    await self.comprehensive_monitor.track_tool_call(
                        session_id="default",
                        tool_name=name,
                        arguments=arguments,
                        result={"status": "success", "response": result},
                        error=None
                    )
                
                self.logger.info("Tool completed successfully", tool_name=name)
                
                return [types.TextContent(
                    type="text",
                    text=result
                )]
                
            except Exception as e:
                # Track tool errors
                if self.comprehensive_monitor:
                    await self.comprehensive_monitor.track_tool_call(
                        session_id="default",
                        tool_name=name,
                        arguments=arguments,
                        result=None,
                        error=str(e)
                    )
                
                self.logger.error("Tool execution failed", tool_name=name, error=str(e))
                error_response = {
                    "status": "error",
                    "error_message": str(e),
                    "tool_name": name
                }
                return [types.TextContent(
                    type="text",
                    text=json.dumps(error_response, indent=2)
                )]
    
    async def start(self) -> None:
        """Start the MCP server."""
        self.logger.info("Starting ICE Locator MCP Server")
        
        # Initialize telemetry and monitoring
        if self.comprehensive_monitor:
            await self.comprehensive_monitor.initialize()
            await self.comprehensive_monitor.start_monitoring({
                "server_version": self.config.server_version,
                "startup_time": datetime.now().isoformat()
            })
            self.logger.info("Comprehensive monitoring started")
        
        # Initialize components
        await self.proxy_manager.initialize()
        await self.search_engine.initialize()
        
        self.logger.info("ICE Locator MCP Server started successfully")
    
    async def stop(self) -> None:
        """Stop the MCP server and cleanup resources."""
        self.logger.info("Stopping ICE Locator MCP Server")
        
        # Cleanup components
        await self.search_engine.cleanup()
        await self.proxy_manager.cleanup()
        
        # Cleanup telemetry and monitoring
        if self.comprehensive_monitor:
            await self.comprehensive_monitor.stop_monitoring("server_shutdown")
            await self.comprehensive_monitor.cleanup()
            self.logger.info("Comprehensive monitoring cleaned up")
        
        self.logger.info("ICE Locator MCP Server stopped")


async def main() -> None:
    """Main entry point for the server."""
    
    # Setup logging
    setup_logging()
    
    # Create and start server
    server = ICELocatorServer()
    
    try:
        await server.start()
        
        # Run server with stdio transport
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ice-locator",
                    server_version="0.1.0",
                    capabilities=server.server.get_capabilities()
                )
            )
            
    except KeyboardInterrupt:
        logging.info("Received interrupt signal")
    except Exception as e:
        logging.error(f"Server error: {e}")
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())