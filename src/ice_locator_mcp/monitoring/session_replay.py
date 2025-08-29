"""
Session Replay Module for ICE Locator MCP Server.

Provides session recording and replay capabilities for debugging, user experience analysis,
and system optimization while maintaining strict privacy controls.
"""

import asyncio
import json
import gzip
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum
import uuid

import structlog


class EventType(Enum):
    """Types of events that can be recorded in session replay."""
    
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    TOOL_CALL = "tool_call"
    TOOL_RESPONSE = "tool_response"
    ERROR = "error"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    RATE_LIMIT = "rate_limit"
    PROXY_ROTATION = "proxy_rotation"
    CAPTCHA_ENCOUNTERED = "captcha_encountered"
    FORM_SUBMISSION = "form_submission"
    HTTP_REQUEST = "http_request"
    HTTP_RESPONSE = "http_response"
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"


@dataclass
class ReplayEvent:
    """Represents a single event in a session replay."""
    
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    event_type: EventType = EventType.USER_ACTION
    session_id: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[int] = None
    privacy_level: str = "standard"  # standard, strict, minimal
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.privacy_level == "strict":
            self.data = self._redact_sensitive_data(self.data)
    
    def _redact_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive information based on privacy level."""
        sensitive_fields = {
            "first_name", "last_name", "middle_name", "alien_number",
            "date_of_birth", "social_security_number", "passport_number",
            "phone_number", "email", "address"
        }
        
        redacted = {}
        for key, value in data.items():
            if key in sensitive_fields:
                if isinstance(value, str) and value:
                    redacted[key] = f"[REDACTED_{len(value)}_CHARS]"
                else:
                    redacted[key] = "[REDACTED]"
            elif isinstance(value, dict):
                redacted[key] = self._redact_sensitive_data(value)
            elif isinstance(value, list):
                redacted[key] = [
                    self._redact_sensitive_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                redacted[key] = value
        
        return redacted
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["event_type"] = self.event_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReplayEvent":
        """Create ReplayEvent from dictionary."""
        event = cls()
        event.event_id = data.get("event_id", str(uuid.uuid4()))
        event.timestamp = datetime.fromisoformat(data["timestamp"])
        event.event_type = EventType(data["event_type"])
        event.session_id = data.get("session_id", "")
        event.data = data.get("data", {})
        event.metadata = data.get("metadata", {})
        event.duration_ms = data.get("duration_ms")
        event.privacy_level = data.get("privacy_level", "standard")
        return event


@dataclass
class SessionReplay:
    """Represents a complete session replay."""
    
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    events: List[ReplayEvent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Calculate total session duration."""
        if self.end_time:
            return self.end_time - self.start_time
        return None
    
    @property
    def event_count(self) -> int:
        """Get total number of events."""
        return len(self.events)
    
    def add_event(self, event: ReplayEvent):
        """Add an event to the replay."""
        event.session_id = self.session_id
        self.events.append(event)
    
    def get_events_by_type(self, event_type: EventType) -> List[ReplayEvent]:
        """Get all events of a specific type."""
        return [event for event in self.events if event.event_type == event_type]
    
    def get_events_in_timerange(self, start: datetime, end: datetime) -> List[ReplayEvent]:
        """Get events within a specific time range."""
        return [
            event for event in self.events
            if start <= event.timestamp <= end
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert replay to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "events": [event.to_dict() for event in self.events],
            "metadata": self.metadata,
            "duration_seconds": int(self.duration.total_seconds()) if self.duration else None,
            "event_count": self.event_count
        }


