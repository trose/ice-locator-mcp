"""
Privacy-first data redaction for analytics and monitoring.

Comprehensive redaction of sensitive information from search queries,
results, and analytics data to ensure privacy protection.
"""

import re
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class RedactionConfig:
    """Configuration for data redaction."""
    
    redaction_level: str = "strict"  # strict, moderate, minimal
    hash_replacements: bool = True
    preserve_structure: bool = True
    custom_patterns: List[str] = None
    
    def __post_init__(self):
        if self.custom_patterns is None:
            self.custom_patterns = []


class DataRedactor:
    """Comprehensive data redaction for privacy protection."""
    
    def __init__(self, config: RedactionConfig = None):
        self.config = config or RedactionConfig()
        self.logger = structlog.get_logger(__name__)
        
        # Compile regex patterns for efficient matching
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for different types of sensitive data."""
        
        # A-Number patterns (various formats)
        self.a_number_patterns = [
            re.compile(r'\bA\d{8,9}\b', re.IGNORECASE),
            re.compile(r'\b\d{8,9}\b(?=.*alien)', re.IGNORECASE),
            re.compile(r'alien[_\s]*number[_\s]*:?\s*[A]?\d{8,9}', re.IGNORECASE),
        ]
        
        # Date patterns (birth dates, etc.)
        self.date_patterns = [
            re.compile(r'\b\d{4}-\d{2}-\d{2}\b'),  # YYYY-MM-DD
            re.compile(r'\b\d{2}/\d{2}/\d{4}\b'),  # MM/DD/YYYY
            re.compile(r'\b\d{2}-\d{2}-\d{4}\b'),  # MM-DD-YYYY
            re.compile(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b'),  # M/D/YY or MM/DD/YYYY
        ]
        
        # Name patterns (more sophisticated)
        self.name_patterns = [
            re.compile(r'\bfirst_name[_\s]*:?\s*["\']?([^",\'\n]+)["\']?', re.IGNORECASE),
            re.compile(r'\blast_name[_\s]*:?\s*["\']?([^",\'\n]+)["\']?', re.IGNORECASE),
            re.compile(r'\bmiddle_name[_\s]*:?\s*["\']?([^",\'\n]+)["\']?', re.IGNORECASE),
            re.compile(r'\bname[_\s]*:?\s*["\']?([^",\'\n]+)["\']?', re.IGNORECASE),
        ]
        
        # Location/facility patterns
        self.location_patterns = [
            re.compile(r'\bfacility[_\s]*(?:name)?[_\s]*:?\s*["\']?([^",\'\n]+)["\']?', re.IGNORECASE),
            re.compile(r'\bdetention[_\s]*center[_\s]*:?\s*["\']?([^",\'\n]+)["\']?', re.IGNORECASE),
            re.compile(r'\bprocessing[_\s]*center[_\s]*:?\s*["\']?([^",\'\n]+)["\']?', re.IGNORECASE),
            re.compile(r'\bcity[_\s]*:?\s*["\']?([^",\'\n]+)["\']?', re.IGNORECASE),
            re.compile(r'\bstate[_\s]*:?\s*["\']?([^",\'\n]+)["\']?', re.IGNORECASE),
        ]
        
        # Country patterns
        self.country_patterns = [
            re.compile(r'\bcountry[_\s]*(?:of[_\s]*birth)?[_\s]*:?\s*["\']?([^",\'\n]+)["\']?', re.IGNORECASE),
            re.compile(r'\bnationality[_\s]*:?\s*["\']?([^",\'\n]+)["\']?', re.IGNORECASE),
        ]
    
    def redact_search_query(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive information from search query parameters."""
        
        if not isinstance(query_data, dict):
            return query_data
        
        redacted = {}
        
        for key, value in query_data.items():
            if isinstance(value, str):
                redacted[key] = self._redact_string_value(key, value)
            elif isinstance(value, dict):
                redacted[key] = self.redact_search_query(value)
            elif isinstance(value, list):
                redacted[key] = [self.redact_search_query(item) if isinstance(item, dict) 
                               else self._redact_string_value(key, str(item)) 
                               for item in value]
            else:
                # Non-sensitive data types (numbers, booleans)
                redacted[key] = value
        
        return redacted
    
    def redact_search_results(self, results_data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive information from search results."""
        
        if not isinstance(results_data, dict):
            return results_data
        
        redacted = {}
        
        for key, value in results_data.items():
            if key == "results" and isinstance(value, list):
                # Redact individual result records
                redacted[key] = [self._redact_detainee_record(record) for record in value]
            elif key in ["search_metadata", "user_guidance"]:
                # Keep metadata but redact sensitive parts
                redacted[key] = self._redact_metadata(value)
            elif isinstance(value, str):
                redacted[key] = self._redact_string_value(key, value)
            elif isinstance(value, dict):
                redacted[key] = self.redact_search_results(value)
            else:
                redacted[key] = value
        
        return redacted
    
    def redact_analytics_data(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact analytics data while preserving useful metrics."""
        
        if not isinstance(analytics_data, dict):
            return analytics_data
        
        redacted = {}
        
        for key, value in analytics_data.items():
            if key in ["request_count", "success_rate", "response_time", "error_count"]:
                # Preserve performance metrics
                redacted[key] = value
            elif key in ["tool_name", "operation_type", "status"]:
                # Preserve operational metrics
                redacted[key] = value
            elif isinstance(value, str):
                redacted[key] = self._redact_string_value(key, value)
            elif isinstance(value, dict):
                redacted[key] = self.redact_analytics_data(value)
            elif isinstance(value, list):
                redacted[key] = [self.redact_analytics_data(item) if isinstance(item, dict)
                               else self._redact_if_sensitive(str(item))
                               for item in value]
            else:
                redacted[key] = value
        
        return redacted
    
    def _redact_string_value(self, key: str, value: str) -> str:
        """Redact sensitive information from string values based on context."""
        
        # Check if this is a sensitive field by key name
        sensitive_keys = [
            "first_name", "last_name", "middle_name", "name",
            "alien_number", "a_number", "date_of_birth", "dob",
            "country_of_birth", "nationality", "facility_name",
            "facility_location", "detention_center", "address"
        ]
        
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            return self._generate_placeholder(key, value)
        
        # Apply pattern-based redaction
        return self._redact_patterns(value)
    
    def _redact_patterns(self, text: str) -> str:
        """Apply pattern-based redaction to text."""
        
        if not isinstance(text, str):
            return text
        
        redacted_text = text
        
        # Redact A-numbers
        for pattern in self.a_number_patterns:
            redacted_text = pattern.sub("[A_NUMBER]", redacted_text)
        
        # Redact dates
        for pattern in self.date_patterns:
            redacted_text = pattern.sub("[DATE]", redacted_text)
        
        # Redact names (be careful with common words)
        for pattern in self.name_patterns:
            if "first_name" in text.lower() or "last_name" in text.lower():
                redacted_text = pattern.sub(lambda m: f"{m.group().split(':')[0]}:[NAME]", redacted_text)
        
        # Redact locations
        for pattern in self.location_patterns:
            redacted_text = pattern.sub(lambda m: f"{m.group().split(':')[0]}:[LOCATION]", redacted_text)
        
        # Redact countries
        for pattern in self.country_patterns:
            redacted_text = pattern.sub(lambda m: f"{m.group().split(':')[0]}:[COUNTRY]", redacted_text)
        
        return redacted_text
    
    def _redact_detainee_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive information from detainee records."""
        
        if not isinstance(record, dict):
            return record
        
        # Map of sensitive fields to redaction placeholders
        sensitive_fields = {
            "alien_number": "[A_NUMBER]",
            "name": "[NAME]", 
            "first_name": "[FIRST_NAME]",
            "last_name": "[LAST_NAME]",
            "date_of_birth": "[DATE_OF_BIRTH]",
            "country_of_birth": "[COUNTRY]",
            "facility_name": "[FACILITY]",
            "facility_location": "[LOCATION]",
            "address": "[ADDRESS]"
        }
        
        redacted = {}
        
        for key, value in record.items():
            if key in sensitive_fields:
                redacted[key] = sensitive_fields[key]
            elif key in ["custody_status", "last_updated", "confidence_score"]:
                # Preserve non-sensitive metadata
                redacted[key] = value
            else:
                redacted[key] = self._redact_if_sensitive(str(value))
        
        return redacted
    
    def _redact_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Redact metadata while preserving useful analytics."""
        
        if not isinstance(metadata, dict):
            return metadata
        
        redacted = {}
        
        # Preserve useful metadata
        preserve_keys = [
            "search_date", "total_results", "processing_time_ms",
            "success_rate", "error_type", "suggestions_count"
        ]
        
        for key, value in metadata.items():
            if key in preserve_keys:
                redacted[key] = value
            elif isinstance(value, str):
                redacted[key] = self._redact_patterns(value)
            elif isinstance(value, dict):
                redacted[key] = self._redact_metadata(value)
            elif isinstance(value, list):
                # Redact list items that might contain sensitive data
                redacted[key] = [self._redact_if_sensitive(str(item)) for item in value]
            else:
                redacted[key] = value
        
        return redacted
    
    def _generate_placeholder(self, key: str, value: str) -> str:
        """Generate appropriate placeholder for sensitive data."""
        
        if self.config.hash_replacements:
            # Generate consistent hash for analytics correlation
            hash_value = hashlib.md5(f"{key}:{value}".encode()).hexdigest()[:8]
            return f"[{key.upper()}_{hash_value}]"
        else:
            return f"[{key.upper()}]"
    
    def _redact_if_sensitive(self, text: str) -> str:
        """Apply redaction if text appears to contain sensitive information."""
        
        if not isinstance(text, str):
            return text
        
        # Quick checks for obvious sensitive data
        if any(pattern.search(text) for pattern in self.a_number_patterns):
            return self._redact_patterns(text)
        
        if any(pattern.search(text) for pattern in self.date_patterns):
            return self._redact_patterns(text)
        
        # If no obvious sensitive data, return as-is
        return text
    
    def validate_redaction(self, original: Dict[str, Any], redacted: Dict[str, Any]) -> bool:
        """Validate that redaction was successful and no sensitive data remains."""
        
        redacted_text = str(redacted).lower()
        
        # Check for common sensitive data patterns that should not appear
        sensitive_indicators = [
            r'\ba\d{8,9}\b',  # A-numbers
            r'\b\d{4}-\d{2}-\d{2}\b',  # Dates
            r'\b[a-z]+ detention center\b',  # Facility names
        ]
        
        for pattern in sensitive_indicators:
            if re.search(pattern, redacted_text):
                self.logger.warning(
                    "Potential sensitive data found in redacted content",
                    pattern=pattern
                )
                return False
        
        return True


def create_redactor(level: str = "strict") -> DataRedactor:
    """Create a data redactor with specified redaction level."""
    
    config = RedactionConfig(redaction_level=level)
    return DataRedactor(config)