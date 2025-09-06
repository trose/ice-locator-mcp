#!/usr/bin/env python3
"""
Tests for the ExtensionManager class.

This module contains tests to verify the functionality of the ExtensionManager,
including extension simulation, fingerprint generation, and behavior simulation.
"""

import asyncio
import json
import os
import sys
import pytest
import random

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ice_locator_mcp.anti_detection.extension_manager import ExtensionManager, ExtensionProfile


class TestExtensionManager:
    """Test cases for the ExtensionManager class."""
    
    @pytest.fixture
    def extension_manager(self):
        """Create an ExtensionManager instance for testing."""
        return ExtensionManager()
    
    def test_extension_profile_serialization(self):
        """Test ExtensionProfile serialization and deserialization."""
        # Create an extension profile
        profile = ExtensionProfile(
            id="test-extension-id",
            name="Test Extension",
            version="1.0.0",
            description="A test extension",
            permissions=["storage", "activeTab"]
        )
        
        # Convert to dict
        profile_dict = profile.to_dict()
        assert isinstance(profile_dict, dict)
        assert "id" in profile_dict
        assert "name" in profile_dict
        assert "version" in profile_dict
        assert "description" in profile_dict
        assert "permissions" in profile_dict
        
        # Convert back from dict
        restored_profile = ExtensionProfile.from_dict(profile_dict)
        assert restored_profile.id == profile.id
        assert restored_profile.name == profile.name
        assert restored_profile.version == profile.version
        assert restored_profile.description == profile.description
        assert restored_profile.permissions == profile.permissions
    
    def test_get_random_extensions(self, extension_manager):
        """Test getting random extensions."""
        # Get random extensions
        extensions = extension_manager.get_random_extensions(5)
        
        # Verify results
        assert len(extensions) == 5
        assert all(isinstance(ext, ExtensionProfile) for ext in extensions)
        
        # Check that we have a mix of enabled and disabled extensions
        enabled_count = sum(1 for ext in extensions if ext.enabled)
        assert 0 <= enabled_count <= len(extensions)
    
    def test_generate_extension_fingerprints(self, extension_manager):
        """Test generating extension fingerprints."""
        # Create test extensions
        extensions = [
            ExtensionProfile(
                id="test1",
                name="Test Extension 1",
                version="1.0.0",
                description="Test extension 1",
                permissions=["storage"],
                enabled=True
            ),
            ExtensionProfile(
                id="test2",
                name="Test Extension 2",
                version="2.0.0",
                description="Test extension 2",
                permissions=["activeTab"],
                enabled=False
            )
        ]
        
        # Generate fingerprints
        fingerprints = extension_manager.generate_extension_fingerprints(extensions)
        
        # Verify results
        assert isinstance(fingerprints, dict)
        assert "manifests" in fingerprints
        assert "management" in fingerprints
        assert "count" in fingerprints
        
        # Should only count enabled extensions
        assert fingerprints["count"] == 1
        
        # Check manifests
        assert len(fingerprints["manifests"]) == 1  # Only enabled extension
        assert fingerprints["manifests"][0]["name"] == "Test Extension 1"
        
        # Check management data
        assert len(fingerprints["management"]) == 2  # All extensions
        management_names = [ext["name"] for ext in fingerprints["management"]]
        assert "Test Extension 1" in management_names
        assert "Test Extension 2" in management_names
    
    def test_generate_extension_key(self, extension_manager):
        """Test generating extension keys."""
        # Generate multiple keys
        keys = [extension_manager._generate_extension_key() for _ in range(5)]
        
        # Verify properties
        assert all(isinstance(key, str) for key in keys)
        assert all(len(key) == 57 for key in keys)  # 56 chars + '='
        assert all(key.endswith('=') for key in keys)
        assert len(set(keys)) == 5  # All unique (with high probability)
    
    @pytest.mark.asyncio
    async def test_inject_extension_scripts(self, extension_manager):
        """Test injecting extension scripts."""
        # Create test extensions
        extensions = extension_manager.get_random_extensions(3)
        
        # Inject scripts
        js_code = await extension_manager.inject_extension_scripts(extensions)
        
        # Verify results
        assert isinstance(js_code, str)
        assert len(js_code) > 0
        assert "chrome.runtime" in js_code
        assert "chrome.management" in js_code
        assert "chrome.storage" in js_code
    
    def test_get_extension_categories(self, extension_manager):
        """Test getting extension categories."""
        # Create test extensions with known categories
        extensions = [
            ExtensionProfile(
                id="adblock",
                name="uBlock Origin",
                version="1.0.0",
                description="Ad blocker",
                permissions=["webRequest"],
                enabled=True
            ),
            ExtensionProfile(
                id="grammar",
                name="Grammarly",
                version="1.0.0",
                description="Grammar checker",
                permissions=["activeTab"],
                enabled=True
            )
        ]
        
        # Get categories
        categories = extension_manager.get_extension_categories(extensions)
        
        # Verify results
        assert isinstance(categories, set)
        assert "ad_blocker" in categories
        assert "grammar_checker" in categories
    
    @pytest.mark.asyncio
    async def test_simulate_extension_behavior(self, extension_manager):
        """Test simulating extension behavior."""
        # Create test extensions
        extensions = extension_manager.get_random_extensions(3)
        
        # Simulate behavior
        js_code = await extension_manager.simulate_extension_behavior(extensions)
        
        # Verify results
        assert isinstance(js_code, str)
        assert len(js_code) > 0
        assert "extension" in js_code.lower()
        assert "simulate" in js_code.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])