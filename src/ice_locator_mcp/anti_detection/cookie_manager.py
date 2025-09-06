"""
Advanced Cookie Management System for ICE Locator MCP Server.

This module provides sophisticated cookie handling and management to maintain
realistic session states, including cookie rotation, validation, and realistic
expiration patterns to avoid detection.
"""

import asyncio
import json
import time
import random
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import structlog
from playwright.async_api import BrowserContext

# Remove the circular import - we'll handle BrowserSession differently


@dataclass
class CookieProfile:
    """Represents a cookie with all relevant information."""
    name: str
    value: str
    domain: str
    path: str = "/"
    expires: Optional[float] = None  # Unix timestamp
    httpOnly: bool = False
    secure: bool = False
    sameSite: str = "Lax"
    creation_time: float = time.time()
    last_accessed: float = time.time()
    
    def is_expired(self) -> bool:
        """Check if the cookie is expired."""
        if self.expires is None:
            return False
        return time.time() > self.expires
    
    def is_session_cookie(self) -> bool:
        """Check if this is a session cookie (no expiration)."""
        return self.expires is None
    
    def time_to_expiry(self) -> Optional[float]:
        """Get time until expiry in seconds, or None for session cookies."""
        if self.expires is None:
            return None
        return max(0, self.expires - time.time())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CookieProfile':
        """Create from dictionary."""
        return cls(**data)


