"""
Session Persistence and Management System for ICE Locator MCP Server.

This module provides comprehensive session persistence and management capabilities
to maintain realistic session states across multiple requests, mimicking real user behavior.
"""

import asyncio
import json
import time
import os
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from pathlib import Path
import structlog
from datetime import datetime, timedelta

from .browser_simulator import BrowserSession
from .cookie_manager import CookieManager, CookieProfile


@dataclass
class PersistentSession:
    """Represents a persistent browser session with all relevant state information."""
    session_id: str
    profile_name: str
    user_agent: str
    start_time: float
    last_activity: float
    pages_visited: int
    actions_performed: List[str]
    cookies: List[Dict[str, Any]]  # This will now store CookieProfile data
    local_storage: Dict[str, str]
    session_storage: Dict[str, str]
    viewport_width: int
    viewport_height: int
    language: str
    timezone: str
    
    @classmethod
    def from_browser_session(cls, session_id: str, browser_session: BrowserSession, cookie_manager: CookieManager = None) -> 'PersistentSession':
        """Create a PersistentSession from a BrowserSession."""
        # Extract cookies and storage data
        cookies = []
        local_storage = {}
        session_storage = {}
        
        # If we have a cookie manager and browser context, extract real cookies
        if cookie_manager and hasattr(browser_session, 'context') and browser_session.context:
            # Extract cookies from the browser context
            cookie_profiles = asyncio.run(cookie_manager.extract_cookies_from_context(browser_session.context))
            # Convert to dictionary format for serialization
            cookies = [cookie.to_dict() for cookie in cookie_profiles]
        
        return cls(
            session_id=session_id,
            profile_name=browser_session.profile.name,
            user_agent=browser_session.profile.user_agent,
            start_time=browser_session.start_time,
            last_activity=browser_session.last_activity,
            pages_visited=browser_session.pages_visited,
            actions_performed=browser_session.actions_performed.copy(),
            cookies=cookies,
            local_storage=local_storage,
            session_storage=session_storage,
            viewport_width=1920,  # Default values, would be extracted from browser context
            viewport_height=1080,
            language="en-US",
            timezone="America/New_York"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersistentSession':
        """Create from dictionary."""
        return cls(**data)


class SessionManager:
    """Manages persistent browser sessions across multiple requests."""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.logger = structlog.get_logger(__name__)
        self.storage_path = Path(storage_path) if storage_path else Path.home() / ".cache" / "ice-locator-mcp" / "sessions"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.session_timeout = 1800  # 30 minutes
        self.max_sessions = 1000
        
        # In-memory cache of active sessions
        self.active_sessions: Dict[str, PersistentSession] = {}
        
        # Initialize cookie manager
        self.cookie_manager = CookieManager()  # Add this line
        
        self.logger.info("Session manager initialized", storage_path=str(self.storage_path))
    
    async def save_session(self, session_id: str, browser_session: BrowserSession) -> bool:
        """Save a browser session to persistent storage."""
        try:
            # Create persistent session from browser session with real cookie data
            persistent_session = PersistentSession.from_browser_session(
                session_id, browser_session, self.cookie_manager
            )
            
            # Update last activity
            persistent_session.last_activity = time.time()
            
            # Save to in-memory cache
            self.active_sessions[session_id] = persistent_session
            
            # Save to disk
            session_file = self.storage_path / f"session_{session_id}.json"
            with open(session_file, 'w') as f:
                json.dump(persistent_session.to_dict(), f, indent=2)
            
            self.logger.debug("Session saved", session_id=session_id)
            return True
            
        except Exception as e:
            self.logger.error("Failed to save session", session_id=session_id, error=str(e))
            return False
    
    async def restore_session(self, session_id: str, browser_session: BrowserSession) -> bool:
        """Restore a browser session with persistent state."""
        try:
            persistent_session = await self.load_session(session_id)
            if not persistent_session:
                return False
            
            # Restore session state to browser session
            # 1. Set cookies in the browser context
            if persistent_session.cookies and browser_session.context:
                # Convert dictionary cookies back to CookieProfile objects
                cookie_profiles = [CookieProfile.from_dict(cookie_data) for cookie_data in persistent_session.cookies]
                # Prepare cookies for session (validation, rotation, etc.)
                prepared_cookies = await self.cookie_manager.prepare_cookies_for_session(cookie_profiles)
                # Set cookies in browser context
                await self.cookie_manager.set_cookies_in_context(browser_session.context, prepared_cookies)
            
            # 2. Restore local storage (not implemented yet)
            # 3. Restore session storage (not implemented yet)
            # 4. Set viewport size
            # 5. Set language and timezone
            
            # Update browser session metrics
            browser_session.start_time = persistent_session.start_time
            browser_session.last_activity = persistent_session.last_activity
            browser_session.pages_visited = persistent_session.pages_visited
            browser_session.actions_performed = persistent_session.actions_performed.copy()
            
            self.logger.debug("Session restored", session_id=session_id)
            return True
            
        except Exception as e:
            self.logger.error("Failed to restore session", session_id=session_id, error=str(e))
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session from persistent storage."""
        try:
            # Remove from in-memory cache
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            # Remove from disk
            session_file = self.storage_path / f"session_{session_id}.json"
            if session_file.exists():
                session_file.unlink()
            
            self.logger.debug("Session deleted", session_id=session_id)
            return True
            
        except Exception as e:
            self.logger.error("Failed to delete session", session_id=session_id, error=str(e))
            return False
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions from storage."""
        try:
            current_time = time.time()
            deleted_count = 0
            
            # Clean up in-memory cache
            expired_sessions = [
                session_id for session_id, session in self.active_sessions.items()
                if current_time - session.last_activity > self.session_timeout
            ]
            
            for session_id in expired_sessions:
                del self.active_sessions[session_id]
                deleted_count += 1
            
            # Clean up disk storage
            for session_file in self.storage_path.glob("session_*.json"):
                try:
                    file_age = current_time - session_file.stat().st_mtime
                    if file_age > self.session_timeout:
                        session_file.unlink()
                        deleted_count += 1
                except Exception:
                    # File might have been deleted by another process
                    pass
            
            self.logger.debug("Cleaned up expired sessions", deleted_count=deleted_count)
            return deleted_count
            
        except Exception as e:
            self.logger.error("Failed to cleanup expired sessions", error=str(e))
            return 0
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a session without loading it fully."""
        try:
            # Check in-memory cache first
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                return {
                    "session_id": session.session_id,
                    "profile_name": session.profile_name,
                    "start_time": session.start_time,
                    "last_activity": session.last_activity,
                    "pages_visited": session.pages_visited,
                    "actions_count": len(session.actions_performed),
                    "is_active": time.time() - session.last_activity < self.session_timeout
                }
            
            # Check disk storage
            session_file = self.storage_path / f"session_{session_id}.json"
            if not session_file.exists():
                return None
            
            # Read just the basic info from file
            with open(session_file, 'r') as f:
                data = json.load(f)
            
            return {
                "session_id": data["session_id"],
                "profile_name": data["profile_name"],
                "start_time": data["start_time"],
                "last_activity": data["last_activity"],
                "pages_visited": data["pages_visited"],
                "actions_count": len(data["actions_performed"]),
                "is_active": time.time() - data["last_activity"] < self.session_timeout
            }
            
        except Exception as e:
            self.logger.error("Failed to get session info", session_id=session_id, error=str(e))
            return None
    
    async def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions with basic information."""
        try:
            sessions = {}
            
            # Add active sessions from memory
            for session_id, session in self.active_sessions.items():
                sessions[session_id] = {
                    "session_id": session.session_id,
                    "profile_name": session.profile_name,
                    "start_time": session.start_time,
                    "last_activity": session.last_activity,
                    "pages_visited": session.pages_visited,
                    "actions_count": len(session.actions_performed),
                    "is_active": time.time() - session.last_activity < self.session_timeout,
                    "storage": "memory"
                }
            
            # Add sessions from disk (not already in memory)
            for session_file in self.storage_path.glob("session_*.json"):
                try:
                    session_id = session_file.stem.replace("session_", "")
                    if session_id not in sessions:  # Only add if not already in memory
                        with open(session_file, 'r') as f:
                            data = json.load(f)
                        
                        sessions[session_id] = {
                            "session_id": data["session_id"],
                            "profile_name": data["profile_name"],
                            "start_time": data["start_time"],
                            "last_activity": data["last_activity"],
                            "pages_visited": data["pages_visited"],
                            "actions_count": len(data["actions_performed"]),
                            "is_active": time.time() - data["last_activity"] < self.session_timeout,
                            "storage": "disk"
                        }
                except Exception:
                    # Skip corrupted files
                    pass
            
            # Convert to list and sort by last activity (most recent first)
            sessions_list = list(sessions.values())
            sessions_list.sort(key=lambda x: x["last_activity"], reverse=True)
            
            return sessions_list
            
        except Exception as e:
            self.logger.error("Failed to list sessions", error=str(e))
            return []
