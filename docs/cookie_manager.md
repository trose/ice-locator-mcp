# Cookie Manager

The CookieManager provides sophisticated cookie handling and management to maintain realistic session states, including cookie rotation, validation, and realistic expiration patterns to avoid detection.

## Overview

The CookieManager is responsible for managing browser cookies in a way that mimics real user behavior while avoiding detection by anti-bot systems. It provides features such as:

- Cookie rotation to prevent tracking
- Cookie validation and integrity checking
- Realistic expiration patterns
- Categorization of cookies for different handling strategies

## Key Features

### Cookie Rotation

The CookieManager implements intelligent cookie rotation to avoid detection:

- **Session Cookies**: Rotated with a 10% probability after 5 minutes
- **Persistent Cookies**: Rotated with a 5% probability after 1 hour
- **Tracking Cookies**: Rotated with a 20% probability after 30 minutes

### Cookie Validation

Cookies are validated to ensure they meet realistic patterns:

- Invalid cookies (missing name or domain) are removed
- Expired cookies are filtered out
- Cookie integrity is maintained

### Realistic Expiration

The CookieManager ensures cookies have realistic expiration patterns:

- Session cookies remain session cookies
- Persistent cookies are capped at 1 year maximum expiration
- Expired cookies are converted to session cookies

## API Reference

### CookieProfile

Represents a cookie with all relevant information:

- `name`: Cookie name
- `value`: Cookie value
- `domain`: Cookie domain
- `path`: Cookie path (default: "/")
- `expires`: Unix timestamp for expiration (None for session cookies)
- `httpOnly`: HTTP-only flag
- `secure`: Secure flag
- `sameSite`: SameSite policy
- `creation_time`: When the cookie was created
- `last_accessed`: When the cookie was last accessed

### CookieManager

Main class for managing cookies:

#### Methods

- `extract_cookies_from_context(context)`: Extract cookies from a browser context
- `set_cookies_in_context(context, cookies)`: Set cookies in a browser context
- `rotate_cookies(cookies)`: Rotate cookies that need rotation
- `validate_cookies(cookies)`: Validate cookies and remove invalid/expired ones
- `apply_realistic_expiration(cookies)`: Apply realistic expiration patterns
- `prepare_cookies_for_session(cookies)`: Prepare cookies for use in a new session

## Usage Example

```python
from cookie_manager import CookieManager, CookieProfile

# Create cookie manager
cookie_manager = CookieManager()

# Create sample cookies
cookies = [
    CookieProfile(
        name="session_id",
        value="abc123",
        domain="example.com",
        expires=None,  # Session cookie
        httpOnly=True,
        secure=True
    )
]

# Prepare cookies for session
prepared_cookies = await cookie_manager.prepare_cookies_for_session(cookies)

# Set cookies in browser context
await cookie_manager.set_cookies_in_context(context, prepared_cookies)
```

## Integration Points

The CookieManager integrates with:

- BrowserSimulator for cookie extraction and setting
- SessionManager for persistent cookie storage
- AntiDetectionCoordinator for overall anti-detection strategy

## Benefits

- **Improved Success Rate**: Realistic cookie handling reduces detection risk
- **Enhanced Evasion**: Cookie rotation prevents tracking
- **Maintained Performance**: Efficient implementation with minimal overhead
- **Resource Efficiency**: Smart cookie management optimizes browser resources

## Future Enhancements

Planned improvements include:

- Advanced cookie fingerprinting protection
- Cross-domain cookie synchronization
- Cookie encryption for sensitive data
- Integration with browser clustering for distributed cookie management