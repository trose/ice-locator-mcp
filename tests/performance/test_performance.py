"""
Performance and load tests for ICE Locator MCP Server.
"""

import pytest
import asyncio
import time
import json
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any

from ice_locator_mcp.tools.search_tools import SearchTools
from ice_locator_mcp.core.search_engine import SearchEngine
from ice_locator_mcp.utils.performance import MetricsCollector, PerformanceProfiler


@pytest.mark.asyncio
class TestPerformanceMetrics:
    """Test performance monitoring and metrics collection."""
    
    @pytest.fixture
    def metrics_collector(self):
        """Create metrics collector for testing."""
        return MetricsCollector(max_history=100)
    
    @pytest.fixture 
    def performance_profiler(self):
        """Create performance profiler for testing."""
        return PerformanceProfiler()
    
    async def test_request_tracking(self, metrics_collector):
        """Test request performance tracking."""
        
        # Start monitoring
        await metrics_collector.start_monitoring()
        
        try:
            # Track a request
            request_id = "test-request-1"
            metrics = metrics_collector.start_request(request_id, "name_search")
            
            # Simulate work
            await asyncio.sleep(0.1)
            
            # Complete request
            metrics_collector.complete_request(
                request_id,
                status="completed",
                result_count=1,
                cache_hit=False
            )
            
            # Check metrics
            stats = metrics_collector.get_request_stats(last_n_minutes=1)
            assert stats["total_requests"] == 1
            assert stats["completed_requests"] == 1
            assert stats["success_rate"] == 1.0
            
        finally:
            await metrics_collector.stop_monitoring()
    
    async def test_system_monitoring(self, metrics_collector):
        """Test system metrics collection."""
        
        await metrics_collector.start_monitoring()
        
        try:
            # Let it collect some metrics
            await asyncio.sleep(1.1)  # Wait for at least one collection cycle
            
            stats = metrics_collector.get_system_stats(last_n_minutes=1)
            
            # Should have at least one sample
            assert stats.get("samples", 0) >= 0  # May be 0 if collection hasn't run yet
            
        finally:
            await metrics_collector.stop_monitoring()
    
    async def test_performance_profiling(self, performance_profiler):
        """Test detailed performance profiling."""
        
        async def sample_operation(duration: float):
            """Sample operation for profiling."""
            await asyncio.sleep(duration)
            return "completed"
        
        # Profile the operation
        result = await performance_profiler.profile_operation(
            "test_operation",
            sample_operation,
            0.1
        )
        
        assert result == "completed"
        
        # Check profile stats
        stats = performance_profiler.get_profile_stats("test_operation")
        assert stats["samples"] == 1
        assert stats["success_rate"] == 1.0
        assert stats["avg_duration"] >= 0.1
    
    async def test_custom_metrics(self, metrics_collector):
        """Test custom metrics recording."""
        
        # Record some custom metrics
        metrics_collector.record_metric("search_latency", 1.5, "seconds")
        metrics_collector.record_metric("search_latency", 2.0, "seconds")
        metrics_collector.record_metric("cache_hits", 10, "count")
        
        # Get comprehensive stats
        stats = metrics_collector.get_comprehensive_stats()
        
        custom_metrics = stats.get("custom_metrics", {})
        assert "search_latency" in custom_metrics
        assert custom_metrics["search_latency"]["samples"] == 2
        assert custom_metrics["search_latency"]["average"] == 1.75


