# Session Persistence and Management

The SessionManager module provides comprehensive session persistence and management capabilities to maintain realistic session states across multiple requests, mimicking real user behavior.

## Overview

In modern web scraping and automation, maintaining consistent session states is crucial for avoiding detection and ensuring realistic behavior. The SessionManager handles:

- Saving browser sessions to persistent storage
- Loading sessions from persistent storage
- Restoring browser sessions with persistent state
- Managing session lifecycle and cleanup
- Providing session information and statistics

## Key Features

### Session Persistence
Sessions are stored both in-memory (for fast access) and on disk (for persistence across application restarts). This dual storage approach ensures optimal performance while maintaining data durability.

### Session Restoration
The manager can restore browser sessions with their complete state, including:
- Browser profile information
- Navigation history
- User actions performed
- Session metrics (pages visited, activity timestamps)

### Expiration Management
Sessions automatically expire after 30 minutes of inactivity. The manager includes cleanup mechanisms to remove expired sessions and free up resources.

### Comprehensive API
The SessionManager provides a complete API for session management operations:
- Save sessions
- Load sessions
- Restore sessions
- Delete sessions
- List all sessions
- Get session information
- Clean up expired sessions

## Implementation Details

### PersistentSession Data Class
The [PersistentSession](file:///Users/trose/src/locator-mcp/src/ice_locator_mcp/anti_detection/session_manager.py#L21-L56) data class represents a persistent browser session with all relevant state information:

- `session_id`: Unique identifier for the session
- `profile_name`: Name of the browser profile used
- `user_agent`: User agent string
- `start_time`: Session creation timestamp
- `last_activity`: Last activity timestamp
- `pages_visited`: Number of pages visited
- `actions_performed`: List of actions performed
- `cookies`: Session cookies (placeholder)
- `local_storage`: Local storage data (placeholder)
- `session_storage`: Session storage data (placeholder)
- `viewport_width`: Viewport width
- `viewport_height`: Viewport height
- `language`: Browser language
- `timezone`: Browser timezone

### SessionManager Class
The [SessionManager](file:///Users/trose/src/locator-mcp/src/ice_locator_mcp/anti_detection/session_manager.py#L59-L252) class manages persistent browser sessions:

#### Constructor
```python
SessionManager(storage_path: Optional[str] = None)
```
- `storage_path`: Directory for persistent session storage (defaults to `~/.cache/ice-locator-mcp/sessions`)

#### Methods

##### save_session
```python
async def save_session(self, session_id: str, browser_session: BrowserSession) -> bool
```
Save a browser session to persistent storage.

##### load_session
```python
async def load_session(self, session_id: str) -> Optional[PersistentSession]
```
Load a session from persistent storage.

##### restore_session
```python
async def restore_session(self, session_id: str, browser_session: BrowserSession) -> bool
```
Restore a browser session with persistent state.

##### delete_session
```python
async def delete_session(self, session_id: str) -> bool
```
Delete a session from persistent storage.

##### cleanup_expired_sessions
```python
async def cleanup_expired_sessions(self) -> int
```
Clean up expired sessions from storage.

##### get_session_info
```python
async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]
```
Get information about a session without loading it fully.

##### list_sessions
```python
async def list_sessions(self) -> List[Dict[str, Any]]
```
List all sessions with basic information.

## Usage Examples

### Basic Session Management
```python
from src.ice_locator_mcp.anti_detection.session_manager import SessionManager

# Create session manager
session_manager = SessionManager()

# Save a session
await session_manager.save_session("session_1", browser_session)

# Load a session
loaded_session = await session_manager.load_session("session_1")

# Restore a session
await session_manager.restore_session("session_1", new_browser_session)

# Delete a session
await session_manager.delete_session("session_1")
```

### Session Information
```python
# Get session information
info = await session_manager.get_session_info("session_1")
print(f"Session active: {info['is_active']}")

# List all sessions
sessions = await session_manager.list_sessions()
for session in sessions:
    print(f"Session {session['session_id']}: {session['pages_visited']} pages visited")
```

### Cleanup Operations
```python
# Clean up expired sessions
deleted_count = await session_manager.cleanup_expired_sessions()
print(f"Cleaned up {deleted_count} expired sessions")
```

## Integration with Browser Simulator

The SessionManager integrates seamlessly with the BrowserSimulator to provide persistent session management:

1. Sessions are saved after each browser interaction
2. Sessions are automatically loaded when needed
3. Session state is restored to maintain continuity
4. Expired sessions are automatically cleaned up

## Best Practices

1. **Regular Cleanup**: Periodically call `cleanup_expired_sessions()` to free up resources
2. **Error Handling**: Always check return values for proper error handling
3. **Session IDs**: Use unique, meaningful session IDs for easy identification
4. **Storage Management**: Monitor storage usage and implement retention policies as needed

## Future Enhancements

Planned improvements include:
- Full cookie persistence and restoration
- Local storage and session storage persistence
- Cross-session data sharing
- Advanced session analytics
- Integration with user behavior patterns