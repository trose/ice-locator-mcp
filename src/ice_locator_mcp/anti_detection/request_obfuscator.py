"""
Request obfuscation engine for anti-detection.

Handles user-agent rotation, header randomization, and behavioral simulation.
"""

import asyncio
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import structlog
from fake_useragent import UserAgent

from .behavioral_simulator import BehavioralSimulator


@dataclass
class BrowserProfile:
    """Browser profile for realistic fingerprinting."""
    name: str
    user_agent: str
    platform: str
    vendor: str
    languages: List[str]
    headers: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'user_agent': self.user_agent,
            'platform': self.platform,
            'vendor': self.vendor,
            'languages': self.languages,
            'headers': self.headers.copy()
        }


@dataclass
class RequestContext:
    """Context information for request obfuscation."""
    session_id: str
    request_count: int = 0
    consecutive_requests: int = 0
    last_request_time: float = 0.0
    error_count: int = 0
    current_page: str = ""
    referrer: str = ""
    user_actions: List[str] = None
    viewport_width: int = 1920
    viewport_height: int = 1080
    
    def __post_init__(self):
        if self.user_actions is None:
            self.user_actions = []


class RequestObfuscator:
    """Handles request obfuscation for anti-detection."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        self.user_agent_generator = UserAgent()
        self.behavioral_simulator = BehavioralSimulator()
        
        # Browser profiles
        self.browser_profiles = self._load_browser_profiles()
        self.current_profile: Optional[BrowserProfile] = None
        self.profile_rotation_time = 0.0
        self.profile_duration = 1800  # 30 minutes
        
        # Request contexts by session
        self.session_contexts: Dict[str, RequestContext] = {}
        
        # Timing profiles
        self.timing_profiles = {
            'human_fast': {'base': 1.0, 'variance': 0.5, 'pattern': 'burst'},
            'human_normal': {'base': 2.0, 'variance': 1.0, 'pattern': 'steady'},
            'human_slow': {'base': 4.0, 'variance': 2.0, 'pattern': 'deliberate'}
        }
        self.current_timing_profile = 'human_normal'
    
    async def obfuscate_request(self, 
                              session_id: str,
                              base_headers: Dict[str, str],
                              request_type: str = "general") -> Dict[str, str]:
        """Apply comprehensive obfuscation to request headers."""
        
        # Get or create session context
        context = self._get_session_context(session_id)
        
        # Update context
        context.request_count += 1
        context.consecutive_requests += 1
        current_time = time.time()
        
        # Reset consecutive count if enough time has passed
        if current_time - context.last_request_time > 300:  # 5 minutes
            context.consecutive_requests = 1
        
        context.last_request_time = current_time
        
        # Get current browser profile
        profile = await self._get_current_profile()
        
        # Build obfuscated headers
        headers = base_headers.copy()
        
        # Core browser headers
        headers.update(profile.headers)
        headers['User-Agent'] = profile.user_agent
        
        # Dynamic headers based on context
        headers.update(await self._generate_dynamic_headers(context, profile))
        
        # Request-specific headers
        headers.update(await self._generate_request_headers(request_type, context))
        
        # Add randomization
        headers.update(await self._add_header_randomization(headers))
        
        self.logger.debug(
            "Request obfuscated",
            session_id=session_id,
            request_count=context.request_count,
            profile=profile.name,
            request_type=request_type
        )
        
        return headers
    
    async def calculate_delay(self, 
                            session_id: str,
                            request_type: str,
                            context_info: Optional[Dict[str, Any]] = None) -> float:
        """Calculate human-like delay for next request."""
        
        context = self._get_session_context(session_id)
        profile = self.timing_profiles[self.current_timing_profile]
        
        # Base delay
        base_delay = profile['base']
        
        # Add variance
        variance = random.uniform(-profile['variance'], profile['variance'])
        
        # Request type multipliers
        type_multiplier = {
            'page_load': 0.5,
            'form_submit': 1.0,
            'search': 1.2,
            'navigation': 0.8,
            'ajax': 0.3
        }.get(request_type, 1.0)
        
        # Context-based adjustments
        context_multiplier = 1.0
        
        # Slow down if making many consecutive requests
        if context.consecutive_requests > 3:
            context_multiplier += 0.5 * (context.consecutive_requests - 3)
        
        # Slow down after errors
        if context.error_count > 0:
            context_multiplier += 0.3 * context.error_count
        
        # Speed up for related actions (within reason)
        if (context_info and 
            context_info.get('related_to_previous') and 
            context.consecutive_requests <= 2):
            context_multiplier *= 0.7
        
        final_delay = base_delay * type_multiplier * context_multiplier + variance
        
        # Ensure minimum and maximum delays
        final_delay = max(0.5, min(final_delay, 10.0))
        
        self.logger.debug(
            "Delay calculated",
            session_id=session_id,
            request_type=request_type,
            delay=final_delay,
            consecutive_requests=context.consecutive_requests
        )
        
        return final_delay
    
    async def simulate_human_behavior(self,
                                    session_id: str, 
                                    action: str,
                                    **kwargs) -> None:
        """Simulate human-like behavior patterns."""
        
        context = self._get_session_context(session_id)
        context.user_actions.append(action)
        
        if action == "form_filling":
            await self._simulate_form_filling(kwargs.get('form_data', {}))
        
        elif action == "page_reading":
            await self._simulate_page_reading(kwargs.get('content_length', 1000))
        
        elif action == "navigation":
            await self._simulate_navigation(kwargs.get('nav_type', 'click'))
        
        elif action == "mouse_movement":
            # Simulate realistic mouse movement
            start_x = kwargs.get('start_x', 0)
            start_y = kwargs.get('start_y', 0)
            end_x = kwargs.get('end_x', context.viewport_width // 2)
            end_y = kwargs.get('end_y', context.viewport_height // 2)
            await self.behavioral_simulator.simulate_mouse_movement(
                session_id, start_x, start_y, end_x, end_y
            )
        
        elif action == "scrolling":
            # Simulate realistic scrolling
            total_height = kwargs.get('total_height', 2000)
            viewport_height = kwargs.get('viewport_height', context.viewport_height)
            await self.behavioral_simulator.simulate_scrolling(
                session_id, total_height, viewport_height
            )
        
        elif action == "decision_making":
            # Simulate human decision-making process
            complexity = kwargs.get('complexity', 'medium')
            time_pressure = kwargs.get('time_pressure', False)
            await self.behavioral_simulator.simulate_decision_making(
                session_id, complexity, time_pressure
            )
        
        elif action == "thinking":
            await self._simulate_thinking_pause()
    
    async def mark_error(self, session_id: str, error_type: str) -> None:
        """Mark an error for the session context."""
        context = self._get_session_context(session_id)
        context.error_count += 1
        
        # Adjust timing profile based on errors
        if context.error_count >= 3:
            self.current_timing_profile = 'human_slow'
        elif context.error_count >= 1:
            self.current_timing_profile = 'human_normal'
    
    def _get_session_context(self, session_id: str) -> RequestContext:
        """Get or create session context."""
        if session_id not in self.session_contexts:
            self.session_contexts[session_id] = RequestContext(session_id=session_id)
        return self.session_contexts[session_id]
    
    async def _get_current_profile(self) -> BrowserProfile:
        """Get current browser profile, rotating if needed."""
        current_time = time.time()
        
        # Rotate profile if needed
        if (self.current_profile is None or 
            current_time - self.profile_rotation_time > self.profile_duration):
            
            self.current_profile = random.choice(self.browser_profiles)
            self.profile_rotation_time = current_time
            
            self.logger.debug(
                "Browser profile rotated",
                new_profile=self.current_profile.name
            )
        
        return self.current_profile
    
    async def _generate_dynamic_headers(self, 
                                      context: RequestContext,
                                      profile: BrowserProfile) -> Dict[str, str]:
        """Generate dynamic headers based on context and profile."""
        headers = {}
        
        # Accept-Language with some variation
        if profile.languages:
            lang_weights = []
            for i, lang in enumerate(profile.languages[:3]):
                weight = 1.0 - (i * 0.1) + random.uniform(-0.05, 0.05)
                lang_weights.append(f"{lang};q={weight:.1f}")
            
            headers['Accept-Language'] = ','.join(lang_weights)
        
        # DNT (Do Not Track) - randomly set
        if random.random() < 0.3:
            headers['DNT'] = '1'
        
        # Referrer based on context
        if context.referrer:
            headers['Referer'] = context.referrer
        elif context.request_count > 1:
            # Generate plausible referrer
            headers['Referer'] = 'https://locator.ice.gov/'
        
        return headers
    
    async def _generate_request_headers(self,
                                      request_type: str,
                                      context: RequestContext) -> Dict[str, str]:
        """Generate headers specific to request type."""
        headers = {}
        
        if request_type == "ajax":
            headers['X-Requested-With'] = 'XMLHttpRequest'
        
        elif request_type == "form_submit":
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            headers['Cache-Control'] = 'no-cache'
        
        elif request_type == "navigation":
            headers['Upgrade-Insecure-Requests'] = '1'
        
        # Connection management
        if context.consecutive_requests > 1:
            headers['Connection'] = 'keep-alive'
        else:
            headers['Connection'] = random.choice(['keep-alive', 'close'])
        
        return headers
    
    async def _add_header_randomization(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Add randomization to headers."""
        random_headers = {}
        
        # Randomly vary Accept header
        if 'Accept' not in headers:
            accept_options = [
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            ]
            random_headers['Accept'] = random.choice(accept_options)
        
        # Randomly add or omit optional headers
        if random.random() < 0.7:
            random_headers['Accept-Encoding'] = 'gzip, deflate, br'
        
        if random.random() < 0.5:
            random_headers['Cache-Control'] = random.choice(['no-cache', 'max-age=0'])
        
        if random.random() < 0.3:
            random_headers['Pragma'] = 'no-cache'
        
        return random_headers
    
    def _load_browser_profiles(self) -> List[BrowserProfile]:
        """Load predefined browser profiles."""
        profiles = []
        
        # Chrome profiles
        chrome_versions = ['119.0.0.0', '118.0.0.0', '117.0.0.0']
        for version in chrome_versions:
            for platform in ['Windows NT 10.0; Win64; x64', 'Macintosh; Intel Mac OS X 10_15_7']:
                profiles.append(BrowserProfile(
                    name=f"Chrome {version} on {platform.split(';')[0]}",
                    user_agent=f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
                    platform=platform,
                    vendor="Google Inc.",
                    languages=['en-US', 'en', 'es'],
                    headers={
                        'Sec-Ch-Ua': f'"Google Chrome";v="{version.split(".")[0]}", "Chromium";v="{version.split(".")[0]}", "Not?A_Brand";v="24"',
                        'Sec-Ch-Ua-Mobile': '?0',
                        'Sec-Fetch-Site': 'same-origin',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-User': '?1',
                        'Sec-Fetch-Dest': 'document'
                    }
                ))
        
        # Firefox profiles
        firefox_versions = ['119.0', '118.0', '117.0']
        for version in firefox_versions:
            for platform in ['Windows NT 10.0; Win64; x64', 'Macintosh; Intel Mac OS X 10.15']:
                profiles.append(BrowserProfile(
                    name=f"Firefox {version} on {platform.split(';')[0]}",
                    user_agent=f"Mozilla/5.0 ({platform}; rv:{version}) Gecko/20100101 Firefox/{version}",
                    platform=platform,
                    vendor="",
                    languages=['en-US', 'en'],
                    headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Upgrade-Insecure-Requests': '1'
                    }
                ))
        
        return profiles
    
    async def _simulate_form_filling(self, form_data: Dict[str, str]) -> None:
        """Simulate human-like form filling behavior."""
        total_chars = sum(len(str(value)) for value in form_data.values())
        
        # Simulate typing speed (2-5 chars per second)
        typing_time = total_chars / random.uniform(2.0, 5.0)
        
        # Add thinking pauses
        thinking_time = len(form_data) * random.uniform(0.5, 2.0)
        
        total_time = typing_time + thinking_time
        await asyncio.sleep(min(total_time, 10.0))  # Cap at 10 seconds
    
    async def _simulate_page_reading(self, content_length: int) -> None:
        """Simulate time spent reading page content."""
        # Average reading speed: 200-300 words per minute
        words_estimate = content_length / 5  # Rough word count
        reading_time = words_estimate / random.uniform(200, 300) * 60
        
        # Add scanning variation
        if random.random() < 0.3:  # 30% chance of just scanning
            reading_time *= 0.3
        
        await asyncio.sleep(min(reading_time, 8.0))  # Cap at 8 seconds
    
    async def _simulate_navigation(self, nav_type: str) -> None:
        """Simulate navigation behavior."""
        delays = {
            'click': random.uniform(0.1, 0.3),
            'scroll': random.uniform(0.5, 1.5),
            'back': random.uniform(0.2, 0.8),
            'refresh': random.uniform(1.0, 2.0)
        }
        
        delay = delays.get(nav_type, 0.5)
        await asyncio.sleep(delay)
    
    async def _simulate_thinking_pause(self) -> None:
        """Simulate human thinking pause."""
        pause_time = random.uniform(1.0, 4.0)
        await asyncio.sleep(pause_time)