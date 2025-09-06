"""
Example demonstrating residential proxy integration with IP reputation checking.
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.proxy_manager import ProxyManager
from ice_locator_mcp.core.config import ProxyConfig


async def main():
    """Demonstrate residential proxy integration capabilities."""
    # Create a proxy config
    config = ProxyConfig()
    
    # Initialize proxy manager
    proxy_manager = ProxyManager(config)
    
    try:
        # Initialize the proxy manager
        await proxy_manager.initialize()
        print("✓ Proxy manager initialized")
        
        # Show proxy pool information
        print(f"✓ Loaded {len(proxy_manager.proxy_pool)} proxies")
        
        # Show proxy analytics
        analytics = await proxy_manager.get_proxy_analytics()
        print(f"✓ Healthy proxies: {analytics['overview']['healthy_proxies']}/{analytics['overview']['total_proxies']}")
        print(f"✓ Average success rate: {analytics['performance']['average_success_rate']:.2%}")
        print(f"✓ Average response time: {analytics['performance']['average_response_time']:.2f}s")
        
        # Show residential proxy count
        residential_count = analytics['distribution']['residential_proxies']
        datacenter_count = analytics['distribution']['datacenter_proxies']
        print(f"✓ Residential proxies: {residential_count}")
        print(f"✓ Datacenter proxies: {datacenter_count}")
        
        # Get proxy recommendations
        recommendations = await proxy_manager.get_proxy_recommendations()
        if recommendations:
            print("\n--- Proxy Recommendations ---")
            for rec in recommendations:
                print(f"• {rec['title']}: {rec['description']}")
                print(f"  Action: {rec['action']}")
                print(f"  Priority: {rec['priority']}")
        else:
            print("✓ No proxy recommendations - configuration looks good!")
        
        # Demonstrate proxy selection with reputation scoring
        print("\n--- Proxy Selection Demo ---")
        for i in range(3):
            proxy = await proxy_manager.get_proxy()
            if proxy:
                metrics = proxy_manager.proxy_metrics.get(proxy.endpoint, None)
                reputation = metrics.reputation_score if metrics else 0.5
                is_residential = "✓" if proxy.is_residential else "✗"
                print(f"Selected Proxy #{i+1}: {proxy.endpoint} (Residential: {is_residential}, Reputation: {reputation:.2f})")
            else:
                print(f"Selected Proxy #{i+1}: None (no healthy proxies available)")
        
        print("\n✓ Residential proxy integration example completed successfully!")
        
    except Exception as e:
        print(f"Error during residential proxy integration demonstration: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        await proxy_manager.cleanup()
        print("✓ Cleaned up proxy manager")


if __name__ == "__main__":
    asyncio.run(main())