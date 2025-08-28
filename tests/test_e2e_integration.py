"""
End-to-End Integration Tests for ICE Locator MCP Server.

Tests complete workflows from MCP client interactions through to 
ICE website scraping, including all anti-detection and processing components.
"""

import asyncio
import pytest
import json
import time
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

from src.ice_locator_mcp.server import ICELocatorServer
from src.ice_locator_mcp.core.config import Config
from src.ice_locator_mcp.anti_detection.coordinator import AntiDetectionCoordinator
from src.ice_locator_mcp.tools.search_engine import SearchEngine
from src.ice_locator_mcp.scraping.session_manager import SessionManager


class MockMCPMessage:
    """Mock MCP message for testing."""
    
    def __init__(self, method: str, params: Dict[str, Any]):
        self.method = method
        self.params = params


class MockMCPSession:
    """Mock MCP session for testing."""
    
    def __init__(self):
        self.messages = []
        self.responses = []
    
    async def send_message(self, message):
        self.messages.append(message)
        return {"id": len(self.messages), "result": "acknowledged"}
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]):
        """Mock tool call."""
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Mock result for {name} with args: {arguments}"
                }
            ],
            "isError": False
        }


@pytest.fixture
async def mock_ice_server():
    """Create mock ICE server for testing."""
    
    class MockResponse:
        def __init__(self, content: str, status_code: int = 200, cookies=None):
            self.content = content
            self.text = content
            self.status_code = status_code
            self.cookies = cookies or {}
        
        def json(self):
            return json.loads(self.content)
    
    # Mock successful search response
    search_response_html = """
    <html>
    <body>
        <div class="detainee-result">
            <div class="name">John William Doe</div>
            <div class="alien-number">A123456789</div>
            <div class="facility">Example Detention Center</div>
            <div class="address">123 Main St, Houston, TX 77001</div>
            <div class="booking-date">2023-01-15</div>
        </div>
    </body>
    </html>
    """
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = MockResponse(search_response_html)
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        yield mock_client


@pytest.fixture
async def test_config():
    """Create test configuration."""
    return Config({
        'server': {
            'debug': True,
            'rate_limiting': {'enabled': False}
        },
        'proxy': {'enabled': False},
        'caching': {'enabled': False},
        'anti_detection': {
            'behavioral_simulation': False,
            'traffic_distribution': False
        }
    })


@pytest.fixture
async def ice_server(test_config):
    """Create ICE Locator MCP server instance."""
    server = ICELocatorServer(test_config)
    await server.initialize()
    yield server
    await server.cleanup()


class TestCompleteWorkflows:
    """Test complete end-to-end workflows."""
    
    @pytest.mark.asyncio
    async def test_basic_name_search_workflow(self, ice_server, mock_ice_server):
        """Test complete name search workflow from MCP client to result."""
        
        # Create mock MCP session
        session = MockMCPSession()
        
        # Test search by name tool call
        result = await ice_server.handle_tool_call(
            "search_by_name",
            {
                "first_name": "John",
                "last_name": "Doe",
                "fuzzy_match": True,
                "confidence_threshold": 0.8
            },
            session
        )
        
        assert result["isError"] is False
        assert len(result["content"]) > 0
        assert "John" in result["content"][0]["text"]
        
        # Verify the search was processed through all components
        assert mock_ice_server.called
    
    @pytest.mark.asyncio
    async def test_alien_number_search_workflow(self, ice_server, mock_ice_server):
        """Test A-Number search workflow."""
        
        session = MockMCPSession()
        
        result = await ice_server.handle_tool_call(
            "search_by_alien_number",
            {
                "alien_number": "A123456789",
                "validate_format": True
            },
            session
        )
        
        assert result["isError"] is False
        assert "A123456789" in result["content"][0]["text"]
    
    @pytest.mark.asyncio
    async def test_facility_search_workflow(self, ice_server, mock_ice_server):
        """Test facility search workflow."""
        
        session = MockMCPSession()
        
        result = await ice_server.handle_tool_call(
            "search_by_facility",
            {
                "facility_name": "Example Detention Center",
                "city": "Houston",
                "state": "TX"
            },
            session
        )
        
        assert result["isError"] is False
        assert "Houston" in result["content"][0]["text"]
    
    @pytest.mark.asyncio
    async def test_natural_language_search_workflow(self, ice_server, mock_ice_server):
        """Test natural language query processing workflow."""
        
        session = MockMCPSession()
        
        result = await ice_server.handle_tool_call(
            "parse_natural_query",
            {
                "query": "Find John Doe at Houston facility",
                "auto_execute": True
            },
            session
        )
        
        assert result["isError"] is False
        content_text = result["content"][0]["text"]
        assert "John" in content_text or "parsed" in content_text.lower()
    
    @pytest.mark.asyncio
    async def test_bulk_search_workflow(self, ice_server, mock_ice_server):
        """Test bulk search operations."""
        
        session = MockMCPSession()
        
        searches = [
            {
                "type": "name",
                "first_name": "John",
                "last_name": "Doe"
            },
            {
                "type": "alien_number",
                "alien_number": "A123456789"
            },
            {
                "type": "facility",
                "facility_name": "Example Center"
            }
        ]
        
        result = await ice_server.handle_tool_call(
            "bulk_search",
            {
                "searches": searches,
                "max_concurrent": 2,
                "include_summary": True
            },
            session
        )
        
        assert result["isError"] is False
        assert "bulk" in result["content"][0]["text"].lower() or "summary" in result["content"][0]["text"].lower()


