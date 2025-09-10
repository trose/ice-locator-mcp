#!/usr/bin/env python3
"""
Test individual server components to isolate the issue.
"""

import asyncio
import os
import sys

# Add the src directory to the path
sys.path.insert(0, '/Users/trose/src/locator-mcp/src')

async def test_components():
    """Test individual server components."""
    print("Testing server components...")
    
    try:
        # Test 1: Import all modules
        print("1. Testing imports...")
        from ice_locator_mcp.core.config import ServerConfig
        from ice_locator_mcp.anti_detection.proxy_manager import ProxyManager
        from ice_locator_mcp.core.search_engine import SearchEngine
        from ice_locator_mcp.tools.search_tools import SearchTools
        from ice_locator_mcp.server import ICELocatorServer
        print("   ✓ All imports successful")
        
        # Test 2: Create configuration
        print("2. Testing configuration...")
        config = ServerConfig()
        print("   ✓ Configuration created")
        
        # Test 3: Create proxy manager
        print("3. Testing proxy manager...")
        proxy_manager = ProxyManager(config.proxy_config)
        print("   ✓ Proxy manager created")
        
        # Test 4: Create search engine
        print("4. Testing search engine...")
        search_engine = SearchEngine(
            proxy_manager=proxy_manager,
            config=config.search_config
        )
        print("   ✓ Search engine created")
        
        # Test 5: Initialize search engine
        print("5. Testing search engine initialization...")
        await search_engine.initialize()
        print("   ✓ Search engine initialized")
        
        # Test 6: Create search tools
        print("6. Testing search tools...")
        search_tools = SearchTools(search_engine)
        print("   ✓ Search tools created")
        
        # Test 7: Create server
        print("7. Testing server creation...")
        server = ICELocatorServer(config)
        print("   ✓ Server created")
        
        # Test 8: Start server
        print("8. Testing server start...")
        await server.start()
        print("   ✓ Server started")
        
        # Test 9: Stop server
        print("9. Testing server stop...")
        await server.stop()
        print("   ✓ Server stopped")
        
        print("\n✅ All components working correctly!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Set environment variables to disable monitoring
    os.environ["ICE_LOCATOR_ANALYTICS_ENABLED"] = "false"
    os.environ["ICE_LOCATOR_MCPCAT_ENABLED"] = "false"
    os.environ["ICE_LOCATOR_PROXY_ENABLED"] = "false"
    
    asyncio.run(test_components())

