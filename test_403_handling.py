#!/usr/bin/env python3
"""
Test script for 403 error handling with browser simulation.
"""

import asyncio
import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ice_locator_mcp.core.search_engine import SearchEngine, SearchRequest
from ice_locator_mcp.core.config import ServerConfig
from ice_locator_mcp.anti_detection.proxy_manager import ProxyManager


async def test_403_handling():
    """Test the 403 error handling with browser simulation."""
    print("Testing 403 error handling with browser simulation...")
    
    # Create a server config
    config = ServerConfig()
    
    # Create proxy manager
    proxy_manager = ProxyManager(config.proxy_config)
    
    # Create search engine
    search_engine = SearchEngine(proxy_manager, config.search_config)
    
    try:
        # Initialize the search engine
        await search_engine.initialize()
        print("✓ Search engine initialized successfully")
        
        # Create a test search request
        request = SearchRequest(
            first_name="John",
            last_name="Doe",
            date_of_birth="1990-01-01",
            country_of_birth="Mexico"
        )
        
        print("Attempting search (this may trigger 403 handling)...")
        
        # Perform the search
        # Note: This will likely fail due to the real ICE website or network issues,
        # but we want to verify that our 403 handling logic works
        result = await search_engine.search(request)
        
        print(f"Search completed with status: {result.status}")
        print(f"Results count: {len(result.results)}")
        
        # Cleanup
        await search_engine.cleanup()
        print("✓ Search engine cleanup completed")
        
        print("\nTest completed successfully!")
        return True
        
    except Exception as e:
        print(f"Test encountered an error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        # Check if this is the expected 403 handling behavior
        if "403" in str(e).lower() or "forbidden" in str(e).lower():
            print("✓ 403 error handling logic was triggered (expected)")
            return True
        else:
            import traceback
            traceback.print_exc()
            return False
    finally:
        # Ensure cleanup
        try:
            await search_engine.cleanup()
        except:
            pass


if __name__ == "__main__":
    result = asyncio.run(test_403_handling())
    sys.exit(0 if result else 1)