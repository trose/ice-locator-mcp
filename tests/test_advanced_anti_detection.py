"""
Tests for advanced anti-detection features.

Tests behavioral simulation, traffic distribution, enhanced proxy management,
and the coordination between all anti-detection components.
"""

import asyncio
import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch

from src.ice_locator_mcp.anti_detection.behavioral_simulator import (
    BehavioralSimulator, BehaviorType, SessionPhase
)
from src.ice_locator_mcp.anti_detection.traffic_distributor import (
    TrafficDistributor, TrafficPattern, RequestPriority
)
from src.ice_locator_mcp.anti_detection.coordinator import AntiDetectionCoordinator
from src.ice_locator_mcp.core.config import Config


class TestBehavioralSimulator:
    """Test suite for behavioral simulation."""
    
    @pytest.fixture
    async def simulator(self):
        """Create behavioral simulator instance."""
        sim = BehavioralSimulator()
        yield sim
        # Cleanup
        sim.sessions.clear()
    
    @pytest.mark.asyncio
    async def test_start_session(self, simulator):
        """Test starting a behavioral session."""
        session = await simulator.start_session(
            "test_session",
            BehaviorType.FOCUSED_SEARCH,
            ["find_person", "submit_form"]
        )
        
        assert session.session_id == "test_session"
        assert session.behavior_type == BehaviorType.FOCUSED_SEARCH
        assert len(session.goals) == 2
        assert session.current_phase == SessionPhase.INITIAL_LANDING
        assert session.attention_span > 0
    
    @pytest.mark.asyncio
    async def test_page_interaction_simulation(self, simulator):
        """Test page interaction simulation."""
        session_id = "interaction_test"
        await simulator.start_session(session_id, BehaviorType.CASUAL_BROWSING)
        
        page_content = {
            'content_length': 1000,
            'has_forms': True
        }
        
        result = await simulator.simulate_page_interaction(
            session_id,
            page_content,
            'form_input'
        )
        
        assert 'pre_delay' in result
        assert 'post_delay' in result
        assert 'typing_pattern' in result
        assert 'fatigue_level' in result
        assert result['pre_delay'] > 0
        assert result['post_delay'] > 0
    
    @pytest.mark.asyncio
    async def test_error_behavior_handling(self, simulator):
        """Test error recovery behavior simulation."""
        session_id = "error_test"
        await simulator.start_session(session_id, BehaviorType.RESEARCH_SESSION)
        
        # First error - should retry after pause
        result1 = await simulator.handle_error_behavior(session_id, "timeout", 1)
        assert result1['action'] in ['retry_after_pause', 'retry_immediate']
        assert result1['delay'] > 0
        
        # Multiple errors - should change approach or give up
        result3 = await simulator.handle_error_behavior(session_id, "captcha", 3)
        assert result3['action'] in ['give_up', 'change_approach']
    
    @pytest.mark.asyncio
    async def test_natural_delay_calculation(self, simulator):
        """Test natural delay calculation."""
        session_id = "delay_test"
        await simulator.start_session(session_id, BehaviorType.FORM_FILLING)
        
        delay1 = await simulator.calculate_natural_delay(session_id, "search")
        delay2 = await simulator.calculate_natural_delay(session_id, "form_input", {'complexity': 'complex'})
        delay3 = await simulator.calculate_natural_delay(session_id, "navigation", {'related_to_previous': True})
        
        assert delay1 > 0
        assert delay2 > delay1  # Complex actions should take longer
        assert delay3 < delay1  # Related actions should be faster
    
    @pytest.mark.asyncio
    async def test_session_summary(self, simulator):
        """Test session summary generation."""
        session_id = "summary_test"
        await simulator.start_session(session_id, BehaviorType.FOCUSED_SEARCH)
        
        # Simulate some activity
        await simulator.simulate_page_interaction(
            session_id,
            {'content_length': 500},
            'search'
        )
        
        summary = await simulator.get_session_summary(session_id)
        
        assert summary['session_id'] == session_id
        assert summary['behavior_type'] == BehaviorType.FOCUSED_SEARCH.value
        assert 'duration' in summary
        assert 'metrics' in summary
        assert 'state' in summary


