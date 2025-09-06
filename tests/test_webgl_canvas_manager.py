"""
Tests for the WebGLCanvasManager module.
"""

import pytest
import asyncio
import random
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.webgl_canvas_manager import WebGLCanvasManager, WebGLProfile, CanvasProfile


class TestWebGLCanvasManager:
    """Test cases for the WebGLCanvasManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.webgl_canvas_manager = WebGLCanvasManager()
    
    def test_webgl_profile_creation(self):
        """Test WebGLProfile dataclass creation and methods."""
        webgl = WebGLProfile(
            vendor="Test Vendor",
            renderer="Test Renderer",
            version="WebGL 1.0",
            shading_language_version="WebGL GLSL ES 1.0",
            extensions=["EXT_blend_minmax", "OES_texture_float"],
            parameters={"VERSION": "WebGL 1.0", "VENDOR": "Test Vendor"},
            max_texture_size=16384,
            max_viewport_dims=16384,
            red_bits=8,
            green_bits=8,
            blue_bits=8,
            alpha_bits=8,
            depth_bits=24,
            stencil_bits=0
        )
        
        # Test to_dict method
        webgl_dict = webgl.to_dict()
        assert isinstance(webgl_dict, dict)
        assert webgl_dict["vendor"] == "Test Vendor"
        assert webgl_dict["renderer"] == "Test Renderer"
        assert "EXT_blend_minmax" in webgl_dict["extensions"]
        assert webgl_dict["parameters"]["VERSION"] == "WebGL 1.0"
        assert webgl_dict["max_texture_size"] == 16384
        
        # Test from_dict method
        new_webgl = WebGLProfile.from_dict(webgl_dict)
        assert new_webgl.vendor == webgl.vendor
        assert new_webgl.renderer == webgl.renderer
        assert "EXT_blend_minmax" in new_webgl.extensions
        assert new_webgl.parameters["VERSION"] == "WebGL 1.0"
        assert new_webgl.max_texture_size == webgl.max_texture_size
    
    def test_canvas_profile_creation(self):
        """Test CanvasProfile dataclass creation and methods."""
        canvas = CanvasProfile(
            text_rendering_variation=0.1,
            pixel_noise_level=0.005,
            rendering_timing_variation=0.2,
            fill_text_offset_variation=(0.005, 0.003),
            to_data_url_noise=True,
            get_image_data_noise=False
        )
        
        # Test to_dict method
        canvas_dict = canvas.to_dict()
        assert isinstance(canvas_dict, dict)
        assert canvas_dict["text_rendering_variation"] == 0.1
        assert canvas_dict["pixel_noise_level"] == 0.005
        assert canvas_dict["rendering_timing_variation"] == 0.2
        assert canvas_dict["fill_text_offset_variation"] == [0.005, 0.003]
        assert canvas_dict["to_data_url_noise"] is True
        assert canvas_dict["get_image_data_noise"] is False
        
        # Test from_dict method
        new_canvas = CanvasProfile.from_dict(canvas_dict)
        assert new_canvas.text_rendering_variation == canvas.text_rendering_variation
        assert new_canvas.pixel_noise_level == canvas.pixel_noise_level
        assert new_canvas.rendering_timing_variation == canvas.rendering_timing_variation
        assert new_canvas.fill_text_offset_variation == canvas.fill_text_offset_variation
        assert new_canvas.to_data_url_noise == canvas.to_data_url_noise
        assert new_canvas.get_image_data_noise == canvas.get_image_data_noise
    
    def test_get_random_webgl_profile(self):
        """Test getting random WebGL profile."""
        webgl_profile = self.webgl_canvas_manager.get_random_webgl_profile()
        assert isinstance(webgl_profile, WebGLProfile)
        assert isinstance(webgl_profile.vendor, str)
        assert isinstance(webgl_profile.renderer, str)
        assert isinstance(webgl_profile.extensions, list)
        assert isinstance(webgl_profile.parameters, dict)
        
        # Check that we have some extensions
        assert len(webgl_profile.extensions) > 0
        
        # Check that we have parameters
        assert len(webgl_profile.parameters) > 0
        
        # Check specific parameter values
        assert "VERSION" in webgl_profile.parameters
        assert "VENDOR" in webgl_profile.parameters
        assert "RENDERER" in webgl_profile.parameters
    
    def test_get_random_canvas_profile(self):
        """Test getting random canvas profile."""
        canvas_profile = self.webgl_canvas_manager.get_random_canvas_profile()
        assert isinstance(canvas_profile, CanvasProfile)
        assert isinstance(canvas_profile.text_rendering_variation, float)
        assert isinstance(canvas_profile.pixel_noise_level, float)
        assert isinstance(canvas_profile.rendering_timing_variation, float)
        assert isinstance(canvas_profile.fill_text_offset_variation, tuple)
        assert isinstance(canvas_profile.to_data_url_noise, bool)
        assert isinstance(canvas_profile.get_image_data_noise, bool)
        
        # Check value ranges
        assert 0.05 <= canvas_profile.text_rendering_variation <= 0.15
        assert 0.001 <= canvas_profile.pixel_noise_level <= 0.01
        assert 0.1 <= canvas_profile.rendering_timing_variation <= 0.5
        assert len(canvas_profile.fill_text_offset_variation) == 2
    
    def test_generate_webgl_canvas_fingerprint(self):
        """Test generating WebGL and canvas fingerprint."""
        webgl_profile = self.webgl_canvas_manager.get_random_webgl_profile()
        canvas_profile = self.webgl_canvas_manager.get_random_canvas_profile()
        
        fingerprint = self.webgl_canvas_manager.generate_webgl_canvas_fingerprint(webgl_profile, canvas_profile)
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64  # SHA256 hash length
        
        # Test that same profiles generate same fingerprint
        fingerprint2 = self.webgl_canvas_manager.generate_webgl_canvas_fingerprint(webgl_profile, canvas_profile)
        assert fingerprint == fingerprint2
    
    def test_are_profiles_consistent(self):
        """Test checking if WebGL and canvas profiles are consistent."""
        # Test with desktop GPU profile
        webgl_desktop = WebGLProfile(
            vendor="NVIDIA Corporation",
            renderer="NVIDIA GeForce GTX 1080 OpenGL Engine",
            version="WebGL 1.0",
            shading_language_version="WebGL GLSL ES 1.0",
            extensions=["EXT_blend_minmax"],
            parameters={"VERSION": "WebGL 1.0"},
            max_texture_size=16384,
            max_viewport_dims=16384,
            red_bits=8,
            green_bits=8,
            blue_bits=8,
            alpha_bits=8,
            depth_bits=24,
            stencil_bits=0
        )
        
        canvas_profile = CanvasProfile(
            text_rendering_variation=0.1,
            pixel_noise_level=0.005,
            rendering_timing_variation=0.2,
            fill_text_offset_variation=(0.005, 0.003),
            to_data_url_noise=True,
            get_image_data_noise=False
        )
        
        # Desktop GPU with high texture size should be consistent
        assert self.webgl_canvas_manager.are_profiles_consistent(webgl_desktop, canvas_profile) is True
        
        # Test with mobile GPU profile
        webgl_mobile = WebGLProfile(
            vendor="ARM",
            renderer="Mali-T860",
            version="WebGL 1.0",
            shading_language_version="WebGL GLSL ES 1.0",
            extensions=["EXT_blend_minmax"],
            parameters={"VERSION": "WebGL 1.0"},
            max_texture_size=8192,
            max_viewport_dims=8192,
            red_bits=8,
            green_bits=8,
            blue_bits=8,
            alpha_bits=8,
            depth_bits=24,
            stencil_bits=0
        )
        
        # Mobile GPU with appropriate texture size should be consistent
        assert self.webgl_canvas_manager.are_profiles_consistent(webgl_mobile, canvas_profile) is True
    
    def test_generate_webgl_spoofing_js(self):
        """Test generating WebGL spoofing JavaScript."""
        webgl_profile = self.webgl_canvas_manager.get_random_webgl_profile()
        js_code = self.webgl_canvas_manager._generate_webgl_spoofing_js(webgl_profile)
        
        assert isinstance(js_code, str)
        assert len(js_code) > 0
        assert "WebGL rendering spoofing" in js_code
        assert "getParameter" in js_code
        assert "getExtension" in js_code
        assert webgl_profile.vendor.replace('"', '\\"') in js_code
        assert webgl_profile.renderer.replace('"', '\\"') in js_code
    
    def test_generate_canvas_spoofing_js(self):
        """Test generating canvas spoofing JavaScript."""
        canvas_profile = self.webgl_canvas_manager.get_random_canvas_profile()
        js_code = self.webgl_canvas_manager._generate_canvas_spoofing_js(canvas_profile)
        
        assert isinstance(js_code, str)
        assert len(js_code) > 0
        assert "Canvas rendering spoofing" in js_code
        assert "fillText" in js_code
        assert "measureText" in js_code
        assert "toDataURL" in js_code
        assert "getImageData" in js_code


if __name__ == "__main__":
    pytest.main([__file__])