class SessionRecorder:
    """Records user sessions for replay and analysis."""
    
    def __init__(self, storage_path: Optional[Path] = None,
                 compression_enabled: bool = True,
                 privacy_level: str = "standard"):
        """Initialize session recorder."""
        self.logger = structlog.get_logger(__name__)
        
        # Storage configuration
        self.storage_path = storage_path or Path.home() / ".cache" / "ice-locator-mcp" / "replays"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Recording configuration
        self.compression_enabled = compression_enabled
        self.privacy_level = privacy_level  # standard, strict, minimal
        self.max_events_per_session = 10000
        self.auto_flush_interval = 300  # 5 minutes
        
        # Active sessions
        self.active_replays: Dict[str, SessionReplay] = {}
        
        # Privacy controls
        self.record_http_requests = privacy_level != "strict"
        self.record_response_data = privacy_level == "minimal"
        self.record_user_inputs = privacy_level != "strict"
        
        self.logger.info("Session recorder initialized",
                        storage_path=str(self.storage_path),
                        privacy_level=privacy_level,
                        compression=compression_enabled)
    
    async def start_recording(self, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Start recording a session."""
        if session_id in self.active_replays:
            self.logger.warning("Session already being recorded", session_id=session_id)
            return False
        
        replay = SessionReplay(
            session_id=session_id,
            start_time=datetime.now(),
            metadata=metadata or {}
        )
        
        # Add session start event
        start_event = ReplayEvent(
            event_type=EventType.SESSION_START,
            session_id=session_id,
            data={"metadata": metadata or {}},
            privacy_level=self.privacy_level
        )
        replay.add_event(start_event)
        
        self.active_replays[session_id] = replay
        
        self.logger.info("Started recording session", session_id=session_id)
        return True
    
    async def stop_recording(self, session_id: str) -> bool:
        """Stop recording a session and save to disk."""
        replay = self.active_replays.get(session_id)
        if not replay:
            self.logger.warning("Session not found for recording", session_id=session_id)
            return False
        
        replay.end_time = datetime.now()
        
        # Add session end event
        end_event = ReplayEvent(
            event_type=EventType.SESSION_END,
            session_id=session_id,
            data={
                "duration_seconds": int(replay.duration.total_seconds()) if replay.duration else 0,
                "event_count": replay.event_count
            },
            privacy_level=self.privacy_level
        )
        replay.add_event(end_event)
        
        # Save to disk
        await self._save_replay(replay)
        
        # Remove from active sessions
        del self.active_replays[session_id]
        
        self.logger.info("Stopped recording session",
                        session_id=session_id,
                        duration=str(replay.duration),
                        events=replay.event_count)
        return True
    
    async def record_event(self, session_id: str, event_type: EventType,
                          data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None,
                          duration_ms: Optional[int] = None):
        """Record an event in the session replay."""
        replay = self.active_replays.get(session_id)
        if not replay:
            # Auto-create session if it doesn't exist
            await self.start_recording(session_id)
            replay = self.active_replays.get(session_id)
        
        if not replay:
            self.logger.error("Failed to create replay session", session_id=session_id)
            return
        
        # Create event
        event = ReplayEvent(
            event_type=event_type,
            session_id=session_id,
            data=data,
            metadata=metadata or {},
            duration_ms=duration_ms,
            privacy_level=self.privacy_level
        )
        
        replay.add_event(event)
        
        # Auto-flush if session has too many events
        if len(replay.events) >= self.max_events_per_session:
            await self._partial_flush(replay)
        
        self.logger.debug("Recorded event",
                         session_id=session_id,
                         event_type=event_type.value,
                         event_count=len(replay.events))
    
    async def record_tool_call(self, session_id: str, tool_name: str,
                              arguments: Dict[str, Any], result: Optional[Dict[str, Any]] = None,
                              error: Optional[str] = None, duration_ms: Optional[int] = None):
        """Record a tool call event."""
        # Tool call start
        await self.record_event(
            session_id=session_id,
            event_type=EventType.TOOL_CALL,
            data={
                "tool_name": tool_name,
                "arguments": arguments,
                "timestamp": datetime.now().isoformat()
            },
            metadata={"call_id": str(uuid.uuid4())},
            duration_ms=duration_ms
        )
        
        # Tool response
        if result is not None or error is not None:
            response_data = {
                "tool_name": tool_name,
                "success": error is None,
                "timestamp": datetime.now().isoformat()
            }
            
            if self.record_response_data:
                if result:
                    response_data["result"] = result
                if error:
                    response_data["error"] = error
            
            await self.record_event(
                session_id=session_id,
                event_type=EventType.TOOL_RESPONSE,
                data=response_data,
                duration_ms=duration_ms
            )
    
    async def record_http_request(self, session_id: str, method: str, url: str,
                                 headers: Optional[Dict[str, str]] = None,
                                 data: Optional[Dict[str, Any]] = None):
        """Record an HTTP request."""
        if not self.record_http_requests:
            return
        
        request_data = {
            "method": method,
            "url": url,
            "timestamp": datetime.now().isoformat()
        }
        
        if headers and self.privacy_level == "minimal":
            # Only record non-sensitive headers
            safe_headers = {k: v for k, v in headers.items() 
                          if k.lower() not in ["authorization", "cookie", "x-api-key"]}
            request_data["headers"] = safe_headers
        
        if data and self.record_user_inputs:
            request_data["data"] = data
        
        await self.record_event(
            session_id=session_id,
            event_type=EventType.HTTP_REQUEST,
            data=request_data
        )
    
    async def record_http_response(self, session_id: str, status_code: int,
                                  headers: Optional[Dict[str, str]] = None,
                                  response_time_ms: Optional[int] = None):
        """Record an HTTP response."""
        if not self.record_http_requests:
            return
        
        response_data = {
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        }
        
        if headers and self.privacy_level == "minimal":
            # Only record non-sensitive headers
            safe_headers = {k: v for k, v in headers.items()
                          if k.lower() not in ["set-cookie", "x-session-token"]}
            response_data["headers"] = safe_headers
        
        await self.record_event(
            session_id=session_id,
            event_type=EventType.HTTP_RESPONSE,
            data=response_data,
            duration_ms=response_time_ms
        )
    
    async def record_error(self, session_id: str, error_type: str, error_message: str,
                          stack_trace: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        """Record an error event."""
        error_data = {
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat()
        }
        
        if stack_trace and self.privacy_level == "minimal":
            error_data["stack_trace"] = stack_trace
        
        if context:
            error_data["context"] = context
        
        await self.record_event(
            session_id=session_id,
            event_type=EventType.ERROR,
            data=error_data
        )
    
    async def load_replay(self, session_id: str) -> Optional[SessionReplay]:
        """Load a session replay from disk."""
        replay_file = self.storage_path / f"replay_{session_id}.json"
        if self.compression_enabled:
            replay_file = self.storage_path / f"replay_{session_id}.json.gz"
        
        if not replay_file.exists():
            return None
        
        try:
            if self.compression_enabled:
                with gzip.open(replay_file, 'rt') as f:
                    data = json.load(f)
            else:
                with open(replay_file, 'r') as f:
                    data = json.load(f)
            
            # Reconstruct replay object
            replay = SessionReplay(
                session_id=data["session_id"],
                start_time=datetime.fromisoformat(data["start_time"]),
                end_time=datetime.fromisoformat(data["end_time"]) if data["end_time"] else None,
                metadata=data.get("metadata", {})
            )
            
            # Reconstruct events
            for event_data in data.get("events", []):
                event = ReplayEvent.from_dict(event_data)
                replay.events.append(event)
            
            return replay
            
        except Exception as e:
            self.logger.error("Failed to load replay",
                            session_id=session_id, error=str(e))
            return None
    
    async def get_replay_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of a session replay without loading full data."""
        replay = await self.load_replay(session_id)
        if not replay:
            return None
        
        # Analyze events
        event_types = {}
        tool_calls = {}
        errors = []
        
        for event in replay.events:
            event_type = event.event_type.value
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
            if event.event_type == EventType.TOOL_CALL:
                tool_name = event.data.get("tool_name", "unknown")
                tool_calls[tool_name] = tool_calls.get(tool_name, 0) + 1
            
            elif event.event_type == EventType.ERROR:
                errors.append({
                    "timestamp": event.timestamp.isoformat(),
                    "error_type": event.data.get("error_type"),
                    "error_message": event.data.get("error_message")
                })
        
        return {
            "session_id": session_id,
            "start_time": replay.start_time.isoformat(),
            "end_time": replay.end_time.isoformat() if replay.end_time else None,
            "duration_seconds": int(replay.duration.total_seconds()) if replay.duration else None,
            "total_events": replay.event_count,
            "event_types": event_types,
            "tool_calls": tool_calls,
            "errors": errors,
            "metadata": replay.metadata
        }
    
    async def list_available_replays(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List available session replays."""
        replays = []
        
        pattern = "replay_*.json.gz" if self.compression_enabled else "replay_*.json"
        for replay_file in sorted(self.storage_path.glob(pattern), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]:
            session_id = replay_file.stem.replace("replay_", "").replace(".json", "")
            
            try:
                summary = await self.get_replay_summary(session_id)
                if summary:
                    replays.append(summary)
            except Exception as e:
                self.logger.error("Failed to get replay summary",
                                session_id=session_id, error=str(e))
        
        return replays
    
    async def _save_replay(self, replay: SessionReplay):
        """Save a session replay to disk."""
        try:
            replay_file = self.storage_path / f"replay_{replay.session_id}.json"
            
            if self.compression_enabled:
                replay_file = self.storage_path / f"replay_{replay.session_id}.json.gz"
                with gzip.open(replay_file, 'wt') as f:
                    json.dump(replay.to_dict(), f, indent=2 if not self.compression_enabled else None)
            else:
                with open(replay_file, 'w') as f:
                    json.dump(replay.to_dict(), f, indent=2)
            
            self.logger.debug("Saved replay to disk", 
                            session_id=replay.session_id,
                            file_size=replay_file.stat().st_size)
            
        except Exception as e:
            self.logger.error("Failed to save replay",
                            session_id=replay.session_id, error=str(e))
    
    async def _partial_flush(self, replay: SessionReplay):
        """Partially flush events to disk when session gets too large."""
        try:
            # Save current state
            await self._save_replay(replay)
            
            # Keep only recent events in memory
            recent_events = replay.events[-1000:]  # Keep last 1000 events
            replay.events = recent_events
            
            self.logger.debug("Performed partial flush", 
                            session_id=replay.session_id,
                            events_kept=len(recent_events))
            
        except Exception as e:
            self.logger.error("Failed to perform partial flush",
                            session_id=replay.session_id, error=str(e))
    
    async def cleanup_old_replays(self, days: int = 30):
        """Clean up old replay files."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        try:
            pattern = "replay_*.json*"
            for replay_file in self.storage_path.glob(pattern):
                if datetime.fromtimestamp(replay_file.stat().st_mtime) < cutoff_date:
                    replay_file.unlink()
                    self.logger.debug("Removed old replay file", file=replay_file.name)
        
        except Exception as e:
            self.logger.error("Failed to cleanup old replays", error=str(e))