class TestTrafficDistributor:
    """Test suite for traffic distribution."""
    
    @pytest.fixture
    async def distributor(self):
        """Create traffic distributor instance."""
        config = {'base_interval': 1.0}
        dist = TrafficDistributor(config)
        await dist.start()
        yield dist
        await dist.stop()
    
    @pytest.mark.asyncio
    async def test_start_stop(self):
        """Test starting and stopping distributor."""
        distributor = TrafficDistributor()
        
        assert not distributor.running
        
        await distributor.start()
        assert distributor.running
        assert distributor.scheduler_task is not None
        
        await distributor.stop()
        assert not distributor.running
    
    @pytest.mark.asyncio
    async def test_request_scheduling(self, distributor):
        """Test request scheduling."""
        request_id = await distributor.schedule_request(
            "req_1",
            "session_1",
            "search",
            RequestPriority.HIGH
        )
        
        assert request_id == "req_1"
        assert len(distributor.request_queue[RequestPriority.HIGH]) == 1
        
        # Check request details
        queued_request = distributor.request_queue[RequestPriority.HIGH][0]
        assert queued_request.request_id == "req_1"
        assert queued_request.session_id == "session_1"
        assert queued_request.priority == RequestPriority.HIGH
    
    @pytest.mark.asyncio
    async def test_request_completion(self, distributor):
        """Test marking requests as completed."""
        request_id = "completion_test"
        
        # Mark successful completion
        await distributor.mark_request_completed(request_id, True, 1.5)
        assert distributor.metrics.successful_requests == 1
        assert distributor.metrics.average_response_time > 0
        
        # Mark failed completion
        await distributor.mark_request_completed("failed_req", False, 0.0, "timeout")
        assert distributor.metrics.failed_requests == 1
        assert distributor.metrics.success_rate < 1.0
    
    @pytest.mark.asyncio
    async def test_traffic_patterns(self, distributor):
        """Test different traffic patterns."""
        # Test steady state
        await distributor.set_traffic_pattern(TrafficPattern.STEADY_STATE)
        assert distributor.current_pattern == TrafficPattern.STEADY_STATE
        
        # Test burst then quiet
        await distributor.set_traffic_pattern(
            TrafficPattern.BURST_THEN_QUIET,
            burst_duration=30,
            quiet_duration=120
        )
        assert distributor.current_pattern == TrafficPattern.BURST_THEN_QUIET
        assert distributor.pattern_state['burst_duration'] == 30
    
    @pytest.mark.asyncio
    async def test_adaptive_timing(self, distributor):
        """Test adaptive timing adjustments."""
        initial_interval = distributor.current_interval
        
        # Simulate multiple failures
        for i in range(5):
            await distributor.mark_request_completed(f"fail_{i}", False, 0.0, "blocked")
        
        # Interval should increase due to failures
        assert distributor.current_interval > initial_interval
        
        # Simulate successes
        for i in range(10):
            await distributor.mark_request_completed(f"success_{i}", True, 1.0)
        
        # Should adapt back towards faster timing
        assert distributor.metrics.success_rate > 0.5


