"""
Example demonstrating advanced font enumeration protection.
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.font_enumeration_protection import FontEnumerationProtectionManager, FontEnumerationProfile


async def main():
    """Demonstrate FontEnumerationProtectionManager usage."""
    # Create FontEnumerationProtectionManager instance
    font_protection_manager = FontEnumerationProtectionManager()
    
    # Generate a random font enumeration protection profile
    profile = font_protection_manager.get_random_profile()
    print("Random Font Enumeration Protection Profile:")
    print(f"  Font Families Count: {len(profile.font_families)}")
    print(f"  Include Emoji Fonts: {profile.include_emoji_fonts}")
    print(f"  Include Monospace Fonts: {profile.include_monospace_fonts}")
    print(f"  Include Serif Fonts: {profile.include_serif_fonts}")
    print(f"  Include Sans-serif Fonts: {profile.include_sans_serif_fonts}")
    print(f"  Include Cursive Fonts: {profile.include_cursive_fonts}")
    print(f"  Include Fantasy Fonts: {profile.include_fantasy_fonts}")
    print(f"  Device Type: {profile.device_type}")
    print(f"  Is Consistent: {profile.is_consistent}")
    print(f"  Sample Fonts: {profile.font_families[:5]}")
    print()
    
    # Generate device-specific profiles
    windows_profile = font_protection_manager.get_device_specific_profile("desktop_windows")
    mac_profile = font_protection_manager.get_device_specific_profile("desktop_macos")
    linux_profile = font_protection_manager.get_device_specific_profile("desktop_linux")
    ios_profile = font_protection_manager.get_device_specific_profile("mobile_ios")
    android_profile = font_protection_manager.get_device_specific_profile("mobile_android")
    tablet_profile = font_protection_manager.get_device_specific_profile("tablet")
    
    print("Device-Specific Font Profiles:")
    print(f"  Windows - Fonts: {len(windows_profile.font_families)}, Device: {windows_profile.device_type}")
    print(f"  macOS - Fonts: {len(mac_profile.font_families)}, Device: {mac_profile.device_type}")
    print(f"  Linux - Fonts: {len(linux_profile.font_families)}, Device: {linux_profile.device_type}")
    print(f"  iOS - Fonts: {len(ios_profile.font_families)}, Device: {ios_profile.device_type}")
    print(f"  Android - Fonts: {len(android_profile.font_families)}, Device: {android_profile.device_type}")
    print(f"  Tablet - Fonts: {len(tablet_profile.font_families)}, Device: {tablet_profile.device_type}")
    print()
    
    # Generate a font fingerprint
    fingerprint = font_protection_manager.generate_fingerprint(profile)
    print("Font Fingerprint:")
    print(f"  Hash: {fingerprint}")
    print()
    
    # Check profile consistency
    is_consistent = font_protection_manager.are_profiles_consistent(profile)
    print("Profile Consistency:")
    print(f"  Font profile consistent: {is_consistent}")
    print()
    
    # Generate protection JavaScript code
    js_code = font_protection_manager._generate_protection_js(profile)
    print("Generated JavaScript Code:")
    print(f"  JS length: {len(js_code)} characters")
    print()
    
    # Example of creating a custom profile
    custom_profile = FontEnumerationProfile(
        font_families=["Custom Font 1", "Custom Font 2", "Custom Font 3"],
        include_emoji_fonts=True,
        include_monospace_fonts=False,
        include_serif_fonts=True,
        include_sans_serif_fonts=True,
        include_cursive_fonts=False,
        include_fantasy_fonts=True,
        device_type="desktop_custom",
        is_consistent=True
    )
    
    print("Custom Font Profile:")
    print(f"  Custom font families: {custom_profile.font_families}")
    print(f"  Custom device type: {custom_profile.device_type}")
    print()
    
    # Generate fingerprint for custom profile
    custom_fingerprint = font_protection_manager.generate_fingerprint(custom_profile)
    print("Custom Profile Fingerprint:")
    print(f"  Hash: {custom_fingerprint}")
    print()


if __name__ == "__main__":
    asyncio.run(main())