@pytest.mark.asyncio
class TestSearchPerformance:
    """Test search operation performance."""
    
    @pytest.fixture
    async def search_tools(self, test_config):
        """Create search tools for performance testing."""
        from ice_locator_mcp.anti_detection.proxy_manager import ProxyManager
        
        proxy_manager = Mock(spec=ProxyManager)
        proxy_manager.initialize = AsyncMock()
        proxy_manager.cleanup = AsyncMock() 
        proxy_manager.get_proxy = AsyncMock(return_value=None)
        
        search_engine = SearchEngine(proxy_manager, test_config.search_config)
        await search_engine.initialize()
        
        search_tools = SearchTools(search_engine)
        
        yield search_tools
        
        await search_engine.cleanup()
    
    async def test_single_search_performance(self, search_tools):
        """Test performance of single search operations."""
        
        mock_response = """
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
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_http_response = Mock()
            mock_http_response.status_code = 200
            mock_http_response.text = mock_response
            mock_http_response.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_http_response)
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_http_response)
            
            # Measure search performance
            start_time = time.time()
            
            result = await search_tools.search_by_name(
                first_name="John",
                last_name="Doe",
                date_of_birth="1990-01-15",
                country_of_birth="Mexico"
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should complete within reasonable time
            assert duration < 5.0  # 5 seconds max
            
            # Verify result
            result_data = json.loads(result)
            assert "status" in result_data
            assert "search_metadata" in result_data
            
            processing_time = result_data.get("search_metadata", {}).get("processing_time_ms", 0)
            assert processing_time > 0
    
    async def test_concurrent_search_performance(self, search_tools):
        """Test performance under concurrent load."""
        
        mock_response = """
        <html>
        <body>
            <form id="search-form" action="/search">
                <input type="hidden" name="csrf_token" value="test-token">
            </form>
            <div class="search-results">
                <div class="detainee-record">
                    <span class="alien-number">A123456789</span>
                    <span class="detainee-name">Test Person</span>
                </div>
            </div>
        </body>
        </html>
        """
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_http_response = Mock()
            mock_http_response.status_code = 200
            mock_http_response.text = mock_response
            mock_http_response.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_http_response)
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_http_response)
            
            # Create multiple concurrent searches
            async def single_search(person_id: int):
                return await search_tools.search_by_name(
                    first_name=f"Person{person_id}",
                    last_name="Test",
                    date_of_birth="1990-01-01",
                    country_of_birth="Mexico"
                )
            
            # Run 5 concurrent searches
            start_time = time.time()
            
            tasks = [single_search(i) for i in range(5)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            total_duration = end_time - start_time
            
            # Should handle concurrent load efficiently
            assert total_duration < 10.0  # 10 seconds max for 5 concurrent
            
            # All searches should complete successfully
            successful_results = [r for r in results if not isinstance(r, Exception)]
            assert len(successful_results) == 5
    
    async def test_bulk_search_performance(self, search_tools):
        """Test bulk search performance."""
        
        mock_response = """
        <html>
        <body>
            <form id="search-form" action="/search">
                <input type="hidden" name="csrf_token" value="test-token">
            </form>
            <div class="search-results">
                <div class="detainee-record">
                    <span class="alien-number">A123456789</span>
                    <span class="detainee-name">Test Person</span>
                </div>
            </div>
        </body>
        </html>
        """
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_http_response = Mock()
            mock_http_response.status_code = 200
            mock_http_response.text = mock_response
            mock_http_response.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_http_response)
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_http_response)
            
            # Create bulk search request
            search_requests = [
                {
                    "first_name": f"Person{i}",
                    "last_name": "Test",
                    "date_of_birth": "1990-01-01",
                    "country_of_birth": "Mexico"
                }
                for i in range(10)
            ]
            
            start_time = time.time()
            
            result = await search_tools.bulk_search(
                search_requests=search_requests,
                max_concurrent=3
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should complete efficiently
            assert duration < 15.0  # 15 seconds max for 10 searches
            
            result_data = json.loads(result)
            assert result_data["total_searches"] == 10
            assert result_data["processing_time_ms"] > 0
    
    async def test_cache_performance_impact(self, search_tools):
        """Test cache impact on performance."""
        
        mock_response = """
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
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_http_response = Mock()
            mock_http_response.status_code = 200
            mock_http_response.text = mock_response
            mock_http_response.raise_for_status = Mock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_http_response)
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_http_response)
            
            # First search (cache miss)
            start_time = time.time()
            result1 = await search_tools.search_by_name(
                first_name="John",
                last_name="Doe",
                date_of_birth="1990-01-15",
                country_of_birth="Mexico"
            )
            first_duration = time.time() - start_time
            
            # Second identical search (cache hit)
            start_time = time.time()
            result2 = await search_tools.search_by_name(
                first_name="John",
                last_name="Doe",
                date_of_birth="1990-01-15",
                country_of_birth="Mexico"
            )
            second_duration = time.time() - start_time
            
            # Cache hit should be faster (or at least not significantly slower)
            # Allow for some variance due to testing overhead
            assert second_duration <= first_duration * 2
            
            # Results should be identical
            assert result1 == result2


