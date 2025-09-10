#!/usr/bin/env python3
"""
Test MCP integration on main branch with sample names.
"""

import asyncio
import json
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_main_branch():
    """Test MCP integration on main branch."""
    print("Testing MCP integration on main branch...")
    
    # Sample Hispanic names for testing
    test_names = [
        ("JOSE", "GARCIA", "1980-01-01", "Mexico"),
        ("MARIA", "RODRIGUEZ", "1985-05-15", "Guatemala"),
        ("CARLOS", "MARTINEZ", "1990-03-20", "El Salvador"),
        ("ANA", "HERNANDEZ", "1988-07-10", "Honduras"),
        ("LUIS", "LOPEZ", "1982-11-25", "Nicaragua"),
        ("SOFIA", "GONZALEZ", "1995-09-12", "Costa Rica"),
        ("DIEGO", "PEREZ", "1987-04-08", "Panama"),
        ("VALENTINA", "SANCHEZ", "1992-12-03", "Colombia"),
        ("SEBASTIAN", "RAMIREZ", "1989-06-18", "Venezuela"),
        ("ISABELLA", "TORRES", "1993-08-30", "Ecuador")
    ]
    
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
                print("Session created successfully!")
                
                # Test 1: List tools
                print("\n--- Test 1: List tools ---")
                try:
                    tools = await session.list_tools()
                    print(f"✅ Tools listed successfully: {len(tools)} tools found")
                    for tool in tools:
                        print(f"  - {tool.name}: {tool.description}")
                except Exception as e:
                    print(f"❌ Error listing tools: {e}")
                    return
                
                # Test 2: Search with each name
                print(f"\n--- Test 2: Search with {len(test_names)} names ---")
                results = []
                
                for i, (first_name, last_name, date_of_birth, country_of_birth) in enumerate(test_names, 1):
                    print(f"\n{i}/10: Searching for {first_name} {last_name}...")
                    
                    try:
                        result = await session.call_tool(
                            name="search_detainee_by_name",
                            arguments={
                                "first_name": first_name,
                                "last_name": last_name,
                                "date_of_birth": date_of_birth,
                                "country_of_birth": country_of_birth,
                                "fuzzy_search": True
                            }
                        )
                        
                        # Parse result
                        try:
                            result_data = json.loads(result.content[0].text)
                            status = result_data.get("status", "unknown")
                            print(f"  ✅ Result: {status}")
                            
                            results.append({
                                "name": f"{first_name} {last_name}",
                                "status": status,
                                "result": result_data
                            })
                            
                        except json.JSONDecodeError:
                            print(f"  ✅ Result: {result.content[0].text[:100]}...")
                            results.append({
                                "name": f"{first_name} {last_name}",
                                "status": "raw_result",
                                "result": result.content[0].text
                            })
                        
                    except Exception as e:
                        print(f"  ❌ Error: {e}")
                        results.append({
                            "name": f"{first_name} {last_name}",
                            "status": "error",
                            "result": str(e)
                        })
                
                # Summary
                print(f"\n--- Test Summary ---")
                print(f"Total searches: {len(results)}")
                success_count = len([r for r in results if r["status"] not in ["error", "raw_result"]])
                print(f"Successful searches: {success_count}")
                error_count = len([r for r in results if r["status"] == "error"])
                print(f"Errors: {error_count}")
                
                # Save results
                with open("mcp_main_branch_test_results.json", "w") as f:
                    json.dump(results, f, indent=2)
                print(f"Results saved to mcp_main_branch_test_results.json")
                
    except Exception as e:
        print(f"Connection error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_main_branch())

