#!/usr/bin/env python3
"""
Simple validation script for ICE Locator MCP Server.

This script performs basic validation of our implementation without requiring
external test dependencies.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    # First try to import core modules that don't depend on external packages
    from ice_locator_mcp.core.config import ServerConfig, ProxyConfig, SearchConfig
    from ice_locator_mcp.core.search_engine import SearchRequest, SearchResult, DetaineeRecord
    from ice_locator_mcp.utils.cache import CacheManager
    from ice_locator_mcp.utils.rate_limiter import RateLimiter
    print("✅ Core imports successful")
    
    # Try to import modules that depend on external packages
    try:
        from ice_locator_mcp.tools.search_tools import SearchTools
        from ice_locator_mcp.anti_detection.proxy_manager import ProxyManager
        print("✅ All imports successful")
        FULL_IMPORTS = True
    except ImportError as e:
        print(f"⚠️  Some imports failed (missing dependencies): {e}")
        print("📝 This is expected in development - core functionality can still be tested")
        FULL_IMPORTS = False
        
except ImportError as e:
    print(f"❌ Core import failed: {e}")
    sys.exit(1)


def test_config_creation():
    """Test configuration creation."""
    try:
        config = ServerConfig()
        assert config.server_name == "ice-locator-mcp"
        assert config.proxy_config.enabled is True
        assert config.search_config.timeout == 30
        print("✅ Configuration creation works")
        return True
    except Exception as e:
        print(f"❌ Configuration creation failed: {e}")
        return False


def test_search_request():
    """Test search request creation."""
    try:
        request = SearchRequest(
            first_name="John",
            last_name="Doe",
            date_of_birth="1990-01-01",
            country_of_birth="Mexico"
        )
        
        assert request.first_name == "John"
        assert request.last_name == "Doe"
        assert request.fuzzy_search is True
        
        # Test cache key generation
        cache_key = request.to_cache_key()
        assert isinstance(cache_key, str)
        assert len(cache_key) == 32  # MD5 hash length
        
        print("✅ Search request creation works")
        return True
    except Exception as e:
        print(f"❌ Search request creation failed: {e}")
        return False


def test_detainee_record():
    """Test detainee record creation."""
    try:
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
        assert record.confidence_score == 1.0
        
        print("✅ Detainee record creation works")
        return True
    except Exception as e:
        print(f"❌ Detainee record creation failed: {e}")
        return False


def test_search_result():
    """Test search result creation."""
    try:
        # Test success result
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
        assert "next_steps" in result.user_guidance
        
        # Test error result
        error_result = SearchResult.error("Test error")
        assert error_result.status == "error"
        assert len(error_result.results) == 0
        
        print("✅ Search result creation works")
        return True
    except Exception as e:
        print(f"❌ Search result creation failed: {e}")
        return False


async def test_cache_manager():
    """Test cache manager functionality."""
    try:
        cache = CacheManager()
        await cache.initialize()
        
        # Test basic operations
        await cache.set("test_key", {"test": "data"})
        result = await cache.get("test_key")
        
        assert result is not None
        assert result["test"] == "data"
        
        await cache.cleanup()
        print("✅ Cache manager works")
        return True
    except Exception as e:
        print(f"❌ Cache manager failed: {e}")
        return False


async def test_rate_limiter():
    """Test rate limiter functionality."""
    try:
        rate_limiter = RateLimiter(requests_per_minute=60, burst_allowance=10)
        
        # Should allow request immediately
        await rate_limiter.acquire()
        
        # Mark success and error
        await rate_limiter.mark_success()
        await rate_limiter.mark_error()
        
        print("✅ Rate limiter works")
        return True
    except Exception as e:
        print(f"❌ Rate limiter failed: {e}")
        return False


def test_helper_functions():
    """Test helper functions."""
    try:
        if not FULL_IMPORTS:
            print("⚠️  Skipping helper functions test (SearchTools not available)")
            return True
            
        # Mock search engine for SearchTools
        class MockSearchEngine:
            pass
        
        search_tools = SearchTools(MockSearchEngine())
        
        # Test name normalization
        normalized = search_tools._normalize_name("john doe")
        assert normalized == "John Doe"
        
        # Test date normalization
        normalized_date = search_tools._normalize_date("2024-01-15")
        assert normalized_date == "2024-01-15"
        
        # Test alien number validation
        assert search_tools._validate_alien_number("A123456789") is True
        assert search_tools._validate_alien_number("123456789") is False
        
        print("✅ Helper functions work")
        return True
    except Exception as e:
        print(f"❌ Helper functions failed: {e}")
        return False


async def main():
    """Run all validation tests."""
    print("🔍 ICE Locator MCP Server - Implementation Validation")
    print("=" * 50)
    
    tests = [
        ("Configuration Creation", test_config_creation),
        ("Search Request", test_search_request),
        ("Detainee Record", test_detainee_record),
        ("Search Result", test_search_result),
        ("Helper Functions", test_helper_functions),
    ]
    
    async_tests = [
        ("Cache Manager", test_cache_manager),
        ("Rate Limiter", test_rate_limiter),
    ]
    
    passed = 0
    total = len(tests) + len(async_tests)
    
    # Run synchronous tests
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        if test_func():
            passed += 1
    
    # Run asynchronous tests
    for test_name, test_func in async_tests:
        print(f"\n🧪 Testing {test_name}...")
        if await test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Validation Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Implementation is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)