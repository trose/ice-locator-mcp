"""
TLS Client with JA3 fingerprint randomization.

This module provides a wrapper around noble-tls to implement
TLS fingerprint randomization for anti-detection purposes.
"""

import asyncio
import random
import time
from typing import Any, Dict, Optional, Union
import structlog
import httpx
from noble_tls import Client, Session
from noble_tls.exceptions.exceptions import TLSClientException

from ...core.config import SearchConfig


class TLSClient:
    """TLS client with JA3 fingerprint randomization."""
    
    def __init__(self, config: SearchConfig):
        self.config = config
        self.logger = structlog.get_logger(__name__)
        self.sessions: Dict[str, Session] = {}
        
        # Browser TLS profiles for fingerprint variation
        self.tls_profiles = [
            "chrome_109", "chrome_108", "chrome_107", "chrome_106", "chrome_105",
            "chrome_104", "chrome_103", "chrome_102", "chrome_101", "chrome_100",
            "chrome_99",
            "firefox_109", "firefox_108", "firefox_107", "firefox_106", "firefox_105",
            "firefox_104", "firefox_102", "firefox_100", "firefox_99"
        ]
    
    async def initialize(self) -> None:
        """Initialize TLS client."""
        self.logger.info("Initializing TLS client with JA3 fingerprint randomization")
        # No specific initialization needed for noble-tls
        self.logger.info("TLS client initialized successfully")
    
    async def create_session(self, session_id: str, profile: Optional[str] = None) -> Session:
        """Create a new TLS session with randomized fingerprint."""
        # Select a random TLS profile if none specified
        if profile is None:
            profile = random.choice(self.tls_profiles)
        
        try:
            # Create session with randomized JA3 fingerprint
            from noble_tls.utils.identifiers import Client
            # Convert profile string to Client enum
            client_attr = profile.upper().replace("-", "_")
            if hasattr(Client, client_attr):
                client = getattr(Client, client_attr)
            else:
                # Fallback to a default client if profile not found
                client = Client.CHROME_109
            
            session = Session(
                client=client,
                random_tls_extension_order=True,
                header_order=["accept", "user-agent", "accept-encoding", "content-length", "content-type", "accept-language"],
            )
            
            # Store session
            self.sessions[session_id] = session
            
            self.logger.debug(
                "Created TLS session with randomized fingerprint",
                session_id=session_id,
                profile=profile
            )
            
            return session
            
        except Exception as e:
            self.logger.error(
                "Failed to create TLS session",
                session_id=session_id,
                profile=profile,
                error=str(e)
            )
            raise
    
    async def get_session(self, session_id: str) -> Session:
        """Get existing session or create new one."""
        if session_id not in self.sessions:
            await self.create_session(session_id)
        return self.sessions[session_id]
    
    async def request(self, 
                     session_id: str,
                     method: str,
                     url: str,
                     headers: Optional[Dict[str, str]] = None,
                     data: Optional[Union[str, bytes, Dict]] = None,
                     **kwargs) -> httpx.Response:
        """Make HTTP request with TLS fingerprint randomization."""
        try:
            # Get or create session
            session = await self.get_session(session_id)
            
            # Prepare request parameters
            request_kwargs = {
                "method": method,
                "url": url,
                "headers": headers or {},
                "data": data,
                **kwargs
            }
            
            # Add timeout from config if not specified
            if "timeout" not in request_kwargs:
                request_kwargs["timeout"] = self.config.timeout
            
            # Make request using noble-tls session
            response = await session.execute_request(**request_kwargs)
            
            # Convert to httpx.Response for compatibility
            httpx_response = httpx.Response(
                status_code=response.status_code,
                headers=response.headers,
                content=response.content,
                request=httpx.Request(method, url, headers=headers or {})
            )
            
            self.logger.debug(
                "TLS request completed",
                session_id=session_id,
                method=method,
                url=url,
                status_code=response.status_code
            )
            
            return httpx_response
            
        except TLSClientException as e:
            self.logger.warning(
                "TLS client error, falling back to standard HTTP client",
                session_id=session_id,
                method=method,
                url=url,
                error=str(e)
            )
            
            # Fallback to standard httpx client
            return await self._fallback_request(method, url, headers, data, **kwargs)
            
        except Exception as e:
            self.logger.error(
                "Failed to make TLS request",
                session_id=session_id,
                method=method,
                url=url,
                error=str(e)
            )
            raise
    
    async def get(self, 
                  session_id: str,
                  url: str,
                  headers: Optional[Dict[str, str]] = None,
                  **kwargs) -> httpx.Response:
        """Make GET request with TLS fingerprint randomization."""
        return await self.request(session_id, "GET", url, headers=headers, **kwargs)
    
    async def post(self,
                   session_id: str,
                   url: str,
                   headers: Optional[Dict[str, str]] = None,
                   data: Optional[Union[str, bytes, Dict]] = None,
                   **kwargs) -> httpx.Response:
        """Make POST request with TLS fingerprint randomization."""
        return await self.request(session_id, "POST", url, headers=headers, data=data, **kwargs)
    
    async def _fallback_request(self,
                               method: str,
                               url: str,
                               headers: Optional[Dict[str, str]] = None,
                               data: Optional[Union[str, bytes, Dict]] = None,
                               **kwargs) -> httpx.Response:
        """Fallback to standard httpx client."""
        self.logger.info("Using fallback HTTP client")
        
        async with httpx.AsyncClient(timeout=self.config.timeout, follow_redirects=True) as client:
            if method.upper() == "GET":
                return await client.get(url, headers=headers or {}, **kwargs)
            elif method.upper() == "POST":
                return await client.post(url, headers=headers or {}, content=data, **kwargs)
            else:
                # For other methods, use the generic request method
                return await client.request(method, url, headers=headers or {}, content=data, **kwargs)
    
    async def close_session(self, session_id: str) -> None:
        """Close TLS session."""
        if session_id in self.sessions:
            try:
                # Session cleanup for noble-tls (if needed)
                del self.sessions[session_id]
                self.logger.debug("Closed TLS session", session_id=session_id)
            except Exception as e:
                self.logger.warning(
                    "Error closing TLS session",
                    session_id=session_id,
                    error=str(e)
                )
    
    async def close_all_sessions(self) -> None:
        """Close all TLS sessions."""
        session_ids = list(self.sessions.keys())
        for session_id in session_ids:
            await self.close_session(session_id)
    
    def get_random_profile(self) -> str:
        """Get a random TLS profile."""
        return random.choice(self.tls_profiles)
    
    def get_profile_list(self) -> list:
        """Get list of available TLS profiles."""
        return self.tls_profiles.copy()