"""
User Analytics and Session Replay Module.

Provides privacy-first user identification, session tracking, and behavior pattern analysis
for AI usage insights while ensuring compliance with privacy regulations.
"""

import asyncio
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging

import structlog

try:
    import mcpcat
    MCPCAT_AVAILABLE = True
except ImportError:
    mcpcat = None
    MCPCAT_AVAILABLE = False


@dataclass
class UserSession:
    """Represents a user session with privacy-first design."""
    
    session_id: str
    user_hash: Optional[str] = None  # Anonymized user identifier
    start_time: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    search_patterns: List[str] = field(default_factory=list)
    language_preference: str = "en"
    client_type: Optional[str] = None
    client_version: Optional[str] = None
    geographic_region: Optional[str] = None  # Approximate region, not precise location
    is_active: bool = True
    
    def __post_init__(self):
        """Initialize session after creation."""
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
    
    @property
    def duration(self) -> timedelta:
        """Calculate session duration."""
        return self.last_activity - self.start_time
    
    @property
    def tool_call_count(self) -> int:
        """Get total number of tool calls in session."""
        return len(self.tool_calls)
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.now()
    
    def add_tool_call(self, tool_name: str, arguments: Dict[str, Any], 
                     result: Optional[Dict[str, Any]] = None, 
                     error: Optional[str] = None):
        """Add a tool call to the session history."""
        self.update_activity()
        
        # Redact sensitive information from arguments
        sanitized_args = self._sanitize_arguments(arguments)
        
        tool_call = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "arguments": sanitized_args,
            "success": error is None,
            "error": error,
            "duration_ms": None  # Will be filled when tool completes
        }
        
        # Add search pattern analysis
        if tool_name in ["search_detainee_by_name", "smart_detainee_search"]:
            pattern = self._extract_search_pattern(tool_name, sanitized_args)
            if pattern and pattern not in self.search_patterns:
                self.search_patterns.append(pattern)
        
        self.tool_calls.append(tool_call)
    
    def _sanitize_arguments(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Remove or hash sensitive information from tool arguments."""
        sanitized = {}
        
        # Define sensitive fields that should be redacted
        sensitive_fields = {
            "first_name", "last_name", "middle_name", "alien_number",
            "date_of_birth", "social_security_number", "passport_number"
        }
        
        for key, value in arguments.items():
            if key in sensitive_fields:
                # Hash sensitive values for pattern analysis
                if isinstance(value, str) and value:
                    sanitized[key] = f"hash_{hashlib.sha256(value.encode()).hexdigest()[:8]}"
                else:
                    sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _extract_search_pattern(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[str]:
        """Extract search pattern for behavior analysis."""
        patterns = []
        
        if tool_name == "search_detainee_by_name":
            if arguments.get("fuzzy_search"):
                patterns.append("fuzzy_name_search")
            if arguments.get("middle_name"):
                patterns.append("full_name_search")
            else:
                patterns.append("basic_name_search")
        
        elif tool_name == "smart_detainee_search":
            patterns.append("natural_language_search")
            if arguments.get("suggest_corrections"):
                patterns.append("auto_correction_enabled")
        
        elif tool_name == "bulk_search_detainees":
            patterns.append("bulk_search")
            count = len(arguments.get("search_requests", []))
            if count > 10:
                patterns.append("large_batch_search")
        
        return "_".join(patterns) if patterns else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        data = asdict(self)
        data["start_time"] = self.start_time.isoformat()
        data["last_activity"] = self.last_activity.isoformat()
        return data


@dataclass
class BehaviorPattern:
    """Represents detected user behavior patterns."""
    
    pattern_id: str
    pattern_type: str  # "search_frequency", "tool_usage", "session_duration", etc.
    description: str
    confidence: float  # 0.0 to 1.0
    occurrences: int
    first_seen: datetime
    last_seen: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pattern to dictionary."""
        data = asdict(self)
        data["first_seen"] = self.first_seen.isoformat()
        data["last_seen"] = self.last_seen.isoformat()
        return data


class UserAnalytics:
    """Privacy-first user analytics and session tracking system."""
    
    def __init__(self, mcpcat_options: Optional[Dict[str, Any]] = None, 
                 storage_path: Optional[Path] = None,
                 session_timeout: int = 1800):  # 30 minutes
        """Initialize user analytics system."""
        self.logger = structlog.get_logger(__name__)
        self.mcpcat_options = mcpcat_options if MCPCAT_AVAILABLE else None
        self.session_timeout = session_timeout
        
        # Session storage
        self.active_sessions: Dict[str, UserSession] = {}
        self.behavior_patterns: Dict[str, BehaviorPattern] = {}
        
        # Storage configuration
        self.storage_path = storage_path or Path.home() / ".cache" / "ice-locator-mcp" / "analytics"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Analytics configuration
        self.enable_session_replay = True
        self.enable_behavior_analysis = True
        self.enable_pattern_detection = True
        self.max_sessions_in_memory = 1000
        
        # Privacy controls
        self.data_retention_days = 30
        self.anonymization_enabled = True
        self.user_identification_enabled = False  # Disabled by default for privacy
        
        self.logger.info("User analytics initialized", 
                        storage_path=str(self.storage_path),
                        session_timeout=session_timeout,
                        privacy_mode="strict")
    
    async def create_session(self, client_info: Optional[Dict[str, Any]] = None) -> str:
        """Create a new user session."""
        session = UserSession(
            session_id=str(uuid.uuid4()),
            client_type=client_info.get("type") if client_info else None,
            client_version=client_info.get("version") if client_info else None
        )
        
        # Generate anonymized user hash if identification is enabled
        if self.user_identification_enabled and client_info:
            user_identifier = client_info.get("user_id") or client_info.get("client_id")
            if user_identifier:
                session.user_hash = hashlib.sha256(
                    f"{user_identifier}_salt_ice_locator".encode()
                ).hexdigest()[:16]
        
        self.active_sessions[session.session_id] = session
        
        # Cleanup old sessions if needed
        await self._cleanup_old_sessions()
        
        self.logger.info("New session created", 
                        session_id=session.session_id,
                        client_type=session.client_type)
        
        # Track in MCPcat if available
        if self.mcpcat_client:
            await self.mcpcat_client.track_event("session_created", {
                "session_id": session.session_id,
                "client_type": session.client_type,
                "timestamp": session.start_time.isoformat()
            })
        
        return session.session_id
    
    async def track_tool_call(self, session_id: str, tool_name: str, 
                             arguments: Dict[str, Any], 
                             result: Optional[Dict[str, Any]] = None,
                             error: Optional[str] = None,
                             duration_ms: Optional[int] = None):
        """Track a tool call within a session."""
        session = self.active_sessions.get(session_id)
        if not session:
            # Create session if it doesn't exist
            session_id = await self.create_session()
            session = self.active_sessions[session_id]
        
        # Add tool call to session
        session.add_tool_call(tool_name, arguments, result, error)
        
        # Update last tool call with duration
        if duration_ms and session.tool_calls:
            session.tool_calls[-1]["duration_ms"] = duration_ms
        
        # Analyze behavior patterns
        if self.enable_behavior_analysis:
            await self._analyze_behavior_patterns(session)
        
        # Track in MCPcat if available
        if self.mcpcat_client:
            await self.mcpcat_client.track_event("tool_call", {
                "session_id": session_id,
                "tool_name": tool_name,
                "success": error is None,
                "duration_ms": duration_ms,
                "timestamp": datetime.now().isoformat()
            })
        
        self.logger.debug("Tool call tracked", 
                         session_id=session_id,
                         tool_name=tool_name,
                         success=error is None)
    
    async def end_session(self, session_id: str):
        """End a user session and persist data."""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        session.is_active = False
        session.update_activity()
        
        # Persist session data
        await self._persist_session(session)
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        self.logger.info("Session ended", 
                        session_id=session_id,
                        duration=str(session.duration),
                        tool_calls=session.tool_call_count)
        
        # Track in MCPcat if available
        if self.mcpcat_client:
            await self.mcpcat_client.track_event("session_ended", {
                "session_id": session_id,
                "duration_seconds": int(session.duration.total_seconds()),
                "tool_calls": session.tool_call_count,
                "timestamp": session.last_activity.isoformat()
            })
    
    async def get_session_analytics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get analytics data for a specific session."""
        session = self.active_sessions.get(session_id)
        if not session:
            # Try to load from storage
            session = await self._load_session(session_id)
        
        if not session:
            return None
        
        return {
            "session_id": session.session_id,
            "duration": str(session.duration),
            "tool_calls": session.tool_call_count,
            "search_patterns": session.search_patterns,
            "language_preference": session.language_preference,
            "client_type": session.client_type,
            "is_active": session.is_active,
            "start_time": session.start_time.isoformat(),
            "last_activity": session.last_activity.isoformat()
        }
    
    async def get_behavior_patterns(self, pattern_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get detected behavior patterns."""
        patterns = []
        
        for pattern in self.behavior_patterns.values():
            if pattern_type is None or pattern.pattern_type == pattern_type:
                patterns.append(pattern.to_dict())
        
        return sorted(patterns, key=lambda x: x["confidence"], reverse=True)
    
    async def generate_analytics_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate comprehensive analytics report."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Load recent sessions
        recent_sessions = await self._load_recent_sessions(cutoff_date)
        all_sessions = list(self.active_sessions.values()) + recent_sessions
        
        # Calculate metrics
        total_sessions = len(all_sessions)
        total_tool_calls = sum(session.tool_call_count for session in all_sessions)
        avg_session_duration = sum(
            (session.duration.total_seconds() for session in all_sessions), 0
        ) / max(total_sessions, 1)
        
        # Tool usage statistics
        tool_usage = {}
        search_patterns = {}
        language_usage = {}
        
        for session in all_sessions:
            # Language usage
            lang = session.language_preference
            language_usage[lang] = language_usage.get(lang, 0) + 1
            
            # Search patterns
            for pattern in session.search_patterns:
                search_patterns[pattern] = search_patterns.get(pattern, 0) + 1
            
            # Tool usage
            for tool_call in session.tool_calls:
                tool_name = tool_call["tool_name"]
                tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
        
        return {
            "report_period_days": days,
            "generated_at": datetime.now().isoformat(),
            "total_sessions": total_sessions,
            "total_tool_calls": total_tool_calls,
            "average_session_duration_seconds": int(avg_session_duration),
            "tool_usage": dict(sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)),
            "search_patterns": dict(sorted(search_patterns.items(), key=lambda x: x[1], reverse=True)),
            "language_usage": dict(sorted(language_usage.items(), key=lambda x: x[1], reverse=True)),
            "behavior_patterns": await self.get_behavior_patterns()
        }
    
    async def _analyze_behavior_patterns(self, session: UserSession):
        """Analyze session for behavior patterns."""
        if not self.enable_pattern_detection:
            return
        
        # Pattern: High frequency search
        if len(session.tool_calls) > 10:
            pattern_id = f"high_frequency_{session.session_id}"
            if pattern_id not in self.behavior_patterns:
                self.behavior_patterns[pattern_id] = BehaviorPattern(
                    pattern_id=pattern_id,
                    pattern_type="high_frequency_usage",
                    description="User performing high frequency searches",
                    confidence=0.8,
                    occurrences=1,
                    first_seen=session.start_time,
                    last_seen=session.last_activity,
                    metadata={"session_id": session.session_id}
                )
        
        # Pattern: Long session duration
        if session.duration.total_seconds() > 1800:  # 30 minutes
            pattern_id = f"long_session_{session.session_id}"
            if pattern_id not in self.behavior_patterns:
                self.behavior_patterns[pattern_id] = BehaviorPattern(
                    pattern_id=pattern_id,
                    pattern_type="long_session",
                    description="Extended session duration indicating complex search needs",
                    confidence=0.7,
                    occurrences=1,
                    first_seen=session.start_time,
                    last_seen=session.last_activity,
                    metadata={"session_id": session.session_id, "duration_seconds": int(session.duration.total_seconds())}
                )
        
        # Pattern: Repeated search patterns
        pattern_counts = {}
        for pattern in session.search_patterns:
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        for pattern, count in pattern_counts.items():
            if count > 3:
                pattern_id = f"repeated_pattern_{pattern}_{session.session_id}"
                if pattern_id not in self.behavior_patterns:
                    self.behavior_patterns[pattern_id] = BehaviorPattern(
                        pattern_id=pattern_id,
                        pattern_type="repeated_search_pattern",
                        description=f"Repeated use of {pattern} search pattern",
                        confidence=0.6,
                        occurrences=count,
                        first_seen=session.start_time,
                        last_seen=session.last_activity,
                        metadata={"session_id": session.session_id, "pattern": pattern}
                    )
    
    async def _cleanup_old_sessions(self):
        """Remove old inactive sessions from memory."""
        cutoff_time = datetime.now() - timedelta(seconds=self.session_timeout)
        sessions_to_remove = []
        
        for session_id, session in self.active_sessions.items():
            if session.last_activity < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            await self.end_session(session_id)
        
        # Limit memory usage
        if len(self.active_sessions) > self.max_sessions_in_memory:
            # Remove oldest sessions
            sorted_sessions = sorted(
                self.active_sessions.items(),
                key=lambda x: x[1].last_activity
            )
            
            for session_id, _ in sorted_sessions[:len(self.active_sessions) - self.max_sessions_in_memory]:
                await self.end_session(session_id)
    
    async def _persist_session(self, session: UserSession):
        """Persist session data to storage."""
        try:
            session_file = self.storage_path / f"session_{session.session_id}.json"
            with open(session_file, 'w') as f:
                json.dump(session.to_dict(), f, indent=2)
            
            self.logger.debug("Session persisted", session_id=session.session_id)
        except Exception as e:
            self.logger.error("Failed to persist session", 
                            session_id=session.session_id, error=str(e))
    
    async def _load_session(self, session_id: str) -> Optional[UserSession]:
        """Load session data from storage."""
        try:
            session_file = self.storage_path / f"session_{session_id}.json"
            if not session_file.exists():
                return None
            
            with open(session_file, 'r') as f:
                data = json.load(f)
            
            # Convert back to UserSession object
            session = UserSession(session_id=data["session_id"])
            session.user_hash = data.get("user_hash")
            session.start_time = datetime.fromisoformat(data["start_time"])
            session.last_activity = datetime.fromisoformat(data["last_activity"])
            session.tool_calls = data.get("tool_calls", [])
            session.search_patterns = data.get("search_patterns", [])
            session.language_preference = data.get("language_preference", "en")
            session.client_type = data.get("client_type")
            session.client_version = data.get("client_version")
            session.geographic_region = data.get("geographic_region")
            session.is_active = data.get("is_active", False)
            
            return session
            
        except Exception as e:
            self.logger.error("Failed to load session", 
                            session_id=session_id, error=str(e))
            return None
    
    async def _load_recent_sessions(self, cutoff_date: datetime) -> List[UserSession]:
        """Load recent sessions from storage."""
        sessions = []
        
        try:
            for session_file in self.storage_path.glob("session_*.json"):
                # Check file modification time
                if datetime.fromtimestamp(session_file.stat().st_mtime) < cutoff_date:
                    continue
                
                session_id = session_file.stem.replace("session_", "")
                session = await self._load_session(session_id)
                if session and session.start_time >= cutoff_date:
                    sessions.append(session)
                    
        except Exception as e:
            self.logger.error("Failed to load recent sessions", error=str(e))
        
        return sessions
    
    async def cleanup_old_data(self):
        """Clean up old analytics data based on retention policy."""
        cutoff_date = datetime.now() - timedelta(days=self.data_retention_days)
        
        try:
            for session_file in self.storage_path.glob("session_*.json"):
                if datetime.fromtimestamp(session_file.stat().st_mtime) < cutoff_date:
                    session_file.unlink()
                    self.logger.debug("Removed old session file", file=session_file.name)
        
        except Exception as e:
            self.logger.error("Failed to cleanup old data", error=str(e))