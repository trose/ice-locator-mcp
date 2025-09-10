#!/usr/bin/env python3
"""
Test 10 names with MCP server using direct search functionality.
"""

import asyncio
import json
import os
import sys
import csv
from datetime import datetime
import random

# Add the src directory to the path
sys.path.insert(0, '/Users/trose/src/locator-mcp/src')

async def test_10_names_mcp():
    """Test 10 names with MCP server functionality."""
    print("Testing 10 names with MCP server...")
    
    # Set environment variables to disable monitoring
    os.environ["ICE_LOCATOR_ANALYTICS_ENABLED"] = "false"
    os.environ["ICE_LOCATOR_MCPCAT_ENABLED"] = "false"
    os.environ["ICE_LOCATOR_PROXY_ENABLED"] = "false"
    
    # 10 diverse Hispanic names for testing
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
    
    try:
        # Import the search components
        from ice_locator_mcp.core.config import ServerConfig
        from ice_locator_mcp.anti_detection.proxy_manager import ProxyManager
        from ice_locator_mcp.core.search_engine import SearchEngine
        from ice_locator_mcp.tools.search_tools import SearchTools
        
        print("1. Creating configuration...")
        config = ServerConfig()
        
        print("2. Creating proxy manager...")
        proxy_manager = ProxyManager(config.proxy_config)
        
        print("3. Creating search engine...")
        search_engine = SearchEngine(
            proxy_manager=proxy_manager,
            config=config.search_config
        )
        
        print("4. Initializing search engine...")
        await search_engine.initialize()
        
        print("5. Creating search tools...")
        search_tools = SearchTools(search_engine)
        
        print("6. Testing search functionality with 10 names...")
        
        # Create CSV file for results
        csv_file = "mcp_10_names_test_results.csv"
        headers = [
            "test_number", "first_name", "last_name", "date_of_birth", "country_of_birth",
            "search_status", "search_result", "search_timestamp", "processing_time_ms"
        ]
        
        results = []
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            
            for i, (first_name, last_name, date_of_birth, country_of_birth) in enumerate(test_names, 1):
                print(f"\n--- Test {i}/10: {first_name} {last_name} ---")
                start_time = datetime.now()
                
                try:
                    # Perform the search
                    result = await search_tools.search_by_name(
                        first_name=first_name,
                        last_name=last_name,
                        date_of_birth=date_of_birth,
                        country_of_birth=country_of_birth,
                        fuzzy_search=True
                    )
                    
                    end_time = datetime.now()
                    processing_time = (end_time - start_time).total_seconds() * 1000
                    
                    # Parse the result
                    try:
                        result_data = json.loads(result)
                        status = result_data.get("status", "unknown")
                        error_message = result_data.get("search_metadata", {}).get("error_message", "")
                        
                        print(f"  ✅ Status: {status}")
                        if error_message:
                            print(f"  📝 Message: {error_message[:100]}...")
                        
                        # Write to CSV
                        writer.writerow([
                            i, first_name, last_name, date_of_birth, country_of_birth,
                            status, result, datetime.now().isoformat(), f"{processing_time:.2f}"
                        ])
                        
                        results.append({
                            "test_number": i,
                            "name": f"{first_name} {last_name}",
                            "status": status,
                            "processing_time_ms": processing_time,
                            "result": result_data
                        })
                        
                    except json.JSONDecodeError:
                        print(f"  ✅ Raw result: {result[:100]}...")
                        writer.writerow([
                            i, first_name, last_name, date_of_birth, country_of_birth,
                            "raw_result", result, datetime.now().isoformat(), f"{processing_time:.2f}"
                        ])
                        
                        results.append({
                            "test_number": i,
                            "name": f"{first_name} {last_name}",
                            "status": "raw_result",
                            "processing_time_ms": processing_time,
                            "result": result
                        })
                    
                except Exception as e:
                    end_time = datetime.now()
                    processing_time = (end_time - start_time).total_seconds() * 1000
                    
                    print(f"  ❌ Error: {e}")
                    writer.writerow([
                        i, first_name, last_name, date_of_birth, country_of_birth,
                        "error", f"ERROR: {str(e)}", datetime.now().isoformat(), f"{processing_time:.2f}"
                    ])
                    
                    results.append({
                        "test_number": i,
                        "name": f"{first_name} {last_name}",
                        "status": "error",
                        "processing_time_ms": processing_time,
                        "result": str(e)
                    })
        
        # Summary
        print(f"\n--- Test Summary ---")
        print(f"Total searches: {len(results)}")
        success_count = len([r for r in results if r["status"] not in ["error", "raw_result"]])
        error_count = len([r for r in results if r["status"] == "error"])
        avg_processing_time = sum(r["processing_time_ms"] for r in results) / len(results)
        
        print(f"Successful searches: {success_count}")
        print(f"Errors: {error_count}")
        print(f"Average processing time: {avg_processing_time:.2f}ms")
        
        # Save detailed results
        with open("mcp_10_names_detailed_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ MCP 10 names test completed!")
        print(f"📊 Results saved to: {csv_file}")
        print(f"📋 Detailed results saved to: mcp_10_names_detailed_results.json")
        
        # Cleanup
        await search_engine.cleanup()
        await proxy_manager.cleanup()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_10_names_mcp())

