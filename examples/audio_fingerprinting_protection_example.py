"""
Example demonstrating advanced audio fingerprinting protection.
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.audio_fingerprinting_protection import AudioFingerprintingProtectionManager, AudioFingerprintingProfile


async def main():
    """Demonstrate AudioFingerprintingProtectionManager usage."""
    # Create AudioFingerprintingProtectionManager instance
    audio_protection_manager = AudioFingerprintingProtectionManager()
    
    # Generate a random audio fingerprinting protection profile
    profile = audio_protection_manager.get_random_profile()
    print("Random Audio Fingerprinting Protection Profile:")
    print(f"  Sample Rate: {profile.sample_rate} Hz")
    print(f"  Channel Count: {profile.channel_count}")
    print(f"  Latency Hint: {profile.latency_hint}")
    print(f"  Oscillator Type: {profile.oscillator_type}")
    print(f"  Oscillator Frequency: {profile.oscillator_frequency} Hz")
    print(f"  Oscillator Detune: {profile.oscillator_detune} cents")
    print(f"  FFT Size: {profile.fft_size}")
    print(f"  Min Decibels: {profile.min_decibels} dB")
    print(f"  Max Decibels: {profile.max_decibels} dB")
    print(f"  Smoothing Time Constant: {profile.smoothing_time_constant}")
    print(f"  Device Type: {profile.device_type}")
    print(f"  Is Consistent: {profile.is_consistent}")
    print()
    
    # Generate device-specific profiles
    desktop_profile = audio_protection_manager.get_device_specific_profile("desktop_high_end")
    mobile_profile = audio_protection_manager.get_device_specific_profile("mobile_low_end")
    tablet_profile = audio_protection_manager.get_device_specific_profile("tablet")
    
    print("Device-Specific Audio Profiles:")
    print(f"  High-end Desktop - Sample Rate: {desktop_profile.sample_rate} Hz, Channels: {desktop_profile.channel_count}")
    print(f"  Low-end Mobile - Sample Rate: {mobile_profile.sample_rate} Hz, Channels: {mobile_profile.channel_count}")
    print(f"  Tablet - Sample Rate: {tablet_profile.sample_rate} Hz, Channels: {tablet_profile.channel_count}")
    print()
    
    # Generate an audio fingerprint
    fingerprint = audio_protection_manager.generate_fingerprint(profile)
    print("Audio Fingerprint:")
    print(f"  Hash: {fingerprint}")
    print()
    
    # Check profile consistency
    is_consistent = audio_protection_manager.are_profiles_consistent(profile)
    print("Profile Consistency:")
    print(f"  Audio profile consistent: {is_consistent}")
    print()
    
    # Generate protection JavaScript code
    js_code = audio_protection_manager._generate_protection_js(profile)
    print("Generated JavaScript Code:")
    print(f"  JS length: {len(js_code)} characters")
    print()
    
    # Example of creating a custom profile
    custom_profile = AudioFingerprintingProfile(
        sample_rate=48000,
        channel_count=2,
        latency_hint=0.005,
        oscillator_type="sine",
        oscillator_frequency=440.0,
        oscillator_detune=10,
        fft_size=1024,
        min_decibels=-90.0,
        max_decibels=-20.0,
        smoothing_time_constant=0.7,
        device_type="desktop_mid_range",
        is_consistent=True
    )
    
    print("Custom Audio Profile:")
    print(f"  Custom sample rate: {custom_profile.sample_rate} Hz")
    print(f"  Custom oscillator type: {custom_profile.oscillator_type}")
    print(f"  Custom FFT size: {custom_profile.fft_size}")
    print()
    
    # Generate fingerprint for custom profile
    custom_fingerprint = audio_protection_manager.generate_fingerprint(custom_profile)
    print("Custom Profile Fingerprint:")
    print(f"  Hash: {custom_fingerprint}")
    print()


if __name__ == "__main__":
    asyncio.run(main())