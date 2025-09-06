"""
Example demonstrating advanced media device spoofing.
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.media_device_spoofing import MediaDeviceSpoofingManager, MediaDeviceProfile


async def main():
    """Demonstrate MediaDeviceSpoofingManager usage."""
    # Create MediaDeviceSpoofingManager instance
    media_manager = MediaDeviceSpoofingManager()
    
    # Generate a random media device profile
    profile = media_manager.get_random_profile()
    print("Random Media Device Profile:")
    print(f"  Device Type: {profile.device_type}")
    print(f"  Audio Input Devices: {len(profile.audio_input_devices)}")
    print(f"  Audio Output Devices: {len(profile.audio_output_devices)}")
    print(f"  Video Input Devices: {len(profile.video_input_devices)}")
    print(f"  Is Consistent: {profile.is_consistent}")
    print()
    
    # Display audio input devices
    print("Audio Input Devices:")
    for i, device in enumerate(profile.audio_input_devices):
        print(f"  {i+1}. {device.label}")
        print(f"     ID: {device.device_id}")
        print(f"     Group ID: {device.group_id}")
    print()
    
    # Display audio output devices
    print("Audio Output Devices:")
    for i, device in enumerate(profile.audio_output_devices):
        print(f"  {i+1}. {device.label}")
        print(f"     ID: {device.device_id}")
        print(f"     Group ID: {device.group_id}")
    print()
    
    # Display video input devices
    print("Video Input Devices:")
    for i, device in enumerate(profile.video_input_devices):
        print(f"  {i+1}. {device.label}")
        print(f"     ID: {device.device_id}")
        print(f"     Group ID: {device.group_id}")
    print()
    
    # Generate a fingerprint for this profile
    fingerprint = media_manager.generate_fingerprint(profile)
    print(f"Profile Fingerprint: {fingerprint}")
    print()
    
    # Generate device-specific profiles
    print("Device-Specific Profiles:")
    
    # Desktop profile
    desktop_profile = media_manager.get_device_specific_profile("desktop")
    desktop_fingerprint = media_manager.generate_fingerprint(desktop_profile)
    print(f"  Desktop: {len(desktop_profile.audio_input_devices)} audio inputs, {len(desktop_profile.audio_output_devices)} audio outputs, {len(desktop_profile.video_input_devices)} video inputs")
    print(f"  Desktop Fingerprint: {desktop_fingerprint[:16]}...")
    print()
    
    # Mobile profile
    mobile_profile = media_manager.get_device_specific_profile("mobile")
    mobile_fingerprint = media_manager.generate_fingerprint(mobile_profile)
    print(f"  Mobile: {len(mobile_profile.audio_input_devices)} audio inputs, {len(mobile_profile.audio_output_devices)} audio outputs, {len(mobile_profile.video_input_devices)} video inputs")
    print(f"  Mobile Fingerprint: {mobile_fingerprint[:16]}...")
    print()
    
    # Tablet profile
    tablet_profile = media_manager.get_device_specific_profile("tablet")
    tablet_fingerprint = media_manager.generate_fingerprint(tablet_profile)
    print(f"  Tablet: {len(tablet_profile.audio_input_devices)} audio inputs, {len(tablet_profile.audio_output_devices)} audio outputs, {len(tablet_profile.video_input_devices)} video inputs")
    print(f"  Tablet Fingerprint: {tablet_fingerprint[:16]}...")
    print()
    
    # Check profile consistency
    print("Profile Consistency Checks:")
    print(f"  Random Profile Consistent: {media_manager.are_profiles_consistent(profile)}")
    print(f"  Desktop Profile Consistent: {media_manager.are_profiles_consistent(desktop_profile)}")
    print(f"  Mobile Profile Consistent: {media_manager.are_profiles_consistent(mobile_profile)}")
    print(f"  Tablet Profile Consistent: {media_manager.are_profiles_consistent(tablet_profile)}")
    print()
    
    # Generate JavaScript code for spoofing
    js_code = media_manager._generate_spoofing_js(profile)
    print(f"Generated JavaScript Code Length: {len(js_code)} characters")
    print("JavaScript code would be used to spoof media device information in browser contexts.")


if __name__ == "__main__":
    asyncio.run(main())