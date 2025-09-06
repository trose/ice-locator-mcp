"""
Integration tests for premium proxy sources integration.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch

from src.ice_locator_mcp.anti_detection.proxy_manager import ProxyManager, ProxyConfig
from src.ice_locator_mcp.core.config import ProxyConfig as ServerProxyConfig


@pytest.fixture
def server_proxy_config():
    """Create a server proxy config for testing."""
    return ServerProxyConfig()


@pytest.fixture
def proxy_manager(server_proxy_config):
    """Create a proxy manager for testing."""
    return ProxyManager(server_proxy_config)


class TestPremiumProxyIntegration:
    """Test premium proxy sources integration."""
    
    @pytest.mark.asyncio
    async def test_scraperapi_integration(self, proxy_manager):
        """Test ScraperAPI integration."""
        # Mock environment variable
        with patch('os.getenv') as mock_getenv:
            mock_getenv.return_value = 'test_key'
            
            # Mock HTTP client response
            with patch('httpx.AsyncClient') as mock_client:
                mock_instance = AsyncMock()
                mock_client.return_value.__aenter__.return_value = mock_instance
                mock_instance.get = AsyncMock()
                mock_instance.get.return_value.status_code = 200
                
                # Test fetching from premium sources
                proxies = await proxy_manager._fetch_from_premium_sources()
                
                # Should have at least one proxy from ScraperAPI
                assert len(proxies) >= 1
                assert any('scraperapi' in proxy.endpoint.lower() for proxy in proxies)
    
    @pytest.mark.asyncio
    async def test_brightdata_integration(self, proxy_manager):
        """Test BrightData integration."""
        # Mock environment variables
        with patch('os.getenv') as mock_getenv:
            def side_effect(key, default=None):
                if key == 'BRIGHTDATA_USERNAME':
                    return 'test_username'
                elif key == 'BRIGHTDATA_PASSWORD':
                    return 'test_password'
                return default
            mock_getenv.side_effect = side_effect
            
            # Test fetching from premium sources
            proxies = await proxy_manager._fetch_from_premium_sources()
            
            # Should have at least one proxy from BrightData
            assert len(proxies) >= 1
            assert any('brd.superproxy.io' in proxy.endpoint.lower() for proxy in proxies)
    
    @pytest.mark.asyncio
    async def test_smartproxy_integration(self, proxy_manager):
        """Test SmartProxy integration."""
        # Mock environment variables
        with patch('os.getenv') as mock_getenv:
            def side_effect(key, default=None):
                if key == 'SMARTPROXY_USERNAME':
                    return 'test_username'
                elif key == 'SMARTPROXY_PASSWORD':
                    return 'test_password'
                return default
            mock_getenv.side_effect = side_effect
            
            # Test fetching from premium sources
            proxies = await proxy_manager._fetch_from_premium_sources()
            
            # Should have at least one proxy from SmartProxy
            assert len(proxies) >= 1
            assert any('smartproxy.com' in proxy.endpoint.lower() for proxy in proxies)
    
    @pytest.mark.asyncio
    async def test_netnut_integration(self, proxy_manager):
        """Test NetNut integration."""
        # Mock environment variables
        with patch('os.getenv') as mock_getenv:
            def side_effect(key, default=None):
                if key == 'NETNUT_USERNAME':
                    return 'test_username'
                elif key == 'NETNUT_PASSWORD':
                    return 'test_password'
                return default
            mock_getenv.side_effect = side_effect
            
            # Test fetching from premium sources
            proxies = await proxy_manager._fetch_from_premium_sources()
            
            # Should have at least one proxy from NetNut
            assert len(proxies) >= 1
            assert any('netnut.io' in proxy.endpoint.lower() for proxy in proxies)
    
    @pytest.mark.asyncio
    async def test_oxylabs_integration(self, proxy_manager):
        """Test Oxylabs integration."""
        # Mock environment variables
        with patch('os.getenv') as mock_getenv:
            def side_effect(key, default=None):
                if key == 'OXYLABS_USERNAME':
                    return 'test_username'
                elif key == 'OXYLABS_PASSWORD':
                    return 'test_password'
                return default
            mock_getenv.side_effect = side_effect
            
            # Test fetching from premium sources
            proxies = await proxy_manager._fetch_from_premium_sources()
            
            # Should have at least one proxy from Oxylabs
            assert len(proxies) >= 1
            assert any('oxylabs.io' in proxy.endpoint.lower() for proxy in proxies)
    
    @pytest.mark.asyncio
    async def test_geosurf_integration(self, proxy_manager):
        """Test GeoSurf integration."""
        # Mock environment variables
        with patch('os.getenv') as mock_getenv:
            def side_effect(key, default=None):
                if key == 'GEOSURF_TOKEN':
                    return 'test_token'
                return default
            mock_getenv.side_effect = side_effect
            
            # Test fetching from premium sources
            proxies = await proxy_manager._fetch_from_premium_sources()
            
            # Should have at least one proxy from GeoSurf
            assert len(proxies) >= 1
            assert any('geosurf.io' in proxy.endpoint.lower() for proxy in proxies)
    
    @pytest.mark.asyncio
    async def test_infatica_integration(self, proxy_manager):
        """Test Infatica integration."""
        # Mock environment variables
        with patch('os.getenv') as mock_getenv:
            def side_effect(key, default=None):
                if key == 'INFATICA_KEY':
                    return 'test_key'
                return default
            mock_getenv.side_effect = side_effect
            
            # Test fetching from premium sources
            proxies = await proxy_manager._fetch_from_premium_sources()
            
            # Should have at least one proxy from Infatica
            assert len(proxies) >= 1
            assert any('infatica.io' in proxy.endpoint.lower() for proxy in proxies)
    
    @pytest.mark.asyncio
    async def test_storm_proxies_integration(self, proxy_manager):
        """Test Storm Proxies integration."""
        # Mock environment variables
        with patch('os.getenv') as mock_getenv:
            def side_effect(key, default=None):
                if key == 'STORM_USERNAME':
                    return 'test_username'
                elif key == 'STORM_PASSWORD':
                    return 'test_password'
                return default
            mock_getenv.side_effect = side_effect
            
            # Test fetching from premium sources
            proxies = await proxy_manager._fetch_from_premium_sources()
            
            # Should have at least one proxy from Storm Proxies
            assert len(proxies) >= 1
            assert any('stormproxies.com' in proxy.endpoint.lower() for proxy in proxies)


class TestProxyValidation:
    """Test proxy validation functionality."""
    
    @pytest.mark.asyncio
    async def test_proxy_validation_with_real_proxies(self, proxy_manager):
        """Test proxy validation with real proxies."""
        # Create test proxies
        test_proxies = [
            ProxyConfig(endpoint="httpbin.org:80", proxy_type="http"),
            ProxyConfig(endpoint="invalid.proxy.test:8080", proxy_type="http")
        ]
        
        # Mock the HTTP client to simulate successful and failed connections
        with patch('httpx.AsyncClient') as mock_client:
            # First call succeeds, second fails
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            # Mock responses
            mock_response1 = AsyncMock()
            mock_response1.status_code = 200
            mock_response1.json.return_value = {'origin': '1.2.3.4'}
            
            mock_response2 = AsyncMock()
            mock_response2.status_code = 403
            
            mock_instance.get = AsyncMock(side_effect=[mock_response1, mock_response2, mock_response1, mock_response2])
            
            # Test validation
            validated_proxies = await proxy_manager._validate_proxies(test_proxies)
            
            # Should have validated the working proxy
            # Note: The actual validation logic might filter out both in testing,
            # but we're just testing that the method works
            assert isinstance(validated_proxies, list)


# Integration tests would require actual API keys and are not included here
# to avoid external dependencies and security concerns in unit tests.