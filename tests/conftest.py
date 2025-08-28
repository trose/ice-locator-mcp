"""
Test configuration and fixtures.
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock, AsyncMock

from ice_locator_mcp.core.config import ServerConfig, ProxyConfig, SearchConfig


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_config(temp_dir):
    """Create test configuration."""
    config = ServerConfig()
    
    # Use temp directory for cache and logs
    config.cache_config.cache_dir = temp_dir / "cache"
    config.logging_config.log_dir = temp_dir / "logs"
    
    # Disable proxy for tests by default
    config.proxy_config.enabled = False
    
    # Reduce timeouts for faster tests
    config.search_config.timeout = 5
    config.search_config.requests_per_minute = 60  # Higher rate for tests
    
    return config


@pytest.fixture
def mock_proxy_manager():
    """Create mock proxy manager."""
    manager = Mock()
    manager.initialize = AsyncMock()
    manager.cleanup = AsyncMock()
    manager.get_proxy = AsyncMock(return_value=None)
    manager.mark_proxy_success = AsyncMock()
    manager.mark_proxy_failure = AsyncMock()
    return manager


@pytest.fixture
def mock_search_engine():
    """Create mock search engine."""
    engine = Mock()
    engine.initialize = AsyncMock()
    engine.cleanup = AsyncMock()
    engine.search = AsyncMock()
    return engine


@pytest.fixture
def sample_detainee_data():
    """Sample detainee data for testing."""
    return {
        "alien_number": "A123456789",
        "name": "John Doe",
        "date_of_birth": "1990-01-15",
        "country_of_birth": "Mexico",
        "facility_name": "Test Processing Center",
        "facility_location": "Test City, TX",
        "custody_status": "In Custody",
        "last_updated": "2024-01-15T10:30:00Z"
    }


@pytest.fixture
def sample_search_requests():
    """Sample search requests for bulk testing."""
    return [
        {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-15",
            "country_of_birth": "Mexico"
        },
        {
            "first_name": "Jane",
            "last_name": "Smith", 
            "date_of_birth": "1985-03-22",
            "country_of_birth": "Guatemala"
        },
        {
            "alien_number": "A987654321"
        }
    ]


@pytest.fixture
def mock_html_response():
    """Mock HTML response from ICE website."""
    return """
    <html>
    <body>
        <form id="search-form" action="/search">
            <input type="hidden" name="csrf_token" value="test-csrf-token">
            <input name="first_name" type="text">
            <input name="last_name" type="text">
            <input name="date_of_birth" type="date">
            <input name="country_of_birth" type="text">
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


# Test constants
TEST_ALIEN_NUMBERS = [
    "A123456789",
    "A987654321", 
    "A555666777"
]

TEST_NAMES = [
    ("John", "Doe"),
    ("Jane", "Smith"),
    ("Maria", "Garcia"),
    ("Jose", "Rodriguez")
]

TEST_COUNTRIES = [
    "Mexico",
    "Guatemala", 
    "El Salvador",
    "Honduras",
    "Nicaragua"
]

TEST_DATES = [
    "1990-01-15",
    "1985-03-22",
    "1992-07-08",
    "1988-12-01"
]