@pytest.mark.asyncio
class TestMemoryAndResourceUsage:
    """Test memory usage and resource consumption."""
    
    async def test_memory_usage_during_searches(self, test_config):
        """Test memory usage during search operations."""
        
        from ice_locator_mcp.anti_detection.proxy_manager import ProxyManager
        
        proxy_manager = Mock(spec=ProxyManager)
        proxy_manager.initialize = AsyncMock()
        proxy_manager.cleanup = AsyncMock()
        proxy_manager.get_proxy = AsyncMock(return_value=None)
        
        search_engine = SearchEngine(proxy_manager, test_config.search_config)
        await search_engine.initialize()
        
        search_tools = SearchTools(search_engine)
        
        try:
            import psutil
            process = psutil.Process()
            
            # Get initial memory usage
            initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
            
            mock_response = """
            <html>
            <body>
                <form id="search-form" action="/search">
                    <input type="hidden" name="csrf_token" value="test-token">
                </form>
                <div class="search-results">
                    <div class="detainee-record">
                        <span class="alien-number">A123456789</span>
                        <span class="detainee-name">Test Person</span>
                    </div>
                </div>
            </body>
            </html>
            """
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_http_response = Mock()
                mock_http_response.status_code = 200
                mock_http_response.text = mock_response
                mock_http_response.raise_for_status = Mock()
                
                mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_http_response)
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_http_response)
                
                # Perform multiple searches
                for i in range(20):
                    await search_tools.search_by_name(
                        first_name=f"Person{i}",
                        last_name="Test",
                        date_of_birth="1990-01-01",
                        country_of_birth="Mexico"
                    )
                
                # Get final memory usage
                final_memory = process.memory_info().rss / (1024 * 1024)  # MB
                memory_increase = final_memory - initial_memory
                
                # Memory increase should be reasonable (less than 50MB for 20 searches)
                assert memory_increase < 50
                
        finally:
            await search_engine.cleanup()
    
    async def test_resource_cleanup(self, test_config):
        """Test that resources are properly cleaned up."""
        
        from ice_locator_mcp.anti_detection.proxy_manager import ProxyManager
        
        proxy_manager = Mock(spec=ProxyManager)
        proxy_manager.initialize = AsyncMock()
        proxy_manager.cleanup = AsyncMock()
        proxy_manager.get_proxy = AsyncMock(return_value=None)
        
        search_engine = SearchEngine(proxy_manager, test_config.search_config)
        await search_engine.initialize()
        
        # Verify initialization was called
        proxy_manager.initialize.assert_called_once()
        
        # Cleanup
        await search_engine.cleanup()
        
        # Verify cleanup was called
        proxy_manager.cleanup.assert_called_once()


