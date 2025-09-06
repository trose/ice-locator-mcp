"""
Example demonstrating advanced timezone and locale simulation.
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.timezone_locale_manager import TimezoneLocaleManager, TimezoneProfile, LocaleProfile


async def main():
    """Demonstrate TimezoneLocaleManager usage."""
    # Create TimezoneLocaleManager instance
    timezone_locale_manager = TimezoneLocaleManager()
    
    # Generate a random timezone profile
    timezone_profile = timezone_locale_manager.get_random_timezone_profile()
    print("Random Timezone Profile:")
    print(f"  Timezone ID: {timezone_profile.timezone_id}")
    print(f"  Offset: {timezone_profile.offset} minutes")
    print(f"  Locale: {timezone_profile.locale}")
    print(f"  Geolocation: {timezone_profile.geolocation}")
    print()
    
    # Generate a random locale profile
    locale_profile = timezone_locale_manager.get_random_locale_profile()
    print("Random Locale Profile:")
    print(f"  Locale: {locale_profile.locale}")
    print(f"  Language: {locale_profile.language}")
    print(f"  Currency: {locale_profile.currency}")
    print(f"  Text Direction: {locale_profile.text_direction}")
    print()
    
    # Generate a completely realistic timezone/locale combination
    realistic_timezone, realistic_locale = timezone_locale_manager.generate_realistic_timezone_locale()
    print("Realistic Timezone/Locale Combination:")
    print(f"  Timezone ID: {realistic_timezone.timezone_id}")
    print(f"  Locale: {realistic_locale.locale}")
    print(f"  Language: {realistic_locale.language}")
    print(f"  Currency: {realistic_locale.currency}")
    print()
    
    # Check profile consistency
    is_consistent = timezone_locale_manager.is_consistent_timezone_locale(
        realistic_timezone, realistic_locale
    )
    print("Profile Consistency:")
    print(f"  Timezone/Locale profiles consistent: {is_consistent}")
    print()
    
    # Get timezone headers
    headers = timezone_locale_manager.get_timezone_headers(realistic_locale.locale)
    print("Timezone Headers:")
    for key, value in headers.items():
        print(f"  {key}: {value}")
    print()
    
    # Get timezone offset
    offset = timezone_locale_manager.get_timezone_offset(realistic_timezone)
    print("Timezone Offset:")
    print(f"  Offset: {offset} minutes")
    print()
    
    # Get geolocation
    geolocation = timezone_locale_manager.get_geolocation(realistic_timezone)
    print("Geolocation:")
    print(f"  Latitude: {geolocation['latitude']}")
    print(f"  Longitude: {geolocation['longitude']}")
    print()


if __name__ == "__main__":
    asyncio.run(main())