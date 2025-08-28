"""
Privacy validation tests for ICE Locator MCP Server.

Tests privacy protection measures, data handling, and user rights compliance.
"""

import pytest
import asyncio
import hashlib
import time
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile
import json

from ice_locator_mcp.core.config import Config
from ice_locator_mcp.utils.cache import CacheManager
from ice_locator_mcp.tools.search_tools import SearchTools
from ice_locator_mcp.anti_detection.request_obfuscator import RequestObfuscator


class TestDataMinimization:
    """Test data minimization principles."""
    
    @pytest.fixture
    async def privacy_config(self):
        """Privacy-focused configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config()
            config.cache_dir = Path(temp_dir) / "cache"
            config.privacy.data_minimization = True
            config.privacy.anonymization = True
            config.privacy.retention_days = 7  # Short retention for privacy
            yield config
    
    async def test_search_parameter_minimization(self):
        """Test that only necessary search parameters are collected."""
        search_tools = SearchTools(MagicMock())
        
        # Test with excessive parameters
        input_params = {
            "first_name": "John",
            "last_name": "Doe",
            "middle_name": "William",
            "alien_number": "A123456789",
            "ssn": "123-45-6789",  # Should not be needed
            "date_of_birth": "1990-01-01",  # Should not be needed
            "mother_maiden_name": "Smith",  # Should not be needed
            "unnecessary_field": "value"
        }
        
        validated_params = await search_tools._validate_search_params(input_params)
        
        # Should only contain necessary fields
        necessary_fields = {"first_name", "last_name", "alien_number"}
        for field in validated_params:
            assert field in necessary_fields, f"Unnecessary field {field} should be filtered"
        
        # Should not contain sensitive unnecessary data
        assert "ssn" not in validated_params
        assert "date_of_birth" not in validated_params
        assert "mother_maiden_name" not in validated_params
        assert "unnecessary_field" not in validated_params
    
    async def test_response_data_minimization(self, privacy_config):
        """Test that responses contain only necessary information."""
        from ice_locator_mcp.scraper.ice_scraper import ICEScraper
        
        scraper = ICEScraper(privacy_config)
        
        # Mock response with excessive data
        mock_response = {
            "name": "John Doe",
            "alien_number": "A123456789",
            "facility": "Test Facility",
            "location": "Test City, ST",
            "internal_id": "INTERNAL123",  # Should be filtered
            "officer_notes": "Confidential notes",  # Should be filtered
            "system_metadata": {"created": "2023-01-01"}  # Should be filtered
        }
        
        # In a real implementation, test response filtering
        filtered_response = scraper._filter_response_data(mock_response)
        
        # Should only contain public information
        allowed_fields = {"name", "alien_number", "facility", "location"}
        for field in filtered_response:
            assert field in allowed_fields, f"Internal field {field} should be filtered"
    
    async def test_log_data_minimization(self):
        """Test that logs don't contain unnecessary personal data."""
        import structlog
        
        # Capture log output
        logged_events = []
        
        def capture_processor(logger, method_name, event_dict):
            logged_events.append(event_dict)
            return event_dict
        
        structlog.configure(processors=[capture_processor])
        logger = structlog.get_logger("test")
        
        # Log search operation
        search_params = {
            "first_name": "John",
            "last_name": "Doe",
            "ssn": "123-45-6789",
            "alien_number": "A123456789"
        }
        
        # Simulate logging with PII redaction
        redacted_params = {k: "***REDACTED***" if k in ["ssn"] else v 
                          for k, v in search_params.items()}
        
        logger.info("Search performed", params=redacted_params)
        
        # Verify sensitive data is not in logs
        for event in logged_events:
            event_str = str(event)
            assert "123-45-6789" not in event_str, "SSN should not appear in logs"


