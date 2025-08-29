"""
Browser simulation using Playwright for advanced anti-detection.

This module provides a more human-like browsing experience by using
a real browser engine with realistic interactions, JavaScript execution,
and full browser fingerprinting.
"""

import asyncio
import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import structlog
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

from ..core.config import SearchConfig
from .request_obfuscator import BrowserProfile


@dataclass
class BrowserSession:
    """Represents a browser session with realistic behavior."""
    session_id: str
    browser: Browser
    context: BrowserContext
    page: Page
    profile: BrowserProfile
    start_time: float = time.time()
    last_activity: float = time.time()
    pages_visited: int = 0
    actions_performed: List[str] = None
    
    def __post_init__(self):
        if self.actions_performed is None:
            self.actions_performed = []


class BrowserSimulator:
    """Advanced browser simulation using Playwright for realistic anti-detection."""
    
    def __init__(self, config: SearchConfig):
        self.config = config
        self.logger = structlog.get_logger(__name__)
        self.sessions: Dict[str, BrowserSession] = {}
        self.playwright = None
        self.browser = None
        
        # Browser profiles matching the request obfuscator
        self.browser_profiles = [
            BrowserProfile(
                name="Chrome on Windows",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                platform="Win32",
                vendor="Google Inc.",
                languages=["en-US", "en"],
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": '"Windows"',
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1"
                }
            ),
            BrowserProfile(
                name="Firefox on Windows",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
                platform="Win32",
                vendor="",
                languages=["en-US", "en"],
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1"
                }
            ),
            BrowserProfile(
                name="Chrome on macOS",
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                platform="MacIntel",
                vendor="Google Inc.",
                languages=["en-US", "en"],
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": '"macOS"',
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1"
                }
            )
        ]
    
    async def initialize(self) -> None:
        """Initialize Playwright and browser instance."""
        self.logger.info("Initializing Playwright browser simulator")
        
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser with realistic settings
            self.browser = await self.playwright.chromium.launch(
                headless=True,  # Set to False for debugging
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-extensions",
                    "--disable-plugins",
                    "--disable-plugins-discovery",
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    "--disable-ipc-flooding-protection"
                ]
            )
            
            self.logger.info("Playwright browser simulator initialized successfully")
        except Exception as e:
            self.logger.error("Failed to initialize Playwright browser simulator", error=str(e))
            raise
    
    async def create_session(self, session_id: str) -> BrowserSession:
        """Create a new browser session with realistic fingerprint."""
        if not self.browser:
            await self.initialize()
        
        # Select a random browser profile
        profile = random.choice(self.browser_profiles)
        
        # Create browser context with profile settings
        context = await self.browser.new_context(
            user_agent=profile.user_agent,
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/New_York",
            geolocation={"longitude": -74.0060, "latitude": 40.7128},  # New York
            permissions=["geolocation"],
            extra_http_headers=profile.headers,
            java_script_enabled=True,
            bypass_csp=True,
            ignore_https_errors=True
        )
        
        # Add stealth scripts to avoid detection
        await context.add_init_script("""
            // Overwrite the navigator.webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Mock chrome object
            window.chrome = {
                runtime: {},
                csi: function() {},
                loadTimes: function() {}
            };
            
            // Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
                );
            """)
            
        # Add the stealth.js file for more comprehensive evasion
        import os
        stealth_path = os.path.join(os.path.dirname(__file__), "js", "stealth.js")
        if os.path.exists(stealth_path):
            await context.add_init_script(path=stealth_path)
        
        # Create page
        page = await context.new_page()
        
        # Set realistic viewport size
        await page.set_viewport_size({
            "width": random.randint(1200, 1920),
            "height": random.randint(800, 1080)
        })
        
        # Create session
        session = BrowserSession(
            session_id=session_id,
            browser=self.browser,
            context=context,
            page=page,
            profile=profile
        )
        
        self.sessions[session_id] = session
        
        self.logger.info(
            "Created new browser session",
            session_id=session_id,
            profile=profile.name
        )
        
        return session
    
    async def navigate_to_page(self, session_id: str, url: str) -> str:
        """Navigate to a page with human-like behavior."""
        session = self.sessions.get(session_id)
        if not session:
            session = await self.create_session(session_id)
        
        try:
            # Add random delay before navigation to simulate human behavior
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # Navigate to the page
            response = await session.page.goto(url, wait_until="networkidle")
            
            # Update session metrics
            session.pages_visited += 1
            session.last_activity = time.time()
            session.actions_performed.append(f"navigate_to:{url}")
            
            # Simulate human reading time
            await self._simulate_human_reading(session)
            
            # Get page content
            content = await session.page.content()
            
            self.logger.debug(
                "Successfully navigated to page",
                session_id=session_id,
                url=url,
                status_code=response.status if response else "unknown"
            )
            
            return content
            
        except Exception as e:
            self.logger.error(
                "Failed to navigate to page",
                session_id=session_id,
                url=url,
                error=str(e)
            )
            raise
    
    async def fill_form(self, session_id: str, form_data: Dict[str, str]) -> None:
        """Fill a form with human-like typing behavior."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"No session found with ID: {session_id}")
        
        try:
            # Fill each form field with human-like typing
            for selector, value in form_data.items():
                # Find the element
                element = session.page.locator(selector)
                
                # Simulate human focus on element
                await element.focus()
                
                # Add small delay
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
                # Type with human-like delays
                for char in value:
                    await session.page.keyboard.type(char, delay=random.randint(50, 150))
                    # Random pauses during typing
                    if random.random() < 0.1:  # 10% chance of pause
                        await asyncio.sleep(random.uniform(0.2, 0.8))
                
                # Add delay after filling field
                await asyncio.sleep(random.uniform(0.2, 0.5))
                
                session.actions_performed.append(f"fill_form:{selector}")
            
            self.logger.debug(
                "Successfully filled form",
                session_id=session_id,
                fields=list(form_data.keys())
            )
            
        except Exception as e:
            self.logger.error(
                "Failed to fill form",
                session_id=session_id,
                error=str(e)
            )
            raise
    
    async def click_element(self, session_id: str, selector: str) -> None:
        """Click an element with human-like behavior."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"No session found with ID: {session_id}")
        
        try:
            # Find element
            element = session.page.locator(selector)
            
            # Scroll element into view with human-like scrolling
            await element.scroll_into_view_if_needed()
            
            # Add random delay to simulate human decision time
            await asyncio.sleep(random.uniform(0.3, 1.0))
            
            # Click with slight random offset to simulate human imprecision
            await element.click(position={
                "x": random.randint(-5, 5),
                "y": random.randint(-5, 5)
            })
            
            # Add delay after click
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            session.actions_performed.append(f"click:{selector}")
            
            self.logger.debug(
                "Successfully clicked element",
                session_id=session_id,
                selector=selector
            )
            
        except Exception as e:
            self.logger.error(
                "Failed to click element",
                session_id=session_id,
                selector=selector,
                error=str(e)
            )
            raise
    
    async def close_session(self, session_id: str) -> None:
        """Close a browser session and clean up resources."""
        session = self.sessions.get(session_id)
        if not session:
            return
        
        try:
            await session.context.close()
            self.logger.info("Closed browser session", session_id=session_id)
        except Exception as e:
            self.logger.error(
                "Failed to close browser session",
                session_id=session_id,
                error=str(e)
            )
        
        # Remove session from tracking
        del self.sessions[session_id]
    
    async def close_all_sessions(self) -> None:
        """Close all browser sessions and clean up resources."""
        session_ids = list(self.sessions.keys())
        for session_id in session_ids:
            await self.close_session(session_id)
        
        # Stop playwright
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
            self.browser = None
    
    async def _simulate_human_reading(self, session: BrowserSession) -> None:
        """Simulate human reading behavior on a page."""
        # Random reading time based on page content
        reading_time = random.uniform(2.0, 8.0)
        
        # Occasionally scroll the page
        if random.random() < 0.3:  # 30% chance to scroll
            await session.page.mouse.wheel(0, random.randint(100, 500))
            await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Wait for reading time
        await asyncio.sleep(reading_time)