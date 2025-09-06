#!/usr/bin/env python3
"""
Simple reverse proxy example to demonstrate why it wouldn't help with ICE website access.

This is just for educational purposes to show the concept.
In practice, this wouldn't solve our anti-detection needs.
"""

import asyncio
import httpx
from typing import Optional


class SimpleReverseProxy:
    """A simple reverse proxy implementation for demonstration purposes."""
    
    def __init__(self, target_host: str = "https://locator.ice.gov"):
        self.target_host = target_host
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def forward_request(self, method: str, path: str, headers: dict, body: Optional[bytes] = None):
        """
        Forward a request to the target host.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            headers: Request headers
            body: Request body (for POST requests)
            
        Returns:
            Response from the target host
        """
        # Construct the full URL
        url = f"{self.target_host}{path}"
        
        # Remove headers that shouldn't be forwarded
        forward_headers = {k: v for k, v in headers.items() 
                          if not k.lower().startswith('x-forwarded')}
        
        try:
            # Forward the request
            response = await self.client.request(
                method=method,
                url=url,
                headers=forward_headers,
                content=body
            )
            return response
        except Exception as e:
            print(f"Error forwarding request: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def main():
    """Demonstrate the reverse proxy concept."""
    print("Simple Reverse Proxy Example")
    print("=" * 40)
    print("This demonstrates what a self-hosted reverse proxy would do:")
    print("1. Receive requests from clients")
    print("2. Forward them to the target website")
    print("3. Return responses to clients")
    print("\nHowever, this approach has limitations for our use case:")
    print("- All requests would come from the same IP (detectable)")
    print("- No IP rotation or residential IP benefits")
    print("- ICE website would still block the single IP")
    print("- No anti-detection advantages")
    
    # Create a reverse proxy instance
    proxy = SimpleReverseProxy()
    
    print("\nTo use external proxies effectively (our current approach):")
    print("1. Use ProxyManager to get rotating proxies")
    print("2. Configure httpx.AsyncClient with different proxy URLs")
    print("3. Benefit from IP rotation and residential IP diversity")
    
    # Clean up
    await proxy.close()


if __name__ == "__main__":
    asyncio.run(main())