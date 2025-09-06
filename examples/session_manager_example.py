#!/usr/bin/env python3
"""
Example demonstrating session persistence and management functionality.

This script shows how to use the SessionManager to save, load, and restore
browser sessions across multiple requests.
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ice_locator_mcp.anti_detection.session_manager import SessionManager
from src.ice_locator_mcp.anti_detection.request_obfuscator import BrowserProfile
from src.ice_locator_mcp.anti_detection.browser_simulator import BrowserSession


async def create_mock_browser_session(session_id: str):
    """Create a mock browser session for demonstration."""
    # Create a browser profile
    profile = BrowserProfile(
        name="Chrome on Windows",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        platform="Win32",
        vendor="Google Inc.",
        languages=["en-US", "en"],
        headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    
    # Create a mock browser session
    session = BrowserSession(
        session_id=session_id,
        browser=None,  # In a real implementation, this would be an actual browser instance
        context=None,  # In a real implementation, this would be an actual browser context
        page=None,     # In a real implementation, this would be an actual page
        profile=profile
    )
    
    # Simulate some activity
    session.pages_visited = 3
    session.actions_performed = [
        "navigate_to:https://example.com",
        "click:login_button",
        "fill_form:username_field",
        "fill_form:password_field",
        "click:submit_button"
    ]
    
    return session


async def main():
    """Demonstrate session manager functionality."""
    print("Session Manager Example")
    print("=" * 30)
    
    # Create a temporary directory for session storage
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)
        print(f"Using temporary storage path: {storage_path}")
        
        # Create session manager
        session_manager = SessionManager(storage_path=str(storage_path))
        
        # Create a browser session
        session_id = "example_session_1"
        browser_session = await create_mock_browser_session(session_id)
        
        print(f"\n1. Saving session '{session_id}'")
        result = await session_manager.save_session(session_id, browser_session)
        if result:
            print(f"  Successfully saved session '{session_id}'")
        else:
            print(f"  Failed to save session '{session_id}'")
        
        print("\n2. Loading session from memory")
        loaded_session = await session_manager.load_session(session_id)
        if loaded_session:
            print(f"  Loaded session: {loaded_session.session_id}")
            print(f"  Profile: {loaded_session.profile_name}")
            print(f"  Pages visited: {loaded_session.pages_visited}")
            print(f"  Actions performed: {len(loaded_session.actions_performed)}")
        else:
            print("  Failed to load session")
        
        print("\n3. Getting session info")
        session_info = await session_manager.get_session_info(session_id)
        if session_info:
            print(f"  Session ID: {session_info['session_id']}")
            print(f"  Profile: {session_info['profile_name']}")
            print(f"  Pages visited: {session_info['pages_visited']}")
            print(f"  Actions count: {session_info['actions_count']}")
            print(f"  Is active: {session_info['is_active']}")
        else:
            print("  Failed to get session info")
        
        print("\n4. Listing all sessions")
        sessions = await session_manager.list_sessions()
        print(f"  Found {len(sessions)} sessions:")
        for session in sessions:
            print(f"    - {session['session_id']} (Profile: {session['profile_name']}, "
                  f"Pages: {session['pages_visited']}, Active: {session['is_active']})")
        
        print("\n5. Creating another session")
        session_id_2 = "example_session_2"
        browser_session_2 = await create_mock_browser_session(session_id_2)
        browser_session_2.pages_visited = 5
        browser_session_2.actions_performed = [
            "navigate_to:https://example.com",
            "click:search_button",
            "fill_form:search_field",
            "click:search_submit",
            "click:result_link_1",
            "click:result_link_2"
        ]
        
        result = await session_manager.save_session(session_id_2, browser_session_2)
        if result:
            print(f"  Successfully saved session '{session_id_2}'")
        else:
            print(f"  Failed to save session '{session_id_2}'")
        
        print("\n6. Listing all sessions after adding second session")
        sessions = await session_manager.list_sessions()
        print(f"  Found {len(sessions)} sessions:")
        for session in sessions:
            print(f"    - {session['session_id']} (Profile: {session['profile_name']}, "
                  f"Pages: {session['pages_visited']}, Active: {session['is_active']})")
        
        print("\n7. Restoring session to a new browser session")
        # Create a new browser session to restore to
        restore_session = await create_mock_browser_session("restore_target")
        restore_session.pages_visited = 0
        restore_session.actions_performed = []
        
        result = await session_manager.restore_session(session_id, restore_session)
        if result:
            print(f"  Successfully restored session '{session_id}'")
            print(f"  Restored session pages visited: {restore_session.pages_visited}")
            print(f"  Restored session actions: {len(restore_session.actions_performed)}")
        else:
            print(f"  Failed to restore session '{session_id}'")
        
        print("\n8. Deleting a session")
        result = await session_manager.delete_session(session_id)
        if result:
            print(f"  Successfully deleted session '{session_id}'")
        else:
            print(f"  Failed to delete session '{session_id}'")
        
        print("\n9. Listing sessions after deletion")
        sessions = await session_manager.list_sessions()
        print(f"  Found {len(sessions)} sessions:")
        for session in sessions:
            print(f"    - {session['session_id']} (Profile: {session['profile_name']}, "
                  f"Pages: {session['pages_visited']}, Active: {session['is_active']})")
        
        print("\n10. Cleaning up expired sessions")
        # For demonstration, we'll manipulate one session to be expired
        session_id_3 = "expired_session"
        browser_session_3 = await create_mock_browser_session(session_id_3)
        await session_manager.save_session(session_id_3, browser_session_3)
        
        # Manipulate the session file to make it appear old
        expired_file = storage_path / f"session_{session_id_3}.json"
        import time
        import os
        old_time = time.time() - session_manager.session_timeout - 100  # Make it older than timeout
        os.utime(expired_file, (old_time, old_time))
        
        deleted_count = await session_manager.cleanup_expired_sessions()
        print(f"  Cleaned up {deleted_count} expired sessions")
        
        print("\n11. Final session list")
        sessions = await session_manager.list_sessions()
        print(f"  Found {len(sessions)} sessions:")
        for session in sessions:
            print(f"    - {session['session_id']} (Profile: {session['profile_name']}, "
                  f"Pages: {session['pages_visited']}, Active: {session['is_active']})")


if __name__ == "__main__":
    asyncio.run(main())