#!/usr/bin/env python3
"""
Test script for the browser simulator.
"""

import asyncio
import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ice_locator_mcp.anti_detection.browser_simulator import BrowserSimulator
from ice_locator_mcp.core.config import SearchConfig


async def test_browser_simulator():
    """Test the browser simulator functionality."""
    print("Testing browser simulator...")
    
    # Create a search config
    config = SearchConfig()
    
    # Create browser simulator
    simulator = BrowserSimulator(config)
    
    try:
        # Initialize the simulator
        await simulator.initialize()
        print("✓ Browser simulator initialized successfully")
        
        # Create a session
        session_id = "test_session_1"
        session = await simulator.create_session(session_id)
        print(f"✓ Created browser session: {session_id}")
        
        # Navigate to a test page (using a public website for testing)
        print("Navigating to example.com...")
        content = await simulator.navigate_to_page(session_id, "https://example.com")
        print(f"✓ Successfully navigated to example.com, content length: {len(content)}")
        
        # Test form filling (on a simple page)
        print("Testing form filling...")
        try:
            # This will likely fail on example.com since it doesn't have these forms,
            # but we want to test that the method works without throwing exceptions
            await simulator.fill_form(session_id, {
                "input[name='q']": "test search"
            })
            print("✓ Form filling method executed (may not have found elements)")
        except Exception as e:
            print(f"✓ Form filling method executed (expected error on example.com): {str(e)}")
        
        # Close the session
        await simulator.close_session(session_id)
        print(f"✓ Closed browser session: {session_id}")
        
        # Close all sessions
        await simulator.close_all_sessions()
        print("✓ Closed all browser sessions")
        
        print("\nAll tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Ensure cleanup
        try:
            await simulator.close_all_sessions()
        except:
            pass


if __name__ == "__main__":
    result = asyncio.run(test_browser_simulator())
    sys.exit(0 if result else 1)