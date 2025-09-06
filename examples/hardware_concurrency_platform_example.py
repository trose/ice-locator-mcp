"""
Example demonstrating advanced hardware concurrency and platform information masking.
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.hardware_concurrency_platform_manager import HardwareConcurrencyPlatformManager, HardwareConcurrencyPlatformProfile


async def main():
    """Demonstrate HardwareConcurrencyPlatformManager usage."""
    # Create HardwareConcurrencyPlatformManager instance
    hardware_manager = HardwareConcurrencyPlatformManager()
    
    # Generate a random hardware concurrency and platform profile
    profile = hardware_manager.get_random_profile()
    print("Random Hardware Concurrency and Platform Profile:")
    print(f"  Hardware Concurrency: {profile.hardware_concurrency}")
    print(f"  Platform: {profile.platform}")
    print(f"  OS Family: {profile.os_family}")
    print(f"  Architecture: {profile.architecture}")
    print(f"  CPU Class: {profile.cpu_class}")
    print(f"  Device Memory: {profile.device_memory} GB")
    print(f"  Device Type: {profile.device_type}")
    print(f"  Is Consistent: {profile.is_consistent}")
    print()
    
    # Generate device-specific profiles
    win_profile = hardware_manager.get_device_specific_profile("desktop_windows")
    mac_profile = hardware_manager.get_device_specific_profile("desktop_macos")
    linux_profile = hardware_manager.get_device_specific_profile("desktop_linux")
    android_profile = hardware_manager.get_device_specific_profile("mobile_android")
    ios_profile = hardware_manager.get_device_specific_profile("mobile_ios")
    tablet_profile = hardware_manager.get_device_specific_profile("tablet")
    
    print("Device-Specific Hardware Profiles:")
    print(f"  Windows - Cores: {win_profile.hardware_concurrency}, Memory: {win_profile.device_memory} GB")
    print(f"  macOS - Cores: {mac_profile.hardware_concurrency}, Memory: {mac_profile.device_memory} GB")
    print(f"  Linux - Cores: {linux_profile.hardware_concurrency}, Memory: {linux_profile.device_memory} GB")
    print(f"  Android - Cores: {android_profile.hardware_concurrency}, Memory: {android_profile.device_memory} GB")
    print(f"  iOS - Cores: {ios_profile.hardware_concurrency}, Memory: {ios_profile.device_memory} GB")
    print(f"  Tablet - Cores: {tablet_profile.hardware_concurrency}, Memory: {tablet_profile.device_memory} GB")
    print()
    
    # Generate a hardware fingerprint
    fingerprint = hardware_manager.generate_fingerprint(profile)
    print("Hardware Fingerprint:")
    print(f"  Hash: {fingerprint}")
    print()
    
    # Check profile consistency
    is_consistent = hardware_manager.are_profiles_consistent(profile)
    print("Profile Consistency:")
    print(f"  Hardware profile consistent: {is_consistent}")
    print()
    
    # Generate masking JavaScript code
    js_code = hardware_manager._generate_masking_js(profile)
    print("Generated JavaScript Code:")
    print(f"  JS length: {len(js_code)} characters")
    print()
    
    # Example of creating a custom profile
    custom_profile = HardwareConcurrencyPlatformProfile(
        hardware_concurrency=12,
        platform="Linux x86_64",
        os_family="Linux",
        architecture="64-bit",
        cpu_class="x86_64",
        device_memory=32,
        device_type="desktop_linux",
        is_consistent=True
    )
    
    print("Custom Hardware Profile:")
    print(f"  Custom cores: {custom_profile.hardware_concurrency}")
    print(f"  Custom memory: {custom_profile.device_memory} GB")
    print(f"  Custom platform: {custom_profile.platform}")
    print()
    
    # Generate fingerprint for custom profile
    custom_fingerprint = hardware_manager.generate_fingerprint(custom_profile)
    print("Custom Profile Fingerprint:")
    print(f"  Hash: {custom_fingerprint}")
    print()


if __name__ == "__main__":
    asyncio.run(main())