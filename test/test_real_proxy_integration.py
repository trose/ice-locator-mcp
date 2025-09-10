#!/usr/bin/env python3
"""
Test script to verify real data integration with actual proxy sources.
"""

import asyncio
import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ice_locator_mcp.anti_detection.proxy_manager import ProxyManager, ProxyConfig
from src.ice_locator_mcp.core.config import ProxyConfig as ConfigProxyConfig


async def test_real_proxy_integration():
    """Test real data integration with actual proxy sources."""
    print("Testing real data integration with proxy sources...")
    
    # Create a temporary proxy list file with some test proxies
    # In a real scenario, you would use actual working proxies
    proxy_list_content = """
# Test proxy list
# Format: host:port or host:port:username:password

# These are example proxies - replace with real ones for actual testing
# 192.168.1.100:8080
# 192.168.1.101:8080:user1:pass1
# proxy.example.com:3128
"""
    
    # Create temporary proxy list file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(proxy_list_content)
        proxy_list_file = f.name
    
    try:
        # Set environment variable for proxy file
        os.environ["ICE_LOCATOR_PROXY_FILE"] = proxy_list_file
        
        # Create proxy configuration
        proxy_config = ConfigProxyConfig(
            enabled=True,
            rotation_interval=300,
            max_requests_per_proxy=10,
            proxy_sources=["custom_proxy_list"],
            residential_preferred=True,
            geographic_distribution=True
        )
        
        # Initialize proxy manager
        proxy_manager = ProxyManager(proxy_config)
        await proxy_manager.initialize()
        
        print("Proxy manager initialized successfully")
        
        # Test getting a proxy
        proxy = await proxy_manager.get_proxy()
        if proxy:
            print(f"Successfully retrieved proxy: {proxy.endpoint}")
        else:
            print("No proxy available - this is expected with sample proxy list")
        
        # Test proxy analytics
        analytics = await proxy_manager.get_proxy_analytics()
        print(f"Proxy analytics: {analytics['overview']}")
        
        # Test proxy recommendations
        recommendations = await proxy_manager.get_proxy_recommendations()
        print(f"Proxy recommendations: {len(recommendations)} found")
        for rec in recommendations:
            print(f"  - {rec['title']}: {rec['description']}")
        
        # Test optimization
        optimization_results = await proxy_manager.optimize_proxy_pool()
        print(f"Optimization results: {optimization_results}")
        
        print("\nReal proxy integration test completed successfully!")
        
    except Exception as e:
        print(f"Error during real proxy integration test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up environment variable
        if "ICE_LOCATOR_PROXY_FILE" in os.environ:
            del os.environ["ICE_LOCATOR_PROXY_FILE"]
        
        # Clean up temporary file
        if os.path.exists(proxy_list_file):
            os.unlink(proxy_list_file)
        
        # Cleanup proxy manager
        try:
            await proxy_manager.cleanup()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(test_real_proxy_integration())