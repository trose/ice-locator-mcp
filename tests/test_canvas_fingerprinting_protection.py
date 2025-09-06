"""
Tests for the CanvasFingerprintingProtectionManager module.
"""

import pytest
import asyncio
import random
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.canvas_fingerprinting_protection import CanvasFingerprintingProtectionManager, AdvancedCanvasProfile


class TestCanvasFingerprintingProtectionManager:
    """Test cases for the CanvasFingerprintingProtectionManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.canvas_protection_manager = CanvasFingerprintingProtectionManager()
    
    def test_advanced_canvas_profile_creation(self):
        """Test AdvancedCanvasProfile dataclass creation and methods."""
        canvas = AdvancedCanvasProfile(
            text_rendering_noise=0.02,
            text_baseline_variation=0.01,
            font_smoothing_variation=True,
            pixel_data_noise_level=0.005,
            pixel_data_rounding=2,
            color_depth_variation=True,
            rendering_delay_min=1.0,
            rendering_delay_max=5.0,
            timing_jitter=0.5,
            image_data_transformation="shift",
            image_data_block_size=4,
            path_rendering_noise=0.01,
            line_cap_variation=True,
            line_join_variation=True,
            composite_operation_variations=True,
            global_alpha_variation=0.02,
            gradient_noise_level=0.01,
            pattern_distortion_level=0.01,
            webgl_context_protection=True,
            webgl_parameter_noise=0.005
        )
        
        # Test to_dict method
        canvas_dict = canvas.to_dict()
        assert isinstance(canvas_dict, dict)
        assert canvas_dict["text_rendering_noise"] == 0.02
        assert canvas_dict["font_smoothing_variation"] is True
        assert canvas_dict["image_data_transformation"] == "shift"
        assert canvas_dict["image_data_block_size"] == 4
        
        # Test from_dict method
        new_canvas = AdvancedCanvasProfile.from_dict(canvas_dict)
        assert new_canvas.text_rendering_noise == canvas.text_rendering_noise
        assert new_canvas.font_smoothing_variation == canvas.font_smoothing_variation
        assert new_canvas.image_data_transformation == canvas.image_data_transformation
        assert new_canvas.image_data_block_size == canvas.image_data_block_size
    
    def test_get_random_canvas_profile(self):
        """Test getting random advanced canvas profile."""
        canvas_profile = self.canvas_protection_manager.get_random_canvas_profile()
        assert isinstance(canvas_profile, AdvancedCanvasProfile)
        assert isinstance(canvas_profile.text_rendering_noise, float)
        assert isinstance(canvas_profile.pixel_data_noise_level, float)
        assert isinstance(canvas_profile.rendering_delay_min, float)
        assert isinstance(canvas_profile.rendering_delay_max, float)
        assert isinstance(canvas_profile.image_data_transformation, str)
        assert isinstance(canvas_profile.image_data_block_size, int)
        
        # Check value ranges
        assert 0 <= canvas_profile.text_rendering_noise <= 1
        assert 0 <= canvas_profile.pixel_data_noise_level <= 1
        assert canvas_profile.rendering_delay_min >= 0
        assert canvas_profile.rendering_delay_max >= 0
        assert canvas_profile.rendering_delay_min <= canvas_profile.rendering_delay_max
        assert canvas_profile.image_data_block_size > 0
        assert canvas_profile.image_data_transformation in ["none", "shift", "noise"]
    
    def test_get_device_specific_profile(self):
        """Test getting device-specific canvas profile."""
        # Test desktop profile
        desktop_profile = self.canvas_protection_manager.get_device_specific_profile("desktop")
        assert isinstance(desktop_profile, AdvancedCanvasProfile)
        assert desktop_profile.font_smoothing_variation is True
        assert desktop_profile.line_cap_variation is True
        
        # Test mobile profile
        mobile_profile = self.canvas_protection_manager.get_device_specific_profile("mobile")
        assert isinstance(mobile_profile, AdvancedCanvasProfile)
        assert mobile_profile.font_smoothing_variation is False
        assert mobile_profile.line_cap_variation is False
        
        # Test tablet profile
        tablet_profile = self.canvas_protection_manager.get_device_specific_profile("tablet")
        assert isinstance(tablet_profile, AdvancedCanvasProfile)
        
        # Test unknown device type (should return random profile)
        unknown_profile = self.canvas_protection_manager.get_device_specific_profile("unknown")
        assert isinstance(unknown_profile, AdvancedCanvasProfile)
    
    def test_generate_canvas_fingerprint(self):
        """Test generating canvas fingerprint."""
        canvas_profile = self.canvas_protection_manager.get_random_canvas_profile()
        fingerprint = self.canvas_protection_manager.generate_canvas_fingerprint(canvas_profile)
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64  # SHA256 hash length
        
        # Test that same profiles generate same fingerprint
        fingerprint2 = self.canvas_protection_manager.generate_canvas_fingerprint(canvas_profile)
        assert fingerprint == fingerprint2
    
    def test_are_profiles_consistent(self):
        """Test checking if canvas profiles are consistent."""
        # Test with valid profile
        valid_profile = self.canvas_protection_manager.get_random_canvas_profile()
        assert self.canvas_protection_manager.are_profiles_consistent(valid_profile) is True
        
        # Test with invalid profile (negative delay)
        invalid_profile = AdvancedCanvasProfile(
            text_rendering_noise=0.02,
            text_baseline_variation=0.01,
            font_smoothing_variation=True,
            pixel_data_noise_level=0.005,
            pixel_data_rounding=2,
            color_depth_variation=True,
            rendering_delay_min=-1.0,  # Invalid negative value
            rendering_delay_max=5.0,
            timing_jitter=0.5,
            image_data_transformation="shift",
            image_data_block_size=4,
            path_rendering_noise=0.01,
            line_cap_variation=True,
            line_join_variation=True,
            composite_operation_variations=True,
            global_alpha_variation=0.02,
            gradient_noise_level=0.01,
            pattern_distortion_level=0.01,
            webgl_context_protection=True,
            webgl_parameter_noise=0.005
        )
        assert self.canvas_protection_manager.are_profiles_consistent(invalid_profile) is False
        
        # Test with invalid profile (min > max delay)
        invalid_profile2 = AdvancedCanvasProfile(
            text_rendering_noise=0.02,
            text_baseline_variation=0.01,
            font_smoothing_variation=True,
            pixel_data_noise_level=0.005,
            pixel_data_rounding=2,
            color_depth_variation=True,
            rendering_delay_min=10.0,  # Invalid: min > max
            rendering_delay_max=5.0,
            timing_jitter=0.5,
            image_data_transformation="shift",
            image_data_block_size=4,
            path_rendering_noise=0.01,
            line_cap_variation=True,
            line_join_variation=True,
            composite_operation_variations=True,
            global_alpha_variation=0.02,
            gradient_noise_level=0.01,
            pattern_distortion_level=0.01,
            webgl_context_protection=True,
            webgl_parameter_noise=0.005
        )
        assert self.canvas_protection_manager.are_profiles_consistent(invalid_profile2) is False
    
    def test_generate_canvas_protection_js(self):
        """Test generating canvas protection JavaScript."""
        canvas_profile = self.canvas_protection_manager.get_random_canvas_profile()
        js_code = self.canvas_protection_manager._generate_canvas_protection_js(canvas_profile)
        
        assert isinstance(js_code, str)
        assert len(js_code) > 0
        assert "Advanced Canvas Fingerprinting Protection" in js_code
        assert "HTMLCanvasElement.prototype.getContext" in js_code
        assert "fillText" in js_code
        assert "getImageData" in js_code
        assert str(canvas_profile.text_rendering_noise) in js_code
        assert str(canvas_profile.pixel_data_noise_level) in js_code


if __name__ == "__main__":
    pytest.main([__file__])