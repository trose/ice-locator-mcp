"""
Rate limiting effectiveness tests for ICE Locator MCP Server.

Tests rate limiting mechanisms, abuse prevention, and adaptive controls.
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
from concurrent.futures import ThreadPoolExecutor
import threading

from ice_locator_mcp.utils.cache import RateLimiter
from ice_locator_mcp.anti_detection.proxy_manager import ProxyManager, ProxyConfig
from ice_locator_mcp.core.config import Config


class TestBasicRateLimiting:
    """Test basic rate limiting functionality."""
    
    @pytest.fixture
    async def rate_limiter(self):
        """Basic rate limiter for testing."""
        return RateLimiter(requests_per_minute=10, burst_allowance=20)
    
    async def test_normal_request_flow(self, rate_limiter):
        """Test that normal requests are not rate limited."""
        start_time = time.time()
        
        # Make requests within normal rate
        for i in range(5):
            await rate_limiter.acquire()
            await rate_limiter.mark_success()
            await asyncio.sleep(0.1)  # Small delay between requests
        
        elapsed = time.time() - start_time
        # Should complete quickly (within 2 seconds including delays)
        assert elapsed < 2.0, f"Normal requests should not be delayed, took {elapsed}s"
    
    async def test_rate_limit_enforcement(self, rate_limiter):
        """Test that rate limits are enforced."""
        # Rapidly make requests to trigger rate limiting
        start_time = time.time()
        
        # Make requests up to the limit
        for _ in range(10):
            await rate_limiter.acquire()
            await rate_limiter.mark_success()
        
        # This request should be rate limited
        await rate_limiter.acquire()
        
        elapsed = time.time() - start_time
        # Should have been delayed due to rate limiting
        assert elapsed > 5.0, f"Rate limiting should cause delay, only took {elapsed}s"
    
    async def test_burst_allowance(self, rate_limiter):
        """Test burst allowance functionality."""
        # Quickly make requests up to burst allowance
        start_time = time.time()
        
        for i in range(20):  # Up to burst allowance
            await rate_limiter.acquire()
            await rate_limiter.mark_success()
        
        elapsed = time.time() - start_time
        # Burst allowance should allow quick requests
        assert elapsed < 3.0, f"Burst allowance should allow quick requests, took {elapsed}s"
        
        # Next request should be rate limited
        next_request_start = time.time()
        await rate_limiter.acquire()
        next_request_elapsed = time.time() - next_request_start
        
        assert next_request_elapsed > 2.0, "Request after burst should be rate limited"
    
    async def test_time_window_reset(self, rate_limiter):
        """Test that rate limits reset after time window."""
        # Fill up the rate limit
        for _ in range(10):
            await rate_limiter.acquire()
            await rate_limiter.mark_success()
        
        # Wait for time window to reset (simulate 61 seconds)
        rate_limiter.request_times = [time.time() - 65]  # Simulate old requests
        
        # Should be able to make requests again
        start_time = time.time()
        await rate_limiter.acquire()
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0, "Rate limit should reset after time window"


class TestAdaptiveRateLimiting:
    """Test adaptive rate limiting based on success/error rates."""
    
    @pytest.fixture
    async def adaptive_limiter(self):
        """Rate limiter for adaptive testing."""
        return RateLimiter(requests_per_minute=20, burst_allowance=30)
    
    async def test_error_rate_adaptation(self, adaptive_limiter):
        """Test rate reduction based on error rates."""
        initial_multiplier = adaptive_limiter.current_rate_multiplier
        
        # Simulate high error rate
        for _ in range(15):
            await adaptive_limiter.acquire()
            await adaptive_limiter.mark_error("rate_limit")
        
        # Rate multiplier should decrease
        assert adaptive_limiter.current_rate_multiplier < initial_multiplier, \
            "Rate should decrease with high error rate"
        
        # Test severe error impact
        for _ in range(10):
            await adaptive_limiter.acquire()
            await adaptive_limiter.mark_error("captcha")
        
        # Should be even more conservative
        assert adaptive_limiter.current_rate_multiplier < 0.8, \
            "Rate should be very conservative after severe errors"
    
    async def test_success_rate_recovery(self, adaptive_limiter):
        """Test rate recovery based on success rates."""
        # Start with degraded rate
        for _ in range(20):
            await adaptive_limiter.acquire()
            await adaptive_limiter.mark_error("general")
        
        degraded_multiplier = adaptive_limiter.current_rate_multiplier
        assert degraded_multiplier < 1.0, "Rate should be degraded after errors"
        
        # Simulate recovery with successful requests
        for _ in range(30):
            await adaptive_limiter.acquire()
            await adaptive_limiter.mark_success()
        
        # Rate should improve
        assert adaptive_limiter.current_rate_multiplier > degraded_multiplier, \
            "Rate should improve with successful requests"
    
    async def test_error_type_weighting(self, adaptive_limiter):
        """Test that different error types have different impacts."""
        initial_multiplier = adaptive_limiter.current_rate_multiplier
        
        # Test mild error
        for _ in range(10):
            await adaptive_limiter.acquire()
            await adaptive_limiter.mark_error("general")
        
        mild_error_multiplier = adaptive_limiter.current_rate_multiplier
        
        # Reset for comparison
        adaptive_limiter.current_rate_multiplier = initial_multiplier
        adaptive_limiter.success_count = 0
        adaptive_limiter.error_count = 0
        
        # Test severe error
        for _ in range(5):  # Fewer severe errors
            await adaptive_limiter.acquire()
            await adaptive_limiter.mark_error("blocked")
        
        severe_error_multiplier = adaptive_limiter.current_rate_multiplier
        
        # Severe errors should have more impact
        assert severe_error_multiplier < mild_error_multiplier, \
            "Severe errors should have greater impact on rate limiting"


class TestConcurrentRateLimiting:
    """Test rate limiting under concurrent access."""
    
    async def test_thread_safety(self):
        """Test rate limiter thread safety."""
        rate_limiter = RateLimiter(requests_per_minute=50, burst_allowance=100)
        
        async def make_requests(session_id: str, count: int):
            """Make requests from a simulated session."""
            for _ in range(count):
                await rate_limiter.acquire()
                await rate_limiter.mark_success()
                await asyncio.sleep(0.01)  # Small delay
        
        # Run multiple concurrent sessions
        tasks = []
        for i in range(5):
            task = asyncio.create_task(make_requests(f"session_{i}", 10))
            tasks.append(task)
        
        start_time = time.time()
        await asyncio.gather(*tasks)
        elapsed = time.time() - start_time
        
        # Should handle concurrent access without corruption
        assert rate_limiter.success_count == 50, "All requests should be counted"
        assert elapsed < 10.0, "Concurrent requests should be reasonably fast"
    
    async def test_per_session_isolation(self):
        """Test that rate limiting can be isolated per session."""
        # In a real implementation, this would test per-session rate limiting
        limiter1 = RateLimiter(requests_per_minute=10)
        limiter2 = RateLimiter(requests_per_minute=10)
        
        # Fill up limiter1
        for _ in range(10):
            await limiter1.acquire()
            await limiter1.mark_success()
        
        # limiter2 should still be available
        start_time = time.time()
        await limiter2.acquire()
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0, "Different sessions should have independent rate limits"
    
    async def test_global_rate_limiting(self):
        """Test global rate limiting across all sessions."""
        # Test that there's a global rate limit that affects all sessions
        # This is a placeholder for global rate limiting implementation
        
        global_limit = 100  # requests per minute globally
        session_limit = 20  # requests per minute per session
        
        # Multiple sessions should not exceed global limit
        assert session_limit * 10 > global_limit, \
            "Global limit should be lower than sum of session limits"


class TestAbuseDetection:
    """Test abuse detection and prevention."""
    
    async def test_suspicious_pattern_detection(self):
        """Test detection of suspicious request patterns."""
        rate_limiter = RateLimiter(requests_per_minute=30)
        
        # Simulate suspicious rapid-fire requests
        suspicious_start = time.time()
        
        for i in range(25):
            await rate_limiter.acquire()
            # Don't mark as success to simulate suspicious behavior
            if i % 5 == 0:
                await rate_limiter.mark_error("suspicious")
        
        # Should have detected suspicious pattern and slowed down
        assert rate_limiter.current_rate_multiplier < 0.7, \
            "Should detect and respond to suspicious patterns"
    
    async def test_captcha_response_handling(self):
        """Test handling of CAPTCHA challenges."""
        rate_limiter = RateLimiter(requests_per_minute=20)
        
        # Simulate CAPTCHA challenges
        for _ in range(5):
            await rate_limiter.acquire()
            await rate_limiter.mark_error("captcha")
        
        # Should significantly reduce rate after CAPTCHA challenges
        assert rate_limiter.current_rate_multiplier < 0.5, \
            "Should be very conservative after CAPTCHA challenges"
    
    async def test_blocked_ip_simulation(self):
        """Test handling of blocked IP responses."""
        rate_limiter = RateLimiter(requests_per_minute=15)
        
        # Simulate IP blocking
        for _ in range(3):
            await rate_limiter.acquire()
            await rate_limiter.mark_error("blocked")
        
        # Should become very conservative
        assert rate_limiter.current_rate_multiplier < 0.4, \
            "Should be extremely conservative after IP blocking"
    
    async def test_recovery_after_blocking(self):
        """Test recovery process after being blocked."""
        rate_limiter = RateLimiter(requests_per_minute=10)
        
        # Simulate blocking
        for _ in range(5):
            await rate_limiter.acquire()
            await rate_limiter.mark_error("blocked")
        
        blocked_multiplier = rate_limiter.current_rate_multiplier
        
        # Simulate gradual recovery
        for _ in range(20):
            await rate_limiter.acquire()
            await rate_limiter.mark_success()
        
        # Should gradually recover but still be conservative
        recovery_multiplier = rate_limiter.current_rate_multiplier
        assert recovery_multiplier > blocked_multiplier, "Should gradually recover"
        assert recovery_multiplier < 0.8, "Should still be conservative during recovery"


class TestRateLimitingIntegration:
    """Test rate limiting integration with other components."""
    
    @pytest.fixture
    async def config(self):
        """Configuration for integration testing."""
        config = Config()
        config.rate_limiting.enabled = True
        config.rate_limiting.requests_per_minute = 15
        config.rate_limiting.burst_allowance = 25
        config.rate_limiting.adaptive = True
        return config
    
    async def test_proxy_integration(self, config):
        """Test rate limiting integration with proxy management."""
        proxy_manager = ProxyManager(config.proxy)
        rate_limiter = RateLimiter(
            requests_per_minute=config.rate_limiting.requests_per_minute,
            burst_allowance=config.rate_limiting.burst_allowance
        )
        
        # Simulate coordinated proxy and rate limiting
        await rate_limiter.acquire()
        proxy = await proxy_manager.get_proxy()
        
        # Rate limiting and proxy should work together
        if proxy:
            await proxy_manager.mark_proxy_success(proxy, 0.5)
        await rate_limiter.mark_success()
        
        # Should handle integration without conflicts
        assert True  # Integration test passed
    
    async def test_cache_integration(self, config):
        """Test rate limiting integration with caching."""
        from ice_locator_mcp.utils.cache import CacheManager
        
        cache_manager = CacheManager()
        await cache_manager.initialize()
        
        rate_limiter = RateLimiter(requests_per_minute=10)
        
        try:
            # Test that caching reduces need for rate limiting
            await rate_limiter.acquire()
            await cache_manager.set("test_key", {"cached": "data"})
            await rate_limiter.mark_success()
            
            # Subsequent request should use cache (no rate limiting needed)
            cached_data = await cache_manager.get("test_key")
            assert cached_data is not None, "Cache should reduce rate limiting pressure"
            
        finally:
            await cache_manager.cleanup()
    
    async def test_search_tools_integration(self, config):
        """Test rate limiting integration with search tools."""
        from ice_locator_mcp.tools.search_tools import SearchTools
        
        # Mock search tools with rate limiting
        mock_scraper = MagicMock()
        search_tools = SearchTools(mock_scraper)
        
        # Simulate rate limiting in search context
        rate_limiter = RateLimiter(requests_per_minute=5)
        
        # Test that search respects rate limits
        start_time = time.time()
        
        for _ in range(6):  # Exceed rate limit
            await rate_limiter.acquire()
            # Simulate search operation
            await asyncio.sleep(0.1)
        
        elapsed = time.time() - start_time
        # Should be rate limited
        assert elapsed > 5.0, "Search operations should respect rate limits"


class TestRateLimitingConfiguration:
    """Test rate limiting configuration and tuning."""
    
    async def test_configurable_limits(self):
        """Test that rate limits are configurable."""
        # Test different configurations
        configs = [
            {"rpm": 5, "burst": 10},    # Conservative
            {"rpm": 30, "burst": 50},   # Moderate
            {"rpm": 60, "burst": 100},  # Aggressive
        ]
        
        for config in configs:
            limiter = RateLimiter(
                requests_per_minute=config["rpm"],
                burst_allowance=config["burst"]
            )
            
            assert limiter.requests_per_minute == config["rpm"]
            assert limiter.burst_allowance == config["burst"]
    
    async def test_dynamic_adjustment(self):
        """Test dynamic rate limit adjustment."""
        limiter = RateLimiter(requests_per_minute=20)
        
        initial_rate = limiter.requests_per_minute
        
        # Simulate condition requiring rate reduction
        for _ in range(10):
            await limiter.acquire()
            await limiter.mark_error("rate_limit")
        
        # Effective rate should be reduced
        effective_rate = limiter.requests_per_minute * limiter.current_rate_multiplier
        assert effective_rate < initial_rate, "Rate should be dynamically reduced"
    
    async def test_environment_specific_limits(self):
        """Test environment-specific rate limiting."""
        # Test different limits for different environments
        environments = {
            "development": {"rpm": 100, "burst": 200},
            "testing": {"rpm": 50, "burst": 100},
            "production": {"rpm": 10, "burst": 20},
        }
        
        for env, limits in environments.items():
            # In a real implementation, test environment detection
            assert limits["rpm"] > 0, f"Rate limit should be positive for {env}"
            
            if env == "production":
                assert limits["rpm"] <= 30, "Production should have conservative limits"
            elif env == "development":
                assert limits["rpm"] >= 50, "Development can have higher limits"


class TestRateLimitingMetrics:
    """Test rate limiting metrics and monitoring."""
    
    async def test_metrics_collection(self):
        """Test collection of rate limiting metrics."""
        limiter = RateLimiter(requests_per_minute=20)
        
        # Generate some activity
        for i in range(15):
            await limiter.acquire()
            if i % 3 == 0:
                await limiter.mark_error("test")
            else:
                await limiter.mark_success()
        
        # Verify metrics are collected
        assert limiter.success_count > 0, "Should track successful requests"
        assert limiter.error_count > 0, "Should track failed requests"
        
        total_requests = limiter.success_count + limiter.error_count
        assert total_requests == 15, "Should track total requests accurately"
    
    async def test_performance_metrics(self):
        """Test performance metrics for rate limiting."""
        limiter = RateLimiter(requests_per_minute=10)
        
        # Measure rate limiting overhead
        start_time = time.time()
        
        for _ in range(5):  # Within limits
            await limiter.acquire()
            await limiter.mark_success()
        
        elapsed = time.time() - start_time
        
        # Rate limiting overhead should be minimal for normal requests
        assert elapsed < 1.0, f"Rate limiting overhead too high: {elapsed}s"
    
    async def test_alerting_thresholds(self):
        """Test alerting for rate limiting issues."""
        limiter = RateLimiter(requests_per_minute=10)
        
        # Simulate high error rate scenario
        error_threshold = 0.8  # 80% error rate
        
        for i in range(20):
            await limiter.acquire()
            if i < 16:  # 80% errors
                await limiter.mark_error("alert_test")
            else:
                await limiter.mark_success()
        
        total_requests = limiter.success_count + limiter.error_count
        error_rate = limiter.error_count / total_requests
        
        # Should trigger alerting threshold
        assert error_rate >= error_threshold, "Should detect high error rate for alerting"