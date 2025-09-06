"""
Example demonstrating advanced viewport and screen simulation.
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.viewport_manager import ViewportManager, ViewportProfile


async def main():
    """Demonstrate viewport manager capabilities."""
    print("=== Viewport Manager Example ===\n")
    
    # Create viewport manager
    viewport_manager = ViewportManager()
    print("✓ ViewportManager initialized")
    
    # Example 1: Generate a realistic viewport
    print("\n--- Generate Realistic Viewport ---")
    viewport = viewport_manager.generate_realistic_viewport()
    print(f"Generated viewport: {viewport.width}x{viewport.height}")
    print(f"Device scale factor: {viewport.device_scale_factor}")
    print(f"Screen dimensions: {viewport.screen_width}x{viewport.screen_height}")
    print(f"Available screen: {viewport.avail_width}x{viewport.avail_height}")
    print(f"Color depth: {viewport.color_depth}")
    print(f"Device category: {viewport_manager.get_device_category(viewport)}")
    
    # Example 2: Get random viewports by device type
    print("\n--- Random Viewports by Device Type ---")
    device_types = ["desktop", "laptop", "mobile", "tablet"]
    
    for device_type in device_types:
        viewport = viewport_manager.get_random_viewport(device_type)
        print(f"{device_type.capitalize()} viewport: {viewport.width}x{viewport.height} "
              f"(scale: {viewport.device_scale_factor})")
    
    # Example 3: Get random device profiles
    print("\n--- Random Device Profiles ---")
    for i in range(3):
        device_profile = viewport_manager.get_random_device_profile()
        viewport = device_profile.viewport
        print(f"Device: {device_profile.name}")
        print(f"  Viewport: {viewport.width}x{viewport.height}")
        print(f"  User Agent: {device_profile.user_agent[:50]}...")
        print(f"  Platform: {device_profile.platform}")
        print()
    
    # Example 4: Viewport analysis
    print("\n--- Viewport Analysis ---")
    test_viewports = [
        ("Desktop", viewport_manager.get_random_viewport("desktop")),
        ("Laptop", viewport_manager.get_random_viewport("laptop")),
        ("Mobile", viewport_manager.get_random_viewport("mobile")),
        ("Tablet", viewport_manager.get_random_viewport("tablet"))
    ]
    
    for name, viewport in test_viewports:
        print(f"{name} Viewport Analysis:")
        print(f"  Dimensions: {viewport_manager.get_viewport_dimensions(viewport)}")
        print(f"  Screen: {viewport_manager.get_screen_dimensions(viewport)}")
        print(f"  Is Mobile: {viewport_manager.is_mobile_viewport(viewport)}")
        print(f"  Is Tablet: {viewport_manager.is_tablet_viewport(viewport)}")
        print(f"  Category: {viewport_manager.get_device_category(viewport)}")
        print()
    
    # Example 5: Viewport serialization
    print("\n--- Viewport Serialization ---")
    viewport = viewport_manager.get_random_viewport("mobile")
    viewport_dict = viewport.to_dict()
    print(f"Serialized viewport: {viewport_dict}")
    
    # Deserialize
    deserialized_viewport = ViewportProfile.from_dict(viewport_dict)
    print(f"Deserialized viewport: {deserialized_viewport.width}x{deserialized_viewport.height}")
    
    print("\n=== Viewport Manager Example Completed ===")


if __name__ == "__main__":
    asyncio.run(main())