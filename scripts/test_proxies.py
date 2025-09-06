#!/usr/bin/env python3
"""
Simple script to test proxy functionality and availability.
"""

import asyncio
import httpx
import os
import sys
from typing import List


async def test_proxy_connectivity(proxy_url: str, test_url: str = "https://httpbin.org/ip") -> bool:
    """
    Test if a proxy can connect to a test URL.
    
    Args:
        proxy_url: Proxy URL in format http://host:port
        test_url: URL to test connectivity with
        
    Returns:
        True if proxy works, False otherwise
    """
    try:
        async with httpx.AsyncClient(
            proxies={"http://": proxy_url, "https://": proxy_url},
            timeout=10.0
        ) as client:
            response = await client.get(test_url)
            return response.status_code == 200
    except Exception:
        return False


async def fetch_free_proxies() -> List[str]:
    """
    Fetch a list of free proxies from public sources.
    
    Returns:
        List of proxy URLs
    """
    proxies = []
    
    # Try to get proxies from proxyscrape
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
            )
            if response.status_code == 200:
                proxy_lines = response.text.strip().split('\n')
                for line in proxy_lines[:20]:  # Limit to first 20 proxies
                    line = line.strip()
                    if line:
                        proxies.append(f"http://{line}")
    except Exception as e:
        print(f"Failed to fetch proxies from proxyscrape: {e}")
    
    return proxies


async def main():
    """Main test function."""
    print("Testing proxy functionality...")
    
    # Check if proxies are enabled
    proxy_enabled = os.getenv("ICE_LOCATOR_PROXY_ENABLED", "true").lower() in ("true", "1", "yes", "on")
    print(f"Proxy enabled: {proxy_enabled}")
    
    if not proxy_enabled:
        print("WARNING: Proxies are disabled. Testing direct connectivity to ICE website...")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://locator.ice.gov")
                print(f"Direct access status code: {response.status_code}")
                if response.status_code == 403:
                    print("ERROR: Direct access blocked by ICE website (403 Forbidden)")
                    print("Proxies are required for accessing the ICE website.")
        except Exception as e:
            print(f"Direct access failed: {e}")
        return
    
    # Test free proxies
    print("Fetching free proxies...")
    free_proxies = await fetch_free_proxies()
    print(f"Found {len(free_proxies)} free proxies")
    
    if not free_proxies:
        print("No free proxies available from public sources")
        return
    
    # Test a few proxies
    print("Testing proxy connectivity...")
    working_proxies = []
    
    for proxy_url in free_proxies[:5]:  # Test first 5 proxies
        print(f"Testing {proxy_url}...")
        if await test_proxy_connectivity(proxy_url):
            working_proxies.append(proxy_url)
            print(f"  ✓ Working")
        else:
            print(f"  ✗ Failed")
    
    print(f"\nWorking proxies: {len(working_proxies)}/{min(5, len(free_proxies))}")
    
    if not working_proxies:
        print("\nWARNING: No free proxies are working!")
        print("Free proxies are often unreliable and may be blocked by target websites.")
        print("For production use, consider using premium residential proxies.")
    else:
        print(f"\nWorking proxies found: {working_proxies}")


if __name__ == "__main__":
    asyncio.run(main())