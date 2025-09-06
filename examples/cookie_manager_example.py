#!/usr/bin/env python3
"""
Example demonstrating advanced cookie handling and management functionality.

This script shows how to use the CookieManager to handle cookie rotation,
validation, and realistic expiration patterns to maintain realistic session states.
"""

import asyncio
import sys
import os
import time
import random

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ice_locator_mcp.anti_detection.cookie_manager import CookieManager, CookieProfile


async def create_sample_cookies():
    """Create sample cookies for demonstration."""
    cookies = [
        CookieProfile(
            name="session_id",
            value="abc123xyz789",
            domain="example.com",
            path="/",
            expires=None,  # Session cookie
            httpOnly=True,
            secure=True,
            sameSite="Lax",
            creation_time=time.time() - 300,  # Created 5 minutes ago
            last_accessed=time.time() - 60   # Accessed 1 minute ago
        ),
        CookieProfile(
            name="user_preference",
            value="dark_mode",
            domain="example.com",
            path="/",
            expires=time.time() + 3600,  # Expires in 1 hour
            httpOnly=False,
            secure=True,
            sameSite="Strict",
            creation_time=time.time() - 600,  # Created 10 minutes ago
            last_accessed=time.time() - 300  # Accessed 5 minutes ago
        ),
        CookieProfile(
            name="tracking_cookie",
            value="track987654321",
            domain="google-analytics.com",
            path="/",
            expires=time.time() + 86400,  # Expires in 1 day
            httpOnly=False,
            secure=True,
            sameSite="None",
            creation_time=time.time() - 1800,  # Created 30 minutes ago
            last_accessed=time.time() - 900   # Accessed 15 minutes ago
        ),
        CookieProfile(
            name="persistent_cookie",
            value="persistent_value",
            domain="example.com",
            path="/",
            expires=time.time() + (7 * 24 * 60 * 60),  # Expires in 7 days
            httpOnly=False,
            secure=True,
            sameSite="Lax",
            creation_time=time.time() - 3600,  # Created 1 hour ago
            last_accessed=time.time() - 1800  # Accessed 30 minutes ago
        )
    ]
    return cookies


async def main():
    """Demonstrate cookie manager functionality."""
    print("Cookie Manager Example")
    print("=" * 30)
    
    # Create cookie manager
    cookie_manager = CookieManager()
    
    # Create sample cookies
    cookies = await create_sample_cookies()
    print(f"\n1. Created {len(cookies)} sample cookies:")
    for i, cookie in enumerate(cookies):
        print(f"   {i+1}. {cookie.name} = {cookie.value} (domain: {cookie.domain})")
    
    print("\n2. Validating cookies...")
    valid_cookies = await cookie_manager.validate_cookies(cookies)
    print(f"   Valid cookies: {len(valid_cookies)}")
    
    print("\n3. Applying realistic expiration patterns...")
    processed_cookies = await cookie_manager.apply_realistic_expiration(valid_cookies)
    print(f"   Processed cookies: {len(processed_cookies)}")
    
    # Show expiration information
    for cookie in processed_cookies:
        if cookie.is_session_cookie():
            print(f"   - {cookie.name}: Session cookie")
        else:
            time_to_expiry = cookie.time_to_expiry()
            if time_to_expiry is not None:
                hours_to_expiry = time_to_expiry / 3600
                print(f"   - {cookie.name}: Expires in {hours_to_expiry:.2f} hours")
    
    print("\n4. Preparing cookies for session (validation, expiration, rotation)...")
    prepared_cookies = await cookie_manager.prepare_cookies_for_session(processed_cookies)
    print(f"   Prepared cookies: {len(prepared_cookies)}")
    
    # Show which cookies were rotated
    print("\n5. Checking for rotated cookies...")
    original_values = {c.name: c.value for c in cookies}
    for cookie in prepared_cookies:
        original_value = original_values.get(cookie.name)
        if original_value and original_value != cookie.value:
            print(f"   - {cookie.name}: Value rotated from '{original_value}' to '{cookie.value}'")
        else:
            print(f"   - {cookie.name}: Value unchanged")
    
    print("\n6. Testing cookie categories...")
    for cookie in prepared_cookies:
        category = cookie_manager._get_cookie_category(cookie)
        print(f"   - {cookie.name}: {category} category")
    
    print("\n7. Testing cookie rotation decision...")
    # Create an old session cookie to test rotation
    old_session_cookie = CookieProfile(
        name="old_session",
        value="old_value_12345",
        domain="example.com",
        creation_time=time.time() - 3600,  # Created 1 hour ago
        last_accessed=time.time() - 1800   # Accessed 30 minutes ago
    )
    
    # Test rotation decision multiple times
    rotation_results = []
    for i in range(20):
        should_rotate = cookie_manager._should_rotate_cookie(old_session_cookie)
        rotation_results.append(should_rotate)
    
    rotation_count = sum(rotation_results)
    print(f"   Old session cookie rotation decision over 20 tests: {rotation_count}/20 times")
    
    print("\n8. Generating rotated values...")
    original_value = "session_abcdef123456"
    for i in range(5):
        rotated_value = cookie_manager._generate_rotated_value(original_value)
        print(f"   - Original: {original_value}")
        print(f"   - Rotated:  {rotated_value}")
        print(f"   - Length:   {len(original_value)} -> {len(rotated_value)}")
        print()
    
    print("Cookie Manager demonstration completed!")


if __name__ == "__main__":
    asyncio.run(main())