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
                    "--disable-ipc-flooding-protection",
                    "--disable-background-networking",
                    "--disable-default-apps",
                    "--disable-features=TranslateUI",
                    "--disable-sync",
                    "--metrics-recording-only",
                    "--no-first-run",
                    "--safebrowsing-disable-auto-update",
                    "--disable-component-extensions-with-background-pages",
                    "--disable-features=OptimizationHints",
                    "--disable-features=InterestFeedContentSuggestions",
                    "--disable-features=PrivacySandboxSettings4",
                    "--disable-features=AutofillServerCommunication",
                    "--disable-features=PasswordManager",
                    "--disable-features=AutofillAssistant",
                    "--disable-features=msAutofillEdgeCoupons",
                    "--disable-features=UserAgentClientHint",
                    "--disable-features=ChromeWhatsNewUI",
                    "--disable-features=ChromeTipsNextToDomains",
                    "--disable-features=ChromeWhatsNewUI",
                    "--disable-features=ChromeTipsNextToDomains",
                    "--disable-features=msAutofillEdgeCoupons",
                    "--disable-features=AutofillAssistant",
                    "--disable-features=PasswordManager",
                    "--disable-features=AutofillServerCommunication",
                    "--disable-features=PrivacySandboxSettings4",
                    "--disable-features=InterestFeedContentSuggestions",
                    "--disable-features=OptimizationHints",
                    "--disable-component-extensions-with-background-pages",
                    "--disable-ipc-flooding-protection",
                    "--disable-renderer-backgrounding",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-background-timer-throttling",
                    "--disable-features=IsolateOrigins,site-per-process",
                    "--disable-web-security",
                    "--disable-plugins-discovery",
                    "--disable-plugins",
                    "--disable-extensions",
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox"
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
            viewport={"width": random.randint(1200, 1920), "height": random.randint(800, 1080)},
            locale="en-US",
            timezone_id="America/New_York",
            geolocation={"longitude": -74.0060, "latitude": 40.7128},  # New York
            permissions=["geolocation"],
            extra_http_headers=profile.headers,
            java_script_enabled=True,
            bypass_csp=True,
            ignore_https_errors=True,
            # Additional anti-detection measures
            device_scale_factor=random.choice([1, 1.25, 1.5, 2]),
            is_mobile=False,
            has_touch=False,
            # More realistic browser fingerprinting
            color_scheme="light",
            reduced_motion="no-preference",
            forced_colors="none",
            accept_downloads=False,
            # Emulate realistic browser features
            screen={"width": random.randint(1200, 1920), "height": random.randint(800, 1080)}
        )
        
        # Add stealth scripts to avoid detection
        await context.add_init_script("""
            // Overwrite the navigator.webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Mock chrome object with more realistic properties
            window.chrome = {
                runtime: {
                    connect: function() {
                        return {
                            onMessage: { addListener: function() {} },
                            onDisconnect: { addListener: function() {} },
                            postMessage: function() {},
                            disconnect: function() {}
                        };
                    },
                    sendMessage: function() {},
                    onConnect: undefined,
                    onMessage: undefined
                },
                csi: function() {},
                loadTimes: function() {},
                app: {
                    isInstalled: false
                }
            };
            
            // Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
                );
            
            // Hide webdriver property
            delete navigator.__proto__.webdriver;
            
            // Mock plugins with more realistic values
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    { filename: "internal-pdf-viewer", name: "Chrome PDF Plugin", description: "Portable Document Format" },
                    { filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai", name: "Chrome PDF Viewer", description: "Portable Document Format" },
                    { filename: "internal-nacl-plugin", name: "Native Client", description: "Native Client" }
                ],
            });
            
            // Mock mimeTypes
            Object.defineProperty(navigator, 'mimeTypes', {
                get: () => [
                    { type: "application/pdf", suffixes: "pdf", description: "Portable Document Format" },
                    { type: "text/pdf", suffixes: "pdf", description: "Portable Document Format" }
                ],
            });
            
            // Hide languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            // Hide memory with realistic values
            if (!window.performance.memory) {
              Object.defineProperty(window.performance, 'memory', {
                get: () => ({
                  usedJSHeapSize: Math.floor(Math.random() * 10000000) + 10000000,
                  totalJSHeapSize: Math.floor(Math.random() * 20000000) + 20000000,
                  jsHeapSizeLimit: Math.floor(Math.random() * 2000000000) + 2000000000
                })
              });
            }
            
            // Hide outerHeight and outerWidth
            Object.defineProperty(window, 'outerHeight', {
              get: () => window.innerHeight
            });

            Object.defineProperty(window, 'outerWidth', {
              get: () => window.innerWidth
            });
            
            // Hide screen properties with realistic values
            Object.defineProperty(screen, 'availLeft', {
              get: () => 0
            });

            Object.defineProperty(screen, 'availTop', {
              get: () => 0
            });

            Object.defineProperty(screen, 'availWidth', {
              get: () => screen.width
            });

            Object.defineProperty(screen, 'availHeight', {
              get: () => screen.height
            });

            Object.defineProperty(screen, 'colorDepth', {
              get: () => 24
            });

            Object.defineProperty(screen, 'pixelDepth', {
              get: () => 24
            });
            
            // Hide devicePixelRatio with realistic values
            if (!window.devicePixelRatio) {
              window.devicePixelRatio = Math.random() > 0.5 ? 1 : 1.5;
            }
            
            // Hide onorientationchange
            if (!window.onorientationchange) {
              window.onorientationchange = null;
            }
            
            // Hide orientation
            if (!window.orientation) {
              window.orientation = 0;
            }
            
            // Hide localStorage and sessionStorage
            if (!window.localStorage) {
              window.localStorage = {
                getItem: function() { return null; },
                setItem: function() {},
                removeItem: function() {},
                clear: function() {},
                key: function() { return null; },
                length: 0
              };
            }

            if (!window.sessionStorage) {
              window.sessionStorage = {
                getItem: function() { return null; },
                setItem: function() {},
                removeItem: function() {},
                clear: function() {},
                key: function() { return null; },
                length: 0
              };
            }
            
            // Add toString methods
            if (window.chrome && window.chrome.runtime) {
              window.chrome.runtime.toString = function() {
                return "[object Object]";
              };
            }

            if (window.chrome && window.chrome.csi) {
              window.chrome.csi.toString = function() {
                return "function csi() { [native code] }";
              };
            }

            if (window.chrome && window.chrome.loadTimes) {
              window.chrome.loadTimes.toString = function() {
                return "function loadTimes() { [native code] }";
              };
            }
            
            // Advanced hardware concurrency spoofing
            Object.defineProperty(navigator, 'hardwareConcurrency', {
              get: () => Math.floor(Math.random() * 8) + 2 // Random value between 2-10
            });
            
            // Advanced device memory spoofing
            if (!navigator.deviceMemory) {
              Object.defineProperty(navigator, 'deviceMemory', {
                get: () => Math.floor(Math.random() * 8) + 4 // Random value between 4-12 GB
              });
            }
            
            // Advanced connection information spoofing
            if (!navigator.connection) {
              Object.defineProperty(navigator, 'connection', {
                get: () => ({
                  downlink: Math.random() * 10 + 1, // 1-11 Mbps
                  effectiveType: ['4g', '3g', '2g'][Math.floor(Math.random() * 3)],
                  rtt: Math.floor(Math.random() * 100) + 50, // 50-150 ms
                  saveData: false
                })
              });
            }
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
        
        # Emulate realistic browser features
        await page.add_init_script("""
            // Emulate WebGL vendor and renderer with more realistic values
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter.apply(this, [parameter]);
            };
            
            // Hide WebGL debug renderer info
            const getExtension = WebGLRenderingContext.prototype.getExtension;
            WebGLRenderingContext.prototype.getExtension = function(name) {
                if (name === 'WEBGL_debug_renderer_info') {
                    return null;
                }
                return getExtension.apply(this, [name]);
            };
            
            // Advanced canvas fingerprinting protection
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(contextType) {
                const context = originalGetContext.apply(this, [contextType]);
                
                if (contextType === '2d' && context) {
                    // Add slight noise to canvas operations to prevent fingerprinting
                    const originalFillText = context.fillText;
                    context.fillText = function() {
                        // Add tiny random offset to prevent exact pixel matching
                        const args = Array.from(arguments);
                        if (args.length >= 3) {
                            args[1] = parseFloat(args[1]) + (Math.random() * 0.0001 - 0.00005);
                            args[2] = parseFloat(args[2]) + (Math.random() * 0.0001 - 0.00005);
                        }
                        return originalFillText.apply(this, args);
                    };
                    
                    // Override toDataURL to add noise
                    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                    HTMLCanvasElement.prototype.toDataURL = function() {
                        const context = this.getContext('2d');
                        if (context) {
                            // Add a tiny random colored pixel to prevent exact matching
                            context.fillStyle = `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.random() * 0.001})`;
                            context.fillRect(Math.random() * this.width, Math.random() * this.height, 1, 1);
                        }
                        return originalToDataURL.apply(this, arguments);
                    };
                }
                
                return context;
            };
            
            // Mock chrome object
            if (!window.chrome) {
                window.chrome = {
                    runtime: {
                        connect: function() {
                            return {
                                onMessage: { addListener: function() {} },
                                onDisconnect: { addListener: function() {} },
                                postMessage: function() {},
                                disconnect: function() {}
                            };
                        },
                        sendMessage: function() {}
                    }
                };
            }
            
            // Mock permissions
            if (!window.Notification) {
                window.Notification = {
                    permission: 'default'
                };
            }
            
            // Mock plugins
            if (!navigator.plugins) {
                navigator.plugins = {
                    length: 3
                };
            }
            
            // Advanced audio context spoofing
            if (!window.AudioContext) {
                window.AudioContext = function() {
                    return {
                        sampleRate: 44100,
                        destination: {
                            maxChannelCount: 2
                        },
                        createOscillator: function() {
                            return {
                                frequency: { value: 0 },
                                type: 'sine',
                                connect: function() {},
                                start: function() {},
                                stop: function() {},
                                disconnect: function() {}
                            };
                        },
                        createAnalyser: function() {
                            return {
                                fftSize: 2048,
                                frequencyBinCount: 1024,
                                connect: function() {},
                                disconnect: function() {}
                            };
                        },
                        close: function() { return Promise.resolve(); }
                    };
                };
            }
            
            // Advanced hardware concurrency spoofing
            if (!navigator.hardwareConcurrency) {
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => Math.floor(Math.random() * 8) + 2 // Random value between 2-10
                });
            }
            
            // Advanced device memory spoofing
            if (!navigator.deviceMemory) {
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => Math.floor(Math.random() * 8) + 4 // Random value between 4-12 GB
                });
            }
            """)
        
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
                
                # Wait for element to be visible
                await element.wait_for(state="visible", timeout=10000)
                
                # Simulate human focus on element
                await element.focus()
                
                # Add small delay
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
                # Clear existing content
                await element.clear()
                
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
            
            # Wait for element to be visible
            await element.wait_for(state="visible", timeout=10000)
            
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
    
    async def get_page_content(self, session_id: str) -> str:
        """Get the current page content."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"No session found with ID: {session_id}")
        
        try:
            content = await session.page.content()
            return content
        except Exception as e:
            self.logger.error(
                "Failed to get page content",
                session_id=session_id,
                error=str(e)
            )
            raise
    
    async def wait_for_selector(self, session_id: str, selector: str, timeout: int = 30000) -> bool:
        """Wait for an element to appear on the page."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"No session found with ID: {session_id}")
        
        try:
            await session.page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            self.logger.warning(
                "Element not found within timeout",
                session_id=session_id,
                selector=selector,
                error=str(e)
            )
            return False
    
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
        
        # Occasionally scroll the page in a more human-like pattern
        if random.random() < 0.3:  # 30% chance to scroll
            # Simulate human-like scrolling pattern
            scroll_actions = random.randint(1, 3)
            for _ in range(scroll_actions):
                scroll_distance = random.randint(100, 500)
                await session.page.mouse.wheel(0, scroll_distance)
                # Random pauses between scrolls
                await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Wait for reading time
        await asyncio.sleep(reading_time)
    
    async def simulate_human_mouse_movement(self, session: BrowserSession) -> None:
        """Simulate human-like mouse movements."""
        try:
            # Get viewport dimensions
            viewport_size = await session.page.evaluate("() => ({width: window.innerWidth, height: window.innerHeight})")
            
            # Simulate random mouse movements
            movements = random.randint(3, 7)
            for _ in range(movements):
                x = random.randint(0, viewport_size['width'])
                y = random.randint(0, viewport_size['height'])
                
                # Move mouse with human-like timing
                await session.page.mouse.move(x, y, steps=random.randint(10, 30))
                
                # Random pauses
                if random.random() < 0.2:  # 20% chance of pause
                    await asyncio.sleep(random.uniform(0.1, 0.5))
                    
        except Exception as e:
            self.logger.debug("Failed to simulate human mouse movement", error=str(e))
    
    async def simulate_human_typing(self, session: BrowserSession, text: str) -> str:
        """Simulate human-like typing with realistic delays and errors."""
        try:
            typed_text = ""
            
            for i, char in enumerate(text):
                # Type the character
                typed_text += char
                
                # Human-like typing delay
                delay = random.randint(50, 150)
                await asyncio.sleep(delay / 1000.0)
                
                # Occasional typing mistakes (and corrections)
                if random.random() < 0.02 and i > 0:  # 2% chance of mistake
                    # Add a random character
                    mistake_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                    typed_text += mistake_char
                    
                    # Short delay
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                    
                    # Backspace to correct
                    typed_text = typed_text[:-1]
                    
                    # Another short delay
                    await asyncio.sleep(random.uniform(0.1, 0.2))
                    
                    # Retype the correct character
                    typed_text += char
                    
                    # Slightly longer delay after correction
                    await asyncio.sleep(random.uniform(0.2, 0.4))
                
                # Occasional pauses during typing
                if random.random() < 0.1:  # 10% chance of pause
                    await asyncio.sleep(random.uniform(0.2, 0.8))
            
            return typed_text
            
        except Exception as e:
            self.logger.debug("Failed to simulate human typing", error=str(e))
            return text
    
    async def simulate_human_form_filling(self, session_id: str, form_data: Dict[str, str]) -> None:
        """Fill a form with sophisticated human-like behavior."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"No session found with ID: {session_id}")
        
        try:
            # Simulate thinking time before starting to fill form
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # Fill each form field with human-like behavior
            for selector, value in form_data.items():
                # Find the element
                element = session.page.locator(selector)
                
                # Wait for element to be visible
                await element.wait_for(state="visible", timeout=10000)
                
                # Simulate human focus on element
                await element.focus()
                
                # Small delay after focusing
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
                # Clear existing content with human-like behavior
                await element.click()
                await asyncio.sleep(random.uniform(0.05, 0.1))
                
                # Select all text
                await session.page.keyboard.press("Control+A")
                await asyncio.sleep(random.uniform(0.05, 0.1))
                
                # Delete selected text
                await session.page.keyboard.press("Backspace")
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
                # Type with human-like typing simulation
                typed_value = await self.simulate_human_typing(session, value)
                
                # Add delay after filling field
                await asyncio.sleep(random.uniform(0.2, 0.5))
                
                session.actions_performed.append(f"fill_form:{selector}")
            
            self.logger.debug(
                "Successfully filled form with human-like behavior",
                session_id=session_id,
                fields=list(form_data.keys())
            )
            
        except Exception as e:
            self.logger.error(
                "Failed to fill form with human-like behavior",
                session_id=session_id,
                error=str(e)
            )
            raise
