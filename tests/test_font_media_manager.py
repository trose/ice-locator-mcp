"""
Tests for the FontMediaManager module.
"""

import pytest
import asyncio
import random
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.font_media_manager import FontMediaManager, FontProfile, MediaProfile


class TestFontMediaManager:
    """Test cases for the FontMediaManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.font_media_manager = FontMediaManager()
    
    def test_font_profile_creation(self):
        """Test FontProfile dataclass creation and methods."""
        font = FontProfile(
            name="Arial",
            generic_family="sans-serif",
            is_monospace=False,
            is_serif=False,
            is_sans_serif=True,
            is_display=False,
            is_handwriting=False
        )
        
        # Test to_dict method
        font_dict = font.to_dict()
        assert isinstance(font_dict, dict)
        assert font_dict["name"] == "Arial"
        assert font_dict["generic_family"] == "sans-serif"
        assert font_dict["is_sans_serif"] is True
        
        # Test from_dict method
        new_font = FontProfile.from_dict(font_dict)
        assert new_font.name == font.name
        assert new_font.generic_family == font.generic_family
        assert new_font.is_sans_serif == font.is_sans_serif
    
    def test_media_profile_creation(self):
        """Test MediaProfile dataclass creation and methods."""
        media = MediaProfile(
            audio_codecs=["audio/mp3", "audio/wav"],
            video_codecs=["video/mp4", "video/webm"],
            media_devices=[{"deviceId": "test123", "kind": "audioinput", "label": "Test Mic", "groupId": "group123"}],
            webgl_extensions=["WEBGL_debug_renderer_info", "OES_texture_float"],
            webgl_parameters={"VERSION": "WebGL 1.0", "VENDOR": "Test Vendor"}
        )
        
        # Test to_dict method
        media_dict = media.to_dict()
        assert isinstance(media_dict, dict)
        assert "audio/mp3" in media_dict["audio_codecs"]
        assert "video/mp4" in media_dict["video_codecs"]
        assert len(media_dict["media_devices"]) == 1
        assert "WEBGL_debug_renderer_info" in media_dict["webgl_extensions"]
        assert media_dict["webgl_parameters"]["VERSION"] == "WebGL 1.0"
        
        # Test from_dict method
        new_media = MediaProfile.from_dict(media_dict)
        assert "audio/mp3" in new_media.audio_codecs
        assert "video/mp4" in new_media.video_codecs
        assert len(new_media.media_devices) == 1
        assert "WEBGL_debug_renderer_info" in new_media.webgl_extensions
        assert new_media.webgl_parameters["VERSION"] == "WebGL 1.0"
    
    def test_get_random_font_list(self):
        """Test getting random font list."""
        font_list = self.font_media_manager.get_random_font_list(10)
        assert isinstance(font_list, list)
        assert len(font_list) == 10
        assert all(isinstance(font, FontProfile) for font in font_list)
        
        # Test with default count
        font_list_default = self.font_media_manager.get_random_font_list()
        assert len(font_list_default) == 20
        
        # Test with count larger than available fonts
        font_list_large = self.font_media_manager.get_random_font_list(100)
        assert len(font_list_large) <= len(self.font_media_manager.common_fonts)
    
    def test_get_random_media_profile(self):
        """Test getting random media profile."""
        media_profile = self.font_media_manager.get_random_media_profile()
        assert isinstance(media_profile, MediaProfile)
        assert isinstance(media_profile.audio_codecs, list)
        assert isinstance(media_profile.video_codecs, list)
        assert isinstance(media_profile.media_devices, list)
        assert isinstance(media_profile.webgl_extensions, list)
        assert isinstance(media_profile.webgl_parameters, dict)
        
        # Check that we have some codecs
        assert len(media_profile.audio_codecs) > 0
        assert len(media_profile.video_codecs) > 0
        
        # Check that we have some media devices
        assert len(media_profile.media_devices) > 0
        
        # Check that we have some WebGL extensions
        assert len(media_profile.webgl_extensions) > 0
        
        # Check that we have WebGL parameters
        assert len(media_profile.webgl_parameters) > 0
    
    def test_generate_realistic_media_devices(self):
        """Test generating realistic media devices."""
        devices = self.font_media_manager._generate_realistic_media_devices()
        assert isinstance(devices, list)
        assert len(devices) >= 6  # Should have at least audio input, audio output, and video input devices
        
        # Check device structure
        for device in devices:
            assert "deviceId" in device
            assert "kind" in device
            assert "label" in device
            assert "groupId" in device
            assert len(device["deviceId"]) == 32  # Should be 32 characters
            assert len(device["groupId"]) == 16  # Should be 16 characters
    
    def test_generate_device_id(self):
        """Test generating device IDs."""
        device_id = self.font_media_manager._generate_device_id()
        assert isinstance(device_id, str)
        assert len(device_id) == 32
        assert device_id.isalnum()  # Should only contain alphanumeric characters
    
    def test_generate_group_id(self):
        """Test generating group IDs."""
        group_id = self.font_media_manager._generate_group_id()
        assert isinstance(group_id, str)
        assert len(group_id) == 16
        assert group_id.isalnum()  # Should only contain alphanumeric characters
    
    def test_get_font_names(self):
        """Test getting font names from font profile."""
        font_profiles = [
            FontProfile("Arial", "sans-serif", False, False, True, False, False),
            FontProfile("Times New Roman", "serif", False, True, False, False, False),
            FontProfile("Courier New", "monospace", True, False, False, False, False)
        ]
        
        font_names = self.font_media_manager.get_font_names(font_profiles)
        assert isinstance(font_names, list)
        assert len(font_names) == 3
        assert "Arial" in font_names
        assert "Times New Roman" in font_names
        assert "Courier New" in font_names
    
    def test_is_monospace_font(self):
        """Test checking if font is monospace."""
        monospace_font = FontProfile("Courier New", "monospace", True, False, False, False, False)
        non_monospace_font = FontProfile("Arial", "sans-serif", False, False, True, False, False)
        
        assert self.font_media_manager.is_monospace_font(monospace_font) is True
        assert self.font_media_manager.is_monospace_font(non_monospace_font) is False
    
    def test_is_serif_font(self):
        """Test checking if font is serif."""
        serif_font = FontProfile("Times New Roman", "serif", False, True, False, False, False)
        sans_serif_font = FontProfile("Arial", "sans-serif", False, False, True, False, False)
        
        assert self.font_media_manager.is_serif_font(serif_font) is True
        assert self.font_media_manager.is_serif_font(sans_serif_font) is False
    
    def test_generate_font_spoofing_js(self):
        """Test generating font spoofing JavaScript."""
        font_profiles = self.font_media_manager.get_random_font_list(5)
        js_code = self.font_media_manager._generate_font_spoofing_js(font_profiles)
        
        assert isinstance(js_code, str)
        assert len(js_code) > 0
        assert "Font enumeration spoofing" in js_code
        assert "measureText" in js_code
    
    def test_generate_media_spoofing_js(self):
        """Test generating media spoofing JavaScript."""
        media_profile = self.font_media_manager.get_random_media_profile()
        js_code = self.font_media_manager._generate_media_spoofing_js(media_profile)
        
        assert isinstance(js_code, str)
        assert len(js_code) > 0
        assert "Media capability spoofing" in js_code
        assert "enumerateDevices" in js_code
        assert "canPlayType" in js_code


if __name__ == "__main__":
    pytest.main([__file__])