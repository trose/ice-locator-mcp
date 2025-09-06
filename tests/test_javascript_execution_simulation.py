"""
Tests for advanced JavaScript execution simulation in browser simulator.
"""

import asyncio
import sys
import os
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.browser_simulator import BrowserSimulator, BrowserSession
from ice_locator_mcp.anti_detection.request_obfuscator import BrowserProfile
from ice_locator_mcp.core.config import SearchConfig


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    config = MagicMock(spec=SearchConfig)
    config.proxy = MagicMock()
    return config


@pytest.fixture
async def browser_simulator(mock_config):
    """Create a browser simulator instance for testing."""
    simulator = BrowserSimulator(mock_config)
    yield simulator
    # Cleanup
    try:
        await simulator.close_all_sessions()
    except:
        pass


@pytest.fixture
def mock_session():
    """Create a mock browser session for testing."""
    session = MagicMock(spec=BrowserSession)
    session.session_id = "test_session"
    session.actions_performed = []
    session.page = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_execute_javascript_with_timing(browser_simulator, mock_session):
    """Test JavaScript execution with timing control."""
    # Setup
    browser_simulator.sessions["test_session"] = mock_session
    mock_session.page.evaluate = AsyncMock(return_value="test_result")
    
    # Test execution
    script = "return document.title;"
    result = await browser_simulator.execute_javascript_with_timing(
        "test_session", script, "page", "medium"
    )
    
    # Verify
    assert result == "test_result"
    mock_session.page.evaluate.assert_called_once_with(script)
    assert "js_execute:page" in mock_session.actions_performed


@pytest.mark.asyncio
async def test_execute_javascript_with_timing_complexity_levels(browser_simulator, mock_session):
    """Test JavaScript execution with different complexity levels."""
    # Setup
    browser_simulator.sessions["test_session"] = mock_session
    mock_session.page.evaluate = AsyncMock(return_value="test_result")
    
    # Test different complexity levels
    for complexity in ["simple", "medium", "complex"]:
        result = await browser_simulator.execute_javascript_with_timing(
            "test_session", "return 42;", "page", complexity
        )
        assert result == "test_result"
    
    # Verify all calls were made
    assert mock_session.page.evaluate.call_count == 3


@pytest.mark.asyncio
async def test_execute_javascript_invalid_session(browser_simulator):
    """Test JavaScript execution with invalid session ID."""
    with pytest.raises(ValueError, match="No session found with ID"):
        await browser_simulator.execute_javascript_with_timing(
            "invalid_session", "return 42;", "page", "medium"
        )


@pytest.mark.asyncio
async def test_handle_client_side_challenge_generic(browser_simulator, mock_session):
    """Test handling generic client-side challenges."""
    # Setup
    browser_simulator.sessions["test_session"] = mock_session
    mock_session.page.evaluate = AsyncMock(return_value=True)
    
    # Test challenge handling
    result = await browser_simulator.handle_client_side_challenge(
        "test_session", "generic", 2
    )
    
    # Verify
    assert isinstance(result, dict)
    assert "success" in result
    assert "attempts" in result
    assert "challenge_type" in result
    assert result["challenge_type"] == "generic"
    assert "solution_time" in result
    assert "error" in result


@pytest.mark.asyncio
async def test_handle_client_side_challenge_captcha(browser_simulator, mock_session):
    """Test handling CAPTCHA challenges."""
    # Setup
    browser_simulator.sessions["test_session"] = mock_session
    mock_session.page.evaluate = AsyncMock(return_value=True)
    
    # Test CAPTCHA challenge handling
    result = await browser_simulator.handle_client_side_challenge(
        "test_session", "captcha", 3
    )
    
    # Verify
    assert isinstance(result, dict)
    assert result["challenge_type"] == "captcha"


@pytest.mark.asyncio
async def test_handle_client_side_challenge_turnstile(browser_simulator, mock_session):
    """Test handling Turnstile challenges."""
    # Setup
    browser_simulator.sessions["test_session"] = mock_session
    mock_session.page.evaluate = AsyncMock(return_value=True)
    
    # Test Turnstile challenge handling
    result = await browser_simulator.handle_client_side_challenge(
        "test_session", "turnstile", 2
    )
    
    # Verify
    assert isinstance(result, dict)
    assert result["challenge_type"] == "turnstile"


@pytest.mark.asyncio
async def test_handle_client_side_challenge_custom(browser_simulator, mock_session):
    """Test handling custom JavaScript challenges."""
    # Setup
    browser_simulator.sessions["test_session"] = mock_session
    mock_session.page.evaluate = AsyncMock(return_value=True)
    
    # Test custom challenge handling
    result = await browser_simulator.handle_client_side_challenge(
        "test_session", "custom", 1
    )
    
    # Verify
    assert isinstance(result, dict)
    assert result["challenge_type"] == "custom"


@pytest.mark.asyncio
async def test_handle_client_side_challenge_invalid_session(browser_simulator):
    """Test challenge handling with invalid session ID."""
    with pytest.raises(ValueError, match="No session found with ID"):
        await browser_simulator.handle_client_side_challenge(
            "invalid_session", "generic", 1
        )