class CookieManager:
    """Manages advanced cookie handling for realistic session states."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        # Common domains that should be treated with special care
        self.tracking_domains: Set[str] = {
            "google-analytics.com",
            "facebook.com",
            "doubleclick.net",
            "googlesyndication.com",
            "googletagmanager.com",
            "adservice.google.com",
            "adsystem.com"
        }
        
        # Cookie rotation patterns for different domain types
        self.rotation_patterns = {
            "session": {
                "min_rotation_interval": 300,  # 5 minutes
                "max_rotation_interval": 1800,  # 30 minutes
                "rotation_probability": 0.1     # 10% chance per request
            },
            "persistent": {
                "min_rotation_interval": 3600,  # 1 hour
                "max_rotation_interval": 86400, # 24 hours
                "rotation_probability": 0.05    # 5% chance per request
            },
            "tracking": {
                "min_rotation_interval": 1800,  # 30 minutes
                "max_rotation_interval": 7200,  # 2 hours
                "rotation_probability": 0.2     # 20% chance per request
            }
        }
    
    async def extract_cookies_from_context(self, context: BrowserContext) -> List[CookieProfile]:
        """Extract all cookies from a browser context."""
        try:
            browser_cookies = await context.cookies()
            cookie_profiles = []
            
            for cookie in browser_cookies:
                cookie_profile = CookieProfile(
                    name=cookie.get('name', ''),
                    value=cookie.get('value', ''),
                    domain=cookie.get('domain', ''),
                    path=cookie.get('path', '/'),
                    expires=cookie.get('expires'),
                    httpOnly=cookie.get('httpOnly', False),
                    secure=cookie.get('secure', False),
                    sameSite=cookie.get('sameSite', 'Lax'),
                    creation_time=time.time(),
                    last_accessed=time.time()
                )
                cookie_profiles.append(cookie_profile)
            
            self.logger.debug("Extracted cookies from context", count=len(cookie_profiles))
            return cookie_profiles
            
        except Exception as e:
            self.logger.error("Failed to extract cookies from context", error=str(e))
            return []
    
    async def set_cookies_in_context(self, context: BrowserContext, cookies: List[CookieProfile]) -> bool:
        """Set cookies in a browser context."""
        try:
            # Convert CookieProfile objects to Playwright cookie format
            playwright_cookies = []
            for cookie in cookies:
                if not cookie.is_expired():  # Don't set expired cookies
                    playwright_cookie = {
                        'name': cookie.name,
                        'value': cookie.value,
                        'domain': cookie.domain,
                        'path': cookie.path,
                        'httpOnly': cookie.httpOnly,
                        'secure': cookie.secure,
                        'sameSite': cookie.sameSite
                    }
                    if cookie.expires is not None:
                        playwright_cookie['expires'] = cookie.expires
                    
                    playwright_cookies.append(playwright_cookie)
            
            # Set cookies in context
            await context.add_cookies(playwright_cookies)
            
            self.logger.debug("Set cookies in context", count=len(playwright_cookies))
            return True
            
        except Exception as e:
            self.logger.error("Failed to set cookies in context", error=str(e))
            return False
    
    def _get_cookie_category(self, cookie: CookieProfile) -> str:
        """Determine the category of a cookie for rotation purposes."""
        # Check if it's a tracking cookie
        for domain in self.tracking_domains:
            if domain in cookie.domain:
                return "tracking"
        
        # Check if it's a session cookie
        if cookie.is_session_cookie():
            return "session"
        
        # Otherwise it's a persistent cookie
        return "persistent"
    
    def _should_rotate_cookie(self, cookie: CookieProfile) -> bool:
        """Determine if a cookie should be rotated based on its category and age."""
        category = self._get_cookie_category(cookie)
        pattern = self.rotation_patterns.get(category, self.rotation_patterns["persistent"])
        
        # Check probability
        if random.random() > pattern["rotation_probability"]:
            return False
        
        # Check age
        age = time.time() - cookie.creation_time
        min_age = pattern["min_rotation_interval"]
        
        return age >= min_age
    
    async def rotate_cookies(self, cookies: List[CookieProfile]) -> List[CookieProfile]:
        """Rotate cookies that need rotation to avoid detection."""
        rotated_cookies = []
        rotation_count = 0
        
        for cookie in cookies:
            if self._should_rotate_cookie(cookie) and not cookie.is_expired():
                # Rotate the cookie by changing its value
                rotated_cookie = CookieProfile(
                    name=cookie.name,
                    value=self._generate_rotated_value(cookie.value),
                    domain=cookie.domain,
                    path=cookie.path,
                    expires=cookie.expires,
                    httpOnly=cookie.httpOnly,
                    secure=cookie.secure,
                    sameSite=cookie.sameSite,
                    creation_time=time.time(),  # Reset creation time
                    last_accessed=time.time()
                )
                rotated_cookies.append(rotated_cookie)
                rotation_count += 1
            else:
                # Keep the original cookie
                cookie.last_accessed = time.time()
                rotated_cookies.append(cookie)
        
        if rotation_count > 0:
            self.logger.debug("Rotated cookies", count=rotation_count)
        
        return rotated_cookies
    
    def _generate_rotated_value(self, original_value: str) -> str:
        """Generate a rotated value for a cookie that maintains realistic patterns."""
        # For session identifiers, maintain similar length and character patterns
        if len(original_value) > 10 and any(c.isdigit() for c in original_value):
            # Likely a session ID or similar - generate a similar pattern
            chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            return ''.join(random.choice(chars) for _ in range(len(original_value)))
        else:
            # For other cookies, slightly modify the value
            if len(original_value) > 5:
                # Change a few characters but keep the general structure
                modified_value = list(original_value)
                # Change 1-3 characters
                change_count = min(random.randint(1, 3), len(modified_value))
                for _ in range(change_count):
                    pos = random.randint(0, len(modified_value) - 1)
                    if modified_value[pos].isalpha():
                        modified_value[pos] = random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
                    elif modified_value[pos].isdigit():
                        modified_value[pos] = random.choice("0123456789")
                return ''.join(modified_value)
            else:
                # For short values, just generate a new similar value
                chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                return ''.join(random.choice(chars) for _ in range(len(original_value)))
    
    async def validate_cookies(self, cookies: List[CookieProfile]) -> List[CookieProfile]:
        """Validate cookies and remove invalid or expired ones."""
        valid_cookies = []
        expired_count = 0
        invalid_count = 0
        
        for cookie in cookies:
            # Check if cookie is valid
            if not cookie.name or not cookie.domain:
                invalid_count += 1
                continue
            
            # Check if cookie is expired
            if cookie.is_expired():
                expired_count += 1
                continue
            
            # Update last accessed time
            cookie.last_accessed = time.time()
            valid_cookies.append(cookie)
        
        if expired_count > 0 or invalid_count > 0:
            self.logger.debug("Validated cookies", 
                            valid=len(valid_cookies), 
                            expired=expired_count, 
                            invalid=invalid_count)
        
        return valid_cookies
    
    async def apply_realistic_expiration(self, cookies: List[CookieProfile]) -> List[CookieProfile]:
        """Apply realistic expiration patterns to cookies."""
        processed_cookies = []
        
        for cookie in cookies:
            # If it's already a session cookie or has realistic expiration, keep as is
            if cookie.is_session_cookie():
                processed_cookies.append(cookie)
                continue
            
            # For persistent cookies, ensure realistic expiration times
            if cookie.expires is not None:
                # Check if expiration is too far in the future (more than 1 year)
                max_expiration = time.time() + (365 * 24 * 60 * 60)  # 1 year
                if cookie.expires > max_expiration:
                    # Cap at 1 year
                    cookie.expires = max_expiration
                elif cookie.expires < time.time():
                    # Already expired, make it a session cookie
                    cookie.expires = None
            
            processed_cookies.append(cookie)
        
        return processed_cookies
    
    async def prepare_cookies_for_session(self, cookies: List[CookieProfile]) -> List[CookieProfile]:
        """Prepare cookies for use in a new session with rotation and validation."""
        # Validate cookies first
        cookies = await self.validate_cookies(cookies)
        
        # Apply realistic expiration patterns
        cookies = await self.apply_realistic_expiration(cookies)
        
        # Rotate cookies as needed
        cookies = await self.rotate_cookies(cookies)
        
        # Update last accessed times
        current_time = time.time()
        for cookie in cookies:
            cookie.last_accessed = current_time
        
        self.logger.debug("Prepared cookies for session", count=len(cookies))
        return cookies