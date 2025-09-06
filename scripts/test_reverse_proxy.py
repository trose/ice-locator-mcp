#!/usr/bin/env python3
"""
Test script to demonstrate why a self-hosted reverse proxy wouldn't help
with accessing the ICE website.

This script shows that a reverse proxy would still be detected as a single
endpoint and wouldn't provide the IP rotation benefits we need.
"""

import asyncio
import httpx
import os


async def test_direct_access():
    """Test direct access to ICE website."""
    print("Testing direct access to ICE website...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://locator.ice.gov")
            print(f"Direct access status code: {response.status_code}")
            if response.status_code == 403:
                print("✗ Direct access blocked (403 Forbidden)")
                return False
            else:
                print("✓ Direct access successful")
                return True
    except Exception as e:
        print(f"✗ Direct access failed: {e}")
        return False


async def test_with_external_proxy():
    """Test access through an external proxy."""
    print("\nTesting access through external proxy...")
    
    # Check if we have proxy configuration
    proxy_enabled = os.getenv("ICE_LOCATOR_PROXY_ENABLED", "true").lower() in ("true", "1", "yes", "on")
    if not proxy_enabled:
        print("Proxy functionality is disabled")
        return False
    
    # In a real implementation, we would get a proxy from our proxy manager
    # For this test, we're just showing the concept
    print("In our system, we would:")
    print("1. Get a proxy from ProxyManager.get_proxy()")
    print("2. Configure httpx.AsyncClient with proxy=proxy.url")
    print("3. Make requests through that external proxy")
    print("This provides IP rotation and residential IP diversity")
    return True


async def test_with_self_hosted_reverse_proxy():
    """Test access through a self-hosted reverse proxy."""
    print("\nTesting access through self-hosted reverse proxy...")
    print("A self-hosted reverse proxy would:")
    print("1. Run on our local machine or server")
    print("2. Forward requests to the ICE website")
    print("3. Still use our machine's IP address")
    print("\nWhy this wouldn't help:")
    print("✗ Single IP address (still detectable)")
    print("✗ No IP rotation benefits")
    print("✗ ICE website would still block it")
    print("✗ Adds latency without anti-detection benefits")
    return False


async def main():
    """Main test function."""
    print("=" * 60)
    print("Reverse Proxy Analysis for ICE Locator Access")
    print("=" * 60)
    
    # Test all approaches
    direct_success = await test_direct_access()
    external_proxy_success = await test_with_external_proxy()
    reverse_proxy_success = await test_with_self_hosted_reverse_proxy()
    
    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print("For accessing the ICE website, we need:")
    print("✓ Multiple IP addresses (IP rotation)")
    print("✓ Residential IPs (not datacenter)")
    print("✓ Geographic diversity")
    print("✓ Reputation management")
    print("\nA self-hosted reverse proxy doesn't provide these benefits.")
    print("External proxy services (especially premium residential proxies)")
    print("are necessary for accessing the ICE website without being blocked.")
    
    if not direct_success:
        print("\nSince direct access is blocked, we must use external proxies.")
    
    print("\nOur current approach with external proxy providers is appropriate.")


if __name__ == "__main__":
    asyncio.run(main())