class TestAntiDetectionCoordinator:
    """Test suite for anti-detection coordination."""
    
    @pytest.fixture
    async def coordinator(self):
        """Create coordinator instance."""
        config = Config({
            'proxy': {'enabled': False},  # Disable for testing
            'traffic_distribution': {'base_interval': 0.5}
        })
        
        coord = AntiDetectionCoordinator(config)
        
        # Mock components for testing
        coord.proxy_manager = AsyncMock()
        coord.proxy_manager.initialize = AsyncMock()
        coord.proxy_manager.get_proxy = AsyncMock(return_value=None)
        coord.proxy_manager.mark_proxy_success = AsyncMock()
        coord.proxy_manager.mark_proxy_failure = AsyncMock()
        coord.proxy_manager.cleanup = AsyncMock()
        
        await coord.initialize()
        yield coord
        await coord.cleanup()
    
    @pytest.mark.asyncio
    async def test_initialization(self, coordinator):
        """Test coordinator initialization."""
        assert coordinator.current_strategy == 'balanced'
        assert coordinator.detection_level == 'low'
        assert len(coordinator.active_sessions) == 0
        
        # Check that components are initialized
        coordinator.proxy_manager.initialize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_session_management(self, coordinator):
        """Test session start and tracking."""
        session_info = await coordinator.start_session(
            "test_session",
            BehaviorType.FOCUSED_SEARCH,
            ["goal1", "goal2"]
        )
        
        assert session_info['session_id'] == "test_session"
        assert session_info['strategy'] == coordinator.current_strategy
        assert "test_session" in coordinator.active_sessions
        
        session_data = coordinator.active_sessions["test_session"]
        assert session_data['behavior_type'] == BehaviorType.FOCUSED_SEARCH
        assert len(session_data['goals']) == 2
    
    @pytest.mark.asyncio
    async def test_request_execution(self, coordinator):
        """Test coordinated request execution."""
        # Start a session
        await coordinator.start_session("req_session")
        
        # Mock request handler
        mock_handler = AsyncMock(return_value={'status': 'success', 'data': 'test'})
        
        request_info = {
            'type': 'search',
            'headers': {'User-Agent': 'test'},
            'page_content': {'content_length': 500},
            'interaction_type': 'search'
        }
        
        result = await coordinator.execute_request(
            "req_session",
            request_info,
            mock_handler
        )
        
        assert result['success'] is True
        assert 'result' in result
        assert 'response_time' in result
        assert result['detection_level'] == coordinator.detection_level
    
    @pytest.mark.asyncio
    async def test_strategy_adaptation(self, coordinator):
        """Test strategy adaptation based on detection level."""
        initial_strategy = coordinator.current_strategy
        
        # Adapt to higher threat level
        await coordinator.adapt_detection_strategy('high')
        assert coordinator.detection_level == 'high'
        assert coordinator.current_strategy == 'stealth'
        
        # Adapt to critical level
        await coordinator.adapt_detection_strategy('critical')
        assert coordinator.detection_level == 'critical'
        assert coordinator.current_strategy == 'maximum_evasion'
    
    @pytest.mark.asyncio
    async def test_comprehensive_status(self, coordinator):
        """Test comprehensive status reporting."""
        await coordinator.start_session("status_session")
        
        # Mock component status
        coordinator.proxy_manager.get_proxy_analytics = AsyncMock(return_value={
            'total_proxies': 5,
            'healthy_proxies': 4
        })
        
        status = await coordinator.get_comprehensive_status()
        
        assert 'coordinator' in status
        assert 'traffic_distribution' in status
        assert status['coordinator']['active_sessions'] == 1
        assert status['coordinator']['strategy'] == coordinator.current_strategy
    
    @pytest.mark.asyncio
    async def test_error_handling_and_adaptation(self, coordinator):
        """Test error handling and adaptive responses."""
        await coordinator.start_session("error_session")
        
        # Mock request handler that fails with detection error
        mock_handler = AsyncMock(side_effect=Exception("CAPTCHA required"))
        
        request_info = {
            'type': 'search',
            'max_retries': 1
        }
        
        # Should detect the error and adapt
        initial_detection_level = coordinator.detection_level
        
        try:
            await coordinator.execute_request("error_session", request_info, mock_handler)
        except Exception:
            pass  # Expected to fail
        
        # Should have adapted detection level
        assert coordinator.global_metrics['detection_events'] > 0
        
    @pytest.mark.asyncio
    async def test_component_integration(self, coordinator):
        """Test integration between all components."""
        # Enable all components
        coordinator.enable_proxy_rotation = True
        coordinator.enable_behavioral_simulation = True
        coordinator.enable_traffic_distribution = True
        
        await coordinator.start_session("integration_test", BehaviorType.FORM_FILLING)
        
        # Mock successful request
        mock_handler = AsyncMock(return_value={'success': True})
        
        request_info = {
            'type': 'form_submit',
            'priority': 'high',
            'page_content': {'content_length': 800, 'has_forms': True},
            'interaction_type': 'form_input'
        }
        
        result = await coordinator.execute_request(
            "integration_test",
            request_info,
            mock_handler
        )
        
        assert result['success'] is True
        
        # Verify component interactions
        assert coordinator.active_sessions["integration_test"]['request_count'] == 1
        assert coordinator.global_metrics['total_requests'] == 1


