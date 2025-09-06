"""
Tests for the AudioFingerprintingProtectionManager module.
"""

import pytest
import asyncio
import random
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.audio_fingerprinting_protection import AudioFingerprintingProtectionManager, AudioFingerprintingProfile


class TestAudioFingerprintingProtectionManager:
    """Test cases for the AudioFingerprintingProtectionManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.audio_manager = AudioFingerprintingProtectionManager()
    
    def test_audio_fingerprinting_profile_creation(self):
        """Test AudioFingerprintingProfile dataclass creation and methods."""
        profile = AudioFingerprintingProfile(
            sample_rate=44100,
            channel_count=2,
            latency_hint=0.01,
            oscillator_type="sine",
            oscillator_frequency=440.0,
            oscillator_detune=0,
            fft_size=2048,
            min_decibels=-100.0,
            max_decibels=-30.0,
            smoothing_time_constant=0.8,
            device_type="desktop_high_end",
            is_consistent=True
        )
        
        # Test to_dict method
        profile_dict = profile.to_dict()
        assert isinstance(profile_dict, dict)
        assert profile_dict["sample_rate"] == 44100
        assert profile_dict["channel_count"] == 2
        assert profile_dict["oscillator_type"] == "sine"
        assert profile_dict["device_type"] == "desktop_high_end"
        
        # Test from_dict method
        new_profile = AudioFingerprintingProfile.from_dict(profile_dict)
        assert new_profile.sample_rate == profile.sample_rate
        assert new_profile.channel_count == profile.channel_count
        assert new_profile.oscillator_type == profile.oscillator_type
        assert new_profile.device_type == profile.device_type
    
    def test_get_random_profile(self):
        """Test getting random audio fingerprinting protection profile."""
        profile = self.audio_manager.get_random_profile()
        assert isinstance(profile, AudioFingerprintingProfile)
        assert isinstance(profile.sample_rate, int)
        assert isinstance(profile.channel_count, int)
        assert isinstance(profile.latency_hint, float)
        assert isinstance(profile.oscillator_type, str)
        assert isinstance(profile.oscillator_frequency, float)
        assert isinstance(profile.oscillator_detune, int)
        assert isinstance(profile.fft_size, int)
        assert isinstance(profile.min_decibels, float)
        assert isinstance(profile.max_decibels, float)
        assert isinstance(profile.smoothing_time_constant, float)
        assert isinstance(profile.device_type, str)
        assert isinstance(profile.is_consistent, bool)
        
        # Check value ranges
        assert 8000 <= profile.sample_rate <= 192000
        assert 1 <= profile.channel_count <= 32
        assert 0 <= profile.latency_hint <= 1
        assert profile.oscillator_frequency >= 20
        assert profile.oscillator_detune >= -1200
        assert profile.fft_size >= 32
        assert profile.min_decibels < profile.max_decibels
        assert 0 <= profile.smoothing_time_constant <= 1
        assert profile.is_consistent is True
    
    def test_get_device_specific_profile(self):
        """Test getting device-specific audio fingerprinting protection profile."""
        # Test desktop high-end profile
        high_end_profile = self.audio_manager.get_device_specific_profile("desktop_high_end")
        assert isinstance(high_end_profile, AudioFingerprintingProfile)
        assert high_end_profile.sample_rate >= 44100
        assert high_end_profile.channel_count >= 2
        assert "desktop_high_end" in high_end_profile.device_type
        
        # Test mobile low-end profile
        low_end_profile = self.audio_manager.get_device_specific_profile("mobile_low_end")
        assert isinstance(low_end_profile, AudioFingerprintingProfile)
        assert low_end_profile.sample_rate >= 22050
        assert low_end_profile.channel_count >= 1
        assert "mobile_low_end" in low_end_profile.device_type
        
        # Test tablet profile
        tablet_profile = self.audio_manager.get_device_specific_profile("tablet")
        assert isinstance(tablet_profile, AudioFingerprintingProfile)
        assert tablet_profile.sample_rate >= 44100
        assert tablet_profile.channel_count >= 1
        assert "tablet" in tablet_profile.device_type
        
        # Test unknown device type (should return random profile)
        unknown_profile = self.audio_manager.get_device_specific_profile("unknown")
        assert isinstance(unknown_profile, AudioFingerprintingProfile)
    
    def test_generate_fingerprint(self):
        """Test generating audio fingerprinting protection fingerprint."""
        profile = self.audio_manager.get_random_profile()
        fingerprint = self.audio_manager.generate_fingerprint(profile)
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64  # SHA256 hash length
        
        # Test that same profiles generate same fingerprint
        fingerprint2 = self.audio_manager.generate_fingerprint(profile)
        assert fingerprint == fingerprint2
    
    def test_are_profiles_consistent(self):
        """Test checking if audio fingerprinting profiles are consistent."""
        # Test with valid profile
        valid_profile = self.audio_manager.get_random_profile()
        assert self.audio_manager.are_profiles_consistent(valid_profile) is True
        
        # Test with invalid profile (unreasonable sample rate)
        invalid_profile = AudioFingerprintingProfile(
            sample_rate=1000000,  # Too high
            channel_count=2,
            latency_hint=0.01,
            oscillator_type="sine",
            oscillator_frequency=440.0,
            oscillator_detune=0,
            fft_size=2048,
            min_decibels=-100.0,
            max_decibels=-30.0,
            smoothing_time_constant=0.8,
            device_type="desktop_high_end",
            is_consistent=True
        )
        assert self.audio_manager.are_profiles_consistent(invalid_profile) is False
        
        # Test with invalid profile (FFT size not power of 2)
        invalid_profile2 = AudioFingerprintingProfile(
            sample_rate=44100,
            channel_count=2,
            latency_hint=0.01,
            oscillator_type="sine",
            oscillator_frequency=440.0,
            oscillator_detune=0,
            fft_size=1000,  # Not power of 2
            min_decibels=-100.0,
            max_decibels=-30.0,
            smoothing_time_constant=0.8,
            device_type="desktop_high_end",
            is_consistent=True
        )
        assert self.audio_manager.are_profiles_consistent(invalid_profile2) is False
        
        # Test with invalid profile (min decibels >= max decibels)
        invalid_profile3 = AudioFingerprintingProfile(
            sample_rate=44100,
            channel_count=2,
            latency_hint=0.01,
            oscillator_type="sine",
            oscillator_frequency=440.0,
            oscillator_detune=0,
            fft_size=2048,
            min_decibels=-30.0,  # Higher than max
            max_decibels=-100.0,  # Lower than min
            smoothing_time_constant=0.8,
            device_type="desktop_high_end",
            is_consistent=True
        )
        assert self.audio_manager.are_profiles_consistent(invalid_profile3) is False
    
    def test_generate_protection_js(self):
        """Test generating audio fingerprinting protection JavaScript."""
        profile = self.audio_manager.get_random_profile()
        js_code = self.audio_manager._generate_protection_js(profile)
        
        assert isinstance(js_code, str)
        assert len(js_code) > 0
        assert "Advanced Audio Fingerprinting Protection" in js_code
        assert "AudioContext" in js_code
        assert "createOscillator" in js_code
        assert "createAnalyser" in js_code
        assert str(profile.sample_rate) in js_code
        assert profile.oscillator_type.replace('"', '\\"') in js_code
        assert str(profile.fft_size) in js_code


if __name__ == "__main__":
    pytest.main([__file__])