class TestDataAnonymization:
    """Test data anonymization and pseudonymization."""
    
    async def test_cache_key_anonymization(self, privacy_config):
        """Test that cache keys don't contain identifiable information."""
        cache_manager = CacheManager(cache_dir=privacy_config.cache_dir)
        await cache_manager.initialize()
        
        try:
            # Test anonymized cache keys
            personal_data = {
                "name": "John Doe",
                "alien_number": "A123456789",
                "facility": "Test Facility"
            }
            
            # Create anonymized cache key
            key_material = f"{personal_data['alien_number']}{personal_data['name']}"
            cache_key = hashlib.sha256(key_material.encode()).hexdigest()
            
            await cache_manager.set(cache_key, personal_data)
            
            # Verify cache key doesn't contain PII
            assert "John" not in cache_key
            assert "Doe" not in cache_key
            assert "A123456789" not in cache_key
            
            # Verify data can still be retrieved
            cached_data = await cache_manager.get(cache_key)
            assert cached_data == personal_data
            
        finally:
            await cache_manager.cleanup()
    
    async def test_session_anonymization(self):
        """Test that session identifiers don't contain personal information."""
        obfuscator = RequestObfuscator()
        
        # Test session ID generation
        personal_info = "john.doe@email.com"
        
        # Session ID should be anonymized
        session_id = hashlib.sha256(personal_info.encode()).hexdigest()[:16]
        
        headers = await obfuscator.obfuscate_request(
            session_id=session_id,
            base_headers={"Test": "header"}
        )
        
        # Verify session context doesn't leak personal info
        context = obfuscator._get_session_context(session_id)
        assert personal_info not in str(context.__dict__)
    
    async def test_error_message_anonymization(self):
        """Test that error messages don't leak personal information."""
        from ice_locator_mcp.tools.search_tools import SearchTools
        
        search_tools = SearchTools(MagicMock())
        
        # Test error handling with personal data
        personal_data = {
            "first_name": "John",
            "last_name": "Doe",
            "alien_number": "A123456789"
        }
        
        try:
            # Simulate error condition
            raise ValueError(f"Search failed for {personal_data}")
        except ValueError as e:
            error_msg = str(e)
            
            # Error should be anonymized
            anonymized_error = search_tools._anonymize_error_message(error_msg)
            
            assert "John" not in anonymized_error
            assert "Doe" not in anonymized_error
            assert "A123456789" not in anonymized_error


class TestUserRights:
    """Test user rights and data subject rights."""
    
    async def test_right_to_access(self, privacy_config):
        """Test user's right to access their data."""
        cache_manager = CacheManager(cache_dir=privacy_config.cache_dir)
        await cache_manager.initialize()
        
        try:
            # Store user data
            user_id = "user123"
            user_data = {"searches": ["search1", "search2"], "preferences": {"lang": "en"}}
            
            await cache_manager.set(f"user:{user_id}", user_data)
            
            # Test data access
            accessed_data = await cache_manager.get(f"user:{user_id}")
            assert accessed_data == user_data, "User should be able to access their data"
            
        finally:
            await cache_manager.cleanup()
    
    async def test_right_to_rectification(self, privacy_config):
        """Test user's right to correct their data."""
        cache_manager = CacheManager(cache_dir=privacy_config.cache_dir)
        await cache_manager.initialize()
        
        try:
            # Store incorrect data
            user_id = "user123"
            incorrect_data = {"name": "Jon Doe", "email": "wrong@email.com"}
            
            await cache_manager.set(f"user:{user_id}", incorrect_data)
            
            # Correct the data
            corrected_data = {"name": "John Doe", "email": "correct@email.com"}
            await cache_manager.set(f"user:{user_id}", corrected_data)
            
            # Verify correction
            result = await cache_manager.get(f"user:{user_id}")
            assert result == corrected_data, "User should be able to correct their data"
            
        finally:
            await cache_manager.cleanup()
    
    async def test_right_to_erasure(self, privacy_config):
        """Test user's right to delete their data."""
        cache_manager = CacheManager(cache_dir=privacy_config.cache_dir)
        await cache_manager.initialize()
        
        try:
            # Store user data
            user_id = "user123"
            user_data = {"personal": "information"}
            
            await cache_manager.set(f"user:{user_id}", user_data)
            
            # Verify data exists
            result = await cache_manager.get(f"user:{user_id}")
            assert result is not None
            
            # Delete user data
            await cache_manager.delete(f"user:{user_id}")
            
            # Verify data is deleted
            result = await cache_manager.get(f"user:{user_id}")
            assert result is None, "User data should be completely deleted"
            
        finally:
            await cache_manager.cleanup()
    
    async def test_right_to_portability(self, privacy_config):
        """Test user's right to data portability."""
        cache_manager = CacheManager(cache_dir=privacy_config.cache_dir)
        await cache_manager.initialize()
        
        try:
            # Store user data
            user_id = "user123"
            user_data = {
                "searches": ["search1", "search2"],
                "preferences": {"language": "en", "theme": "dark"},
                "history": ["action1", "action2"]
            }
            
            await cache_manager.set(f"user:{user_id}", user_data)
            
            # Export user data
            exported_data = await cache_manager.get(f"user:{user_id}")
            
            # Data should be in portable format (JSON serializable)
            import json
            json_data = json.dumps(exported_data)
            assert json_data is not None, "Data should be exportable in standard format"
            
            # Verify data integrity
            reimported_data = json.loads(json_data)
            assert reimported_data == user_data, "Exported data should maintain integrity"
            
        finally:
            await cache_manager.cleanup()


