"""
Tests for TLS client with JA3 fingerprint randomization.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch

from src.ice_locator_mcp.anti_detection.tls.client import TLSClient
from src.ice_locator_mcp.core.config import SearchConfig
import httpx


@pytest.fixture
def search_config():
    """Create a search config for testing."""
    return SearchConfig()


@pytest.fixture
def tls_client(search_config):
    """Create a TLS client for testing."""
    return TLSClient(search_config)


class TestTLSClient:
    """Test TLS client functionality."""
    
    @pytest.mark.asyncio
    async def test_initialize(self, tls_client):
        """Test TLS client initialization."""
        await tls_client.initialize()
        # Initialization should complete without errors
        assert True
    
    @pytest.mark.asyncio
    async def test_create_session(self, tls_client):
        """Test creating TLS session."""
        session_id = "test_session"
        session = await tls_client.create_session(session_id)
        
        # Session should be created and stored
        assert session is not None
        assert session_id in tls_client.sessions
        assert tls_client.sessions[session_id] == session
    
    @pytest.mark.asyncio
    async def test_create_session_with_profile(self, tls_client):
        """Test creating TLS session with specific profile."""
        session_id = "test_session"
        profile = "chrome_109"
        session = await tls_client.create_session(session_id, profile)
        
        # Session should be created
        assert session is not None
    
    @pytest.mark.asyncio
    async def test_get_session(self, tls_client):
        """Test getting existing session."""
        session_id = "test_session"
        
        # Create session
        created_session = await tls_client.create_session(session_id)
        
        # Get session
        retrieved_session = await tls_client.get_session(session_id)
        
        # Should be the same session
        assert created_session == retrieved_session
    
    @pytest.mark.asyncio
    async def test_get_session_creates_new(self, tls_client):
        """Test getting session creates new if not exists."""
        session_id = "test_session"
        
        # Get non-existent session should create new one
        session = await tls_client.get_session(session_id)
        
        # Session should be created and stored
        assert session is not None
        assert session_id in tls_client.sessions
    
    @pytest.mark.asyncio
    async def test_get_random_profile(self, tls_client):
        """Test getting random TLS profile."""
        profile = tls_client.get_random_profile()
        
        # Should return a valid profile
        assert profile in tls_client.get_profile_list()
    
    @pytest.mark.asyncio
    async def test_get_profile_list(self, tls_client):
        """Test getting TLS profile list."""
        profiles = tls_client.get_profile_list()
        
        # Should return list of profiles
        assert isinstance(profiles, list)
        assert len(profiles) > 0
    
    @pytest.mark.asyncio
    async def test_close_session(self, tls_client):
        """Test closing TLS session."""
        session_id = "test_session"
        
        # Create session
        await tls_client.create_session(session_id)
        assert session_id in tls_client.sessions
        
        # Close session
        await tls_client.close_session(session_id)
        assert session_id not in tls_client.sessions
    
    @pytest.mark.asyncio
    async def test_close_all_sessions(self, tls_client):
        """Test closing all TLS sessions."""
        # Create multiple sessions
        session_ids = ["session_1", "session_2", "session_3"]
        for session_id in session_ids:
            await tls_client.create_session(session_id)
        
        # Verify sessions exist
        for session_id in session_ids:
            assert session_id in tls_client.sessions
        
        # Close all sessions
        await tls_client.close_all_sessions()
        
        # Verify all sessions closed
        assert len(tls_client.sessions) == 0


# Integration tests would require actual network access and are not included here
# to avoid external dependencies in unit tests.