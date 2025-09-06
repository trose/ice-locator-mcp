"""
Tests for the HardwareConcurrencyPlatformManager module.
"""

import pytest
import asyncio
import random
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.hardware_concurrency_platform_manager import HardwareConcurrencyPlatformManager, HardwareConcurrencyPlatformProfile


class TestHardwareConcurrencyPlatformManager:
    """Test cases for the HardwareConcurrencyPlatformManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.hardware_manager = HardwareConcurrencyPlatformManager()
    
    def test_hardware_concurrency_platform_profile_creation(self):
        """Test HardwareConcurrencyPlatformProfile dataclass creation and methods."""
        profile = HardwareConcurrencyPlatformProfile(
            hardware_concurrency=8,
            platform="Win32",
            os_family="Windows",
            architecture="64-bit",
            cpu_class="x86_64",
            device_memory=16,
            device_type="desktop_windows",
            is_consistent=True
        )
        
        # Test to_dict method
        profile_dict = profile.to_dict()
        assert isinstance(profile_dict, dict)
        assert profile_dict["hardware_concurrency"] == 8
        assert profile_dict["platform"] == "Win32"
        assert profile_dict["os_family"] == "Windows"
        assert profile_dict["device_memory"] == 16
        
        # Test from_dict method
        new_profile = HardwareConcurrencyPlatformProfile.from_dict(profile_dict)
        assert new_profile.hardware_concurrency == profile.hardware_concurrency
        assert new_profile.platform == profile.platform
        assert new_profile.os_family == profile.os_family
        assert new_profile.device_memory == profile.device_memory
    
    def test_get_random_profile(self):
        """Test getting random hardware concurrency and platform profile."""
        profile = self.hardware_manager.get_random_profile()
        assert isinstance(profile, HardwareConcurrencyPlatformProfile)
        assert isinstance(profile.hardware_concurrency, int)
        assert isinstance(profile.platform, str)
        assert isinstance(profile.os_family, str)
        assert isinstance(profile.architecture, str)
        assert isinstance(profile.cpu_class, str)
        assert isinstance(profile.device_memory, int)
        assert isinstance(profile.device_type, str)
        assert isinstance(profile.is_consistent, bool)
        
        # Check value ranges
        assert 1 <= profile.hardware_concurrency <= 64
        assert 1 <= profile.device_memory <= 128
        assert profile.is_consistent is True
    
    def test_get_device_specific_profile(self):
        """Test getting device-specific hardware concurrency and platform profile."""
        # Test desktop Windows profile
        win_profile = self.hardware_manager.get_device_specific_profile("desktop_windows")
        assert isinstance(win_profile, HardwareConcurrencyPlatformProfile)
        assert win_profile.platform == "Win32"
        assert win_profile.os_family == "Windows"
        assert win_profile.cpu_class == "x86_64"
        
        # Test desktop macOS profile
        mac_profile = self.hardware_manager.get_device_specific_profile("desktop_macos")
        assert isinstance(mac_profile, HardwareConcurrencyPlatformProfile)
        assert mac_profile.platform == "MacIntel"
        assert mac_profile.os_family == "macOS"
        assert mac_profile.cpu_class == "x86_64"
        
        # Test mobile Android profile
        android_profile = self.hardware_manager.get_device_specific_profile("mobile_android")
        assert isinstance(android_profile, HardwareConcurrencyPlatformProfile)
        assert android_profile.platform == "Linux armv8l"
        assert android_profile.os_family == "Android"
        assert android_profile.cpu_class == "ARM"
        
        # Test unknown device type (should return random profile)
        unknown_profile = self.hardware_manager.get_device_specific_profile("unknown")
        assert isinstance(unknown_profile, HardwareConcurrencyPlatformProfile)
    
    def test_generate_fingerprint(self):
        """Test generating hardware concurrency and platform fingerprint."""
        profile = self.hardware_manager.get_random_profile()
        fingerprint = self.hardware_manager.generate_fingerprint(profile)
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64  # SHA256 hash length
        
        # Test that same profiles generate same fingerprint
        fingerprint2 = self.hardware_manager.generate_fingerprint(profile)
        assert fingerprint == fingerprint2
    
    def test_are_profiles_consistent(self):
        """Test checking if hardware concurrency and platform profiles are consistent."""
        # Test with valid profile
        valid_profile = self.hardware_manager.get_random_profile()
        assert self.hardware_manager.are_profiles_consistent(valid_profile) is True
        
        # Test with invalid profile (unreasonable hardware concurrency)
        invalid_profile = HardwareConcurrencyPlatformProfile(
            hardware_concurrency=100,  # Too high
            platform="Win32",
            os_family="Windows",
            architecture="64-bit",
            cpu_class="x86_64",
            device_memory=16,
            device_type="desktop_windows",
            is_consistent=True
        )
        assert self.hardware_manager.are_profiles_consistent(invalid_profile) is False
        
        # Test with invalid profile (inconsistent platform and OS family)
        inconsistent_profile = HardwareConcurrencyPlatformProfile(
            hardware_concurrency=8,
            platform="Win32",
            os_family="macOS",  # Inconsistent with platform
            architecture="64-bit",
            cpu_class="x86_64",
            device_memory=16,
            device_type="desktop_windows",
            is_consistent=True
        )
        assert self.hardware_manager.are_profiles_consistent(inconsistent_profile) is False
    
    def test_generate_masking_js(self):
        """Test generating hardware concurrency and platform masking JavaScript."""
        profile = self.hardware_manager.get_random_profile()
        js_code = self.hardware_manager._generate_masking_js(profile)
        
        assert isinstance(js_code, str)
        assert len(js_code) > 0
        assert "Advanced Hardware Concurrency and Platform Information Masking" in js_code
        assert "hardwareConcurrency" in js_code
        assert "platform" in js_code
        assert "cpuClass" in js_code
        assert "deviceMemory" in js_code
        assert str(profile.hardware_concurrency) in js_code
        assert profile.platform.replace('"', '\\"') in js_code


if __name__ == "__main__":
    pytest.main([__file__])