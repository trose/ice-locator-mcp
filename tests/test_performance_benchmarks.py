"""
Performance Benchmarking Tests for ICE Locator MCP Server.

Comprehensive performance testing including load testing, stress testing,
memory profiling, and scalability analysis.
"""

import asyncio
import pytest
import time
import psutil
import gc
from typing import Dict, List, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import statistics

from src.ice_locator_mcp.server import ICELocatorServer
from src.ice_locator_mcp.core.config import Config


@dataclass
class PerformanceMetrics:
    """Performance metrics container."""
    execution_time: float
    memory_usage: float  # MB
    cpu_usage: float     # Percentage
    request_count: int
    success_rate: float
    error_count: int
    throughput: float    # Requests per second
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'execution_time': self.execution_time,
            'memory_usage_mb': self.memory_usage,
            'cpu_usage_percent': self.cpu_usage,
            'request_count': self.request_count,
            'success_rate': self.success_rate,
            'error_count': self.error_count,
            'throughput_rps': self.throughput
        }


class PerformanceMonitor:
    """Performance monitoring utility."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.start_time = None
        self.start_memory = None
        self.start_cpu = None
        
    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.start_cpu = self.process.cpu_percent()
        gc.collect()  # Clean up before monitoring
    
    def get_metrics(self, request_count: int, error_count: int) -> PerformanceMetrics:
        """Get current performance metrics."""
        end_time = time.time()
        end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        end_cpu = self.process.cpu_percent()
        
        execution_time = end_time - self.start_time
        memory_usage = end_memory - self.start_memory
        cpu_usage = end_cpu
        
        success_count = request_count - error_count
        success_rate = success_count / request_count if request_count > 0 else 0
        throughput = request_count / execution_time if execution_time > 0 else 0
        
        return PerformanceMetrics(
            execution_time=execution_time,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            request_count=request_count,
            success_rate=success_rate,
            error_count=error_count,
            throughput=throughput
        )


@pytest.fixture
async def performance_config():
    """Configuration optimized for performance testing."""
    return Config({
        'server': {
            'debug': False,
            'log_level': 'WARNING'  # Reduce logging overhead
        },
        'caching': {
            'enabled': True,
            'ttl': 3600
        },
        'rate_limiting': {
            'enabled': False  # Disable for performance testing
        },
        'anti_detection': {
            'behavioral_simulation': False,  # Disable for pure performance
            'traffic_distribution': False,
            'proxy_rotation': False
        }
    })


@pytest.fixture
async def performance_server(performance_config):
    """Create server instance for performance testing."""
    server = ICELocatorServer(performance_config)
    await server.initialize()
    yield server
    await server.cleanup()


class TestBasicPerformance:
    """Basic performance benchmarks."""
    
    @pytest.mark.asyncio
    async def test_single_request_performance(self, performance_server):
        """Test performance of single request."""
        
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        # Mock successful response
        with pytest.mock.patch('httpx.AsyncClient') as mock_client:
            mock_response = pytest.mock.MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>Mock result</body></html>"
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Execute single request
            session = pytest.mock.MagicMock()
            start_time = time.time()
            
            result = await performance_server.handle_tool_call(
                "search_by_name",
                {"first_name": "John", "last_name": "Doe"},
                session
            )
            
            end_time = time.time()
        
        # Verify performance
        request_time = end_time - start_time
        assert request_time < 2.0, f"Single request took too long: {request_time:.3f}s"
        assert result["isError"] is False
        
        metrics = monitor.get_metrics(1, 0)
        print(f"Single request metrics: {metrics.to_dict()}")
        
        # Performance assertions
        assert metrics.memory_usage < 50, f"Memory usage too high: {metrics.memory_usage:.1f}MB"
        assert metrics.success_rate == 1.0
    
    @pytest.mark.asyncio
    async def test_sequential_requests_performance(self, performance_server):
        """Test performance of sequential requests."""
        
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        request_count = 20
        error_count = 0
        
        with pytest.mock.patch('httpx.AsyncClient') as mock_client:
            mock_response = pytest.mock.MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>Mock result</body></html>"
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            session = pytest.mock.MagicMock()
            
            # Execute sequential requests
            for i in range(request_count):
                try:
                    result = await performance_server.handle_tool_call(
                        "search_by_name",
                        {"first_name": f"John{i}", "last_name": "Doe"},
                        session
                    )
                    if result["isError"]:
                        error_count += 1
                except Exception:
                    error_count += 1
        
        metrics = monitor.get_metrics(request_count, error_count)
        print(f"Sequential requests metrics: {metrics.to_dict()}")
        
        # Performance assertions
        assert metrics.execution_time < 10.0, f"Sequential requests took too long: {metrics.execution_time:.3f}s"
        assert metrics.success_rate >= 0.9, f"Success rate too low: {metrics.success_rate:.2f}"
        assert metrics.throughput >= 2.0, f"Throughput too low: {metrics.throughput:.2f} rps"


class TestConcurrentPerformance:
    """Concurrent request performance tests."""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_performance(self, performance_server):
        """Test performance under concurrent load."""
        
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        concurrent_requests = 10
        error_count = 0
        
        with pytest.mock.patch('httpx.AsyncClient') as mock_client:
            mock_response = pytest.mock.MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>Mock result</body></html>"
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            session = pytest.mock.MagicMock()
            
            # Create concurrent tasks
            async def make_request(request_id: int):
                try:
                    result = await performance_server.handle_tool_call(
                        "search_by_name",
                        {"first_name": f"User{request_id}", "last_name": "Test"},
                        session
                    )
                    return result["isError"]
                except Exception:
                    return True
            
            # Execute concurrent requests
            tasks = [make_request(i) for i in range(concurrent_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count errors
            error_count = sum(1 for r in results if isinstance(r, Exception) or r is True)
        
        metrics = monitor.get_metrics(concurrent_requests, error_count)
        print(f"Concurrent requests metrics: {metrics.to_dict()}")
        
        # Performance assertions
        assert metrics.execution_time < 5.0, f"Concurrent requests took too long: {metrics.execution_time:.3f}s"
        assert metrics.success_rate >= 0.8, f"Success rate too low under concurrency: {metrics.success_rate:.2f}"
        assert metrics.throughput >= 3.0, f"Concurrent throughput too low: {metrics.throughput:.2f} rps"
    
    @pytest.mark.asyncio
    async def test_high_concurrency_stress(self, performance_server):
        """Test performance under high concurrent stress."""
        
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        concurrent_requests = 50
        error_count = 0
        
        with pytest.mock.patch('httpx.AsyncClient') as mock_client:
            mock_response = pytest.mock.MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>Mock result</body></html>"
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            session = pytest.mock.MagicMock()
            
            async def stress_request(request_id: int):
                try:
                    # Add some variation in request types
                    tools = ["search_by_name", "search_by_alien_number", "parse_natural_query"]
                    tool = tools[request_id % len(tools)]
                    
                    if tool == "search_by_name":
                        args = {"first_name": f"User{request_id}", "last_name": "Stress"}
                    elif tool == "search_by_alien_number":
                        args = {"alien_number": f"A{request_id:09d}"}
                    else:  # parse_natural_query
                        args = {"query": f"Find person {request_id}", "auto_execute": False}
                    
                    result = await performance_server.handle_tool_call(tool, args, session)
                    return result["isError"]
                except Exception:
                    return True
            
            # Execute high concurrency stress test
            tasks = [stress_request(i) for i in range(concurrent_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count errors
            error_count = sum(1 for r in results if isinstance(r, Exception) or r is True)
        
        metrics = monitor.get_metrics(concurrent_requests, error_count)
        print(f"High concurrency stress metrics: {metrics.to_dict()}")
        
        # Stress test assertions (more lenient)
        assert metrics.execution_time < 15.0, f"Stress test took too long: {metrics.execution_time:.3f}s"
        assert metrics.success_rate >= 0.7, f"Success rate too low under stress: {metrics.success_rate:.2f}"
        assert metrics.memory_usage < 200, f"Memory usage too high under stress: {metrics.memory_usage:.1f}MB"


class TestMemoryPerformance:
    """Memory usage and leak testing."""
    
    @pytest.mark.asyncio
    async def test_memory_stability(self, performance_server):
        """Test memory usage stability over multiple operations."""
        
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        operations = 100
        error_count = 0
        
        with pytest.mock.patch('httpx.AsyncClient') as mock_client:
            mock_response = pytest.mock.MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>Mock result</body></html>"
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            session = pytest.mock.MagicMock()
            
            # Perform many operations
            for i in range(operations):
                try:
                    result = await performance_server.handle_tool_call(
                        "search_by_name",
                        {"first_name": f"Memory{i}", "last_name": "Test"},
                        session
                    )
                    if result["isError"]:
                        error_count += 1
                except Exception:
                    error_count += 1
                
                # Periodic cleanup check
                if i % 25 == 0:
                    gc.collect()
        
        # Final cleanup and measurement
        gc.collect()
        final_objects = len(gc.get_objects())
        object_growth = final_objects - initial_objects
        
        metrics = monitor.get_metrics(operations, error_count)
        print(f"Memory stability metrics: {metrics.to_dict()}")
        print(f"Object growth: {object_growth} objects")
        
        # Memory assertions
        assert metrics.memory_usage < 100, f"Memory growth too high: {metrics.memory_usage:.1f}MB"
        assert object_growth < 1000, f"Too many objects created: {object_growth}"
        assert metrics.success_rate >= 0.95, f"Success rate degraded: {metrics.success_rate:.2f}"
    
    @pytest.mark.asyncio
    async def test_memory_leak_detection(self, performance_server):
        """Test for memory leaks over extended operation."""
        
        session = pytest.mock.MagicMock()
        memory_samples = []
        
        with pytest.mock.patch('httpx.AsyncClient') as mock_client:
            mock_response = pytest.mock.MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>Mock result</body></html>"
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Take memory samples during operation
            for batch in range(10):  # 10 batches of operations
                # Perform batch of operations
                for i in range(10):
                    await performance_server.handle_tool_call(
                        "search_by_name",
                        {"first_name": f"Leak{batch}_{i}", "last_name": "Test"},
                        session
                    )
                
                # Sample memory usage
                gc.collect()
                memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
                memory_samples.append(memory_mb)
        
        print(f"Memory samples: {memory_samples}")
        
        # Analyze memory trend
        if len(memory_samples) >= 3:
            # Check if memory is consistently growing
            recent_avg = statistics.mean(memory_samples[-3:])
            early_avg = statistics.mean(memory_samples[:3])
            memory_growth = recent_avg - early_avg
            
            print(f"Memory growth over test: {memory_growth:.1f}MB")
            
            # Should not have excessive memory growth
            assert memory_growth < 50, f"Potential memory leak detected: {memory_growth:.1f}MB growth"


class TestScalabilityAnalysis:
    """Scalability and performance analysis."""
    
    @pytest.mark.asyncio
    async def test_throughput_scaling(self, performance_server):
        """Test throughput scaling with increasing load."""
        
        load_levels = [5, 10, 20, 30]
        throughput_results = []
        
        with pytest.mock.patch('httpx.AsyncClient') as mock_client:
            mock_response = pytest.mock.MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>Mock result</body></html>"
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            session = pytest.mock.MagicMock()
            
            for load in load_levels:
                monitor = PerformanceMonitor()
                monitor.start_monitoring()
                
                error_count = 0
                
                # Create concurrent tasks for this load level
                async def load_request(request_id: int):
                    try:
                        result = await performance_server.handle_tool_call(
                            "search_by_name",
                            {"first_name": f"Load{request_id}", "last_name": "Test"},
                            session
                        )
                        return result["isError"]
                    except Exception:
                        return True
                
                tasks = [load_request(i) for i in range(load)]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                error_count = sum(1 for r in results if isinstance(r, Exception) or r is True)
                metrics = monitor.get_metrics(load, error_count)
                
                throughput_results.append({
                    'load': load,
                    'throughput': metrics.throughput,
                    'success_rate': metrics.success_rate,
                    'execution_time': metrics.execution_time
                })
                
                print(f"Load {load}: {metrics.throughput:.2f} rps, {metrics.success_rate:.2f} success rate")
        
        # Analyze scaling characteristics
        print(f"Throughput scaling results: {throughput_results}")
        
        # Basic scalability assertions
        for i, result in enumerate(throughput_results):
            assert result['success_rate'] >= 0.7, f"Success rate too low at load {result['load']}: {result['success_rate']:.2f}"
            assert result['throughput'] > 0, f"No throughput at load {result['load']}"
            
            # Execution time should be reasonable
            expected_max_time = result['load'] * 0.5  # Rough estimate
            assert result['execution_time'] < expected_max_time, f"Execution time too high at load {result['load']}: {result['execution_time']:.2f}s"
    
    @pytest.mark.asyncio
    async def test_response_time_distribution(self, performance_server):
        """Test response time distribution and percentiles."""
        
        response_times = []
        request_count = 50
        
        with pytest.mock.patch('httpx.AsyncClient') as mock_client:
            mock_response = pytest.mock.MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>Mock result</body></html>"
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            session = pytest.mock.MagicMock()
            
            # Collect individual response times
            for i in range(request_count):
                start_time = time.time()
                
                try:
                    result = await performance_server.handle_tool_call(
                        "search_by_name",
                        {"first_name": f"Response{i}", "last_name": "Time"},
                        session
                    )
                    
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    if not result["isError"]:
                        response_times.append(response_time)
                        
                except Exception:
                    pass  # Skip failed requests for timing analysis
        
        # Analyze response time distribution
        if response_times:
            response_times.sort()
            
            p50 = statistics.median(response_times)
            p95 = response_times[int(0.95 * len(response_times))]
            p99 = response_times[int(0.99 * len(response_times))]
            avg_time = statistics.mean(response_times)
            
            print(f"Response time analysis:")
            print(f"  Average: {avg_time:.3f}s")
            print(f"  P50: {p50:.3f}s")
            print(f"  P95: {p95:.3f}s") 
            print(f"  P99: {p99:.3f}s")
            
            # Performance assertions
            assert avg_time < 1.0, f"Average response time too high: {avg_time:.3f}s"
            assert p95 < 2.0, f"P95 response time too high: {p95:.3f}s"
            assert p99 < 3.0, f"P99 response time too high: {p99:.3f}s"
        
        else:
            pytest.fail("No successful requests to analyze response times")


if __name__ == '__main__':
    pytest.main([__file__, "-v", "-s"])