class TestProxyManagerEnhancements:
    """Test suite for enhanced proxy management features."""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock proxy configuration."""
        config = MagicMock()
        config.enabled = True
        config.rotation_interval = 1800
        config.health_check_interval = 300
        config.proxy_list_file = None
        return config
    
    @pytest.mark.asyncio
    async def test_comprehensive_health_checks(self, mock_config):
        """Test comprehensive proxy health checking."""
        from src.ice_locator_mcp.anti_detection.proxy_manager import ProxyManager, ProxyConfig
        
        manager = ProxyManager(mock_config)
        
        # Mock HTTP client responses
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'origin': '192.168.1.1'}
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            proxy = ProxyConfig("proxy.example.com:8080", country="US")
            
            # Test health check (this would normally call _health_check_proxy)
            await manager._perform_basic_connectivity_check(proxy)
            
            # Verify proxy was marked as successful
            assert proxy.endpoint in manager.proxy_metrics
            metrics = manager.proxy_metrics[proxy.endpoint]
            assert metrics.success_count > 0
    
    @pytest.mark.asyncio
    async def test_proxy_analytics(self, mock_config):
        """Test proxy analytics generation."""
        from src.ice_locator_mcp.anti_detection.proxy_manager import (
            ProxyManager, ProxyConfig, ProxyMetrics
        )
        
        manager = ProxyManager(mock_config)
        
        # Add test proxies and metrics
        proxy1 = ProxyConfig("proxy1.example.com:8080", country="US", is_residential=True)
        proxy2 = ProxyConfig("proxy2.example.com:8080", country="CA", is_residential=False)
        
        manager.proxy_pool = [proxy1, proxy2]
        
        # Add metrics
        metrics1 = ProxyMetrics()
        metrics1.request_count = 10
        metrics1.success_count = 8
        metrics1.average_response_time = 2.5
        
        metrics2 = ProxyMetrics()
        metrics2.request_count = 5
        metrics2.success_count = 3
        metrics2.average_response_time = 4.0
        
        manager.proxy_metrics = {
            proxy1.endpoint: metrics1,
            proxy2.endpoint: metrics2
        }
        
        # Get analytics
        analytics = await manager.get_proxy_analytics()
        
        assert analytics['overview']['total_proxies'] == 2
        assert analytics['performance']['total_requests'] == 15
        assert analytics['distribution']['residential_proxies'] == 1
        assert 'US' in analytics['distribution']['by_country']
        assert 'CA' in analytics['distribution']['by_country']
    
    @pytest.mark.asyncio
    async def test_proxy_optimization(self, mock_config):
        """Test automatic proxy pool optimization."""
        from src.ice_locator_mcp.anti_detection.proxy_manager import (
            ProxyManager, ProxyConfig, ProxyMetrics
        )
        
        manager = ProxyManager(mock_config)
        
        # Add proxy with poor performance
        bad_proxy = ProxyConfig("bad-proxy.example.com:8080")
        good_proxy = ProxyConfig("good-proxy.example.com:8080")
        
        manager.proxy_pool = [bad_proxy, good_proxy]
        
        # Add metrics showing bad proxy performance
        bad_metrics = ProxyMetrics()
        bad_metrics.request_count = 20
        bad_metrics.success_count = 2  # 10% success rate
        bad_metrics.last_success = time.time() - 90000  # 25 hours ago
        
        good_metrics = ProxyMetrics()
        good_metrics.request_count = 15
        good_metrics.success_count = 14  # 93% success rate
        good_metrics.last_success = time.time() - 300  # 5 minutes ago
        
        manager.proxy_metrics = {
            bad_proxy.endpoint: bad_metrics,
            good_proxy.endpoint: good_metrics
        }
        
        # Run optimization
        results = await manager.optimize_proxy_pool()
        
        assert results['proxies_removed'] == 1
        assert bad_proxy not in manager.proxy_pool
        assert good_proxy in manager.proxy_pool
        assert len(results['actions_taken']) > 0


if __name__ == '__main__':
    pytest.main([__file__])