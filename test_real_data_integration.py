#!/usr/bin/env python3
"""
Test script to verify real data integration works correctly.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ice_locator_mcp.core.search_engine import SearchEngine, SearchRequest
from ice_locator_mcp.core.config import SearchConfig, ProxyConfig as ConfigProxyConfig
from ice_locator_mcp.anti_detection.proxy_manager import ProxyManager


async def test_real_data_integration():
    """Test real data integration with the ICE website."""
    print("Testing real data integration...")
    
    # Create search configuration
    config = SearchConfig(
        base_url="https://locator.ice.gov",
        timeout=30,
        requests_per_minute=10,
        burst_allowance=5
    )
    
    # Create proxy configuration
    proxy_config = ConfigProxyConfig(
        enabled=True,
        rotation_interval=300,
        max_requests_per_proxy=10
    )
    
    # Initialize proxy manager
    proxy_manager = ProxyManager(proxy_config)
    await proxy_manager.initialize()
    
    try:
        # Initialize search engine
        search_engine = SearchEngine(proxy_manager, config)
        await search_engine.initialize()
        
        # Create a test search request (using a common name that might have results)
        search_request = SearchRequest(
            first_name="John",
            last_name="Doe"
        )
        
        print("Performing search for John Doe...")
        result = await search_engine.search(search_request)
        
        print(f"Search completed with status: {result.status}")
        print(f"Number of results: {len(result.results)}")
        print(f"Search metadata: {result.search_metadata}")
        
        if result.results:
            print("\nFirst result:")
            first_result = result.results[0]
            print(f"  Name: {first_result.name}")
            print(f"  Alien Number: {first_result.alien_number}")
            print(f"  Date of Birth: {first_result.date_of_birth}")
            print(f"  Country of Birth: {first_result.country_of_birth}")
            print(f"  Facility: {first_result.facility_name}")
            print(f"  Location: {first_result.facility_location}")
            print(f"  Status: {first_result.custody_status}")
        else:
            print("No results found (this is expected for test names)")
            
            # Check if there was an error and provide more details
            if result.status == "error":
                error_msg = result.search_metadata.get("error_message", "Unknown error")
                print(f"Error details: {error_msg}")
        
        print("\nReal data integration test completed!")
        
    except Exception as e:
        print(f"Error during real data integration test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        await search_engine.cleanup()
        await proxy_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(test_real_data_integration())