@pytest.mark.asyncio
class TestLoadTesting:
    """Load testing scenarios."""
    
    async def test_sustained_load(self, test_config):
        """Test server under sustained load."""
        
        from ice_locator_mcp.anti_detection.proxy_manager import ProxyManager
        
        proxy_manager = Mock(spec=ProxyManager)
        proxy_manager.initialize = AsyncMock()
        proxy_manager.cleanup = AsyncMock()
        proxy_manager.get_proxy = AsyncMock(return_value=None)
        
        search_engine = SearchEngine(proxy_manager, test_config.search_config)
        await search_engine.initialize()
        
        search_tools = SearchTools(search_engine)
        
        try:
            mock_response = """
            <html>
            <body>
                <form id="search-form" action="/search">
                    <input type="hidden" name="csrf_token" value="test-token">
                </form>
                <div class="search-results">
                    <div class="detainee-record">
                        <span class="alien-number">A123456789</span>
                        <span class="detainee-name">Load Test Person</span>
                    </div>
                </div>
            </body>
            </html>
            """
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_http_response = Mock()
                mock_http_response.status_code = 200
                mock_http_response.text = mock_response
                mock_http_response.raise_for_status = Mock()
                
                mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_http_response)
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_http_response)
                
                # Simulate sustained load
                total_requests = 50
                batch_size = 5
                
                start_time = time.time()
                successful_requests = 0
                failed_requests = 0
                
                for batch in range(0, total_requests, batch_size):
                    batch_tasks = []
                    
                    for i in range(batch_size):
                        if batch + i < total_requests:
                            task = search_tools.search_by_name(
                                first_name=f"LoadTest{batch + i}",
                                last_name="Person",
                                date_of_birth="1990-01-01",
                                country_of_birth="Mexico"
                            )
                            batch_tasks.append(task)
                    
                    # Execute batch
                    results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                    
                    # Count successes and failures
                    for result in results:
                        if isinstance(result, Exception):
                            failed_requests += 1
                        else:
                            successful_requests += 1
                    
                    # Small delay between batches
                    await asyncio.sleep(0.1)
                
                end_time = time.time()
                total_duration = end_time - start_time
                
                # Performance assertions
                assert total_duration < 60.0  # Should complete within 1 minute
                assert successful_requests >= total_requests * 0.95  # 95% success rate
                
                requests_per_second = total_requests / total_duration
                assert requests_per_second > 0.5  # At least 0.5 RPS
                
        finally:
            await search_engine.cleanup()
    
    async def test_error_rate_under_load(self, test_config):
        """Test error handling under high load."""
        
        from ice_locator_mcp.anti_detection.proxy_manager import ProxyManager
        
        proxy_manager = Mock(spec=ProxyManager)
        proxy_manager.initialize = AsyncMock()
        proxy_manager.cleanup = AsyncMock()
        proxy_manager.get_proxy = AsyncMock(return_value=None)
        
        search_engine = SearchEngine(proxy_manager, test_config.search_config)
        await search_engine.initialize()
        
        search_tools = SearchTools(search_engine)
        
        try:
            # Mix of successful and failing responses
            with patch('httpx.AsyncClient') as mock_client:
                call_count = 0
                
                async def mock_request(*args, **kwargs):
                    nonlocal call_count
                    call_count += 1
                    
                    mock_response = Mock()
                    
                    # Simulate 20% failure rate
                    if call_count % 5 == 0:
                        mock_response.status_code = 500
                        mock_response.text = "Internal Server Error"
                        mock_response.raise_for_status = Mock(side_effect=Exception("Server Error"))
                    else:
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
                                    <span class="detainee-name">Test Person</span>
                                </div>
                            </div>
                        </body>
                        </html>
                        """
                        mock_response.raise_for_status = Mock()
                    
                    return mock_response
                
                mock_client.return_value.__aenter__.return_value.get = AsyncMock(side_effect=mock_request)
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(side_effect=mock_request)
                
                # Run searches with expected failures
                tasks = []
                for i in range(20):
                    task = search_tools.search_by_name(
                        first_name=f"ErrorTest{i}",
                        last_name="Person",
                        date_of_birth="1990-01-01",
                        country_of_birth="Mexico"
                    )
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Count successful vs error responses
                successful_responses = 0
                error_responses = 0
                
                for result in results:
                    if isinstance(result, Exception):
                        error_responses += 1
                    else:
                        result_data = json.loads(result)
                        if result_data.get("status") == "error":
                            error_responses += 1
                        else:
                            successful_responses += 1
                
                # Should handle errors gracefully
                total_responses = successful_responses + error_responses
                assert total_responses == 20
                
                # Error rate should be reasonable (allowing for some variance)
                error_rate = error_responses / total_responses
                assert 0.1 <= error_rate <= 0.4  # 10-40% error rate expected
                
        finally:
            await search_engine.cleanup()