class TestAntiDetectionIntegration:
    """Test anti-detection integration in workflows."""
    
    @pytest.fixture
    async def anti_detection_config(self):
        """Config with anti-detection enabled."""
        return Config({
            'anti_detection': {
                'behavioral_simulation': True,
                'traffic_distribution': True,
                'proxy_rotation': False  # Disabled for testing
            }
        })
    
    @pytest.mark.asyncio
    async def test_behavioral_simulation_integration(self, anti_detection_config):
        """Test behavioral simulation integration in searches."""
        
        coordinator = AntiDetectionCoordinator(anti_detection_config)
        await coordinator.initialize()
        
        # Start a session
        session_info = await coordinator.start_session(
            "test_session",
            behavior_type="focused_search"
        )
        
        assert session_info["session_id"] == "test_session"
        assert "focused_search" in str(session_info["components_active"])
        
        # Mock request handler
        async def mock_request_handler(**kwargs):
            await asyncio.sleep(0.1)  # Simulate network request
            return {"status": "success", "data": "test result"}
        
        # Execute request with behavioral simulation
        result = await coordinator.execute_request(
            "test_session",
            {
                "type": "search",
                "page_content": {"content_length": 1000},
                "interaction_type": "form_input"
            },
            mock_request_handler
        )
        
        assert result["success"] is True
        assert "behavioral_flags" in result
        
        await coordinator.cleanup()
    
    @pytest.mark.asyncio
    async def test_error_handling_and_adaptation(self, anti_detection_config):
        """Test error handling and adaptive behavior."""
        
        coordinator = AntiDetectionCoordinator(anti_detection_config)
        await coordinator.initialize()
        
        await coordinator.start_session("error_test")
        
        # Mock request handler that fails with detection error
        async def failing_request_handler(**kwargs):
            if hasattr(failing_request_handler, 'call_count'):
                failing_request_handler.call_count += 1
            else:
                failing_request_handler.call_count = 1
            
            if failing_request_handler.call_count < 3:
                raise Exception("CAPTCHA required - bot detected")
            else:
                return {"status": "success", "data": "finally worked"}
        
        # Should adapt and eventually succeed
        try:
            result = await coordinator.execute_request(
                "error_test",
                {
                    "type": "search",
                    "max_retries": 3
                },
                failing_request_handler
            )
            
            # Should have adapted detection level
            assert coordinator.detection_level in ['medium', 'high', 'critical']
            
        except Exception:
            # If it still fails, check that adaptation occurred
            assert coordinator.global_metrics['detection_events'] > 0
        
        await coordinator.cleanup()


class TestPerformanceAndStability:
    """Test system performance and stability under load."""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, ice_server, mock_ice_server):
        """Test handling of concurrent requests."""
        
        session = MockMCPSession()
        
        # Create multiple concurrent search requests
        tasks = []
        for i in range(10):
            task = ice_server.handle_tool_call(
                "search_by_name",
                {
                    "first_name": f"John{i}",
                    "last_name": f"Doe{i}"
                },
                session
            )
            tasks.append(task)
        
        # Execute all requests concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        execution_time = time.time() - start_time
        
        # Verify results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= 8  # Allow for some failures
        
        # Should complete within reasonable time (with mocked network)
        assert execution_time < 5.0
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, ice_server, mock_ice_server):
        """Test memory usage doesn't grow excessively."""
        
        import gc
        import sys
        
        session = MockMCPSession()
        
        # Get initial memory usage
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Perform many operations
        for i in range(50):
            await ice_server.handle_tool_call(
                "search_by_name",
                {
                    "first_name": f"Test{i}",
                    "last_name": "User"
                },
                session
            )
            
            # Periodic cleanup
            if i % 10 == 0:
                gc.collect()
        
        # Check final memory usage
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Memory growth should be reasonable
        memory_growth = final_objects - initial_objects
        assert memory_growth < 1000, f"Excessive memory growth: {memory_growth} objects"
    
    @pytest.mark.asyncio
    async def test_long_running_stability(self, ice_server, mock_ice_server):
        """Test system stability over extended operation."""
        
        session = MockMCPSession()
        
        # Simulate long-running operation
        start_time = time.time()
        error_count = 0
        success_count = 0
        
        # Run for 30 iterations (simulating longer operation)
        for i in range(30):
            try:
                result = await ice_server.handle_tool_call(
                    "search_by_name",
                    {
                        "first_name": "TestUser",
                        "last_name": f"Session{i}"
                    },
                    session
                )
                
                if result["isError"]:
                    error_count += 1
                else:
                    success_count += 1
                    
                # Brief pause to simulate real usage
                await asyncio.sleep(0.1)
                
            except Exception:
                error_count += 1
        
        execution_time = time.time() - start_time
        
        # Verify stability metrics
        total_operations = success_count + error_count
        success_rate = success_count / total_operations if total_operations > 0 else 0
        
        assert success_rate >= 0.9, f"Success rate too low: {success_rate}"
        assert execution_time < 20.0, f"Operation took too long: {execution_time}s"


