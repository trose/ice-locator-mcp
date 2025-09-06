"""
Tests for TLS client with JA3 fingerprint randomization.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch

from src.ice_locator_mcp.anti_detection.tls.client import TLSClient
from src.ice_locator_mcp.core.config import SearchConfig
from noble_tls.exceptions.exceptions import TLSClientException
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

    @pytest.mark.asyncio
    async def test_create_session_exception_handling(self, tls_client):
        """Test exception handling in create_session."""
        session_id = "test_session"
        
        # Mock Session to raise an exception
        with patch('src.ice_locator_mcp.anti_detection.tls.client.Session') as mock_session:
            mock_session.side_effect = Exception("Test exception")
            
            # Should raise the exception
            with pytest.raises(Exception, match="Test exception"):
                await tls_client.create_session(session_id)

    @pytest.mark.asyncio
    async def test_request_tls_exception_handling(self, tls_client):
        """Test TLSClientException handling in request method."""
        session_id = "test_session"
        url = "https://httpbin.org/get"
        
        # Mock session to raise TLSClientException
        with patch.object(tls_client, 'get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.execute_request.side_effect = TLSClientException("TLS error")
            mock_get_session.return_value = mock_session
            
            # Mock _fallback_request to return a response
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200
            with patch.object(tls_client, '_fallback_request', return_value=mock_response) as mock_fallback:
                response = await tls_client.request(session_id, "GET", url)
                
                # Should call fallback and return its response
                assert response == mock_response
                mock_fallback.assert_called_once()

    @pytest.mark.asyncio
    async def test_request_general_exception_handling(self, tls_client):
        """Test general Exception handling in request method."""
        session_id = "test_session"
        url = "https://httpbin.org/get"
        
        # Mock session to raise a general exception
        with patch.object(tls_client, 'get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.execute_request.side_effect = Exception("General error")
            mock_get_session.return_value = mock_session
            
            # Should raise the exception
            with pytest.raises(Exception, match="General error"):
                await tls_client.request(session_id, "GET", url)

    @pytest.mark.asyncio
    async def test_fallback_request_other_method(self, tls_client):
        """Test _fallback_request with non-GET/POST method."""
        # Mock httpx.AsyncClient to return a response
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        
        with patch('src.ice_locator_mcp.anti_detection.tls.client.httpx.AsyncClient') as mock_client:
            mock_async_client = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_async_client
            mock_async_client.request.return_value = mock_response
            
            # Call with PUT method (should go to else branch)
            response = await tls_client._fallback_request("PUT", "https://httpbin.org/put")
            
            # Should return the response from the generic request method
            assert response == mock_response
            mock_async_client.request.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_session_exception_handling(self, tls_client):
        """Test exception handling in close_session."""
        session_id = "test_session"
        
        # Create a session first
        await tls_client.create_session(session_id)
        assert session_id in tls_client.sessions
        
        # Test normal close operation
        await tls_client.close_session(session_id)
        assert session_id not in tls_client.sessions
        
        # Test closing non-existent session (should not raise error)
        await tls_client.close_session("non_existent_session")
        # Should complete without error