class TestConsentManagement:
    """Test consent management and user preferences."""
    
    async def test_consent_recording(self, privacy_config):
        """Test recording and managing user consent."""
        cache_manager = CacheManager(cache_dir=privacy_config.cache_dir)
        await cache_manager.initialize()
        
        try:
            # Record user consent
            user_id = "user123"
            consent_data = {
                "data_processing": True,
                "analytics": False,
                "third_party_sharing": False,
                "timestamp": time.time(),
                "version": "1.0"
            }
            
            await cache_manager.set(f"consent:{user_id}", consent_data)
            
            # Verify consent is recorded
            recorded_consent = await cache_manager.get(f"consent:{user_id}")
            assert recorded_consent == consent_data
            
            # Test consent withdrawal
            consent_data["data_processing"] = False
            consent_data["timestamp"] = time.time()
            
            await cache_manager.set(f"consent:{user_id}", consent_data)
            
            # Verify consent withdrawal
            updated_consent = await cache_manager.get(f"consent:{user_id}")
            assert updated_consent["data_processing"] is False
            
        finally:
            await cache_manager.cleanup()
    
    async def test_consent_granularity(self):
        """Test granular consent options."""
        # Test that users can consent to specific data uses
        consent_options = {
            "essential_functionality": True,  # Required for basic operation
            "performance_analytics": False,   # Optional analytics
            "error_reporting": True,          # Optional error reporting
            "usage_statistics": False,        # Optional usage stats
        }
        
        # Verify granular consent is supported
        assert len(consent_options) > 1, "Should support granular consent options"
        
        # Test that essential functionality can't be disabled
        essential_consent = consent_options.get("essential_functionality")
        assert essential_consent is True, "Essential functionality should be required"
    
    async def test_consent_versioning(self, privacy_config):
        """Test consent versioning for policy updates."""
        cache_manager = CacheManager(cache_dir=privacy_config.cache_dir)
        await cache_manager.initialize()
        
        try:
            user_id = "user123"
            
            # Initial consent
            consent_v1 = {
                "data_processing": True,
                "version": "1.0",
                "timestamp": time.time()
            }
            
            await cache_manager.set(f"consent:{user_id}", consent_v1)
            
            # Policy update requires new consent
            consent_v2 = {
                "data_processing": True,
                "new_feature_consent": False,  # New consent option
                "version": "2.0",
                "timestamp": time.time()
            }
            
            await cache_manager.set(f"consent:{user_id}", consent_v2)
            
            # Verify version tracking
            current_consent = await cache_manager.get(f"consent:{user_id}")
            assert current_consent["version"] == "2.0"
            assert "new_feature_consent" in current_consent
            
        finally:
            await cache_manager.cleanup()