class TestClientIntegrations:
    """Test different MCP client integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_claude_desktop_integration(self, ice_server):
        """Test Claude Desktop MCP integration scenario."""
        
        # Simulate Claude Desktop MCP configuration
        config_data = {
            "mcpServers": {
                "ice-locator": {
                    "command": "ice-locator-mcp",
                    "args": [],
                    "env": {
                        "ICE_LOCATOR_CONFIG": "/path/to/config.json"
                    }
                }
            }
        }
        
        # Test tool discovery
        tools = await ice_server.list_tools()
        assert len(tools) > 0
        
        # Verify essential tools are available
        tool_names = [tool["name"] for tool in tools]
        essential_tools = [
            "search_by_name",
            "search_by_alien_number", 
            "search_by_facility",
            "parse_natural_query"
        ]
        
        for tool in essential_tools:
            assert tool in tool_names, f"Essential tool {tool} not found"
    
    @pytest.mark.asyncio
    async def test_programmatic_client_integration(self, ice_server):
        """Test programmatic MCP client integration."""
        
        # Simulate programmatic client usage
        session = MockMCPSession()
        
        # Test initialization
        initialization_result = await ice_server.initialize()
        assert initialization_result is None  # Should complete without error
        
        # Test batch operations
        batch_results = []
        
        search_queries = [
            ("search_by_name", {"first_name": "Maria", "last_name": "Garcia"}),
            ("search_by_alien_number", {"alien_number": "A987654321"}),
            ("parse_natural_query", {"query": "Find José Rodriguez in Miami"})
        ]
        
        for tool_name, args in search_queries:
            result = await ice_server.handle_tool_call(tool_name, args, session)
            batch_results.append(result)
        
        # Verify all operations completed
        assert len(batch_results) == len(search_queries)
        for result in batch_results:
            assert "content" in result
            assert len(result["content"]) > 0
    
    @pytest.mark.asyncio
    async def test_error_resilience_in_client_integration(self, ice_server):
        """Test client integration resilience to errors."""
        
        session = MockMCPSession()
        
        # Test invalid parameters
        invalid_result = await ice_server.handle_tool_call(
            "search_by_name",
            {
                "first_name": "",  # Invalid empty name
                "last_name": ""
            },
            session
        )
        
        # Should handle gracefully
        assert "isError" in invalid_result
        if invalid_result["isError"]:
            assert "content" in invalid_result
            assert len(invalid_result["content"]) > 0
        
        # Test non-existent tool
        try:
            await ice_server.handle_tool_call(
                "non_existent_tool",
                {},
                session
            )
        except Exception as e:
            # Should raise appropriate error
            assert "not found" in str(e).lower() or "unknown" in str(e).lower()
        
        # Test malformed parameters
        malformed_result = await ice_server.handle_tool_call(
            "search_by_alien_number",
            {
                "alien_number": "invalid_format_123"
            },
            session
        )
        
        # Should handle validation errors gracefully
        assert "content" in malformed_result


class TestSpanishLanguageIntegration:
    """Test Spanish language support integration."""
    
    @pytest.mark.asyncio
    async def test_spanish_query_processing(self, ice_server, mock_ice_server):
        """Test Spanish language query processing."""
        
        session = MockMCPSession()
        
        # Test Spanish natural language query
        result = await ice_server.handle_tool_call(
            "parse_natural_query",
            {
                "query": "Buscar a María González en Houston",
                "auto_execute": False
            },
            session
        )
        
        assert result["isError"] is False
        content_text = result["content"][0]["text"]
        
        # Should detect Spanish and process appropriately
        assert "maría" in content_text.lower() or "gonzalez" in content_text.lower()
    
    @pytest.mark.asyncio
    async def test_spanish_name_search(self, ice_server, mock_ice_server):
        """Test search with Spanish names and cultural matching."""
        
        session = MockMCPSession()
        
        # Test compound Spanish name
        result = await ice_server.handle_tool_call(
            "search_by_name",
            {
                "first_name": "José Luis",
                "last_name": "García Rodríguez",
                "fuzzy_match": True
            },
            session
        )
        
        assert result["isError"] is False
        assert len(result["content"]) > 0
    
    @pytest.mark.asyncio
    async def test_bilingual_error_messages(self, ice_server):
        """Test bilingual error message handling."""
        
        session = MockMCPSession()
        
        # Test error with Spanish context
        result = await ice_server.handle_tool_call(
            "search_by_name",
            {
                "first_name": "",  # Invalid
                "last_name": "",   # Invalid
                "language": "es"   # Spanish context
            },
            session
        )
        
        # Should provide appropriate error message
        assert "content" in result
        assert len(result["content"]) > 0


if __name__ == '__main__':
    pytest.main([__file__])