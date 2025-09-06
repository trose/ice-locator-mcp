"""
Tests for the MediaDeviceSpoofingManager module.
"""

import pytest
import asyncio
import random
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.media_device_spoofing import MediaDeviceSpoofingManager, MediaDeviceProfile, MediaDevice


class TestMediaDeviceSpoofingManager:
    """Test cases for the MediaDeviceSpoofingManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.media_manager = MediaDeviceSpoofingManager()
    
    def test_media_device_creation(self):
        """Test MediaDevice dataclass creation and methods."""
        device = MediaDevice(
            device_id="test-device-id",
            kind="audioinput",
            label="Test Microphone",
            group_id="test-group-id"
        )
        
        # Test to_dict method
        device_dict = device.to_dict()
        assert isinstance(device_dict, dict)
        assert device_dict["device_id"] == "test-device-id"
        assert device_dict["kind"] == "audioinput"
        assert device_dict["label"] == "Test Microphone"
        assert device_dict["group_id"] == "test-group-id"
        
        # Test from_dict method
        new_device = MediaDevice.from_dict(device_dict)
        assert new_device.device_id == device.device_id
        assert new_device.kind == device.kind
        assert new_device.label == device.label
        assert new_device.group_id == device.group_id
    
    def test_media_device_profile_creation(self):
        """Test MediaDeviceProfile dataclass creation and methods."""
        audio_inputs = [
            MediaDevice(
                device_id="audio-input-1",
                kind="audioinput",
                label="Microphone 1",
                group_id="group-1"
            ),
            MediaDevice(
                device_id="audio-input-2",
                kind="audioinput",
                label="Microphone 2",
                group_id="group-2"
            )
        ]
        
        audio_outputs = [
            MediaDevice(
                device_id="audio-output-1",
                kind="audiooutput",
                label="Speakers 1",
                group_id="group-3"
            )
        ]
        
        video_inputs = [
            MediaDevice(
                device_id="video-input-1",
                kind="videoinput",
                label="Camera 1",
                group_id="group-4"
            )
        ]
        
        profile = MediaDeviceProfile(
            audio_input_devices=audio_inputs,
            audio_output_devices=audio_outputs,
            video_input_devices=video_inputs,
            device_type="desktop",
            is_consistent=True
        )
        
        # Test to_dict method
        profile_dict = profile.to_dict()
        assert isinstance(profile_dict, dict)
        assert len(profile_dict["audio_input_devices"]) == 2
        assert len(profile_dict["audio_output_devices"]) == 1
        assert len(profile_dict["video_input_devices"]) == 1
        assert profile_dict["device_type"] == "desktop"
        assert profile_dict["is_consistent"] is True
        
        # Test from_dict method
        new_profile = MediaDeviceProfile.from_dict(profile_dict)
        assert len(new_profile.audio_input_devices) == len(profile.audio_input_devices)
        assert len(new_profile.audio_output_devices) == len(profile.audio_output_devices)
        assert len(new_profile.video_input_devices) == len(profile.video_input_devices)
        assert new_profile.device_type == profile.device_type
        assert new_profile.is_consistent == profile.is_consistent
    
    def test_get_random_profile(self):
        """Test getting random media device profile."""
        profile = self.media_manager.get_random_profile()
        assert isinstance(profile, MediaDeviceProfile)
        assert isinstance(profile.audio_input_devices, list)
        assert isinstance(profile.audio_output_devices, list)
        assert isinstance(profile.video_input_devices, list)
        assert isinstance(profile.device_type, str)
        assert isinstance(profile.is_consistent, bool)
        
        # Check that devices have realistic properties
        for device in profile.audio_input_devices:
            assert isinstance(device, MediaDevice)
            assert isinstance(device.device_id, str)
            assert isinstance(device.kind, str)
            assert isinstance(device.label, str)
            assert isinstance(device.group_id, str)
            assert device.kind == "audioinput"
            assert len(device.device_id) > 0
            assert len(device.label) > 0
            assert len(device.group_id) > 0
        
        for device in profile.audio_output_devices:
            assert isinstance(device, MediaDevice)
            assert isinstance(device.device_id, str)
            assert isinstance(device.kind, str)
            assert isinstance(device.label, str)
            assert isinstance(device.group_id, str)
            assert device.kind == "audiooutput"
            assert len(device.device_id) > 0
            assert len(device.label) > 0
            assert len(device.group_id) > 0
        
        for device in profile.video_input_devices:
            assert isinstance(device, MediaDevice)
            assert isinstance(device.device_id, str)
            assert isinstance(device.kind, str)
            assert isinstance(device.label, str)
            assert isinstance(device.group_id, str)
            assert device.kind == "videoinput"
            assert len(device.device_id) > 0
            assert len(device.label) > 0
            assert len(device.group_id) > 0
        
        # Check device type
        assert profile.device_type in ["desktop", "mobile", "tablet"]
        
        # Check consistency
        assert profile.is_consistent is True
    
    def test_get_device_specific_profile(self):
        """Test getting device-specific media device profile."""
        # Test desktop profile
        desktop_profile = self.media_manager.get_device_specific_profile("desktop")
        assert isinstance(desktop_profile, MediaDeviceProfile)
        assert desktop_profile.device_type == "desktop"
        
        # Test mobile profile
        mobile_profile = self.media_manager.get_device_specific_profile("mobile")
        assert isinstance(mobile_profile, MediaDeviceProfile)
        assert mobile_profile.device_type == "mobile"
        
        # Test tablet profile
        tablet_profile = self.media_manager.get_device_specific_profile("tablet")
        assert isinstance(tablet_profile, MediaDeviceProfile)
        assert tablet_profile.device_type == "tablet"
        
        # Test unknown device type (should return random profile)
        unknown_profile = self.media_manager.get_device_specific_profile("unknown")
        assert isinstance(unknown_profile, MediaDeviceProfile)
    
    def test_generate_fingerprint(self):
        """Test generating media device fingerprint."""
        profile = self.media_manager.get_random_profile()
        fingerprint = self.media_manager.generate_fingerprint(profile)
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64  # SHA256 hash length
        
        # Test that same profiles generate same fingerprint
        fingerprint2 = self.media_manager.generate_fingerprint(profile)
        assert fingerprint == fingerprint2
    
    def test_are_profiles_consistent(self):
        """Test checking if media device profiles are consistent."""
        # Test with valid profile
        valid_profile = self.media_manager.get_random_profile()
        assert self.media_manager.are_profiles_consistent(valid_profile) is True
        
        # Test with invalid profile (wrong device kind)
        invalid_profile = MediaDeviceProfile(
            audio_input_devices=[
                MediaDevice(
                    device_id="test-id",
                    kind="videoinput",  # Wrong kind
                    label="Test Device",
                    group_id="test-group"
                )
            ],
            audio_output_devices=[],
            video_input_devices=[],
            device_type="desktop",
            is_consistent=True
        )
        assert self.media_manager.are_profiles_consistent(invalid_profile) is False
        
        # Test with invalid profile (wrong device type)
        invalid_profile2 = MediaDeviceProfile(
            audio_input_devices=[
                MediaDevice(
                    device_id="test-id",
                    kind="audioinput",
                    label="Test Device",
                    group_id="test-group"
                )
            ],
            audio_output_devices=[],
            video_input_devices=[],
            device_type="unknown_device",  # Invalid device type
            is_consistent=True
        )
        assert self.media_manager.are_profiles_consistent(invalid_profile2) is False
    
    def test_generate_spoofing_js(self):
        """Test generating media device spoofing JavaScript."""
        profile = self.media_manager.get_random_profile()
        js_code = self.media_manager._generate_spoofing_js(profile)
        
        assert isinstance(js_code, str)
        assert len(js_code) > 0
        assert "Advanced Media Device Spoofing" in js_code
        assert "navigator.mediaDevices" in js_code
        assert "enumerateDevices" in js_code
        assert "getUserMedia" in js_code


if __name__ == "__main__":
    pytest.main([__file__])