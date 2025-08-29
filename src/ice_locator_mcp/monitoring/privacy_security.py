"""
Privacy and Security Monitoring Module.

Implements comprehensive data redaction, sensitive information filtering,
and compliance monitoring features for GDPR, CCPA, and other privacy regulations.
"""

import asyncio
import json
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Pattern
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum
import logging

import structlog


class ComplianceStandard(Enum):
    """Supported compliance standards."""
    
    GDPR = "gdpr"  # General Data Protection Regulation
    CCPA = "ccpa"  # California Consumer Privacy Act
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act


class DataCategory(Enum):
    """Categories of sensitive data."""
    
    PERSONAL_IDENTIFIERS = "personal_identifiers"
    GOVERNMENT_IDS = "government_ids"
    LOCATION_DATA = "location_data"
    CONTACT_INFO = "contact_info"
    TECHNICAL_DATA = "technical_data"


@dataclass
class RedactionRule:
    """Configuration for data redaction rules."""
    
    rule_id: str
    name: str
    pattern: str  # Regex pattern
    replacement: str
    data_category: DataCategory
    enabled: bool = True
    compliance_standards: List[ComplianceStandard] = field(default_factory=list)
    
    def __post_init__(self):
        """Compile regex pattern."""
        try:
            self.compiled_pattern: Pattern = re.compile(self.pattern, re.IGNORECASE)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{self.pattern}': {e}")


class AdvancedDataRedactor:
    """Advanced data redaction system with compliance monitoring."""
    
    def __init__(self, compliance_standards: List[ComplianceStandard] = None):
        """Initialize advanced data redactor."""
        self.logger = structlog.get_logger(__name__)
        self.compliance_standards = compliance_standards or [ComplianceStandard.GDPR]
        
        # Redaction rules
        self.redaction_rules: Dict[str, RedactionRule] = {}
        self.redaction_stats: Dict[str, int] = {}
        
        # Initialize default rules
        self._initialize_default_rules()
        
        self.logger.info("Advanced data redactor initialized",
                        compliance_standards=[std.value for std in self.compliance_standards])
    
    def _initialize_default_rules(self):
        """Initialize default redaction rules for various data types."""
        
        default_rules = [
            # Government IDs
            RedactionRule(
                rule_id="alien_number",
                name="Alien Registration Number",
                pattern=r'\b[Aa]-?\d{8,9}\b',
                replacement="[A_NUMBER_REDACTED]",
                data_category=DataCategory.GOVERNMENT_IDS,
                compliance_standards=[ComplianceStandard.GDPR]
            ),
            
            RedactionRule(
                rule_id="ssn",
                name="Social Security Number",
                pattern=r'\b\d{3}-?\d{2}-?\d{4}\b',
                replacement="[SSN_REDACTED]",
                data_category=DataCategory.GOVERNMENT_IDS,
                compliance_standards=[ComplianceStandard.GDPR, ComplianceStandard.CCPA]
            ),
            
            # Contact Information
            RedactionRule(
                rule_id="email",
                name="Email Address",
                pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                replacement="[EMAIL_REDACTED]",
                data_category=DataCategory.CONTACT_INFO,
                compliance_standards=[ComplianceStandard.GDPR, ComplianceStandard.CCPA]
            ),
            
            RedactionRule(
                rule_id="phone",
                name="Phone Number",
                pattern=r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
                replacement="[PHONE_REDACTED]",
                data_category=DataCategory.CONTACT_INFO,
                compliance_standards=[ComplianceStandard.GDPR, ComplianceStandard.CCPA]
            ),
            
            # Personal Names
            RedactionRule(
                rule_id="full_name",
                name="Full Name",
                pattern=r'\b[A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
                replacement="[NAME_REDACTED]",
                data_category=DataCategory.PERSONAL_IDENTIFIERS,
                compliance_standards=[ComplianceStandard.GDPR, ComplianceStandard.CCPA]
            ),
            
            # Dates of Birth
            RedactionRule(
                rule_id="date_of_birth",
                name="Date of Birth",
                pattern=r'\b(?:0[1-9]|1[0-2])[/-](?:0[1-9]|[12]\d|3[01])[/-](?:19|20)\d{2}\b',
                replacement="[DOB_REDACTED]",
                data_category=DataCategory.PERSONAL_IDENTIFIERS,
                compliance_standards=[ComplianceStandard.GDPR, ComplianceStandard.CCPA]
            ),
            
            # IP Addresses
            RedactionRule(
                rule_id="ip_address",
                name="IP Address",
                pattern=r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
                replacement="[IP_REDACTED]",
                data_category=DataCategory.TECHNICAL_DATA,
                compliance_standards=[ComplianceStandard.GDPR]
            )
        ]
        
        for rule in default_rules:
            self.redaction_rules[rule.rule_id] = rule
    
    def redact_text(self, text: str, context: str = "unknown") -> str:
        """Redact sensitive information from text."""
        if not isinstance(text, str) or not text.strip():
            return text
        
        redacted_text = text
        redactions_made = []
        
        for rule_id, rule in self.redaction_rules.items():
            if not rule.enabled:
                continue
            
            # Check if rule applies to current compliance standards
            if rule.compliance_standards and not any(
                std in self.compliance_standards for std in rule.compliance_standards
            ):
                continue
            
            try:
                matches = rule.compiled_pattern.findall(redacted_text)
                if matches:
                    redacted_text = rule.compiled_pattern.sub(rule.replacement, redacted_text)
                    redactions_made.extend(matches)
                    
                    # Update statistics
                    self.redaction_stats[rule_id] = self.redaction_stats.get(rule_id, 0) + len(matches)
                    
                    self.logger.debug("Data redacted",
                                    rule_id=rule_id,
                                    matches_count=len(matches),
                                    context=context)
            
            except Exception as e:
                self.logger.error("Redaction rule failed", rule_id=rule_id, error=str(e))
        
        return redacted_text
    
    def get_redaction_statistics(self) -> Dict[str, Any]:
        """Get comprehensive redaction statistics."""
        return {
            "total_redactions": sum(self.redaction_stats.values()),
            "redactions_by_rule": dict(self.redaction_stats),
            "active_rules": len([r for r in self.redaction_rules.values() if r.enabled]),
            "total_rules": len(self.redaction_rules),
            "compliance_standards": [std.value for std in self.compliance_standards]
        }


