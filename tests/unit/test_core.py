"""
Unit tests for ICE Locator MCP Server core functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from ice_locator_mcp.core.config import ServerConfig, ProxyConfig, SearchConfig
from ice_locator_mcp.core.search_engine import SearchEngine, SearchRequest, SearchResult, DetaineeRecord
from ice_locator_mcp.anti_detection.proxy_manager import ProxyManager
from ice_locator_mcp.tools.search_tools import SearchTools


class TestServerConfig:
    """Test server configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = ServerConfig()
        
        assert config.server_name == "ice-locator-mcp"
        assert config.server_version == "0.1.0"
        assert config.proxy_config.enabled is True
        assert config.search_config.timeout == 30
        assert config.cache_config.enabled is True
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = ServerConfig()
        
        # Should not raise any exceptions
        config.validate()
        
        # Test invalid values
        config.search_config.timeout = 1  # Too low
        with pytest.raises(ValueError):
            config.validate()
    
    def test_config_from_env(self):
        """Test configuration from environment variables."""
        with patch.dict('os.environ', {
            'ICE_LOCATOR_PROXY_ENABLED': 'false',
            'ICE_LOCATOR_TIMEOUT': '60'
        }):
            config = ServerConfig.from_env()
            
            assert config.proxy_config.enabled is False
            assert config.search_config.timeout == 60


class TestSearchRequest:
    """Test search request functionality."""
    
    def test_search_request_creation(self):
        """Test creating search request."""
        request = SearchRequest(
            first_name="John",
            last_name="Doe",
            date_of_birth="1990-01-01",
            country_of_birth="Mexico"
        )
        
        assert request.first_name == "John"
        assert request.last_name == "Doe"
        assert request.fuzzy_search is True
        assert request.language == "en"
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        request1 = SearchRequest(
            first_name="John",
            last_name="Doe", 
            date_of_birth="1990-01-01",
            country_of_birth="Mexico"
        )
        
        request2 = SearchRequest(
            first_name="john",  # Different case
            last_name="doe",
            date_of_birth="1990-01-01", 
            country_of_birth="mexico"
        )
        
        # Should generate same cache key (case insensitive)
        assert request1.to_cache_key() == request2.to_cache_key()
        
        # Different request should have different key
        request3 = SearchRequest(
            first_name="Jane",
            last_name="Doe",
            date_of_birth="1990-01-01",
            country_of_birth="Mexico"
        )
        
        assert request1.to_cache_key() != request3.to_cache_key()


class TestDetaineeRecord:
    """Test detainee record functionality."""
    
    def test_record_creation(self):
        """Test creating detainee record."""
        record = DetaineeRecord(
            alien_number="A123456789",
            name="John Doe",
            date_of_birth="1990-01-01",
            country_of_birth="Mexico",
            facility_name="Test Facility",
            facility_location="Test City, TX",
            custody_status="In Custody",
            last_updated="2024-01-15T10:30:00Z"
        )
        
        assert record.alien_number == "A123456789"
        assert record.name == "John Doe"
        assert record.confidence_score == 1.0  # Default value


class TestSearchResult:
    """Test search result functionality."""
    
    def test_success_result(self):
        """Test creating successful search result."""
        records = [
            DetaineeRecord(
                alien_number="A123456789",
                name="John Doe",
                date_of_birth="1990-01-01",
                country_of_birth="Mexico",
                facility_name="Test Facility",
                facility_location="Test City, TX", 
                custody_status="In Custody",
                last_updated="2024-01-15T10:30:00Z"
            )
        ]
        
        result = SearchResult.success(records, 1.5)
        
        assert result.status == "found"
        assert len(result.results) == 1
        assert result.search_metadata["total_results"] == 1
        assert "next_steps" in result.user_guidance
    
    def test_error_result(self):
        """Test creating error search result."""
        result = SearchResult.error("Test error message")
        
        assert result.status == "error"
        assert len(result.results) == 0
        assert result.search_metadata["error_message"] == "Test error message"
    
    def test_not_found_result(self):
        """Test creating not found result."""
        result = SearchResult.success([], 1.0)
        
        assert result.status == "not_found"
        assert len(result.results) == 0


