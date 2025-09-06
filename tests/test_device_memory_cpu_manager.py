"""
Tests for the DeviceMemoryCPUManager module.
"""

import pytest
import asyncio
import random
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.device_memory_cpu_manager import DeviceMemoryCPUManager, DeviceMemoryCPUProfile


class TestDeviceMemoryCPUManager:
    """Test cases for the DeviceMemoryCPUManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.device_manager = DeviceMemoryCPUManager()
    
    def test_device_memory_cpu_profile_creation(self):
        """Test DeviceMemoryCPUProfile dataclass creation and methods."""
        profile = DeviceMemoryCPUProfile(
            device_memory=16,
            cpu_class="x86_64",
            hardware_concurrency=8,
            architecture="64-bit",
            device_type="desktop_high_end",
            is_consistent=True
        )
        
        # Test to_dict method
        profile_dict = profile.to_dict()
        assert isinstance(profile_dict, dict)
        assert profile_dict["device_memory"] == 16
        assert profile_dict["cpu_class"] == "x86_64"
        assert profile_dict["hardware_concurrency"] == 8
        assert profile_dict["device_type"] == "desktop_high_end"
        
        # Test from_dict method
        new_profile = DeviceMemoryCPUProfile.from_dict(profile_dict)
        assert new_profile.device_memory == profile.device_memory
        assert new_profile.cpu_class == profile.cpu_class
        assert new_profile.hardware_concurrency == profile.hardware_concurrency
        assert new_profile.device_type == profile.device_type
    
    def test_get_random_profile(self):
        """Test getting random device memory and CPU class profile."""
        profile = self.device_manager.get_random_profile()
        assert isinstance(profile, DeviceMemoryCPUProfile)
        assert isinstance(profile.device_memory, int)
        assert isinstance(profile.cpu_class, str)
        assert isinstance(profile.hardware_concurrency, int)
        assert isinstance(profile.architecture, str)
        assert isinstance(profile.device_type, str)
        assert isinstance(profile.is_consistent, bool)
        
        # Check value ranges
        assert 1 <= profile.device_memory <= 128
        assert 1 <= profile.hardware_concurrency <= 64
        assert profile.is_consistent is True
    
    def test_get_device_specific_profile(self):
        """Test getting device-specific device memory and CPU class profile."""
        # Test desktop high-end profile
        high_end_profile = self.device_manager.get_device_specific_profile("desktop_high_end")
        assert isinstance(high_end_profile, DeviceMemoryCPUProfile)
        assert high_end_profile.cpu_class == "x86_64"
        assert high_end_profile.architecture == "64-bit"
        assert 16 <= high_end_profile.device_memory <= 64
        
        # Test mobile low-end profile
        low_end_profile = self.device_manager.get_device_specific_profile("mobile_low_end")
        assert isinstance(low_end_profile, DeviceMemoryCPUProfile)
        assert low_end_profile.cpu_class == "ARM"
        assert low_end_profile.architecture == "32-bit"
        assert 2 <= low_end_profile.device_memory <= 6
        
        # Test tablet profile
        tablet_profile = self.device_manager.get_device_specific_profile("tablet")
        assert isinstance(tablet_profile, DeviceMemoryCPUProfile)
        assert tablet_profile.cpu_class == "ARM"
        assert tablet_profile.architecture == "64-bit"
        
        # Test unknown device type (should return random profile)
        unknown_profile = self.device_manager.get_device_specific_profile("unknown")
        assert isinstance(unknown_profile, DeviceMemoryCPUProfile)
    
    def test_generate_fingerprint(self):
        """Test generating device memory and CPU class fingerprint."""
        profile = self.device_manager.get_random_profile()
        fingerprint = self.device_manager.generate_fingerprint(profile)
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64  # SHA256 hash length
        
        # Test that same profiles generate same fingerprint
        fingerprint2 = self.device_manager.generate_fingerprint(profile)
        assert fingerprint == fingerprint2
    
    def test_are_profiles_consistent(self):
        """Test checking if device memory and CPU class profiles are consistent."""
        # Test with valid profile
        valid_profile = self.device_manager.get_random_profile()
        assert self.device_manager.are_profiles_consistent(valid_profile) is True
        
        # Test with invalid profile (unreasonable device memory)
        invalid_profile = DeviceMemoryCPUProfile(
            device_memory=200,  # Too high
            cpu_class="x86_64",
            hardware_concurrency=8,
            architecture="64-bit",
            device_type="desktop_high_end",
            is_consistent=True
        )
        assert self.device_manager.are_profiles_consistent(invalid_profile) is False
        
        # Test with invalid profile (inconsistent CPU class and device type)
        inconsistent_profile = DeviceMemoryCPUProfile(
            device_memory=4,
            cpu_class="x86_64",  # Should be ARM for mobile
            hardware_concurrency=4,
            architecture="64-bit",
            device_type="mobile_low_end",
            is_consistent=True
        )
        assert self.device_manager.are_profiles_consistent(inconsistent_profile) is False
    
    def test_generate_spoofing_js(self):
        """Test generating device memory and CPU class spoofing JavaScript."""
        profile = self.device_manager.get_random_profile()
        js_code = self.device_manager._generate_spoofing_js(profile)
        
        assert isinstance(js_code, str)
        assert len(js_code) > 0
        assert "Advanced Device Memory and CPU Class Spoofing" in js_code
        assert "deviceMemory" in js_code
        assert "cpuClass" in js_code
        assert "hardwareConcurrency" in js_code
        assert str(profile.device_memory) in js_code
        assert profile.cpu_class.replace('"', '\\"') in js_code
        assert str(profile.hardware_concurrency) in js_code


if __name__ == "__main__":
    pytest.main([__file__])