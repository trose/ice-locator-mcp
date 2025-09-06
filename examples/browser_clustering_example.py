#!/usr/bin/env python3
"""
Example demonstrating browser clustering functionality.

This script shows how to use the browser cluster manager to distribute
requests across multiple browser instances for improved performance
and reliability.
"""

import asyncio
import sys
import os

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ice_locator_mcp.anti_detection.browser_cluster import BrowserClusterManager
from src.ice_locator_mcp.core.config import SearchConfig


async def main():
    """Demonstrate browser clustering functionality."""
    print("Browser Clustering Example")
    print("=" * 30)
    
    # Create a search configuration
    config = SearchConfig(
        max_retries=3,
        timeout=30
    )
    
    # Create browser cluster manager with 3 instances
    cluster_manager = BrowserClusterManager(config, max_instances=3)
    
    try:
        # Initialize the cluster
        print("Initializing browser cluster...")
        await cluster_manager.initialize()
        print(f"Cluster initialized with {len(cluster_manager.instances)} instances")
        
        # Simulate handling multiple requests
        urls = [
            "https://httpbin.org/html",
            "https://httpbin.org/json",
            "https://httpbin.org/xml",
            "https://httpbin.org/headers",
            "https://httpbin.org/user-agent"
        ]
        
        print("\nHandling requests across cluster instances...")
        tasks = []
        
        for i, url in enumerate(urls):
            session_id = f"session_{i}"
            print(f"Creating task for {url} with session {session_id}")
            task = asyncio.create_task(
                cluster_manager.handle_request(session_id, url)
            )
            tasks.append(task)
        
        # Wait for all requests to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        print("\nRequest Results:")
        print("-" * 20)
        for i, (url, result) in enumerate(zip(urls, results)):
            if isinstance(result, Exception):
                print(f"Request {i+1} ({url}): FAILED - {result}")
            else:
                print(f"Request {i+1} ({url}): SUCCESS")
        
        # Show cluster status
        print("\nCluster Status:")
        print("-" * 20)
        for instance_id, instance in cluster_manager.instances.items():
            print(f"Instance {instance_id}:")
            print(f"  - Available: {instance.is_available}")
            print(f"  - Requests: {instance.request_count}")
            print(f"  - Errors: {instance.error_count}")
            print(f"  - Health Score: {instance.health_score:.2f}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Clean up
        print("\nCleaning up cluster...")
        await cluster_manager.cleanup()
        print("Cluster cleaned up successfully")


if __name__ == "__main__":
    asyncio.run(main())