@pytest.mark.asyncio
class TestSearchTools:
    """Test search tools functionality."""
    
    @pytest.fixture
    def mock_search_engine(self):
        """Create mock search engine."""
        engine = Mock(spec=SearchEngine)
        engine.search = AsyncMock()
        return engine
    
    @pytest.fixture 
    def search_tools(self, mock_search_engine):
        """Create search tools instance."""
        return SearchTools(mock_search_engine)
    
    async def test_search_by_name_validation(self, search_tools):
        """Test name search validation."""
        # Missing required field should raise error
        result = await search_tools.search_by_name(
            first_name="John",
            last_name="",  # Empty last name
            date_of_birth="1990-01-01",
            country_of_birth="Mexico"
        )
        
        # Should return error response
        assert "error" in result.lower()
    
    async def test_alien_number_validation(self, search_tools):
        """Test alien number validation."""
        # Invalid alien number format
        result = await search_tools.search_by_alien_number(
            alien_number="123456789"  # Missing 'A' prefix
        )
        
        # Should return error response
        assert "error" in result.lower()
        assert "invalid alien number" in result.lower()
    
    async def test_natural_language_parsing(self, search_tools):
        """Test natural language query parsing."""
        # Test alien number parsing
        params = await search_tools._parse_natural_language_query(
            "Find A123456789", None
        )
        
        assert params is not None
        assert params["alien_number"] == "A123456789"
        
        # Test name parsing
        params = await search_tools._parse_natural_language_query(
            "Find John Doe from Mexico born 1990", None
        )
        
        assert params is not None
        assert params["first_name"] == "John"
        assert params["last_name"] == "Doe"
        assert params["country_of_birth"] == "Mexico"
    
    async def test_fuzzy_matching(self, search_tools):
        """Test fuzzy matching functionality."""
        variations = await search_tools._generate_name_variations(
            "Jose", "Garcia", None
        )
        
        assert len(variations) > 0
        # Should include common variations
        variations_flat = [name for pair in variations for name in pair]
        assert any("josé" in name.lower() for name in variations_flat)


@pytest.mark.asyncio
class TestProxyManager:
    """Test proxy manager functionality."""
    
    @pytest.fixture
    def proxy_config(self):
        """Create proxy configuration."""
        return ProxyConfig(
            enabled=True,
            rotation_interval=300,
            max_requests_per_proxy=10
        )
    
    @pytest.fixture
    def proxy_manager(self, proxy_config):
        """Create proxy manager instance."""
        return ProxyManager(proxy_config)
    
    async def test_proxy_manager_initialization(self, proxy_manager):
        """Test proxy manager initialization."""
        await proxy_manager.initialize()
        
        # Should have initialized without errors
        assert proxy_manager.config.enabled is True
    
    async def test_proxy_selection(self, proxy_manager):
        """Test proxy selection logic."""
        await proxy_manager.initialize()
        
        # Get proxy (may return None if no proxies available)
        proxy = await proxy_manager.get_proxy()
        
        # If proxy is returned, it should have required attributes
        if proxy:
            assert hasattr(proxy, 'endpoint')
            assert hasattr(proxy, 'url')


class TestHelperFunctions:
    """Test helper and utility functions."""
    
    def test_name_normalization(self):
        """Test name normalization."""
        search_tools = SearchTools(Mock())
        
        # Test case normalization
        assert search_tools._normalize_name("john doe") == "John Doe"
        assert search_tools._normalize_name("MARIA GARCIA") == "Maria Garcia"
        assert search_tools._normalize_name("  jose  rodriguez  ") == "Jose Rodriguez"
    
    def test_date_normalization(self):
        """Test date normalization."""
        search_tools = SearchTools(Mock())
        
        # Test various date formats
        assert search_tools._normalize_date("2024-01-15") == "2024-01-15"
        assert search_tools._normalize_date("01/15/2024") == "2024-01-15"
        assert search_tools._normalize_date("15-01-2024") == "2024-01-2024"
        
        # Invalid format should raise error
        with pytest.raises(ValueError):
            search_tools._normalize_date("invalid-date")
    
    def test_alien_number_validation(self):
        """Test alien number validation.""" 
        search_tools = SearchTools(Mock())
        
        # Valid formats
        assert search_tools._validate_alien_number("A123456789") is True
        assert search_tools._validate_alien_number("A12345678") is True
        
        # Invalid formats
        assert search_tools._validate_alien_number("123456789") is False
        assert search_tools._validate_alien_number("A1234567") is False
        assert search_tools._validate_alien_number("B123456789") is False


if __name__ == "__main__":
    pytest.main([__file__])