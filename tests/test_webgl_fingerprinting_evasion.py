"""
Tests for the WebGLFingerprintingEvasionManager module.
"""

import pytest
import asyncio
import random
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.webgl_fingerprinting_evasion import WebGLFingerprintingEvasionManager, AdvancedWebGLProfile


class TestWebGLFingerprintingEvasionManager:
    """Test cases for the WebGLFingerprintingEvasionManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.webgl_evasion_manager = WebGLFingerprintingEvasionManager()
    
    def test_advanced_webgl_profile_creation(self):
        """Test AdvancedWebGLProfile dataclass creation and methods."""
        webgl = AdvancedWebGLProfile(
            vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            unmasked_vendor="Intel Inc.",
            unmasked_renderer="Intel Iris OpenGL Engine",
            version="WebGL 1.0",
            shading_language_version="WebGL GLSL ES 1.0",
            extensions=["WEBGL_debug_renderer_info", "OES_texture_float"],
            parameters={"VERSION": "WebGL 1.0", "VENDOR": "Intel Inc."},
            max_texture_size=16384,
            max_viewport_dims=(16384, 16384),
            red_bits=8,
            green_bits=8,
            blue_bits=8,
            alpha_bits=8,
            depth_bits=24,
            stencil_bits=0,
            antialiasing="available",
            preferred_webgl_version=1
        )
        
        # Test to_dict method
        webgl_dict = webgl.to_dict()
        assert isinstance(webgl_dict, dict)
        assert webgl_dict["vendor"] == "Intel Inc."
        assert webgl_dict["renderer"] == "Intel Iris OpenGL Engine"
        assert webgl_dict["extensions"][0] == "WEBGL_debug_renderer_info"
        assert webgl_dict["max_texture_size"] == 16384
        assert webgl_dict["red_bits"] == 8
        
        # Test from_dict method
        new_webgl = AdvancedWebGLProfile.from_dict(webgl_dict)
        assert new_webgl.vendor == webgl.vendor
        assert new_webgl.renderer == webgl.renderer
        assert new_webgl.extensions[0] == webgl.extensions[0]
        assert new_webgl.max_texture_size == webgl.max_texture_size
        assert new_webgl.red_bits == webgl.red_bits
    
    def test_get_random_webgl_profile(self):
        """Test getting random WebGL profile."""
        webgl_profile = self.webgl_evasion_manager.get_random_webgl_profile()
        assert isinstance(webgl_profile, AdvancedWebGLProfile)
        assert isinstance(webgl_profile.vendor, str)
        assert isinstance(webgl_profile.renderer, str)
        assert isinstance(webgl_profile.extensions, list)
        assert isinstance(webgl_profile.parameters, dict)
        assert isinstance(webgl_profile.max_texture_size, int)
        assert isinstance(webgl_profile.max_viewport_dims, tuple)
        assert len(webgl_profile.max_viewport_dims) == 2
        assert webgl_profile.preferred_webgl_version in [1, 2]
        
        # Check that we have vendor and renderer
        assert len(webgl_profile.vendor) > 0
        assert len(webgl_profile.renderer) > 0
        
        # Check that we have some extensions
        assert len(webgl_profile.extensions) > 0
        
        # Check that we have some parameters
        assert len(webgl_profile.parameters) > 0
    
    def test_get_random_webgl_profile_webgl1(self):
        """Test getting random WebGL 1 profile."""
        webgl_profile = self.webgl_evasion_manager.get_random_webgl_profile(1)
        assert isinstance(webgl_profile, AdvancedWebGLProfile)
        assert webgl_profile.preferred_webgl_version == 1
        assert "WebGL 1.0" in webgl_profile.version
    
    def test_get_random_webgl_profile_webgl2(self):
        """Test getting random WebGL 2 profile."""
        webgl_profile = self.webgl_evasion_manager.get_random_webgl_profile(2)
        assert isinstance(webgl_profile, AdvancedWebGLProfile)
        assert webgl_profile.preferred_webgl_version == 2
        assert "WebGL 2.0" in webgl_profile.version
    
    def test_generate_webgl_fingerprint(self):
        """Test generating WebGL fingerprint."""
        webgl_profile = self.webgl_evasion_manager.get_random_webgl_profile()
        fingerprint = self.webgl_evasion_manager.generate_webgl_fingerprint(webgl_profile)
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64  # SHA256 hash length
        
        # Test that same profile generates same fingerprint
        fingerprint2 = self.webgl_evasion_manager.generate_webgl_fingerprint(webgl_profile)
        assert fingerprint == fingerprint2
    
    def test_is_webgl_profile_consistent(self):
        """Test checking if WebGL profile is consistent."""
        # Test consistent profile
        webgl_profile = self.webgl_evasion_manager.get_random_webgl_profile()
        is_consistent = self.webgl_evasion_manager.is_webgl_profile_consistent(webgl_profile)
        assert isinstance(is_consistent, bool)
        
        # Test inconsistent profile (empty vendor)
        inconsistent_profile = AdvancedWebGLProfile(
            vendor="",
            renderer="Test Renderer",
            unmasked_vendor="",
            unmasked_renderer="Test Renderer",
            version="WebGL 1.0",
            shading_language_version="WebGL GLSL ES 1.0",
            extensions=["TEST_extension"],
            parameters={"VERSION": "WebGL 1.0"},
            max_texture_size=16384,
            max_viewport_dims=(16384, 16384),
            red_bits=8,
            green_bits=8,
            blue_bits=8,
            alpha_bits=8,
            depth_bits=24,
            stencil_bits=0,
            antialiasing="available",
            preferred_webgl_version=1
        )
        is_inconsistent = self.webgl_evasion_manager.is_webgl_profile_consistent(inconsistent_profile)
        assert is_inconsistent is False
    
    def test_generate_webgl_evasion_js(self):
        """Test generating WebGL evasion JavaScript."""
        webgl_profile = self.webgl_evasion_manager.get_random_webgl_profile()
        js_code = self.webgl_evasion_manager._generate_webgl_evasion_js(webgl_profile)
        assert isinstance(js_code, str)
        assert len(js_code) > 0
        assert "Advanced WebGL fingerprinting evasion" in js_code
        assert "WebGLRenderingContext" in js_code
        assert webgl_profile.vendor in js_code
        assert webgl_profile.renderer in js_code


if __name__ == "__main__":
    pytest.main([__file__])