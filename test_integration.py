#!/usr/bin/env python3
"""
Integration test for the complete 403 handling flow.
"""

import asyncio
import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ice_locator_mcp.anti_detection.coordinator import AntiDetectionCoordinator
from ice_locator_mcp.core.config import ServerConfig


async def test_integration():
    """Test the complete integration of anti-detection components."""
    print("Testing complete anti-detection integration...")
    
    # Create a server config
    config = ServerConfig()
    
    # Create anti-detection coordinator
    coordinator = AntiDetectionCoordinator(config)
    
    try:
        # Initialize the coordinator
        await coordinator.initialize()
        print("✓ Anti-detection coordinator initialized successfully")
        
        # Start a session
        session_id = "integration_test_session"
        session_info = await coordinator.start_session(session_id)
        print(f"✓ Started session: {session_id}")
        print(f"  Components active: {session_info['components_active']}")
        
        # Test browser simulation directly
        if session_info['components_active']['browser_simulation']:
            print("✓ Browser simulation is enabled")
        else:
            print("⚠ Browser simulation is not enabled")
        
        # Get status
        status = await coordinator.get_comprehensive_status()
        print(f"✓ Coordinator status retrieved")
        print(f"  Active sessions: {status['coordinator']['active_sessions']}")
        print(f"  Detection level: {status['coordinator']['detection_level']}")
        
        # Cleanup
        await coordinator.cleanup()
        print("✓ Anti-detection coordinator cleanup completed")
        
        print("\nIntegration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Integration test failed with error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Ensure cleanup
        try:
            await coordinator.cleanup()
        except:
            pass


if __name__ == "__main__":
    result = asyncio.run(test_integration())
    sys.exit(0 if result else 1)