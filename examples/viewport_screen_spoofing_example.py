"""
Example demonstrating advanced viewport and screen dimension spoofing.
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.viewport_screen_spoofing import ViewportScreenSpoofingManager, ViewportScreenProfile


async def main():
    """Demonstrate ViewportScreenSpoofingManager usage."""
    # Create ViewportScreenSpoofingManager instance
    viewport_manager = ViewportScreenSpoofingManager()
    
    # Generate a random viewport and screen dimension profile
    profile = viewport_manager.get_random_profile()
    print("Random Viewport and Screen Dimension Profile:")
    print(f"  Screen Dimensions: {profile.screen_width}x{profile.screen_height}")
    print(f"  Available Screen: {profile.avail_width}x{profile.avail_height}")
    print(f"  Color Depth: {profile.color_depth} bits")
    print(f"  Pixel Depth: {profile.pixel_depth} bits")
    print(f"  Viewport Dimensions: {profile.viewport_width}x{profile.viewport_height}")
    print(f"  Outer Dimensions: {profile.outer_width}x{profile.outer_height}")
    print(f"  Device Pixel Ratio: {profile.device_pixel_ratio}")
    print(f"  Orientation: {profile.orientation_type} ({profile.orientation_angle}°)")
    print(f"  Device Type: {profile.device_type}")
    print(f"  Is Consistent: {profile.is_consistent}")
    print()
    
    # Generate device-specific profiles
    desktop_4k_profile = viewport_manager.get_device_specific_profile("desktop_4k")
    laptop_fhd_profile = viewport_manager.get_device_specific_profile("laptop_fhd")
    mobile_profile = viewport_manager.get_device_specific_profile("mobile_high_end")
    tablet_profile = viewport_manager.get_device_specific_profile("tablet")
    
    print("Device-Specific Viewport Profiles:")
    print(f"  4K Desktop - Screen: {desktop_4k_profile.screen_width}x{desktop_4k_profile.screen_height}, DPR: {desktop_4k_profile.device_pixel_ratio}")
    print(f"  FHD Laptop - Screen: {laptop_fhd_profile.screen_width}x{laptop_fhd_profile.screen_height}, DPR: {laptop_fhd_profile.device_pixel_ratio}")
    print(f"  High-end Mobile - Screen: {mobile_profile.screen_width}x{mobile_profile.screen_height}, DPR: {mobile_profile.device_pixel_ratio}")
    print(f"  Tablet - Screen: {tablet_profile.screen_width}x{tablet_profile.screen_height}, DPR: {tablet_profile.device_pixel_ratio}")
    print()
    
    # Generate a viewport fingerprint
    fingerprint = viewport_manager.generate_fingerprint(profile)
    print("Viewport Fingerprint:")
    print(f"  Hash: {fingerprint}")
    print()
    
    # Check profile consistency
    is_consistent = viewport_manager.are_profiles_consistent(profile)
    print("Profile Consistency:")
    print(f"  Viewport profile consistent: {is_consistent}")
    print()
    
    # Generate spoofing JavaScript code
    js_code = viewport_manager._generate_spoofing_js(profile)
    print("Generated JavaScript Code:")
    print(f"  JS length: {len(js_code)} characters")
    print()
    
    # Example of creating a custom profile
    custom_profile = ViewportScreenProfile(
        screen_width=2560,
        screen_height=1440,
        avail_width=2560,
        avail_height=1400,
        color_depth=32,
        pixel_depth=32,
        viewport_width=2560,
        viewport_height=1400,
        outer_width=2560,
        outer_height=1440,
        device_pixel_ratio=1.5,
        orientation_type="landscape-primary",
        orientation_angle=0,
        device_type="desktop_wqhd",
        is_consistent=True
    )
    
    print("Custom Viewport Profile:")
    print(f"  Custom screen: {custom_profile.screen_width}x{custom_profile.screen_height}")
    print(f"  Custom device pixel ratio: {custom_profile.device_pixel_ratio}")
    print(f"  Custom device type: {custom_profile.device_type}")
    print()
    
    # Generate fingerprint for custom profile
    custom_fingerprint = viewport_manager.generate_fingerprint(custom_profile)
    print("Custom Profile Fingerprint:")
    print(f"  Hash: {custom_fingerprint}")
    print()


if __name__ == "__main__":
    asyncio.run(main())