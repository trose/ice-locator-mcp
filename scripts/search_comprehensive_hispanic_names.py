#!/usr/bin/env python3
"""
Search comprehensive list of Hispanic names using MCP server.
Output CSV with location and status information.
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

def load_names_from_file(filename):
    """Load names from the comprehensive list file."""
    names = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    names.append(line)
    except FileNotFoundError:
        print(f"Error: {filename} not found")
        return []
    return names

async def search_comprehensive_names():
    """Search comprehensive list of Hispanic names."""
    print("Searching comprehensive Hispanic names list...")
    
    # Set environment variables to disable monitoring
    os.environ["ICE_LOCATOR_ANALYTICS_ENABLED"] = "false"
    os.environ["ICE_LOCATOR_MCPCAT_ENABLED"] = "false"
    os.environ["ICE_LOCATOR_PROXY_ENABLED"] = "false"
    
    # Load the comprehensive list
    print("Loading comprehensive names list...")
    full_names = load_names_from_file('comprehensive_hispanic_full_names.txt')
    
    if not full_names:
        print("No names found in the comprehensive list!")
        return
    
    print(f"Loaded {len(full_names):,} names for searching")
    
    # Search ALL names in the comprehensive list
    sample_names = full_names
    sample_size = len(full_names)
    
    print(f"Searching ALL {sample_size:,} names in the comprehensive list")
    
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
        
        print("6. Starting comprehensive search...")
        
        # Create CSV file for results
        csv_file = "comprehensive_hispanic_search_results.csv"
        headers = [
            "search_number", "full_name", "first_name", "last_name", 
            "date_of_birth", "country_of_birth", "search_status", 
            "results_count", "location_found", "facility_name", 
            "detention_status", "search_timestamp", "processing_time_ms",
            "error_message", "user_guidance"
        ]
        
        results = []
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            
            for i, full_name in enumerate(sample_names, 1):
                print(f"\n--- Search {i}/{sample_size}: {full_name} ---")
                start_time = datetime.now()
                
                # Parse the name
                parts = full_name.strip().split()
                if len(parts) < 2:
                    print(f"Skipping invalid name: {full_name}")
                    continue
                
                first_name = parts[0]
                last_name = " ".join(parts[1:])
                
                # Generate realistic date of birth and country of birth
                age = random.randint(18, 65)
                current_year = datetime.now().year
                birth_year = current_year - age
                birth_month = random.randint(1, 12)
                birth_day = random.randint(1, 28)
                date_of_birth = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
                
                countries = ["Mexico", "Guatemala", "El Salvador", "Honduras", "Nicaragua", 
                           "Costa Rica", "Panama", "Colombia", "Venezuela", "Ecuador",
                           "Peru", "Bolivia", "Chile", "Argentina", "Uruguay", "Paraguay"]
                country_of_birth = random.choice(countries)
                
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
                        results_list = result_data.get("results", [])
                        results_count = len(results_list)
                        
                        # Extract location and facility information
                        location_found = ""
                        facility_name = ""
                        detention_status = ""
                        
                        if results_list:
                            # If results found, extract location info
                            first_result = results_list[0]
                            location_found = first_result.get("location", "")
                            facility_name = first_result.get("facility_name", "")
                            detention_status = first_result.get("status", "")
                        
                        error_message = ""
                        user_guidance = ""
                        
                        if status == "error":
                            error_message = result_data.get("search_metadata", {}).get("error_message", "")
                            guidance_data = result_data.get("user_guidance", {})
                            if guidance_data:
                                next_steps = guidance_data.get("next_steps", [])
                                user_guidance = "; ".join(next_steps)
                        
                        print(f"  ✅ Status: {status}, Results: {results_count}")
                        if location_found:
                            print(f"  📍 Location: {location_found}")
                        if facility_name:
                            print(f"  🏢 Facility: {facility_name}")
                        
                        # Write to CSV
                        writer.writerow([
                            i, full_name, first_name, last_name, date_of_birth, country_of_birth,
                            status, results_count, location_found, facility_name, detention_status,
                            datetime.now().isoformat(), f"{processing_time:.2f}",
                            error_message, user_guidance
                        ])
                        
                        results.append({
                            "search_number": i,
                            "name": full_name,
                            "status": status,
                            "results_count": results_count,
                            "location_found": location_found,
                            "facility_name": facility_name,
                            "detention_status": detention_status,
                            "processing_time_ms": processing_time
                        })
                        
                    except json.JSONDecodeError:
                        print(f"  ✅ Raw result: {result[:100]}...")
                        writer.writerow([
                            i, full_name, first_name, last_name, date_of_birth, country_of_birth,
                            "raw_result", 0, "", "", "", datetime.now().isoformat(), 
                            f"{processing_time:.2f}", "JSON decode error", ""
                        ])
                        
                        results.append({
                            "search_number": i,
                            "name": full_name,
                            "status": "raw_result",
                            "results_count": 0,
                            "location_found": "",
                            "facility_name": "",
                            "detention_status": "",
                            "processing_time_ms": processing_time
                        })
                    
                except Exception as e:
                    end_time = datetime.now()
                    processing_time = (end_time - start_time).total_seconds() * 1000
                    
                    print(f"  ❌ Error: {e}")
                    writer.writerow([
                        i, full_name, first_name, last_name, date_of_birth, country_of_birth,
                        "error", 0, "", "", "", datetime.now().isoformat(), 
                        f"{processing_time:.2f}", str(e), ""
                    ])
                    
                    results.append({
                        "search_number": i,
                        "name": full_name,
                        "status": "error",
                        "results_count": 0,
                        "location_found": "",
                        "facility_name": "",
                        "detention_status": "",
                        "processing_time_ms": processing_time
                    })
        
        # Summary
        print(f"\n--- Search Summary ---")
        print(f"Total searches: {len(results)}")
        success_count = len([r for r in results if r["status"] not in ["error", "raw_result"]])
        error_count = len([r for r in results if r["status"] == "error"])
        results_found = len([r for r in results if r["results_count"] > 0])
        avg_processing_time = sum(r["processing_time_ms"] for r in results) / len(results)
        
        print(f"Successful searches: {success_count}")
        print(f"Errors: {error_count}")
        print(f"Searches with results: {results_found}")
        print(f"Average processing time: {avg_processing_time:.2f}ms")
        
        # Save detailed results
        with open("comprehensive_search_detailed_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Comprehensive search completed!")
        print(f"📊 Results saved to: {csv_file}")
        print(f"📋 Detailed results saved to: comprehensive_search_detailed_results.json")
        
        # Cleanup
        await search_engine.cleanup()
        await proxy_manager.cleanup()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(search_comprehensive_names())
