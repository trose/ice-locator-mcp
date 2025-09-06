"""
Tests for the TimezoneLocaleManager module.
"""

import pytest
import asyncio
import random
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.timezone_locale_manager import TimezoneLocaleManager, TimezoneProfile, LocaleProfile


class TestTimezoneLocaleManager:
    """Test cases for the TimezoneLocaleManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.timezone_locale_manager = TimezoneLocaleManager()
    
    def test_timezone_profile_creation(self):
        """Test TimezoneProfile dataclass creation and methods."""
        timezone = TimezoneProfile(
            timezone_id="America/New_York",
            offset=-300,
            locale="en-US",
            language="en",
            country_code="US",
            geolocation={"latitude": 40.7128, "longitude": -74.0060}
        )
        
        # Test to_dict method
        timezone_dict = timezone.to_dict()
        assert isinstance(timezone_dict, dict)
        assert timezone_dict["timezone_id"] == "America/New_York"
        assert timezone_dict["offset"] == -300
        assert timezone_dict["locale"] == "en-US"
        assert timezone_dict["geolocation"]["latitude"] == 40.7128
        
        # Test from_dict method
        new_timezone = TimezoneProfile.from_dict(timezone_dict)
        assert new_timezone.timezone_id == timezone.timezone_id
        assert new_timezone.offset == timezone.offset
        assert new_timezone.locale == timezone.locale
        assert new_timezone.geolocation["latitude"] == timezone.geolocation["latitude"]
    
    def test_locale_profile_creation(self):
        """Test LocaleProfile dataclass creation and methods."""
        locale = LocaleProfile(
            locale="en-US",
            language="en",
            country_code="US",
            currency="USD",
            numbering_system="latn",
            calendar="gregory",
            text_direction="ltr"
        )
        
        # Test to_dict method
        locale_dict = locale.to_dict()
        assert isinstance(locale_dict, dict)
        assert locale_dict["locale"] == "en-US"
        assert locale_dict["language"] == "en"
        assert locale_dict["currency"] == "USD"
        assert locale_dict["text_direction"] == "ltr"
        
        # Test from_dict method
        new_locale = LocaleProfile.from_dict(locale_dict)
        assert new_locale.locale == locale.locale
        assert new_locale.language == locale.language
        assert new_locale.currency == locale.currency
        assert new_locale.text_direction == locale.text_direction
    
    def test_get_random_timezone_profile(self):
        """Test getting random timezone profile."""
        timezone_profile = self.timezone_locale_manager.get_random_timezone_profile()
        assert isinstance(timezone_profile, TimezoneProfile)
        assert isinstance(timezone_profile.timezone_id, str)
        assert isinstance(timezone_profile.offset, int)
        assert isinstance(timezone_profile.locale, str)
        assert isinstance(timezone_profile.geolocation, dict)
        
        # Check that we have valid geolocation data
        assert "latitude" in timezone_profile.geolocation
        assert "longitude" in timezone_profile.geolocation
    
    def test_get_random_locale_profile(self):
        """Test getting random locale profile."""
        locale_profile = self.timezone_locale_manager.get_random_locale_profile()
        assert isinstance(locale_profile, LocaleProfile)
        assert isinstance(locale_profile.locale, str)
        assert isinstance(locale_profile.language, str)
        assert isinstance(locale_profile.currency, str)
        assert isinstance(locale_profile.text_direction, str)
        
        # Check valid text direction
        assert locale_profile.text_direction in ["ltr", "rtl"]
    
    def test_generate_realistic_timezone_locale(self):
        """Test generating realistic timezone/locale combination."""
        timezone_profile, locale_profile = self.timezone_locale_manager.generate_realistic_timezone_locale()
        assert isinstance(timezone_profile, TimezoneProfile)
        assert isinstance(locale_profile, LocaleProfile)
        
        # Check that the profiles are consistent
        is_consistent = self.timezone_locale_manager.is_consistent_timezone_locale(
            timezone_profile, locale_profile
        )
        assert is_consistent is True
    
    def test_get_timezone_headers(self):
        """Test getting timezone headers."""
        headers = self.timezone_locale_manager.get_timezone_headers("en-US")
        assert isinstance(headers, dict)
        assert "accept-language" in headers
        
        # Test default fallback
        default_headers = self.timezone_locale_manager.get_timezone_headers("invalid-locale")
        assert isinstance(default_headers, dict)
        assert "accept-language" in default_headers
    
    def test_get_timezone_offset(self):
        """Test getting timezone offset."""
        timezone_profile = TimezoneProfile(
            timezone_id="America/New_York",
            offset=-300,
            locale="en-US",
            language="en",
            country_code="US",
            geolocation={"latitude": 40.7128, "longitude": -74.0060}
        )
        
        offset = self.timezone_locale_manager.get_timezone_offset(timezone_profile)
        assert isinstance(offset, int)
        assert offset == -300
    
    def test_get_geolocation(self):
        """Test getting geolocation."""
        timezone_profile = TimezoneProfile(
            timezone_id="America/New_York",
            offset=-300,
            locale="en-US",
            language="en",
            country_code="US",
            geolocation={"latitude": 40.7128, "longitude": -74.0060}
        )
        
        geolocation = self.timezone_locale_manager.get_geolocation(timezone_profile)
        assert isinstance(geolocation, dict)
        assert "latitude" in geolocation
        assert "longitude" in geolocation
        assert geolocation["latitude"] == 40.7128
        assert geolocation["longitude"] == -74.0060
    
    def test_is_consistent_timezone_locale(self):
        """Test checking if timezone and locale profiles are consistent."""
        # Test matching profiles
        timezone_profile = TimezoneProfile(
            timezone_id="America/New_York",
            offset=-300,
            locale="en-US",
            language="en",
            country_code="US",
            geolocation={"latitude": 40.7128, "longitude": -74.0060}
        )
        
        locale_profile = LocaleProfile(
            locale="en-US",
            language="en",
            country_code="US",
            currency="USD",
            numbering_system="latn",
            calendar="gregory",
            text_direction="ltr"
        )
        
        is_consistent = self.timezone_locale_manager.is_consistent_timezone_locale(
            timezone_profile, locale_profile
        )
        assert is_consistent is True
        
        # Test compatible profiles
        locale_profile_gb = LocaleProfile(
            locale="en-GB",
            language="en",
            country_code="GB",
            currency="GBP",
            numbering_system="latn",
            calendar="gregory",
            text_direction="ltr"
        )
        
        is_consistent_compatible = self.timezone_locale_manager.is_consistent_timezone_locale(
            timezone_profile, locale_profile_gb
        )
        assert is_consistent_compatible is True
        
        # Test incompatible profiles
        locale_profile_ja = LocaleProfile(
            locale="ja-JP",
            language="ja",
            country_code="JP",
            currency="JPY",
            numbering_system="latn",
            calendar="gregory",
            text_direction="ltr"
        )
        
        is_consistent_incompatible = self.timezone_locale_manager.is_consistent_timezone_locale(
            timezone_profile, locale_profile_ja
        )
        assert is_consistent_incompatible is False


if __name__ == "__main__":
    pytest.main([__file__])