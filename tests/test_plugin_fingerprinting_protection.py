"""
Tests for the PluginFingerprintingProtectionManager module.
"""

import pytest
import asyncio
import random
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.plugin_fingerprinting_protection import PluginFingerprintingProtectionManager, PluginFingerprintingProfile, PluginProfile, ExtensionProfile


class TestPluginFingerprintingProtectionManager:
    """Test cases for the PluginFingerprintingProtectionManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.plugin_manager = PluginFingerprintingProtectionManager()
    
    def test_plugin_profile_creation(self):
        """Test PluginProfile dataclass creation and methods."""
        plugin = PluginProfile(
            name="Test Plugin",
            filename="test-plugin.dll",
            description="A test plugin"
        )
        
        # Test to_dict method
        plugin_dict = plugin.to_dict()
        assert isinstance(plugin_dict, dict)
        assert plugin_dict["name"] == "Test Plugin"
        assert plugin_dict["filename"] == "test-plugin.dll"
        assert plugin_dict["description"] == "A test plugin"
        
        # Test from_dict method
        new_plugin = PluginProfile.from_dict(plugin_dict)
        assert new_plugin.name == plugin.name
        assert new_plugin.filename == plugin.filename
        assert new_plugin.description == plugin.description
    
    def test_extension_profile_creation(self):
        """Test ExtensionProfile dataclass creation and methods."""
        extension = ExtensionProfile(
            id="test-extension-id",
            name="Test Extension",
            version="1.0.0",
            description="A test extension",
            permissions=["storage", "activeTab"],
            enabled=True
        )
        
        # Test to_dict method
        extension_dict = extension.to_dict()
        assert isinstance(extension_dict, dict)
        assert extension_dict["id"] == "test-extension-id"
        assert extension_dict["name"] == "Test Extension"
        assert extension_dict["version"] == "1.0.0"
        assert extension_dict["permissions"] == ["storage", "activeTab"]
        assert extension_dict["enabled"] is True
        
        # Test from_dict method
        new_extension = ExtensionProfile.from_dict(extension_dict)
        assert new_extension.id == extension.id
        assert new_extension.name == extension.name
        assert new_extension.version == extension.version
        assert new_extension.permissions == extension.permissions
        assert new_extension.enabled == extension.enabled
    
    def test_plugin_fingerprinting_profile_creation(self):
        """Test PluginFingerprintingProfile dataclass creation and methods."""
        plugins = [
            PluginProfile(
                name="Test Plugin 1",
                filename="test-plugin-1.dll",
                description="A test plugin 1"
            ),
            PluginProfile(
                name="Test Plugin 2",
                filename="test-plugin-2.dll",
                description="A test plugin 2"
            )
        ]
        
        extensions = [
            ExtensionProfile(
                id="test-extension-1",
                name="Test Extension 1",
                version="1.0.0",
                description="A test extension 1",
                permissions=["storage"],
                enabled=True
            ),
            ExtensionProfile(
                id="test-extension-2",
                name="Test Extension 2",
                version="2.0.0",
                description="A test extension 2",
                permissions=["activeTab"],
                enabled=False
            )
        ]
        
        profile = PluginFingerprintingProfile(
            plugins=plugins,
            extensions=extensions,
            device_type="desktop",
            is_consistent=True
        )
        
        # Test to_dict method
        profile_dict = profile.to_dict()
        assert isinstance(profile_dict, dict)
        assert len(profile_dict["plugins"]) == 2
        assert len(profile_dict["extensions"]) == 2
        assert profile_dict["device_type"] == "desktop"
        assert profile_dict["is_consistent"] is True
        
        # Test from_dict method
        new_profile = PluginFingerprintingProfile.from_dict(profile_dict)
        assert len(new_profile.plugins) == len(profile.plugins)
        assert len(new_profile.extensions) == len(profile.extensions)
        assert new_profile.device_type == profile.device_type
        assert new_profile.is_consistent == profile.is_consistent
    
    def test_get_random_profile(self):
        """Test getting random plugin and extension fingerprinting profile."""
        profile = self.plugin_manager.get_random_profile()
        assert isinstance(profile, PluginFingerprintingProfile)
        assert isinstance(profile.plugins, list)
        assert isinstance(profile.extensions, list)
        assert isinstance(profile.device_type, str)
        assert isinstance(profile.is_consistent, bool)
        
        # Check that plugins have realistic properties
        for plugin in profile.plugins:
            assert isinstance(plugin, PluginProfile)
            assert isinstance(plugin.name, str)
            assert isinstance(plugin.filename, str)
            assert isinstance(plugin.description, str)
            assert len(plugin.name) > 0
            assert len(plugin.filename) > 0
        
        # Check that extensions have realistic properties
        for ext in profile.extensions:
            assert isinstance(ext, ExtensionProfile)
            assert isinstance(ext.id, str)
            assert isinstance(ext.name, str)
            assert isinstance(ext.version, str)
            assert isinstance(ext.description, str)
            assert isinstance(ext.permissions, list)
            assert isinstance(ext.enabled, bool)
            assert len(ext.id) > 0
            assert len(ext.name) > 0
            assert len(ext.version) > 0
        
        # Check device type
        assert profile.device_type in ["desktop", "mobile", "tablet"]
        
        # Check consistency
        assert profile.is_consistent is True
    
    def test_get_device_specific_profile(self):
        """Test getting device-specific plugin and extension fingerprinting profile."""
        # Test desktop profile
        desktop_profile = self.plugin_manager.get_device_specific_profile("desktop")
        assert isinstance(desktop_profile, PluginFingerprintingProfile)
        assert desktop_profile.device_type == "desktop"
        
        # Test mobile profile
        mobile_profile = self.plugin_manager.get_device_specific_profile("mobile")
        assert isinstance(mobile_profile, PluginFingerprintingProfile)
        assert mobile_profile.device_type == "mobile"
        
        # Test tablet profile
        tablet_profile = self.plugin_manager.get_device_specific_profile("tablet")
        assert isinstance(tablet_profile, PluginFingerprintingProfile)
        assert tablet_profile.device_type == "tablet"
        
        # Test unknown device type (should return random profile)
        unknown_profile = self.plugin_manager.get_device_specific_profile("unknown")
        assert isinstance(unknown_profile, PluginFingerprintingProfile)
    
    def test_generate_fingerprint(self):
        """Test generating plugin and extension fingerprint."""
        profile = self.plugin_manager.get_random_profile()
        fingerprint = self.plugin_manager.generate_fingerprint(profile)
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64  # SHA256 hash length
        
        # Test that same profiles generate same fingerprint
        fingerprint2 = self.plugin_manager.generate_fingerprint(profile)
        assert fingerprint == fingerprint2
    
    def test_are_profiles_consistent(self):
        """Test checking if plugin and extension profiles are consistent."""
        # Test with valid profile
        valid_profile = self.plugin_manager.get_random_profile()
        assert self.plugin_manager.are_profiles_consistent(valid_profile) is True
        
        # Test with invalid profile (empty plugin name)
        invalid_profile = PluginFingerprintingProfile(
            plugins=[
                PluginProfile(
                    name="",  # Empty name
                    filename="test.dll",
                    description="Test"
                )
            ],
            extensions=[
                ExtensionProfile(
                    id="test-id",
                    name="Test Extension",
                    version="1.0.0",
                    description="Test",
                    permissions=["storage"]
                )
            ],
            device_type="desktop",
            is_consistent=True
        )
        assert self.plugin_manager.are_profiles_consistent(invalid_profile) is False
        
        # Test with invalid profile (wrong device type)
        invalid_profile2 = PluginFingerprintingProfile(
            plugins=[
                PluginProfile(
                    name="Test Plugin",
                    filename="test.dll",
                    description="Test"
                )
            ],
            extensions=[
                ExtensionProfile(
                    id="test-id",
                    name="Test Extension",
                    version="1.0.0",
                    description="Test",
                    permissions=["storage"]
                )
            ],
            device_type="unknown_device",  # Invalid device type
            is_consistent=True
        )
        assert self.plugin_manager.are_profiles_consistent(invalid_profile2) is False
    
    def test_generate_spoofing_js(self):
        """Test generating plugin and extension spoofing JavaScript."""
        profile = self.plugin_manager.get_random_profile()
        js_code = self.plugin_manager._generate_spoofing_js(profile)
        
        assert isinstance(js_code, str)
        assert len(js_code) > 0
        assert "Advanced Plugin and Extension Fingerprinting Protection" in js_code
        assert "navigator.plugins" in js_code
        assert "navigator.mimeTypes" in js_code
        assert "chrome.runtime" in js_code
        assert "chrome.management" in js_code


if __name__ == "__main__":
    pytest.main([__file__])