"""
Tests for the FingerprintingTester module.
"""

import pytest
import asyncio
import json
import os
import sys
import tempfile

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.testing.fingerprinting_tester import FingerprintingTester, FingerprintTestResult, FingerprintReport


class TestFingerprintingTester:
    """Test cases for the FingerprintingTester class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.tester = FingerprintingTester()
    
    def test_fingerprint_test_result_creation(self):
        """Test FingerprintTestResult dataclass creation and methods."""
        result = FingerprintTestResult(
            test_name="test_webgl_vendor",
            passed=True,
            score=0.95,
            details={"vendor": "Intel Inc."}
        )
        
        # Test to_dict method
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict["test_name"] == "test_webgl_vendor"
        assert result_dict["passed"] is True
        assert result_dict["score"] == 0.95
        assert result_dict["details"]["vendor"] == "Intel Inc."
        
        # Test from_dict method
        new_result = FingerprintTestResult.from_dict(result_dict)
        assert new_result.test_name == result.test_name
        assert new_result.passed == result.passed
        assert new_result.score == result.score
        assert new_result.details["vendor"] == result.details["vendor"]
    
    def test_fingerprint_report_creation(self):
        """Test FingerprintReport dataclass creation and methods."""
        test_results = [
            FingerprintTestResult(
                test_name="test_webgl_vendor",
                passed=True,
                score=0.95,
                details={"vendor": "Intel Inc."}
            ),
            FingerprintTestResult(
                test_name="test_canvas_rendering",
                passed=False,
                score=0.0,
                details={"error": "Canvas not supported"}
            )
        ]
        
        report = FingerprintReport(
            session_id="test_session_123",
            overall_score=0.475,
            test_results=test_results,
            fingerprint_hash="abc123def456"
        )
        
        # Test to_dict method
        report_dict = report.to_dict()
        assert isinstance(report_dict, dict)
        assert report_dict["session_id"] == "test_session_123"
        assert report_dict["overall_score"] == 0.475
        assert len(report_dict["test_results"]) == 2
        assert report_dict["fingerprint_hash"] == "abc123def456"
        
        # Test from_dict method
        new_report = FingerprintReport.from_dict(report_dict)
        assert new_report.session_id == report.session_id
        assert new_report.overall_score == report.overall_score
        assert len(new_report.test_results) == len(report.test_results)
        assert new_report.fingerprint_hash == report.fingerprint_hash
    
    @pytest.mark.asyncio
    async def test_fingerprinting_tester_initialization(self):
        """Test FingerprintingTester initialization."""
        assert hasattr(self.tester, 'webgl_manager')
        assert hasattr(self.tester, 'canvas_manager')
        assert hasattr(self.tester, 'hardware_manager')
        assert hasattr(self.tester, 'device_manager')
        assert hasattr(self.tester, 'audio_manager')
        assert hasattr(self.tester, 'font_manager')
        assert hasattr(self.tester, 'viewport_manager')
        assert hasattr(self.tester, 'plugin_manager')
        assert hasattr(self.tester, 'media_manager')
        assert hasattr(self.tester, 'timezone_manager')
        
        # Check that test configurations exist
        assert isinstance(self.tester.test_configurations, dict)
        assert "webgl_tests" in self.tester.test_configurations
        assert "canvas_tests" in self.tester.test_configurations
        assert "hardware_tests" in self.tester.test_configurations
    
    def test_calculate_overall_score(self):
        """Test calculating overall fingerprinting evasion score."""
        # Test with empty results
        empty_results = []
        empty_score = self.tester._calculate_overall_score(empty_results)
        assert empty_score == 0.0
        
        # Test with mixed results
        mixed_results = [
            FingerprintTestResult("test1", True, 1.0, {}),
            FingerprintTestResult("test2", False, 0.0, {}),
            FingerprintTestResult("test3", True, 1.0, {}),
            FingerprintTestResult("test4", True, 0.5, {})
        ]
        mixed_score = self.tester._calculate_overall_score(mixed_results)
        assert mixed_score == 0.625  # (1.0 + 0.0 + 1.0 + 0.5) / 4
    
    def test_generate_fingerprint_hash(self):
        """Test generating fingerprint hash."""
        test_results = [
            FingerprintTestResult("test1", True, 1.0, {"detail": "value1"}),
            FingerprintTestResult("test2", False, 0.0, {"detail": "value2"})
        ]
        
        fingerprint_hash = self.tester._generate_fingerprint_hash(test_results)
        assert isinstance(fingerprint_hash, str)
        assert len(fingerprint_hash) == 64  # SHA256 hash length
    
    def test_save_and_load_report(self):
        """Test saving and loading fingerprint reports."""
        test_results = [
            FingerprintTestResult(
                test_name="test_webgl_vendor",
                passed=True,
                score=0.95,
                details={"vendor": "Intel Inc."}
            )
        ]
        
        report = FingerprintReport(
            session_id="test_session_123",
            overall_score=0.95,
            test_results=test_results,
            fingerprint_hash="abc123def456"
        )
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Save the report
            self.tester.save_report(report, temp_path)
            
            # Check that file was created
            assert os.path.exists(temp_path)
            
            # Load the report
            loaded_report = self.tester.load_report(temp_path)
            
            # Verify the loaded report
            assert loaded_report.session_id == report.session_id
            assert loaded_report.overall_score == report.overall_score
            assert len(loaded_report.test_results) == len(report.test_results)
            assert loaded_report.fingerprint_hash == report.fingerprint_hash
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__])