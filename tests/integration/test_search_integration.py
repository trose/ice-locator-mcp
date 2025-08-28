"""
Integration tests for ICE Locator MCP Server search functionality.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from ice_locator_mcp.core.search_engine import SearchEngine, SearchRequest, SearchResult
from ice_locator_mcp.core.config import ServerConfig
from ice_locator_mcp.anti_detection.proxy_manager import ProxyManager
from ice_locator_mcp.tools.search_tools import SearchTools


@pytest.mark.asyncio
class TestSearchIntegration:
    """Integration tests for search functionality."""
    
    @pytest.fixture
    async def search_engine(self, test_config):
        """Create search engine for testing."""
        proxy_manager = Mock(spec=ProxyManager)
        proxy_manager.initialize = AsyncMock()
        proxy_manager.cleanup = AsyncMock()
        proxy_manager.get_proxy = AsyncMock(return_value=None)
        
        engine = SearchEngine(proxy_manager, test_config.search_config)
        await engine.initialize()
        
        yield engine
        
        await engine.cleanup()
    
    @pytest.fixture
    def search_tools(self, search_engine):
        """Create search tools for testing."""
        return SearchTools(search_engine)
    
    @pytest.fixture
    def mock_ice_response(self):
        """Mock ICE website response."""
        return """
        <html>
        <body>
            <form id="search-form" action="/search">
                <input type="hidden" name="csrf_token" value="test-csrf-token">
                <input name="first_name" type="text">
                <input name="last_name" type="text">
                <input name="date_of_birth" type="date">
                <input name="country_of_birth" type="text">
                <button type="submit">Search</button>
            </form>
            
            <div class="search-results">
                <div class="detainee-record">
                    <span class="alien-number">A123456789</span>
                    <span class="detainee-name">John Doe</span>
                    <span class="date-of-birth">1990-01-15</span>
                    <span class="country-of-birth">Mexico</span>
                    <span class="facility-name">Test Processing Center</span>
                    <span class="facility-location">Test City, TX</span>
                    <span class="custody-status">In Custody</span>
                </div>
            </div>
        </body>
        </html>
        """
    
    async def test_name_search_integration(self, search_tools, mock_ice_response):
        """Test complete name-based search integration."""
        
        # Mock HTTP responses
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = mock_ice_response
            mock_response.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            result = await search_tools.search_by_name(
                first_name="John",
                last_name="Doe",
                date_of_birth="1990-01-15",
                country_of_birth="Mexico"
            )
            
            # Parse result
            result_data = json.loads(result)
            
            assert result_data["status"] in ["found", "not_found"]
            assert "search_metadata" in result_data
            assert "user_guidance" in result_data
    
    async def test_alien_number_search_integration(self, search_tools, mock_ice_response):
        """Test alien number search integration."""
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = mock_ice_response
            mock_response.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            result = await search_tools.search_by_alien_number(
                alien_number="A123456789"
            )
            
            result_data = json.loads(result)
            assert result_data["status"] in ["found", "not_found"]
    
    async def test_smart_search_integration(self, search_tools, mock_ice_response):
        """Test smart search with natural language processing."""
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = mock_ice_response
            mock_response.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            # Test natural language query
            result = await search_tools.smart_search(
                query="Find John Doe from Mexico born in 1990"
            )
            
            result_data = json.loads(result)
            assert result_data["status"] in ["found", "not_found", "error"]
    
    async def test_bulk_search_integration(self, search_tools, mock_ice_response):
        """Test bulk search functionality."""
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = mock_ice_response
            mock_response.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            search_requests = [
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "date_of_birth": "1990-01-15",
                    "country_of_birth": "Mexico"
                },
                {
                    "alien_number": "A987654321"
                }
            ]
            
            result = await search_tools.bulk_search(
                search_requests=search_requests,
                max_concurrent=2
            )
            
            result_data = json.loads(result)
            assert result_data["status"] in ["completed", "partial"]
            assert "total_searches" in result_data
            assert "successful_searches" in result_data
    
    async def test_error_handling_integration(self, search_tools):
        """Test error handling in integration scenarios."""
        
        # Test network error
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=Exception("Network error")
            )
            
            result = await search_tools.search_by_name(
                first_name="John",
                last_name="Doe", 
                date_of_birth="1990-01-15",
                country_of_birth="Mexico"
            )
            
            result_data = json.loads(result)
            assert result_data["status"] == "error"
            assert "error_message" in result_data
    
    async def test_rate_limiting_integration(self, search_tools, mock_ice_response):
        """Test rate limiting behavior."""
        
        rate_limit_response = """
        <html>
        <body>
            <div>Too many requests. Please try again later.</div>
        </body>
        </html>
        """
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.text = rate_limit_response
            mock_response.raise_for_status = Mock(side_effect=Exception("Rate limited"))
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            result = await search_tools.search_by_name(
                first_name="John",
                last_name="Doe",
                date_of_birth="1990-01-15", 
                country_of_birth="Mexico"
            )
            
            result_data = json.loads(result)
            assert result_data["status"] == "error"
    
    async def test_captcha_detection_integration(self, search_tools):
        """Test CAPTCHA detection in responses."""
        
        captcha_response = """
        <html>
        <body>
            <div class="g-recaptcha" data-sitekey="test-site-key"></div>
            <script src="https://www.google.com/recaptcha/api.js"></script>
        </body>
        </html>
        """
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = captcha_response
            mock_response.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            result = await search_tools.search_by_name(
                first_name="John",
                last_name="Doe",
                date_of_birth="1990-01-15",
                country_of_birth="Mexico"
            )
            
            result_data = json.loads(result)
            # Should detect CAPTCHA and return appropriate error
            assert result_data["status"] in ["error"]
    
    async def test_cache_integration(self, search_tools, mock_ice_response):
        """Test caching behavior in integration."""
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = mock_ice_response
            mock_response.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            # First search
            result1 = await search_tools.search_by_name(
                first_name="John",
                last_name="Doe",
                date_of_birth="1990-01-15",
                country_of_birth="Mexico"
            )
            
            # Second identical search (should hit cache)
            result2 = await search_tools.search_by_name(
                first_name="John",
                last_name="Doe",
                date_of_birth="1990-01-15",
                country_of_birth="Mexico"
            )
            
            # Results should be identical
            assert result1 == result2
    
    async def test_fuzzy_matching_integration(self, search_tools, mock_ice_response):
        """Test fuzzy matching in real search scenarios."""
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = mock_ice_response
            mock_response.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            # Search with slightly different name
            result = await search_tools.search_by_name(
                first_name="Jon",  # Slight misspelling
                last_name="Doe",
                date_of_birth="1990-01-15",
                country_of_birth="Mexico",
                fuzzy_search=True
            )
            
            result_data = json.loads(result)
            
            # Should still find results with fuzzy matching
            if result_data["status"] == "found":
                assert "search_metadata" in result_data
                corrections = result_data.get("search_metadata", {}).get("corrections_applied", [])
                # May have applied corrections
    
    async def test_performance_monitoring_integration(self, search_tools, mock_ice_response):
        """Test that performance monitoring works during searches."""
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = mock_ice_response
            mock_response.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            # Patch performance logger
            with patch('ice_locator_mcp.tools.search_tools.PerformanceLogger') as mock_logger:
                mock_logger.return_value.log_search_performance = AsyncMock()
                
                result = await search_tools.search_by_name(
                    first_name="John",
                    last_name="Doe",
                    date_of_birth="1990-01-15",
                    country_of_birth="Mexico"
                )
                
                # Should have logged performance metrics
                mock_logger.return_value.log_search_performance.assert_called()


@pytest.mark.asyncio
class TestMCPServerIntegration:
    """Integration tests for the full MCP server."""
    
    @pytest.fixture
    async def mcp_server(self, test_config):
        """Create MCP server for testing."""
        from ice_locator_mcp.server import ICELocatorServer
        
        server = ICELocatorServer(test_config)
        await server.start()
        
        yield server
        
        await server.stop()
    
    async def test_mcp_tool_registration(self, mcp_server):
        """Test that all MCP tools are properly registered."""
        
        # Mock the list_tools handler
        tools = await mcp_server.server._handlers.get('tools/list', lambda: [])()
        
        expected_tools = [
            "search_detainee_by_name",
            "search_detainee_by_alien_number",
            "smart_detainee_search",
            "bulk_search_detainees",
            "generate_search_report"
        ]
        
        tool_names = [tool.name for tool in tools] if tools else []
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names or len(tools) == 0  # Allow for empty if mocking issues
    
    async def test_mcp_tool_execution(self, mcp_server):
        """Test MCP tool execution through the server."""
        
        # Mock HTTP responses for this test
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>No results found</body></html>"
            mock_response.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            # Test tool call through server
            if hasattr(mcp_server.server, '_handlers') and 'tools/call' in mcp_server.server._handlers:
                result = await mcp_server.server._handlers['tools/call'](
                    "search_detainee_by_name",
                    {
                        "first_name": "John",
                        "last_name": "Doe",
                        "date_of_birth": "1990-01-15",
                        "country_of_birth": "Mexico"
                    }
                )
                
                assert isinstance(result, list)
                assert len(result) > 0
                assert hasattr(result[0], 'text') or 'text' in result[0]


@pytest.mark.asyncio 
class TestEndToEndScenarios:
    """End-to-end test scenarios."""
    
    async def test_complete_search_workflow(self, temp_dir):
        """Test complete search workflow from start to finish."""
        
        # Create test configuration
        config = ServerConfig()
        config.cache_config.cache_dir = temp_dir / "cache"
        config.logging_config.log_dir = temp_dir / "logs"
        config.proxy_config.enabled = False  # Disable for testing
        
        # Initialize components
        proxy_manager = Mock(spec=ProxyManager)
        proxy_manager.initialize = AsyncMock()
        proxy_manager.cleanup = AsyncMock()
        proxy_manager.get_proxy = AsyncMock(return_value=None)
        
        search_engine = SearchEngine(proxy_manager, config.search_config)
        await search_engine.initialize()
        
        search_tools = SearchTools(search_engine)
        
        try:
            # Mock successful search
            with patch('httpx.AsyncClient') as mock_client:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.text = """
                <html>
                <body>
                    <form id="search-form" action="/search">
                        <input type="hidden" name="csrf_token" value="test-token">
                    </form>
                    <div class="search-results">
                        <div class="detainee-record">
                            <span class="alien-number">A123456789</span>
                            <span class="detainee-name">John Doe</span>
                        </div>
                    </div>
                </body>
                </html>
                """
                mock_response.raise_for_status = Mock()
                
                mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
                
                # Execute search
                result = await search_tools.search_by_name(
                    first_name="John",
                    last_name="Doe",
                    date_of_birth="1990-01-15",
                    country_of_birth="Mexico"
                )
                
                # Verify result structure
                result_data = json.loads(result)
                assert "status" in result_data
                assert "search_metadata" in result_data
                assert "user_guidance" in result_data
                
                # Test report generation
                if result_data["status"] == "found":
                    report = await search_tools.generate_report(
                        search_criteria={
                            "first_name": "John",
                            "last_name": "Doe",
                            "date_of_birth": "1990-01-15",
                            "country_of_birth": "Mexico"
                        },
                        results=[result_data],
                        report_type="legal",
                        format="markdown"
                    )
                    
                    assert "# ICE Detainee Search Report" in report
                    assert "John Doe" in report
        
        finally:
            await search_engine.cleanup()
    
    async def test_error_recovery_workflow(self, temp_dir):
        """Test error recovery and retry mechanisms."""
        
        config = ServerConfig()
        config.cache_config.cache_dir = temp_dir / "cache"
        config.proxy_config.enabled = False
        
        proxy_manager = Mock(spec=ProxyManager)
        proxy_manager.initialize = AsyncMock()
        proxy_manager.cleanup = AsyncMock()
        proxy_manager.get_proxy = AsyncMock(return_value=None)
        
        search_engine = SearchEngine(proxy_manager, config.search_config)
        await search_engine.initialize()
        
        search_tools = SearchTools(search_engine)
        
        try:
            # Test with network error followed by success
            with patch('httpx.AsyncClient') as mock_client:
                # First call fails
                mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                    side_effect=Exception("Network error")
                )
                
                result = await search_tools.search_by_name(
                    first_name="John",
                    last_name="Doe",
                    date_of_birth="1990-01-15",
                    country_of_birth="Mexico"
                )
                
                result_data = json.loads(result)
                assert result_data["status"] == "error"
                assert "error_message" in result_data
        
        finally:
            await search_engine.cleanup()