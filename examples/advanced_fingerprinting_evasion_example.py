"""
Example demonstrating advanced browser fingerprinting evasion techniques.
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.browser_simulator import BrowserSimulator
from ice_locator_mcp.core.config import SearchConfig


async def main():
    """Demonstrate advanced browser fingerprinting evasion capabilities."""
    # Create a mock config
    config = SearchConfig()
    
    # Initialize browser simulator
    browser_sim = BrowserSimulator(config)
    
    try:
        # Initialize the browser
        await browser_sim.initialize()
        print("✓ Browser simulator initialized")
        
        # Create a session
        session_id = "fingerprint_demo_session"
        session = await browser_sim.create_session(session_id)
        print(f"✓ Created browser session: {session_id}")
        
        # Navigate to a test page
        await browser_sim.navigate_to_page(session_id, "https://example.com")
        print("✓ Navigated to example.com")
        
        # Execute JavaScript to demonstrate fingerprinting evasion
        print("\n--- Demonstrating Fingerprinting Evasion ---")
        
        # Check hardware concurrency spoofing
        hardware_concurrency = await browser_sim.execute_javascript_with_timing(
            session_id, 
            "() => navigator.hardwareConcurrency", 
            "page", 
            "simple"
        )
        print(f"Hardware Concurrency: {hardware_concurrency}")
        
        # Check device memory spoofing
        device_memory = await browser_sim.execute_javascript_with_timing(
            session_id, 
            "() => navigator.deviceMemory", 
            "page", 
            "simple"
        )
        print(f"Device Memory: {device_memory} GB")
        
        # Check WebGL fingerprinting protection
        webgl_vendor = await browser_sim.execute_javascript_with_timing(
            session_id, 
            """() => {
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl');
                if (gl) {
                    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                    if (debugInfo) {
                        return gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
                    }
                }
                return 'Not available';
            }""", 
            "page", 
            "medium"
        )
        print(f"WebGL Vendor: {webgl_vendor}")
        
        # Check canvas fingerprinting protection
        canvas_test = await browser_sim.execute_javascript_with_timing(
            session_id, 
            """() => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                if (ctx) {
                    ctx.fillText('Hello World', 10, 10);
                    return canvas.toDataURL().substring(0, 100) + '...';
                }
                return 'Not available';
            }""", 
            "page", 
            "medium"
        )
        print(f"Canvas Data URL (truncated): {canvas_test}")
        
        # Check connection information spoofing
        connection_info = await browser_sim.execute_javascript_with_timing(
            session_id, 
            """() => {
                if (navigator.connection) {
                    return {
                        downlink: navigator.connection.downlink,
                        effectiveType: navigator.connection.effectiveType,
                        rtt: navigator.connection.rtt
                    };
                }
                return 'Not available';
            }""", 
            "page", 
            "simple"
        )
        print(f"Connection Info: {connection_info}")
        
        # Check timezone spoofing
        timezone = await browser_sim.execute_javascript_with_timing(
            session_id, 
            """() => {
                return Intl.DateTimeFormat().resolvedOptions().timeZone;
            }""", 
            "page", 
            "simple"
        )
        print(f"Timezone: {timezone}")
        
        print("\n✓ All advanced fingerprinting evasion examples completed successfully!")
        
    except Exception as e:
        print(f"Error during fingerprinting evasion demonstration: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        await browser_sim.close_all_sessions()
        print("✓ Cleaned up browser sessions")


if __name__ == "__main__":
    asyncio.run(main())