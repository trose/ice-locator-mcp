"""
Tests for the FontEnumerationProtectionManager module.
"""

import pytest
import asyncio
import random
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.font_enumeration_protection import FontEnumerationProtectionManager, FontEnumerationProfile


class TestFontEnumerationProtectionManager:
    """Test cases for the FontEnumerationProtectionManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.font_manager = FontEnumerationProtectionManager()
    
    def test_font_enumeration_profile_creation(self):
        """Test FontEnumerationProfile dataclass creation and methods."""
        profile = FontEnumerationProfile(
            font_families=["Arial", "Times New Roman", "Courier New"],
            include_emoji_fonts=True,
            include_monospace_fonts=True,
            include_serif_fonts=True,
            include_sans_serif_fonts=True,
            include_cursive_fonts=False,
            include_fantasy_fonts=False,
            device_type="desktop_windows",
            is_consistent=True
        )
        
        # Test to_dict method
        profile_dict = profile.to_dict()
        assert isinstance(profile_dict, dict)
        assert "Arial" in profile_dict["font_families"]
        assert profile_dict["include_emoji_fonts"] is True
        assert profile_dict["device_type"] == "desktop_windows"
        
        # Test from_dict method
        new_profile = FontEnumerationProfile.from_dict(profile_dict)
        assert "Arial" in new_profile.font_families
        assert new_profile.include_emoji_fonts is True
        assert new_profile.device_type == "desktop_windows"
    
    def test_get_random_profile(self):
        """Test getting random font enumeration protection profile."""
        profile = self.font_manager.get_random_profile()
        assert isinstance(profile, FontEnumerationProfile)
        assert isinstance(profile.font_families, list)
        assert isinstance(profile.include_emoji_fonts, bool)
        assert isinstance(profile.include_monospace_fonts, bool)
        assert isinstance(profile.include_serif_fonts, bool)
        assert isinstance(profile.include_sans_serif_fonts, bool)
        assert isinstance(profile.include_cursive_fonts, bool)
        assert isinstance(profile.include_fantasy_fonts, bool)
        assert isinstance(profile.device_type, str)
        assert isinstance(profile.is_consistent, bool)
        
        # Check that font families list is not empty
        assert len(profile.font_families) > 0
        
        # Check value ranges
        assert 10 <= len(profile.font_families) <= 30
        assert profile.is_consistent is True
    
    def test_get_device_specific_profile(self):
        """Test getting device-specific font enumeration protection profile."""
        # Test desktop Windows profile
        windows_profile = self.font_manager.get_device_specific_profile("desktop_windows")
        assert isinstance(windows_profile, FontEnumerationProfile)
        assert "desktop_windows" in windows_profile.device_type
        assert len(windows_profile.font_families) >= 15
        
        # Test mobile iOS profile
        ios_profile = self.font_manager.get_device_specific_profile("mobile_ios")
        assert isinstance(ios_profile, FontEnumerationProfile)
        assert "mobile_ios" in ios_profile.device_type
        assert len(ios_profile.font_families) >= 15
        
        # Test tablet profile
        tablet_profile = self.font_manager.get_device_specific_profile("tablet")
        assert isinstance(tablet_profile, FontEnumerationProfile)
        assert "tablet" in tablet_profile.device_type
        assert len(tablet_profile.font_families) >= 15
        
        # Test unknown device type (should return random profile)
        unknown_profile = self.font_manager.get_device_specific_profile("unknown")
        assert isinstance(unknown_profile, FontEnumerationProfile)
    
    def test_generate_fingerprint(self):
        """Test generating font enumeration protection fingerprint."""
        profile = self.font_manager.get_random_profile()
        fingerprint = self.font_manager.generate_fingerprint(profile)
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64  # SHA256 hash length
        
        # Test that same profiles generate same fingerprint
        fingerprint2 = self.font_manager.generate_fingerprint(profile)
        assert fingerprint == fingerprint2
    
    def test_are_profiles_consistent(self):
        """Test checking if font enumeration profiles are consistent."""
        # Test with valid profile
        valid_profile = self.font_manager.get_random_profile()
        assert self.font_manager.are_profiles_consistent(valid_profile) is True
        
        # Test with invalid profile (empty font families)
        invalid_profile = FontEnumerationProfile(
            font_families=[],
            include_emoji_fonts=True,
            include_monospace_fonts=True,
            include_serif_fonts=True,
            include_sans_serif_fonts=True,
            include_cursive_fonts=False,
            include_fantasy_fonts=False,
            device_type="desktop_windows",
            is_consistent=True
        )
        assert self.font_manager.are_profiles_consistent(invalid_profile) is False
        
        # Test with invalid profile (too many font families)
        invalid_profile2 = FontEnumerationProfile(
            font_families=["Font" + str(i) for i in range(150)],  # 150 fonts
            include_emoji_fonts=True,
            include_monospace_fonts=True,
            include_serif_fonts=True,
            include_sans_serif_fonts=True,
            include_cursive_fonts=False,
            include_fantasy_fonts=False,
            device_type="mobile_android",
            is_consistent=True
        )
        assert self.font_manager.are_profiles_consistent(invalid_profile2) is False
    
    def test_generate_protection_js(self):
        """Test generating font enumeration protection JavaScript."""
        profile = self.font_manager.get_random_profile()
        js_code = self.font_manager._generate_protection_js(profile)
        
        assert isinstance(js_code, str)
        assert len(js_code) > 0
        assert "Advanced Font Enumeration Protection" in js_code
        assert "measureText" in js_code
        assert "fillText" in js_code
        assert "strokeText" in js_code


if __name__ == "__main__":
    pytest.main([__file__])