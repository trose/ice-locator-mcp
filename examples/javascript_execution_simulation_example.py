"""
Example demonstrating advanced JavaScript execution simulation.
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.browser_simulator import BrowserSimulator
from ice_locator_mcp.core.config import SearchConfig


async def main():
    """Demonstrate JavaScript execution simulation capabilities."""
    # Create a mock config
    config = SearchConfig()
    
    # Initialize browser simulator
    browser_sim = BrowserSimulator(config)
    
    try:
        # Initialize the browser
        await browser_sim.initialize()
        print("✓ Browser simulator initialized")
        
        # Create a session
        session_id = "js_demo_session"
        session = await browser_sim.create_session(session_id)
        print(f"✓ Created browser session: {session_id}")
        
        # Navigate to a test page
        await browser_sim.navigate_to_page(session_id, "https://example.com")
        print("✓ Navigated to example.com")
        
        # Example 1: Execute JavaScript with timing control
        print("\n--- JavaScript Execution with Timing Control ---")
        script = "() => { return document.title; }"
        result = await browser_sim.execute_javascript_with_timing(
            session_id, script, "page", "medium"
        )
        print(f"Page title: {result}")
        
        # Example 2: Handle client-side challenges
        print("\n--- Client-Side Challenge Handling ---")
        challenge_result = await browser_sim.handle_client_side_challenge(
            session_id, "generic", 2
        )
        print(f"Challenge handling result: {challenge_result}")
        
        # Example 3: Simulate realistic JavaScript execution patterns
        print("\n--- Realistic JavaScript Execution Patterns ---")
        scripts = [
            "() => { return window.location.href; }",
            "() => { return document.querySelectorAll('*').length; }",
            "() => { return navigator.userAgent; }"
        ]
        
        # Sequential pattern
        sequential_results = await browser_sim.simulate_realistic_js_execution_pattern(
            session_id, scripts, "sequential"
        )
        print(f"Sequential execution results: {sequential_results}")
        
        # Burst pattern
        burst_results = await browser_sim.simulate_realistic_js_execution_pattern(
            session_id, scripts, "burst"
        )
        print(f"Burst execution results: {burst_results}")
        
        print("\n✓ All JavaScript execution simulation examples completed successfully!")
        
    except Exception as e:
        print(f"Error during JavaScript execution simulation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        await browser_sim.close_all_sessions()
        print("✓ Cleaned up browser sessions")


if __name__ == "__main__":
    asyncio.run(main())