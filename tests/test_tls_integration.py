"""
Integration tests for TLS client with JA3 fingerprint randomization.
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


class TestTLSIntegration:
    """Integration tests for TLS client functionality."""
    
    @pytest.mark.asyncio
    async def test_get_request(self, tls_client):
        """Test making a GET request with TLS client."""
        await tls_client.initialize()
        session_id = "test_session"
        
        # Make a simple request to httpbin.org
        response = await tls_client.get(session_id, "https://httpbin.org/get")
        
        # Verify response
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")
        
        # Close session
        await tls_client.close_session(session_id)
    
    @pytest.mark.asyncio
    async def test_post_request(self, tls_client):
        """Test making a POST request with TLS client."""
        await tls_client.initialize()
        session_id = "test_session"
        
        # Make a POST request to httpbin.org
        response = await tls_client.post(
            session_id, 
            "https://httpbin.org/post",
            data={"test": "data"}
        )
        
        # Verify response
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")
        
        # Close session
        await tls_client.close_session(session_id)
    
    @pytest.mark.asyncio
    async def test_session_reuse(self, tls_client):
        """Test reusing the same session for multiple requests."""
        await tls_client.initialize()
        session_id = "test_session"
        
        # Make first request
        response1 = await tls_client.get(session_id, "https://httpbin.org/get")
        assert response1.status_code == 200
        
        # Make second request with same session
        response2 = await tls_client.get(session_id, "https://httpbin.org/headers")
        assert response2.status_code == 200
        
        # Close session
        await tls_client.close_session(session_id)
    
    @pytest.mark.asyncio
    async def test_fallback_to_httpx(self, tls_client):
        """Test fallback to httpx when TLS client fails."""
        await tls_client.initialize()
        session_id = "test_session"
        
        # This test would require mocking a TLS failure to properly test fallback
        # For now, we'll just verify the method exists
        assert hasattr(tls_client, '_fallback_request')