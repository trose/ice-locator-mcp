"""
Example demonstrating advanced device memory and CPU class spoofing.
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.device_memory_cpu_manager import DeviceMemoryCPUManager, DeviceMemoryCPUProfile


async def main():
    """Demonstrate DeviceMemoryCPUManager usage."""
    # Create DeviceMemoryCPUManager instance
    device_manager = DeviceMemoryCPUManager()
    
    # Generate a random device memory and CPU class profile
    profile = device_manager.get_random_profile()
    print("Random Device Memory and CPU Class Profile:")
    print(f"  Device Memory: {profile.device_memory} GB")
    print(f"  CPU Class: {profile.cpu_class}")
    print(f"  Hardware Concurrency: {profile.hardware_concurrency}")
    print(f"  Architecture: {profile.architecture}")
    print(f"  Device Type: {profile.device_type}")
    print(f"  Is Consistent: {profile.is_consistent}")
    print()
    
    # Generate device-specific profiles
    high_end_profile = device_manager.get_device_specific_profile("desktop_high_end")
    mid_range_profile = device_manager.get_device_specific_profile("desktop_mid_range")
    low_end_profile = device_manager.get_device_specific_profile("desktop_low_end")
    mobile_high_profile = device_manager.get_device_specific_profile("mobile_high_end")
    mobile_low_profile = device_manager.get_device_specific_profile("mobile_low_end")
    tablet_profile = device_manager.get_device_specific_profile("tablet")
    
    print("Device-Specific Memory and CPU Profiles:")
    print(f"  High-end Desktop - Memory: {high_end_profile.device_memory} GB, CPU: {high_end_profile.cpu_class}, Cores: {high_end_profile.hardware_concurrency}")
    print(f"  Mid-range Desktop - Memory: {mid_range_profile.device_memory} GB, CPU: {mid_range_profile.cpu_class}, Cores: {mid_range_profile.hardware_concurrency}")
    print(f"  Low-end Desktop - Memory: {low_end_profile.device_memory} GB, CPU: {low_end_profile.cpu_class}, Cores: {low_end_profile.hardware_concurrency}")
    print(f"  High-end Mobile - Memory: {mobile_high_profile.device_memory} GB, CPU: {mobile_high_profile.cpu_class}, Cores: {mobile_high_profile.hardware_concurrency}")
    print(f"  Low-end Mobile - Memory: {mobile_low_profile.device_memory} GB, CPU: {mobile_low_profile.cpu_class}, Cores: {mobile_low_profile.hardware_concurrency}")
    print(f"  Tablet - Memory: {tablet_profile.device_memory} GB, CPU: {tablet_profile.cpu_class}, Cores: {tablet_profile.hardware_concurrency}")
    print()
    
    # Generate a device fingerprint
    fingerprint = device_manager.generate_fingerprint(profile)
    print("Device Fingerprint:")
    print(f"  Hash: {fingerprint}")
    print()
    
    # Check profile consistency
    is_consistent = device_manager.are_profiles_consistent(profile)
    print("Profile Consistency:")
    print(f"  Device profile consistent: {is_consistent}")
    print()
    
    # Generate spoofing JavaScript code
    js_code = device_manager._generate_spoofing_js(profile)
    print("Generated JavaScript Code:")
    print(f"  JS length: {len(js_code)} characters")
    print()
    
    # Example of creating a custom profile
    custom_profile = DeviceMemoryCPUProfile(
        device_memory=32,
        cpu_class="x86_64",
        hardware_concurrency=16,
        architecture="64-bit",
        device_type="desktop_high_end",
        is_consistent=True
    )
    
    print("Custom Device Profile:")
    print(f"  Custom memory: {custom_profile.device_memory} GB")
    print(f"  Custom CPU: {custom_profile.cpu_class}")
    print(f"  Custom cores: {custom_profile.hardware_concurrency}")
    print()
    
    # Generate fingerprint for custom profile
    custom_fingerprint = device_manager.generate_fingerprint(custom_profile)
    print("Custom Profile Fingerprint:")
    print(f"  Hash: {custom_fingerprint}")
    print()


if __name__ == "__main__":
    asyncio.run(main())