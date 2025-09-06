"""
Tests for enhanced behavioral analysis evasion functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch

from src.ice_locator_mcp.anti_detection.behavioral_simulator import (
    BehavioralSimulator, BehaviorType, MouseMovementPattern, ScrollingPattern
)
from src.ice_locator_mcp.anti_detection.request_obfuscator import RequestObfuscator


@pytest.fixture
def behavioral_simulator():
    """Create a behavioral simulator for testing."""
    return BehavioralSimulator()


@pytest.fixture
def request_obfuscator():
    """Create a request obfuscator for testing."""
    return RequestObfuscator()


class TestMouseMovementSimulation:
    """Test mouse movement simulation functionality."""
    
    @pytest.mark.asyncio
    async def test_mouse_movement_pattern_generation(self):
        """Test that mouse movement patterns are generated correctly."""
        movement = MouseMovementPattern(0, 0, 100, 100, 1.0)
        movement.generate_waypoints()
        
        # Should have at least 2 waypoints (start and end)
        assert len(movement.waypoints) >= 2
        
        # First waypoint should be at start position (no deviation for start point)
        assert movement.waypoints[0][0] == 0
        assert movement.waypoints[0][1] == 0
        
        # Last waypoint should be at end position (no deviation for end point)
        assert movement.waypoints[-1][0] == 100
        assert movement.waypoints[-1][1] == 100
    
    @pytest.mark.asyncio
    async def test_mouse_movement_simulation(self, behavioral_simulator):
        """Test mouse movement simulation."""
        session_id = "test_session"
        
        # Start a session
        await behavioral_simulator.start_session(session_id)
        
        # Simulate mouse movement
        movement = await behavioral_simulator.simulate_mouse_movement(
            session_id, 0, 0, 500, 500, 2.0
        )
        
        # Should have generated waypoints
        assert len(movement.waypoints) >= 2
        assert movement.duration == 2.0


class TestScrollingPatternSimulation:
    """Test scrolling pattern simulation functionality."""
    
    def test_scrolling_pattern_generation(self):
        """Test that scrolling patterns are generated correctly."""
        scrolling = ScrollingPattern(2000, 800)
        scrolling.generate_scroll_pattern()
        
        # Should have generated scroll events
        assert len(scrolling.scroll_events) > 0
        
        # All positions should be within valid range
        for position, _ in scrolling.scroll_events:
            assert 0 <= position <= 1200  # max_scroll = 2000 - 800
    
    @pytest.mark.asyncio
    async def test_scrolling_simulation(self, behavioral_simulator):
        """Test scrolling simulation."""
        session_id = "test_session"
        
        # Start a session
        await behavioral_simulator.start_session(session_id)
        
        # Simulate scrolling
        scrolling = await behavioral_simulator.simulate_scrolling(
            session_id, 3000, 1000
        )
        
        # Should have generated scroll events
        assert len(scrolling.scroll_events) > 0


class TestDecisionMakingSimulation:
    """Test decision-making simulation functionality."""
    
    @pytest.mark.asyncio
    async def test_decision_making_simulation(self, behavioral_simulator):
        """Test decision-making simulation."""
        session_id = "test_session"
        
        # Start a session
        await behavioral_simulator.start_session(session_id)
        
        # Simulate decision making
        decision_time = await behavioral_simulator.simulate_decision_making(
            session_id, "medium", False
        )
        
        # Should return a positive decision time
        assert decision_time > 0


class TestEnhancedRequestObfuscator:
    """Test enhanced request obfuscator with behavioral simulation."""
    
    @pytest.mark.asyncio
    async def test_mouse_movement_behavior(self, request_obfuscator):
        """Test mouse movement behavior simulation."""
        session_id = "test_session"
        
        # Simulate mouse movement behavior
        with patch.object(request_obfuscator.behavioral_simulator, 'simulate_mouse_movement') as mock_movement:
            mock_movement.return_value = MouseMovementPattern(0, 0, 100, 100, 1.0)
            
            await request_obfuscator.simulate_human_behavior(
                session_id, "mouse_movement",
                start_x=0, start_y=0,
                end_x=100, end_y=100
            )
            
            # Verify the method was called
            mock_movement.assert_called_once_with(session_id, 0, 0, 100, 100)
    
    @pytest.mark.asyncio
    async def test_scrolling_behavior(self, request_obfuscator):
        """Test scrolling behavior simulation."""
        session_id = "test_session"
        
        # Simulate scrolling behavior
        with patch.object(request_obfuscator.behavioral_simulator, 'simulate_scrolling') as mock_scrolling:
            mock_scrolling.return_value = ScrollingPattern(2000, 800)
            
            await request_obfuscator.simulate_human_behavior(
                session_id, "scrolling",
                total_height=2000,
                viewport_height=800
            )
            
            # Verify the method was called
            mock_scrolling.assert_called_once_with(session_id, 2000, 800)
    
    @pytest.mark.asyncio
    async def test_decision_making_behavior(self, request_obfuscator):
        """Test decision-making behavior simulation."""
        session_id = "test_session"
        
        # Simulate decision making behavior
        with patch.object(request_obfuscator.behavioral_simulator, 'simulate_decision_making') as mock_decision:
            mock_decision.return_value = 2.5  # 2.5 seconds decision time
            
            await request_obfuscator.simulate_human_behavior(
                session_id, "decision_making",
                complexity="medium",
                time_pressure=False
            )
            
            # Verify the method was called
            mock_decision.assert_called_once_with(session_id, "medium", False)