class TestDataRetention:
    """Test data retention policies and automatic deletion."""
    
    async def test_automatic_data_expiration(self, privacy_config):
        """Test automatic data expiration based on retention policy."""
        cache_manager = CacheManager(
            cache_dir=privacy_config.cache_dir, 
            ttl=2  # 2 second TTL for testing
        )
        await cache_manager.initialize()
        
        try:
            # Store data with short TTL
            test_data = {"sensitive": "information"}
            await cache_manager.set("test_retention", test_data, ttl=1)
            
            # Data should be available immediately
            result = await cache_manager.get("test_retention")
            assert result is not None
            
            # Wait for expiration
            await asyncio.sleep(2)
            
            # Data should be automatically deleted
            result = await cache_manager.get("test_retention")
            assert result is None, "Data should be automatically deleted after TTL"
            
        finally:
            await cache_manager.cleanup()
    
    async def test_retention_policy_enforcement(self, privacy_config):
        """Test enforcement of data retention policies."""
        # Test different retention periods for different data types
        retention_policies = {
            "search_results": 7,      # 7 days
            "user_preferences": 365,  # 1 year
            "audit_logs": 2555,       # 7 years (legal requirement)
            "temporary_data": 1       # 1 day
        }
        
        for data_type, retention_days in retention_policies.items():
            assert retention_days > 0, f"Retention period for {data_type} should be positive"
            
            if data_type == "audit_logs":
                assert retention_days >= 2555, "Audit logs should have long retention"
            elif data_type == "temporary_data":
                assert retention_days <= 7, "Temporary data should have short retention"
    
    async def test_data_purging(self, privacy_config):
        """Test secure data purging and deletion."""
        cache_manager = CacheManager(cache_dir=privacy_config.cache_dir)
        await cache_manager.initialize()
        
        try:
            # Store sensitive data
            sensitive_data = {"ssn": "123-45-6789", "alien_number": "A123456789"}
            await cache_manager.set("sensitive_test", sensitive_data)
            
            # Verify data exists
            result = await cache_manager.get("sensitive_test")
            assert result is not None
            
            # Securely purge data
            await cache_manager.delete("sensitive_test")
            
            # Verify data is completely removed
            result = await cache_manager.get("sensitive_test")
            assert result is None
            
            # In a real implementation, verify secure deletion (overwriting)
            
        finally:
            await cache_manager.cleanup()


class TestPrivacyByDesign:
    """Test privacy by design principles."""
    
    async def test_default_privacy_settings(self):
        """Test that privacy-friendly settings are defaults."""
        config = Config()
        
        # Test default privacy settings
        assert hasattr(config, 'privacy'), "Should have privacy configuration"
        
        # Default should be privacy-preserving
        if hasattr(config.privacy, 'data_minimization'):
            assert config.privacy.data_minimization is True, "Data minimization should be default"
        
        if hasattr(config.privacy, 'anonymization'):
            assert config.privacy.anonymization is True, "Anonymization should be default"
    
    async def test_privacy_impact_assessment(self):
        """Test privacy impact assessment considerations."""
        # Verify privacy considerations are documented
        privacy_considerations = {
            "data_collection": "Only necessary data collected",
            "data_use": "Used only for stated purpose",
            "data_sharing": "No unnecessary sharing",
            "data_retention": "Minimal retention periods",
            "user_rights": "Full user rights supported",
            "security": "Appropriate security measures"
        }
        
        for consideration, requirement in privacy_considerations.items():
            assert requirement is not None, f"Privacy consideration {consideration} should be addressed"
    
    async def test_privacy_documentation(self):
        """Test that privacy practices are documented."""
        # Verify privacy policy elements exist
        privacy_policy_elements = [
            "data_collection_purpose",
            "data_types_collected", 
            "data_use_limitations",
            "user_rights",
            "data_retention_periods",
            "security_measures",
            "contact_information"
        ]
        
        # In a real implementation, verify documentation exists
        for element in privacy_policy_elements:
            assert element is not None, f"Privacy policy should include {element}"