class ComplianceMonitor:
    """Monitors system compliance with privacy regulations."""
    
    def __init__(self, standards: List[ComplianceStandard] = None):
        """Initialize compliance monitor."""
        self.logger = structlog.get_logger(__name__)
        self.standards = standards or [ComplianceStandard.GDPR]
        
        # Monitoring state
        self.data_processing_log: List[Dict[str, Any]] = []
        self.consent_records: Dict[str, Dict[str, Any]] = {}
        self.audit_trail: List[Dict[str, Any]] = []
        
        self.logger.info("Compliance monitor initialized",
                        standards=[std.value for std in self.standards])
    
    def log_data_processing(self, operation: str, data_types: List[DataCategory],
                           purpose: str, legal_basis: str = None,
                           user_consent: bool = None):
        """Log data processing activities for compliance audit."""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "data_types": [dt.value for dt in data_types],
            "purpose": purpose,
            "legal_basis": legal_basis,
            "user_consent": user_consent,
            "compliance_standards": [std.value for std in self.standards]
        }
        
        self.data_processing_log.append(log_entry)
        
        self.logger.info("Data processing logged",
                        operation=operation,
                        data_types=len(data_types),
                        purpose=purpose)
    
    def record_user_consent(self, user_id: str, consent_type: str,
                           granted: bool, purpose: str):
        """Record user consent for data processing."""
        
        consent_record = {
            "timestamp": datetime.now().isoformat(),
            "consent_type": consent_type,
            "granted": granted,
            "purpose": purpose
        }
        
        if user_id not in self.consent_records:
            self.consent_records[user_id] = {}
        
        self.consent_records[user_id][consent_type] = consent_record
        
        self.logger.info("User consent recorded",
                        user_id=hashlib.sha256(user_id.encode()).hexdigest()[:8],
                        consent_type=consent_type,
                        granted=granted)
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""
        
        return {
            "generated_at": datetime.now().isoformat(),
            "compliance_standards": [std.value for std in self.standards],
            "data_processing_summary": {
                "total_operations": len(self.data_processing_log),
                "operations_last_30_days": len([
                    entry for entry in self.data_processing_log
                    if datetime.fromisoformat(entry["timestamp"]) > 
                    datetime.now() - timedelta(days=30)
                ])
            },
            "consent_summary": {
                "total_users": len(self.consent_records),
                "consent_types": list(set(
                    consent_type for user_consents in self.consent_records.values()
                    for consent_type in user_consents.keys()
                ))
            },
            "compliance_violations": {
                "total": len(self.audit_trail),
                "unresolved": len([v for v in self.audit_trail if not v.get("resolved")])
            }
        }


