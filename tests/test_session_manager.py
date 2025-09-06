#!/usr/bin/env python3
"""
Tests for the SessionManager class.

This module contains tests to verify the functionality of the SessionManager,
including session saving, loading, restoring, and cleanup operations.
"""

import asyncio
import json
import os
import tempfile
import time
from pathlib import Path
import pytest
from unittest.mock import Mock, AsyncMock

# Add the src directory to the path so we can import the modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ice_locator_mcp.anti_detection.session_manager import SessionManager, PersistentSession
from src.ice_locator_mcp.anti_detection.browser_simulator import BrowserSession
from src.ice_locator_mcp.anti_detection.request_obfuscator import BrowserProfile


class TestSessionManager:
    """Test cases for the SessionManager class."""
    
    @pytest.fixture
    def temp_storage_path(self):
        """Create a temporary storage path for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def session_manager(self, temp_storage_path):
        """Create a SessionManager instance for testing."""
        return SessionManager(storage_path=str(temp_storage_path))
    
    @pytest.fixture
    def mock_browser_session(self):
        """Create a mock BrowserSession for testing."""
        profile = BrowserProfile(
            name="test_profile",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            platform="Win32",
            vendor="Google Inc.",
            languages=["en-US", "en"],
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        
        session = Mock(spec=BrowserSession)
        session.profile = profile
        session.start_time = time.time()
        session.last_activity = time.time()
        session.pages_visited = 5
        session.actions_performed = ["navigate_to:example.com", "click:button1"]
        
        return session
    
    @pytest.mark.asyncio
    async def test_save_session(self, session_manager, mock_browser_session):
        """Test saving a session to persistent storage."""
        session_id = "test_session_1"
        
        # Save the session
        result = await session_manager.save_session(session_id, mock_browser_session)
        
        # Verify the operation was successful
        assert result is True
        
        # Verify the session was saved to disk
        session_file = session_manager.storage_path / f"session_{session_id}.json"
        assert session_file.exists()
        
        # Verify the session was cached in memory
        assert session_id in session_manager.active_sessions
    
    @pytest.mark.asyncio
    async def test_load_session_from_memory(self, session_manager, mock_browser_session):
        """Test loading a session from memory cache."""
        session_id = "test_session_2"
        
        # First save the session
        await session_manager.save_session(session_id, mock_browser_session)
        
        # Load the session (should come from memory)
        loaded_session = await session_manager.load_session(session_id)
        
        # Verify the session was loaded correctly
        assert loaded_session is not None
        assert loaded_session.session_id == session_id
        assert loaded_session.profile_name == mock_browser_session.profile.name
        assert loaded_session.pages_visited == mock_browser_session.pages_visited
    
    @pytest.mark.asyncio
    async def test_load_session_from_disk(self, session_manager, mock_browser_session):
        """Test loading a session from disk storage."""
        session_id = "test_session_3"
        
        # Save the session
        await session_manager.save_session(session_id, mock_browser_session)
        
        # Remove from memory cache to force disk load
        del session_manager.active_sessions[session_id]
        
        # Load the session (should come from disk)
        loaded_session = await session_manager.load_session(session_id)
        
        # Verify the session was loaded correctly
        assert loaded_session is not None
        assert loaded_session.session_id == session_id
        assert loaded_session.profile_name == mock_browser_session.profile.name
    
    @pytest.mark.asyncio
    async def test_load_nonexistent_session(self, session_manager):
        """Test loading a session that doesn't exist."""
        session_id = "nonexistent_session"
        
        # Try to load a session that doesn't exist
        loaded_session = await session_manager.load_session(session_id)
        
        # Verify None is returned
        assert loaded_session is None
    
    @pytest.mark.asyncio
    async def test_restore_session(self, session_manager, mock_browser_session):
        """Test restoring a session to a browser session."""
        session_id = "test_session_4"
        
        # Save the session first
        await session_manager.save_session(session_id, mock_browser_session)
        
        # Create a new browser session to restore to
        restore_session = Mock(spec=BrowserSession)
        restore_session.start_time = 0
        restore_session.last_activity = 0
        restore_session.pages_visited = 0
        restore_session.actions_performed = []
        
        # Restore the session
        result = await session_manager.restore_session(session_id, restore_session)
        
        # Verify the operation was successful
        assert result is True
        
        # Verify the browser session was updated (using approximate equality for timestamps)
        assert abs(restore_session.start_time - mock_browser_session.start_time) < 1.0
        assert abs(restore_session.last_activity - mock_browser_session.last_activity) < 1.0
        assert restore_session.pages_visited == mock_browser_session.pages_visited
        assert restore_session.actions_performed == mock_browser_session.actions_performed
    
    @pytest.mark.asyncio
    async def test_delete_session(self, session_manager, mock_browser_session):
        """Test deleting a session from storage."""
        session_id = "test_session_5"
        
        # Save the session first
        await session_manager.save_session(session_id, mock_browser_session)
        
        # Verify the session exists
        session_file = session_manager.storage_path / f"session_{session_id}.json"
        assert session_file.exists()
        assert session_id in session_manager.active_sessions
        
        # Delete the session
        result = await session_manager.delete_session(session_id)
        
        # Verify the operation was successful
        assert result is True
        
        # Verify the session was deleted
        assert not session_file.exists()
        assert session_id not in session_manager.active_sessions
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(self, session_manager, mock_browser_session):
        """Test cleaning up expired sessions."""
        # Save a normal session
        normal_session_id = "normal_session"
        await session_manager.save_session(normal_session_id, mock_browser_session)
        
        # Save an expired session (manipulate the file's mtime)
        expired_session_id = "expired_session"
        await session_manager.save_session(expired_session_id, mock_browser_session)
        
        # Manipulate the expired session file to make it appear old
        expired_file = session_manager.storage_path / f"session_{expired_session_id}.json"
        old_time = time.time() - session_manager.session_timeout - 100  # Make it older than timeout
        os.utime(expired_file, (old_time, old_time))
        
        # Also manipulate the in-memory session
        if expired_session_id in session_manager.active_sessions:
            session_manager.active_sessions[expired_session_id].last_activity = old_time
        
        # Clean up expired sessions
        deleted_count = await session_manager.cleanup_expired_sessions()
        
        # Verify at least one session was deleted
        assert deleted_count >= 1
        
        # Verify the normal session still exists
        assert normal_session_id in session_manager.active_sessions
        normal_file = session_manager.storage_path / f"session_{normal_session_id}.json"
        assert normal_file.exists()
        
        # Verify the expired session was deleted
        assert expired_session_id not in session_manager.active_sessions
        assert not expired_file.exists()
    
    @pytest.mark.asyncio
    async def test_get_session_info(self, session_manager, mock_browser_session):
        """Test getting session information."""
        session_id = "test_session_6"
        
        # Save the session
        await session_manager.save_session(session_id, mock_browser_session)
        
        # Get session info
        info = await session_manager.get_session_info(session_id)
        
        # Verify the info is correct
        assert info is not None
        assert info["session_id"] == session_id
        assert info["profile_name"] == mock_browser_session.profile.name
        assert info["pages_visited"] == mock_browser_session.pages_visited
        assert info["actions_count"] == len(mock_browser_session.actions_performed)
        assert info["is_active"] is True
    
    @pytest.mark.asyncio
    async def test_list_sessions(self, session_manager, mock_browser_session):
        """Test listing all sessions."""
        # Save multiple sessions
        session_ids = ["session_1", "session_2", "session_3"]
        for session_id in session_ids:
            await session_manager.save_session(session_id, mock_browser_session)
        
        # List all sessions
        sessions = await session_manager.list_sessions()
        
        # Verify we have at least the number of sessions we saved
        # (there might be duplicates between memory and disk, but we should have at least 3 unique session IDs)
        session_ids_in_list = list(set(s["session_id"] for s in sessions))
        assert len(session_ids_in_list) == 3
        
        # Verify all session IDs are present
        for session_id in session_ids:
            assert session_id in session_ids_in_list


if __name__ == "__main__":
    pytest.main([__file__])