@pytest.mark.asyncio
async def test_simulate_realistic_js_execution_pattern_sequential(browser_simulator, mock_session):
    """Test sequential JavaScript execution pattern."""
    # Setup
    browser_simulator.sessions["test_session"] = mock_session
    mock_session.page.evaluate = AsyncMock(side_effect=["result1", "result2", "result3"])
    
    # Test sequential pattern
    scripts = [
        "return 'result1';",
        "return 'result2';",
        "return 'result3';"
    ]
    
    results = await browser_simulator.simulate_realistic_js_execution_pattern(
        "test_session", scripts, "sequential"
    )
    
    # Verify
    assert len(results) == 3
    assert results == ["result1", "result2", "result3"]
    assert mock_session.page.evaluate.call_count == 3
    assert "js_pattern_executed:sequential" in mock_session.actions_performed


@pytest.mark.asyncio
async def test_simulate_realistic_js_execution_pattern_interleaved(browser_simulator, mock_session):
    """Test interleaved JavaScript execution pattern."""
    # Setup
    browser_simulator.sessions["test_session"] = mock_session
    mock_session.page.evaluate = AsyncMock(side_effect=["result1", "result2"])
    
    # Test interleaved pattern
    scripts = [
        "return 'result1';",
        "return 'result2';"
    ]
    
    with patch.object(browser_simulator, '_simulate_human_reading'), \
         patch.object(browser_simulator, 'simulate_human_mouse_movement'):
        results = await browser_simulator.simulate_realistic_js_execution_pattern(
            "test_session", scripts, "interleaved"
        )
    
    # Verify
    assert len(results) == 2
    assert "js_pattern_executed:interleaved" in mock_session.actions_performed


@pytest.mark.asyncio
async def test_simulate_realistic_js_execution_pattern_burst(browser_simulator, mock_session):
    """Test burst JavaScript execution pattern."""
    # Setup
    browser_simulator.sessions["test_session"] = mock_session
    mock_session.page.evaluate = AsyncMock(side_effect=["r1", "r2", "r3", "r4"])
    
    # Test burst pattern
    scripts = [
        "return 'r1';",
        "return 'r2';",
        "return 'r3';",
        "return 'r4';"
    ]
    
    results = await browser_simulator.simulate_realistic_js_execution_pattern(
        "test_session", scripts, "burst"
    )
    
    # Verify
    assert len(results) == 4
    assert "js_pattern_executed:burst" in mock_session.actions_performed


@pytest.mark.asyncio
async def test_simulate_realistic_js_execution_pattern_random(browser_simulator, mock_session):
    """Test random JavaScript execution pattern."""
    # Setup
    browser_simulator.sessions["test_session"] = mock_session
    mock_session.page.evaluate = AsyncMock(side_effect=["r1", "r2", "r3"])
    
    # Test random pattern
    scripts = [
        "return 'r1';",
        "return 'r2';",
        "return 'r3';"
    ]
    
    # Patch random.shuffle to control the order
    with patch('random.shuffle') as mock_shuffle:
        mock_shuffle.side_effect = lambda x: x.reverse()  # Reverse the list
        results = await browser_simulator.simulate_realistic_js_execution_pattern(
            "test_session", scripts, "random"
        )
    
    # Verify
    assert len(results) == 3
    assert "js_pattern_executed:random" in mock_session.actions_performed


@pytest.mark.asyncio
async def test_simulate_realistic_js_execution_pattern_invalid_session(browser_simulator):
    """Test JavaScript execution pattern with invalid session ID."""
    scripts = ["return 42;"]
    
    with pytest.raises(ValueError, match="No session found with ID"):
        await browser_simulator.simulate_realistic_js_execution_pattern(
            "invalid_session", scripts, "sequential"
        )


@pytest.mark.asyncio
async def test_handle_captcha_challenge_success(browser_simulator, mock_session):
    """Test successful CAPTCHA challenge handling."""
    # Setup
    mock_session.page.evaluate = AsyncMock(return_value=True)
    
    # Test
    success = await browser_simulator._handle_captcha_challenge(mock_session, 0)
    
    # Verify
    assert isinstance(success, bool)
    mock_session.page.evaluate.assert_called_once()


@pytest.mark.asyncio
async def test_handle_turnstile_challenge_success(browser_simulator, mock_session):
    """Test successful Turnstile challenge handling."""
    # Setup
    mock_session.page.evaluate = AsyncMock(return_value=True)
    
    # Test
    success = await browser_simulator._handle_turnstile_challenge(mock_session, 0)
    
    # Verify
    assert isinstance(success, bool)
    # Check that evaluate was called at least once (it may be called multiple times)
    assert mock_session.page.evaluate.call_count >= 1


@pytest.mark.asyncio
async def test_handle_custom_challenge_success(browser_simulator, mock_session):
    """Test successful custom challenge handling."""
    # Setup
    mock_session.session_id = "test_session"
    browser_simulator.sessions["test_session"] = mock_session
    mock_session.page.evaluate = AsyncMock(return_value=True)
    
    # Test
    success = await browser_simulator._handle_custom_challenge(mock_session, 0)
    
    # Verify
    assert isinstance(success, bool)


@pytest.mark.asyncio
async def test_handle_generic_challenge_success(browser_simulator, mock_session):
    """Test successful generic challenge handling."""
    # Setup
    mock_session.session_id = "test_session"
    browser_simulator.sessions["test_session"] = mock_session
    mock_session.page.evaluate = AsyncMock(return_value="complete")
    
    # Test
    success = await browser_simulator._handle_generic_challenge(mock_session, 0)
    
    # Verify
    assert isinstance(success, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])