class PrivacySecurityMonitor:
    """Comprehensive privacy and security monitoring system."""
    
    def __init__(self, compliance_standards: List[ComplianceStandard] = None,
                 storage_path: Optional[Path] = None):
        """Initialize privacy and security monitor."""
        self.logger = structlog.get_logger(__name__)
        self.compliance_standards = compliance_standards or [ComplianceStandard.GDPR]
        
        # Initialize components
        self.data_redactor = AdvancedDataRedactor(self.compliance_standards)
        self.compliance_monitor = ComplianceMonitor(self.compliance_standards)
        
        # Security monitoring
        self.security_events: List[Dict[str, Any]] = []
        self.access_logs: List[Dict[str, Any]] = []
        
        # Privacy metrics
        self.privacy_metrics = {
            "redaction_effectiveness": 0.0,
            "consent_rate": 0.0,
            "compliance_score": 0.0
        }
        
        self.logger.info("Privacy and security monitor initialized",
                        compliance_standards=[std.value for std in self.compliance_standards])
    
    async def process_search_request(self, request_data: Dict[str, Any],
                                   user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a search request with privacy monitoring."""
        
        # Log data processing activity
        self.compliance_monitor.log_data_processing(
            operation="detainee_search",
            data_types=[
                DataCategory.PERSONAL_IDENTIFIERS,
                DataCategory.GOVERNMENT_IDS,
                DataCategory.LOCATION_DATA
            ],
            purpose="legal_assistance_family_reunification",
            legal_basis="legitimate_interest",  # GDPR Article 6(1)(f)
            user_consent=user_context.get("consent_granted") if user_context else None
        )
        
        # Redact sensitive information from request
        redacted_request = {}
        for key, value in request_data.items():
            if isinstance(value, str):
                redacted_request[key] = self.data_redactor.redact_text(value, f"search_request_{key}")
            else:
                redacted_request[key] = value
        
        # Log access attempt
        self._log_access_attempt(request_data, user_context)
        
        return redacted_request
    
    async def process_search_response(self, response_data: Dict[str, Any],
                                    user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a search response with privacy protection."""
        
        # Redact sensitive information from response
        if isinstance(response_data, dict):
            redacted_response = {}
            for key, value in response_data.items():
                if isinstance(value, str):
                    redacted_response[key] = self.data_redactor.redact_text(value, f"search_response_{key}")
                elif isinstance(value, list):
                    redacted_response[key] = [
                        self.data_redactor.redact_text(item, f"search_response_{key}_item")
                        if isinstance(item, str) else item
                        for item in value
                    ]
                else:
                    redacted_response[key] = value
        else:
            redacted_response = response_data
        
        # Update privacy metrics
        await self._update_privacy_metrics()
        
        return redacted_response
    
    def _log_access_attempt(self, request_data: Dict[str, Any],
                          user_context: Dict[str, Any] = None):
        """Log access attempt for security monitoring."""
        
        access_log = {
            "timestamp": datetime.now().isoformat(),
            "operation": "search_access",
            "user_id": user_context.get("user_id") if user_context else "anonymous",
            "ip_address": user_context.get("ip_address") if user_context else None,
            "request_size": len(str(request_data)),
            "sensitive_fields": [
                key for key in request_data.keys()
                if key in ["first_name", "last_name", "alien_number", "date_of_birth"]
            ]
        }
        
        self.access_logs.append(access_log)
        
        # Check for suspicious patterns
        self._detect_suspicious_activity(access_log)
    
    def _detect_suspicious_activity(self, access_log: Dict[str, Any]):
        """Detect suspicious access patterns."""
        
        user_id = access_log.get("user_id")
        if not user_id or user_id == "anonymous":
            return
        
        # Check for excessive requests
        recent_logs = [
            log for log in self.access_logs[-100:]  # Last 100 logs
            if log.get("user_id") == user_id and
            datetime.fromisoformat(log["timestamp"]) > 
            datetime.now() - timedelta(hours=1)
        ]
        
        if len(recent_logs) > 50:  # More than 50 requests in 1 hour
            security_event = {
                "timestamp": datetime.now().isoformat(),
                "event_type": "excessive_requests",
                "severity": "medium",
                "user_id": user_id,
                "description": f"User made {len(recent_logs)} requests in the last hour",
                "metadata": {"request_count": len(recent_logs)}
            }
            
            self.security_events.append(security_event)
            self.logger.warning("Suspicious activity detected", **security_event)
    
    async def _update_privacy_metrics(self):
        """Update privacy compliance metrics."""
        
        # Redaction effectiveness
        redaction_stats = self.data_redactor.get_redaction_statistics()
        total_redactions = redaction_stats.get("total_redactions", 0)
        self.privacy_metrics["redaction_effectiveness"] = min(total_redactions / 100.0, 1.0)
        
        # Consent rate
        consent_records = self.compliance_monitor.consent_records
        if consent_records:
            granted_consents = sum(
                1 for user_consents in consent_records.values()
                for consent in user_consents.values()
                if consent.get("granted", False)
            )
            total_consents = sum(len(consents) for consents in consent_records.values())
            self.privacy_metrics["consent_rate"] = granted_consents / total_consents if total_consents > 0 else 0.0
        
        # Overall compliance score
        self.privacy_metrics["compliance_score"] = (
            self.privacy_metrics["redaction_effectiveness"] * 0.4 +
            self.privacy_metrics["consent_rate"] * 0.6
        )
    
    def get_privacy_dashboard_data(self) -> Dict[str, Any]:
        """Get data for privacy monitoring dashboard."""
        
        compliance_report = self.compliance_monitor.generate_compliance_report()
        redaction_stats = self.data_redactor.get_redaction_statistics()
        
        return {
            "generated_at": datetime.now().isoformat(),
            "privacy_metrics": self.privacy_metrics,
            "compliance_report": compliance_report,
            "redaction_statistics": redaction_stats,
            "security_events": {
                "total": len(self.security_events),
                "recent": len([
                    event for event in self.security_events
                    if datetime.fromisoformat(event["timestamp"]) > 
                    datetime.now() - timedelta(hours=24)
                ])
            },
            "access_logs": {
                "total": len(self.access_logs),
                "unique_users": len(set(
                    log.get("user_id") for log in self.access_logs
                    if log.get("user_id") and log.get("user_id") != "anonymous"
                ))
            }
        }
    
    async def cleanup_expired_data(self):
        """Clean up data that exceeds retention policies."""
        
        # Clean up old access logs (keep only 90 days)
        cutoff_date = datetime.now() - timedelta(days=90)
        original_count = len(self.access_logs)
        self.access_logs = [
            log for log in self.access_logs
            if datetime.fromisoformat(log["timestamp"]) > cutoff_date
        ]
        
        removed_count = original_count - len(self.access_logs)
        if removed_count > 0:
            self.logger.info("Old access logs cleaned up", removed_count=removed_count)