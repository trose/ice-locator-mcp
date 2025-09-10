#!/usr/bin/env python3
"""
Test the search functionality directly without MCP protocol.
"""

import asyncio
import json
import os
import sys
import csv
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, '/Users/trose/src/locator-mcp/src')

async def test_direct_search():
    """Test search functionality directly."""
    print("Testing search functionality directly...")
    
    # Set environment variables to disable monitoring
    os.environ["ICE_LOCATOR_ANALYTICS_ENABLED"] = "false"
    os.environ["ICE_LOCATOR_MCPCAT_ENABLED"] = "false"
    os.environ["ICE_LOCATOR_PROXY_ENABLED"] = "false"
    
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
        
        print("6. Testing search functionality...")
        
        # Test search with a sample name
        result = await search_tools.search_by_name(
            first_name="JOSE",
            last_name="GARCIA",
            date_of_birth="1980-01-01",
            country_of_birth="Mexico",
            fuzzy_search=True
        )
        
        print(f"Search result: {result}")
        
        # Test with 10 Hispanic names
        print("\n7. Testing with 10 Hispanic names...")
        
        # Read the first 10 names from the file
        names_file = "/Users/trose/src/locator-mcp/hispanic_names_data/organized/hispanic_full_names_huge.txt"
        names = []
        
        try:
            with open(names_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        names.append(line)
                        if len(names) >= 10:
                            break
        except FileNotFoundError:
            print(f"Error: File {names_file} not found.")
            return
        
        print(f"Found {len(names)} names to test:")
        for i, name in enumerate(names, 1):
            print(f"  {i}. {name}")
        
        # Create CSV file for results
        csv_file = "hispanic_names_direct_test_results.csv"
        headers = [
            "full_name", "first_name", "last_name", "date_of_birth", "country_of_birth",
            "search_result", "search_timestamp"
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            
            for i, name in enumerate(names, 1):
                print(f"\n--- Testing name {i}/10: {name} ---")
                
                # Parse the name
                parts = name.strip().split()
                if len(parts) < 2:
                    print(f"Skipping invalid name: {name}")
                    continue
                
                first_name = parts[0]
                last_name = " ".join(parts[1:])
                
                # Generate realistic date of birth and country of birth
                import random
                age = random.randint(18, 65)
                current_year = datetime.now().year
                birth_year = current_year - age
                birth_month = random.randint(1, 12)
                birth_day = 15
                date_of_birth = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
                
                countries = ["Mexico", "Guatemala", "El Salvador", "Honduras", "Nicaragua", 
                           "Costa Rica", "Panama", "Colombia", "Venezuela", "Ecuador"]
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
                    
                    # Parse the result
                    try:
                        result_data = json.loads(result)
                        status = result_data.get("status", "unknown")
                        print(f"  Result: {status}")
                    except json.JSONDecodeError:
                        print(f"  Result: {result[:100]}...")
                    
                    # Write to CSV
                    writer.writerow([
                        name, first_name, last_name, date_of_birth, country_of_birth,
                        result, datetime.now().isoformat()
                    ])
                    
                except Exception as e:
                    print(f"  Error: {e}")
                    writer.writerow([
                        name, first_name, last_name, date_of_birth, country_of_birth,
                        f"ERROR: {str(e)}", datetime.now().isoformat()
                    ])
        
        print(f"\n✅ Direct search test completed! Results saved to {csv_file}")
        
        # Cleanup
        await search_engine.cleanup()
        await proxy_manager.cleanup()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct_search())

