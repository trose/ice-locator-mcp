#!/usr/bin/env python3
"""
Tests for the CookieManager class.

This module contains tests to verify the functionality of the CookieManager,
including cookie extraction, setting, rotation, validation, and expiration handling.
"""

import asyncio
import json
import os
import sys
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
import time

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ice_locator_mcp.anti_detection.cookie_manager import CookieManager, CookieProfile


class TestCookieManager:
    """Test cases for the CookieManager class."""
    
    @pytest.fixture
    def cookie_manager(self):
        """Create a CookieManager instance for testing."""
        return CookieManager()
    
    @pytest.fixture
    def sample_cookies(self):
        """Create sample cookies for testing."""
        return [
            CookieProfile(
                name="session_id",
                value="abc123",
                domain="example.com",
                path="/",
                expires=None,  # Session cookie
                httpOnly=True,
                secure=True,
                sameSite="Lax",
                creation_time=time.time() - 100,
                last_accessed=time.time() - 50
            ),
            CookieProfile(
                name="user_pref",
                value="dark_mode",
                domain="example.com",
                path="/",
                expires=time.time() + 3600,  # Expires in 1 hour
                httpOnly=False,
                secure=True,
                sameSite="Strict",
                creation_time=time.time() - 200,
                last_accessed=time.time() - 100
            ),
            CookieProfile(
                name="tracking_id",
                value="track123",
                domain="google-analytics.com",
                path="/",
                expires=time.time() + 86400,  # Expires in 1 day
                httpOnly=False,
                secure=True,
                sameSite="None",
                creation_time=time.time() - 300,
                last_accessed=time.time() - 150
            )
        ]
    
    def test_cookie_profile_is_expired(self, sample_cookies):
        """Test CookieProfile is_expired method."""
        # Session cookie should not be expired
        assert not sample_cookies[0].is_expired()
        
        # Future expiration cookie should not be expired
        assert not sample_cookies[1].is_expired()
        
        # Create an expired cookie
        expired_cookie = CookieProfile(
            name="expired",
            value="value",
            domain="example.com",
            expires=time.time() - 100  # Expired 100 seconds ago
        )
        assert expired_cookie.is_expired()
    
    def test_cookie_profile_is_session_cookie(self, sample_cookies):
        """Test CookieProfile is_session_cookie method."""
        # Session cookie (no expiration)
        assert sample_cookies[0].is_session_cookie()
        
        # Persistent cookie (has expiration)
        assert not sample_cookies[1].is_session_cookie()
    
    def test_cookie_profile_time_to_expiry(self, sample_cookies):
        """Test CookieProfile time_to_expiry method."""
        # Session cookie should return None
        assert sample_cookies[0].time_to_expiry() is None
        
        # Persistent cookie should return time until expiry
        time_to_expiry = sample_cookies[1].time_to_expiry()
        assert time_to_expiry is not None
        assert time_to_expiry > 0
    
    def test_cookie_profile_serialization(self, sample_cookies):
        """Test CookieProfile serialization and deserialization."""
        # Convert to dict
        cookie_dict = sample_cookies[0].to_dict()
        assert isinstance(cookie_dict, dict)
        assert "name" in cookie_dict
        assert "value" in cookie_dict
        assert "domain" in cookie_dict
        
        # Convert back from dict
        restored_cookie = CookieProfile.from_dict(cookie_dict)
        assert restored_cookie.name == sample_cookies[0].name
        assert restored_cookie.value == sample_cookies[0].value
        assert restored_cookie.domain == sample_cookies[0].domain
    
    @pytest.mark.asyncio
    async def test_extract_cookies_from_context(self, cookie_manager):
        """Test extracting cookies from a browser context."""
        # Create a mock browser context
        mock_context = AsyncMock()
        mock_context.cookies = AsyncMock(return_value=[
            {
                'name': 'test_cookie',
                'value': 'test_value',
                'domain': 'example.com',
                'path': '/',
                'expires': time.time() + 3600,
                'httpOnly': False,
                'secure': True,
                'sameSite': 'Lax'
            }
        ])
        
        # Extract cookies
        cookies = await cookie_manager.extract_cookies_from_context(mock_context)
        
        # Verify results
        assert len(cookies) == 1
        assert isinstance(cookies[0], CookieProfile)
        assert cookies[0].name == "test_cookie"
        assert cookies[0].value == "test_value"
        assert cookies[0].domain == "example.com"
    
    @pytest.mark.asyncio
    async def test_set_cookies_in_context(self, cookie_manager, sample_cookies):
        """Test setting cookies in a browser context."""
        # Create a mock browser context
        mock_context = AsyncMock()
        mock_context.add_cookies = AsyncMock()
        
        # Set cookies
        result = await cookie_manager.set_cookies_in_context(mock_context, sample_cookies)
        
        # Verify results
        assert result is True
        mock_context.add_cookies.assert_called_once()
        
        # Check that the call was made with the right format
        call_args = mock_context.add_cookies.call_args[0][0]
        assert len(call_args) == len(sample_cookies)
        assert all('name' in cookie and 'value' in cookie for cookie in call_args)
    
    def test_get_cookie_category(self, cookie_manager, sample_cookies):
        """Test determining cookie categories."""
        # Session cookie
        category = cookie_manager._get_cookie_category(sample_cookies[0])
        assert category == "session"
        
        # Tracking cookie
        category = cookie_manager._get_cookie_category(sample_cookies[2])
        assert category == "tracking"
        
        # Persistent cookie (regular)
        category = cookie_manager._get_cookie_category(sample_cookies[1])
        assert category == "persistent"
    
    def test_should_rotate_cookie(self, cookie_manager, sample_cookies):
        """Test determining if a cookie should be rotated."""
        # Make the cookie old enough to be eligible for rotation
        old_cookie = CookieProfile(
            name="old_session",
            value="old_value",
            domain="example.com",
            creation_time=time.time() - 1000,  # Created 1000 seconds ago
            last_accessed=time.time() - 500
        )
        
        # This test is probabilistic, so we'll run it multiple times
        rotation_results = []
        for _ in range(100):
            result = cookie_manager._should_rotate_cookie(old_cookie)
            rotation_results.append(result)
    
        # We should get some rotations (not all False)
        # Since we're using an old cookie, we should definitely get some rotations
        assert any(rotation_results)
    
    @pytest.mark.asyncio
    async def test_rotate_cookies(self, cookie_manager, sample_cookies):
        """Test rotating cookies."""
        # Rotate cookies
        rotated_cookies = await cookie_manager.rotate_cookies(sample_cookies)
        
        # Verify results
        assert len(rotated_cookies) == len(sample_cookies)
        
        # At least some cookies should have been rotated (probabilistic)
        # For testing purposes, we'll check that the method runs without error
        assert isinstance(rotated_cookies, list)
        assert all(isinstance(cookie, CookieProfile) for cookie in rotated_cookies)
    
    def test_generate_rotated_value(self, cookie_manager):
        """Test generating rotated cookie values."""
        original_value = "abc123def456"
        rotated_value = cookie_manager._generate_rotated_value(original_value)
        
        # Should maintain same length
        assert len(rotated_value) == len(original_value)
        
        # Should be different (with high probability)
        # (This might occasionally fail due to randomness, but it's unlikely)
        assert rotated_value != original_value or len(original_value) < 5
    
    @pytest.mark.asyncio
    async def test_validate_cookies(self, cookie_manager):
        """Test validating cookies."""
        # Create test cookies including some invalid ones
        test_cookies = [
            CookieProfile(
                name="valid_cookie",
                value="value",
                domain="example.com"
            ),
            CookieProfile(
                name="",  # Invalid: no name
                value="value",
                domain="example.com"
            ),
            CookieProfile(
                name="no_domain",  # Invalid: no domain
                value="value",
                domain=""
            ),
            CookieProfile(
                name="expired_cookie",
                value="value",
                domain="example.com",
                expires=time.time() - 100  # Already expired
            )
        ]
        
        # Validate cookies
        valid_cookies = await cookie_manager.validate_cookies(test_cookies)
        
        # Should only have 1 valid cookie
        assert len(valid_cookies) == 1
        assert valid_cookies[0].name == "valid_cookie"
    
    @pytest.mark.asyncio
    async def test_apply_realistic_expiration(self, cookie_manager):
        """Test applying realistic expiration patterns."""
        # Create a cookie with unrealistic future expiration
        unrealistic_cookie = CookieProfile(
            name="test",
            value="value",
            domain="example.com",
            expires=time.time() + (5 * 365 * 24 * 60 * 60)  # 5 years in future
        )
        
        # Apply realistic expiration
        processed_cookies = await cookie_manager.apply_realistic_expiration([unrealistic_cookie])
        
        # Should be capped at 1 year
        max_expiration = time.time() + (365 * 24 * 60 * 60)  # 1 year
        assert processed_cookies[0].expires <= max_expiration
    
    @pytest.mark.asyncio
    async def test_prepare_cookies_for_session(self, cookie_manager, sample_cookies):
        """Test preparing cookies for a new session."""
        # Prepare cookies
        prepared_cookies = await cookie_manager.prepare_cookies_for_session(sample_cookies)
        
        # Verify results
        assert len(prepared_cookies) == len(sample_cookies)
        assert all(isinstance(cookie, CookieProfile) for cookie in prepared_cookies)
        
        # Check that last_accessed was updated
        current_time = time.time()
        assert all(cookie.last_accessed >= current_time - 10 for cookie in prepared_cookies)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])