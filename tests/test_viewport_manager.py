"""
Tests for the ViewportManager module.
"""

import pytest
import asyncio
import random
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.viewport_manager import ViewportManager, ViewportProfile, DeviceProfile


class TestViewportManager:
    """Test cases for the ViewportManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.viewport_manager = ViewportManager()
    
    def test_viewport_profile_creation(self):
        """Test ViewportProfile dataclass creation and methods."""
        viewport = ViewportProfile(
            width=1920,
            height=1080,
            device_scale_factor=1.0,
            is_mobile=False,
            has_touch=False,
            screen_width=1920,
            screen_height=1080,
            avail_width=1920,
            avail_height=1040,
            color_depth=24,
            pixel_depth=24,
            orientation_type="landscape-primary",
            orientation_angle=0
        )
        
        # Test to_dict method
        viewport_dict = viewport.to_dict()
        assert isinstance(viewport_dict, dict)
        assert viewport_dict["width"] == 1920
        assert viewport_dict["height"] == 1080
        
        # Test from_dict method
        new_viewport = ViewportProfile.from_dict(viewport_dict)
        assert new_viewport.width == viewport.width
        assert new_viewport.height == viewport.height
        assert new_viewport.device_scale_factor == viewport.device_scale_factor
    
    def test_device_profile_creation(self):
        """Test DeviceProfile dataclass creation."""
        viewport = ViewportProfile(
            width=1920,
            height=1080,
            device_scale_factor=1.0,
            is_mobile=False,
            has_touch=False,
            screen_width=1920,
            screen_height=1080,
            avail_width=1920,
            avail_height=1040,
            color_depth=24,
            pixel_depth=24,
            orientation_type="landscape-primary",
            orientation_angle=0
        )
        
        device = DeviceProfile(
            name="Test Device",
            viewport=viewport,
            user_agent="Test User Agent",
            platform="Test Platform"
        )
        
        assert device.name == "Test Device"
        assert device.viewport.width == 1920
        assert device.user_agent == "Test User Agent"
        assert device.platform == "Test Platform"
    
    def test_get_random_viewport_desktop(self):
        """Test getting random desktop viewport."""
        viewport = self.viewport_manager.get_random_viewport("desktop")
        assert isinstance(viewport, ViewportProfile)
        assert viewport.width >= 1280
        assert viewport.height >= 720
        assert not viewport.is_mobile
        assert not viewport.has_touch
    
    def test_get_random_viewport_laptop(self):
        """Test getting random laptop viewport."""
        viewport = self.viewport_manager.get_random_viewport("laptop")
        assert isinstance(viewport, ViewportProfile)
        assert viewport.width >= 1280
        assert viewport.height >= 720
        assert not viewport.is_mobile
        assert not viewport.has_touch
    
    def test_get_random_viewport_mobile(self):
        """Test getting random mobile viewport."""
        viewport = self.viewport_manager.get_random_viewport("mobile")
        assert isinstance(viewport, ViewportProfile)
        assert viewport.width <= 414
        assert viewport.height <= 896
        assert viewport.is_mobile
        assert viewport.has_touch
        assert viewport.device_scale_factor >= 2.0
    
    def test_get_random_viewport_tablet(self):
        """Test getting random tablet viewport."""
        viewport = self.viewport_manager.get_random_viewport("tablet")
        assert isinstance(viewport, ViewportProfile)
        assert viewport.width >= 768
        assert viewport.height >= 1024
        assert viewport.is_mobile
        assert viewport.has_touch
        assert viewport.device_scale_factor >= 2.0
    
    def test_get_random_device_profile(self):
        """Test getting random device profile."""
        device = self.viewport_manager.get_random_device_profile()
        assert isinstance(device, DeviceProfile)
        assert isinstance(device.viewport, ViewportProfile)
        assert isinstance(device.name, str)
        assert isinstance(device.user_agent, str)
        assert isinstance(device.platform, str)
        assert len(device.name) > 0
        assert len(device.user_agent) > 0
        assert len(device.platform) > 0
    
    def test_generate_realistic_viewport(self):
        """Test generating realistic viewport."""
        viewport = self.viewport_manager.generate_realistic_viewport()
        assert isinstance(viewport, ViewportProfile)
        assert viewport.width >= 800
        assert viewport.height >= 600
        assert viewport.screen_width >= viewport.width
        assert viewport.screen_height >= viewport.height
        assert viewport.avail_width <= viewport.screen_width
        assert viewport.avail_height <= viewport.screen_height
        assert viewport.color_depth in [24, 32]
        assert viewport.pixel_depth in [24, 32]
        assert viewport.device_scale_factor in [1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 3.5]
    
    def test_get_viewport_dimensions(self):
        """Test getting viewport dimensions."""
        viewport = ViewportProfile(
            width=1920,
            height=1080,
            device_scale_factor=1.0,
            is_mobile=False,
            has_touch=False,
            screen_width=1920,
            screen_height=1080,
            avail_width=1920,
            avail_height=1040,
            color_depth=24,
            pixel_depth=24,
            orientation_type="landscape-primary",
            orientation_angle=0
        )
        
        dimensions = self.viewport_manager.get_viewport_dimensions(viewport)
        assert isinstance(dimensions, tuple)
        assert len(dimensions) == 2
        assert dimensions[0] == 1920
        assert dimensions[1] == 1080
    
    def test_get_screen_dimensions(self):
        """Test getting screen dimensions."""
        viewport = ViewportProfile(
            width=1920,
            height=1080,
            device_scale_factor=1.0,
            is_mobile=False,
            has_touch=False,
            screen_width=1920,
            screen_height=1080,
            avail_width=1920,
            avail_height=1040,
            color_depth=24,
            pixel_depth=24,
            orientation_type="landscape-primary",
            orientation_angle=0
        )
        
        dimensions = self.viewport_manager.get_screen_dimensions(viewport)
        assert isinstance(dimensions, tuple)
        assert len(dimensions) == 2
        assert dimensions[0] == 1920
        assert dimensions[1] == 1080
    
    def test_is_mobile_viewport(self):
        """Test mobile viewport detection."""
        # Test mobile viewport
        mobile_viewport = ViewportProfile(
            width=375,
            height=667,
            device_scale_factor=2.0,
            is_mobile=True,
            has_touch=True,
            screen_width=375,
            screen_height=667,
            avail_width=375,
            avail_height=627,
            color_depth=32,
            pixel_depth=32,
            orientation_type="portrait-primary",
            orientation_angle=0
        )
        
        assert self.viewport_manager.is_mobile_viewport(mobile_viewport)
        
        # Test desktop viewport
        desktop_viewport = ViewportProfile(
            width=1920,
            height=1080,
            device_scale_factor=1.0,
            is_mobile=False,
            has_touch=False,
            screen_width=1920,
            screen_height=1080,
            avail_width=1920,
            avail_height=1040,
            color_depth=24,
            pixel_depth=24,
            orientation_type="landscape-primary",
            orientation_angle=0
        )
        
        assert not self.viewport_manager.is_mobile_viewport(desktop_viewport)
    
    def test_is_tablet_viewport(self):
        """Test tablet viewport detection."""
        # Test tablet viewport
        tablet_viewport = ViewportProfile(
            width=1024,
            height=1366,
            device_scale_factor=2.0,
            is_mobile=True,
            has_touch=True,
            screen_width=1024,
            screen_height=1366,
            avail_width=1024,
            avail_height=1366,
            color_depth=32,
            pixel_depth=32,
            orientation_type="portrait-primary",
            orientation_angle=0
        )
        
        assert self.viewport_manager.is_tablet_viewport(tablet_viewport)
        
        # Test desktop viewport
        desktop_viewport = ViewportProfile(
            width=1920,
            height=1080,
            device_scale_factor=1.0,
            is_mobile=False,
            has_touch=False,
            screen_width=1920,
            screen_height=1080,
            avail_width=1920,
            avail_height=1040,
            color_depth=24,
            pixel_depth=24,
            orientation_type="landscape-primary",
            orientation_angle=0
        )
        
        assert not self.viewport_manager.is_tablet_viewport(desktop_viewport)
    
    def test_get_device_category(self):
        """Test device category detection."""
        # Test mobile viewport
        mobile_viewport = ViewportProfile(
            width=375,
            height=667,
            device_scale_factor=2.0,
            is_mobile=True,
            has_touch=True,
            screen_width=375,
            screen_height=667,
            avail_width=375,
            avail_height=627,
            color_depth=32,
            pixel_depth=32,
            orientation_type="portrait-primary",
            orientation_angle=0
        )
        
        category = self.viewport_manager.get_device_category(mobile_viewport)
        assert category == "mobile"
        
        # Test tablet viewport
        tablet_viewport = ViewportProfile(
            width=1024,
            height=1366,
            device_scale_factor=2.0,
            is_mobile=True,
            has_touch=True,
            screen_width=1024,
            screen_height=1366,
            avail_width=1024,
            avail_height=1366,
            color_depth=32,
            pixel_depth=32,
            orientation_type="portrait-primary",
            orientation_angle=0
        )
        
        category = self.viewport_manager.get_device_category(tablet_viewport)
        assert category == "tablet"
        
        # Test laptop viewport
        laptop_viewport = ViewportProfile(
            width=1536,
            height=864,
            device_scale_factor=2.0,
            is_mobile=False,
            has_touch=False,
            screen_width=1536,
            screen_height=864,
            avail_width=1536,
            avail_height=824,
            color_depth=24,
            pixel_depth=24,
            orientation_type="landscape-primary",
            orientation_angle=0
        )
        
        category = self.viewport_manager.get_device_category(laptop_viewport)
        assert category == "laptop"
        
        # Test desktop viewport
        desktop_viewport = ViewportProfile(
            width=1920,
            height=1080,
            device_scale_factor=1.0,
            is_mobile=False,
            has_touch=False,
            screen_width=1920,
            screen_height=1080,
            avail_width=1920,
            avail_height=1040,
            color_depth=24,
            pixel_depth=24,
            orientation_type="landscape-primary",
            orientation_angle=0
        )
        
        category = self.viewport_manager.get_device_category(desktop_viewport)
        assert category == "desktop"


if __name__ == "__main__":
    pytest.main([__file__])