"""
Tests for the ViewportScreenSpoofingManager module.
"""

import pytest
import asyncio
import random
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.viewport_screen_spoofing import ViewportScreenSpoofingManager, ViewportScreenProfile


class TestViewportScreenSpoofingManager:
    """Test cases for the ViewportScreenSpoofingManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.viewport_manager = ViewportScreenSpoofingManager()
    
    def test_viewport_screen_profile_creation(self):
        """Test ViewportScreenProfile dataclass creation and methods."""
        profile = ViewportScreenProfile(
            screen_width=1920,
            screen_height=1080,
            avail_width=1920,
            avail_height=1040,
            color_depth=24,
            pixel_depth=24,
            viewport_width=1920,
            viewport_height=1040,
            outer_width=1920,
            outer_height=1080,
            device_pixel_ratio=1.0,
            orientation_type="landscape-primary",
            orientation_angle=0,
            device_type="desktop_fhd",
            is_consistent=True
        )
        
        # Test to_dict method
        profile_dict = profile.to_dict()
        assert isinstance(profile_dict, dict)
        assert profile_dict["screen_width"] == 1920
        assert profile_dict["screen_height"] == 1080
        assert profile_dict["device_pixel_ratio"] == 1.0
        assert profile_dict["device_type"] == "desktop_fhd"
        
        # Test from_dict method
        new_profile = ViewportScreenProfile.from_dict(profile_dict)
        assert new_profile.screen_width == profile.screen_width
        assert new_profile.screen_height == profile.screen_height
        assert new_profile.device_pixel_ratio == profile.device_pixel_ratio
        assert new_profile.device_type == profile.device_type
    
    def test_get_random_profile(self):
        """Test getting random viewport and screen dimension profile."""
        profile = self.viewport_manager.get_random_profile()
        assert isinstance(profile, ViewportScreenProfile)
        assert isinstance(profile.screen_width, int)
        assert isinstance(profile.screen_height, int)
        assert isinstance(profile.avail_width, int)
        assert isinstance(profile.avail_height, int)
        assert isinstance(profile.color_depth, int)
        assert isinstance(profile.pixel_depth, int)
        assert isinstance(profile.viewport_width, int)
        assert isinstance(profile.viewport_height, int)
        assert isinstance(profile.outer_width, int)
        assert isinstance(profile.outer_height, int)
        assert isinstance(profile.device_pixel_ratio, float)
        assert isinstance(profile.orientation_type, str)
        assert isinstance(profile.orientation_angle, int)
        assert isinstance(profile.device_type, str)
        assert isinstance(profile.is_consistent, bool)
        
        # Check value ranges
        assert 320 <= profile.screen_width <= 8192
        assert 240 <= profile.screen_height <= 4320
        assert profile.avail_width <= profile.screen_width
        assert profile.avail_height <= profile.screen_height
        assert profile.viewport_width <= profile.screen_width
        assert profile.viewport_height <= profile.screen_height
        assert profile.outer_width >= profile.viewport_width
        assert profile.outer_height >= profile.viewport_height
        assert profile.color_depth in [16, 24, 32]
        assert profile.pixel_depth in [16, 24, 32]
        assert 0.5 <= profile.device_pixel_ratio <= 4.0
        assert profile.orientation_angle in [0, 90, 180, 270]
        assert profile.is_consistent is True
    
    def test_get_device_specific_profile(self):
        """Test getting device-specific viewport and screen dimension profile."""
        # Test desktop 4K profile
        desktop_4k_profile = self.viewport_manager.get_device_specific_profile("desktop_4k")
        assert isinstance(desktop_4k_profile, ViewportScreenProfile)
        assert "desktop_4k" in desktop_4k_profile.device_type
        assert desktop_4k_profile.screen_width >= 2560
        
        # Test mobile high-end profile
        mobile_profile = self.viewport_manager.get_device_specific_profile("mobile_high_end")
        assert isinstance(mobile_profile, ViewportScreenProfile)
        assert "mobile_high_end" in mobile_profile.device_type
        assert mobile_profile.screen_width <= 2000
        
        # Test tablet profile
        tablet_profile = self.viewport_manager.get_device_specific_profile("tablet")
        assert isinstance(tablet_profile, ViewportScreenProfile)
        assert "tablet" in tablet_profile.device_type
        assert tablet_profile.screen_width <= 3000
        
        # Test unknown device type (should return random profile)
        unknown_profile = self.viewport_manager.get_device_specific_profile("unknown")
        assert isinstance(unknown_profile, ViewportScreenProfile)
    
    def test_generate_fingerprint(self):
        """Test generating viewport and screen dimension fingerprint."""
        profile = self.viewport_manager.get_random_profile()
        fingerprint = self.viewport_manager.generate_fingerprint(profile)
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64  # SHA256 hash length
        
        # Test that same profiles generate same fingerprint
        fingerprint2 = self.viewport_manager.generate_fingerprint(profile)
        assert fingerprint == fingerprint2
    
    def test_are_profiles_consistent(self):
        """Test checking if viewport and screen dimension profiles are consistent."""
        # Test with valid profile
        valid_profile = self.viewport_manager.get_random_profile()
        assert self.viewport_manager.are_profiles_consistent(valid_profile) is True
        
        # Test with invalid profile (screen width too small)
        invalid_profile = ViewportScreenProfile(
            screen_width=100,  # Too small
            screen_height=1080,
            avail_width=100,
            avail_height=1040,
            color_depth=24,
            pixel_depth=24,
            viewport_width=100,
            viewport_height=1040,
            outer_width=100,
            outer_height=1080,
            device_pixel_ratio=1.0,
            orientation_type="landscape-primary",
            orientation_angle=0,
            device_type="desktop_fhd",
            is_consistent=True
        )
        assert self.viewport_manager.are_profiles_consistent(invalid_profile) is False
        
        # Test with invalid profile (available width larger than screen width)
        invalid_profile2 = ViewportScreenProfile(
            screen_width=1920,
            screen_height=1080,
            avail_width=2000,  # Larger than screen width
            avail_height=1040,
            color_depth=24,
            pixel_depth=24,
            viewport_width=1920,
            viewport_height=1040,
            outer_width=1920,
            outer_height=1080,
            device_pixel_ratio=1.0,
            orientation_type="landscape-primary",
            orientation_angle=0,
            device_type="desktop_fhd",
            is_consistent=True
        )
        assert self.viewport_manager.are_profiles_consistent(invalid_profile2) is False
    
    def test_generate_spoofing_js(self):
        """Test generating viewport and screen dimension spoofing JavaScript."""
        profile = self.viewport_manager.get_random_profile()
        js_code = self.viewport_manager._generate_spoofing_js(profile)
        
        assert isinstance(js_code, str)
        assert len(js_code) > 0
        assert "Advanced Viewport and Screen Dimension Spoofing" in js_code
        assert "screen" in js_code
        assert "width" in js_code
        assert "height" in js_code
        assert "window" in js_code
        assert "innerWidth" in js_code
        assert "innerHeight" in js_code
        assert str(profile.screen_width) in js_code
        assert str(profile.screen_height) in js_code
        assert str(profile.viewport_width) in js_code
        assert str(profile.viewport_height) in js_code


if __name__ == "__main__":
    pytest.main([__file__])