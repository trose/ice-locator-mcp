#!/usr/bin/env python3
"""
Demonstrate how to use the ICE Locator MCP Server for detainee searches.

This script shows how to interact with the MCP server to search for detainee information.
"""

import asyncio
import json
import subprocess
import sys
import time
from typing import Dict, Any, List

def start_mcp_server() -> subprocess.Popen:
    """
    Start the ICE Locator MCP Server.
    
    Returns:
        subprocess.Popen: The server process
    """
    print("Starting ICE Locator MCP Server...")
    
    # Start the server using the configuration in mcp.json
    server_process = subprocess.Popen([
        sys.executable, "-m", "ice_locator_mcp"
    ], cwd="/Users/trose/src/locator-mcp", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Give the server time to start
    time.sleep(3)
    
    print("ICE Locator MCP Server started")
    return server_process

def stop_mcp_server(server_process: subprocess.Popen):
    """
    Stop the MCP server process.
    
    Args:
        server_process: The server process to stop
    """
    print("Stopping ICE Locator MCP Server...")
    server_process.terminate()
    try:
        server_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_process.kill()
    print("ICE Locator MCP Server stopped")

async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call an MCP tool using the server.
    
    In a real implementation, this would use the MCP client library to communicate
    with the server. For demonstration purposes, we're simulating the calls.
    
    Args:
        tool_name: Name of the tool to call
        arguments: Arguments for the tool
        
    Returns:
        Dict containing the tool response
    """
    print(f"Calling MCP tool: {tool_name}")
    print(f"Arguments: {json.dumps(arguments, indent=2)}")
    
    # Simulate network delay
    await asyncio.sleep(1)
    
    # Simulate different tool responses
    if tool_name == "search_detainee_by_name":
        # Simulate a successful search response
        response = {
            "status": "found",
            "results": [{
                "name": f"{arguments['first_name']} {arguments.get('middle_name', '')} {arguments['last_name']}".strip(),
                "alien_number": "A123456789",
                "date_of_birth": arguments.get('date_of_birth', '1985-06-15'),
                "country_of_birth": arguments.get('country_of_birth', 'Mexico'),
                "facility_name": "Alligator Alcatraz Detention Center",
                "facility_location": "Everglades, FL",
                "custody_status": "In Detention",
                "last_updated": "2025-08-28T15:30:45Z"
            }]
        }
    elif tool_name == "search_detainee_by_alien_number":
        # Simulate a search by alien number
        response = {
            "status": "found",
            "results": [{
                "name": "JOSE MARIA GONZALEZ",
                "alien_number": arguments['alien_number'],
                "date_of_birth": "1980-03-22",
                "country_of_birth": "Mexico",
                "facility_name": "Alligator Alcatraz Detention Center",
                "facility_location": "Everglades, FL",
                "custody_status": "Awaiting Hearing",
                "last_updated": "2025-08-28T14:22:10Z"
            }]
        }
    elif tool_name == "bulk_search_detainees":
        # Simulate bulk search response
        results = []
        for i, request in enumerate(arguments['search_requests']):
            results.append({
                "status": "found",
                "results": [{
                    "name": f"{request['first_name']} {request['last_name']}",
                    "alien_number": f"A{100000000 + i}",
                    "date_of_birth": request.get('date_of_birth', '1990-01-01'),
                    "country_of_birth": request.get('country_of_birth', 'Mexico'),
                    "facility_name": "Alligator Alcatraz Detention Center",
                    "facility_location": "Everglades, FL",
                    "custody_status": "In Detention",
                    "last_updated": "2025-08-28T16:45:30Z"
                }]
            })
        
        response = {
            "status": "completed",
            "total_searches": len(arguments['search_requests']),
            "successful_searches": len(arguments['search_requests']),
            "failed_searches": 0,
            "results": results,
            "processing_time_ms": 1250
        }
    elif tool_name == "smart_detainee_search":
        # Simulate smart search response
        response = {
            "status": "found",
            "results": [{
                "name": "CARLOS ALBERTO HERNANDEZ",
                "alien_number": "A987654321",
                "date_of_birth": "1975-11-08",
                "country_of_birth": "Guatemala",
                "facility_name": "Miami Processing Center",
                "facility_location": "Miami, FL",
                "custody_status": "Awaiting Deportation",
                "last_updated": "2025-08-28T12:15:22Z",
                "confidence_score": 0.95
            }]
        }
    else:
        response = {
            "status": "error",
            "error_message": f"Unknown tool: {tool_name}"
        }
    
    print(f"Response: {json.dumps(response, indent=2)}")
    return response

async def demonstrate_single_search():
    """Demonstrate a single detainee search."""
    print("\n=== Single Detainee Search Demo ===")
    
    # Example search by name
    search_args = {
        "first_name": "JOSE",
        "last_name": "GONZALEZ",
        "date_of_birth": "1985-06-15",
        "country_of_birth": "Mexico",
        "middle_name": "MARIA",
        "language": "en",
        "fuzzy_search": True
    }
    
    result = await call_mcp_tool("search_detainee_by_name", search_args)
    return result

async def demonstrate_alien_number_search():
    """Demonstrate search by alien number."""
    print("\n=== Alien Number Search Demo ===")
    
    search_args = {
        "alien_number": "A123456789",
        "language": "en"
    }
    
    result = await call_mcp_tool("search_detainee_by_alien_number", search_args)
    return result

async def demonstrate_smart_search():
    """Demonstrate smart natural language search."""
    print("\n=== Smart Search Demo ===")
    
    search_args = {
        "query": "Find Jose Maria Gonzalez from Mexico born in 1985",
        "context": "Family member looking for information",
        "suggest_corrections": True,
        "language": "en"
    }
    
    result = await call_mcp_tool("smart_detainee_search", search_args)
    return result

async def demonstrate_bulk_search():
    """Demonstrate bulk search of multiple detainees."""
    print("\n=== Bulk Search Demo ===")
    
    search_requests = [
        {
            "first_name": "JOSE",
            "last_name": "GONZALEZ",
            "date_of_birth": "1985-06-15",
            "country_of_birth": "Mexico"
        },
        {
            "first_name": "MARIA",
            "last_name": "RODRIGUEZ",
            "date_of_birth": "1990-03-22",
            "country_of_birth": "Guatemala"
        },
        {
            "first_name": "CARLOS",
            "last_name": "HERNANDEZ",
            "date_of_birth": "1978-11-08",
            "country_of_birth": "El Salvador"
        }
    ]
    
    search_args = {
        "search_requests": search_requests,
        "max_concurrent": 3,
        "continue_on_error": True
    }
    
    result = await call_mcp_tool("bulk_search_detainees", search_args)
    return result

async def demonstrate_report_generation():
    """Demonstrate report generation."""
    print("\n=== Report Generation Demo ===")
    
    # This would typically be called after a search to generate a report
    report_args = {
        "search_criteria": {
            "first_name": "JOSE",
            "last_name": "GONZALEZ",
            "date_of_birth": "1985-06-15",
            "country_of_birth": "Mexico"
        },
        "results": [{
            "status": "found",
            "results": [{
                "name": "JOSE MARIA GONZALEZ",
                "alien_number": "A123456789",
                "date_of_birth": "1985-06-15",
                "country_of_birth": "Mexico",
                "facility_name": "Alligator Alcatraz Detention Center",
                "facility_location": "Everglades, FL",
                "custody_status": "In Detention",
                "last_updated": "2025-08-28T15:30:45Z"
            }]
        }],
        "report_type": "legal",
        "format": "markdown"
    }
    
    print("Report generation would create a detailed report based on search results")
    print("This could be used for legal proceedings or family communication")
    return {"status": "success", "message": "Report generated successfully"}

async def main():
    """Main demonstration function."""
    print("ICE Locator MCP Server Usage Demonstration")
    print("=" * 50)
    
    # In a real implementation, we would start the server:
    # server_process = start_mcp_server()
    
    try:
        # Demonstrate different types of searches
        await demonstrate_single_search()
        await demonstrate_alien_number_search()
        await demonstrate_smart_search()
        await demonstrate_bulk_search()
        await demonstrate_report_generation()
        
        print("\n=== Demonstration Complete ===")
        print("The MCP server provides several tools for searching detainee information:")
        print("1. search_detainee_by_name - Search by personal details")
        print("2. search_detainee_by_alien_number - Search by alien registration number")
        print("3. smart_detainee_search - Natural language search")
        print("4. bulk_search_detainees - Search multiple detainees simultaneously")
        print("5. generate_search_report - Create detailed reports for legal/family use")
        
    except Exception as e:
        print(f"Error during demonstration: {e}")
    finally:
        # In a real implementation, we would stop the server:
        # stop_mcp_server(server_process)
        pass

if __name__ == "__main__":
    asyncio.run(main())