#!/usr/bin/env python3
"""
Test script to verify browser-based search with the ICE website.
"""

import asyncio
import json
from src.ice_locator_mcp.core.config import SearchConfig
from src.ice_locator_mcp.anti_detection.browser_simulator import BrowserSimulator

async def test_browser_search():
    """Test browser-based search with the ICE website."""
    print("Testing browser-based search...")
    
    # Create search configuration
    config = SearchConfig()
    
    # Create browser simulator
    browser_sim = BrowserSimulator(config)
    
    try:
        # Initialize the browser
        await browser_sim.initialize()
        print("Browser initialized successfully")
        
        # Create a session
        session_id = "test_session_1"
        
        # Navigate to the ICE website
        print("Navigating to ICE website...")
        try:
            content = await browser_sim.navigate_to_page(session_id, config.base_url)
            print(f"Successfully navigated to {config.base_url}")
            print(f"Page content length: {len(content)} characters")
            
            # Check if we got a valid page
            if "<html" in content.lower():
                print("Received valid HTML content")
            else:
                print("Warning: Content may not be valid HTML")
                
        except Exception as e:
            print(f"Navigation failed: {e}")
            return
        
        # Try to find the search page
        print("Looking for search functionality...")
        try:
            search_content = await browser_sim.navigate_to_page(session_id, f"{config.base_url}/search")
            print("Successfully accessed search page")
        except Exception as e:
            print(f"Could not access search page directly: {e}")
            # This is expected since the website might redirect or require specific navigation
        
        # Close the session
        await browser_sim.close_session(session_id)
        print("Test session completed")
        
    except Exception as e:
        print(f"Browser test failed: {e}")
    finally:
        # Clean up
        await browser_sim.close_all_sessions()
        print("Browser simulator cleaned up")

if __name__ == "__main__":
    asyncio.run(test_browser_search())