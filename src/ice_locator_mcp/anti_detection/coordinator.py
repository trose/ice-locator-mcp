"""
Advanced Anti-Detection Coordinator.

Integrates all anti-detection components to provide a unified interface
for sophisticated detection avoidance strategies.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Callable
import structlog

from .proxy_manager import ProxyManager, ProxyConfig
from .request_obfuscator import RequestObfuscator
from .behavioral_simulator import BehavioralSimulator, BehaviorType
from .traffic_distributor import TrafficDistributor, TrafficPattern, RequestPriority
from .browser_simulator import BrowserSimulator  # Added import for browser simulator
from ..core.config import ServerConfig


class AntiDetectionCoordinator:
    """Coordinates all anti-detection strategies for maximum effectiveness."""
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self.logger = structlog.get_logger(__name__)
        
        # Core components
        self.proxy_manager = ProxyManager(config.proxy_config)
        self.request_obfuscator = RequestObfuscator()
        self.behavioral_simulator = BehavioralSimulator()
        self.traffic_distributor = TrafficDistributor(config)
        self.browser_simulator = BrowserSimulator(config.search_config)  # Added browser simulator
        
        # Coordination state
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.global_metrics = {
            'total_requests': 0,
            'success_rate': 1.0,
            'detection_events': 0,
            'adaptive_adjustments': 0
        }
        
        # Strategy state
        self.current_strategy = 'balanced'
        self.strategy_start_time = time.time()
        self.detection_level = 'low'  # low, medium, high, critical
        
        # Component integration settings
        self.enable_proxy_rotation = True
        self.enable_behavioral_simulation = True
        self.enable_traffic_distribution = True
        self.enable_browser_simulation = True  # Added browser simulation flag
        self.enable_adaptive_strategies = True
        
    async def initialize(self) -> None:
        """Initialize all anti-detection components."""
        self.logger.info("Initializing advanced anti-detection coordinator")
        
        # Initialize components in order
        await self.proxy_manager.initialize()
        await self.traffic_distributor.start()
        if self.enable_browser_simulation:
            await self.browser_simulator.initialize()  # Initialize browser simulator
        
        # Set initial strategy based on configuration
        await self._apply_initial_strategy()
        
        self.logger.info(
            "Anti-detection coordinator initialized",
            strategy=self.current_strategy,
            components_enabled={
                'proxy_rotation': self.enable_proxy_rotation,
                'behavioral_simulation': self.enable_behavioral_simulation,
                'traffic_distribution': self.enable_traffic_distribution,
                'browser_simulation': self.enable_browser_simulation,  # Added to components
                'adaptive_strategies': self.enable_adaptive_strategies
            }
        )
    
    async def execute_request(self,
                            session_id: str,
                            request_info: Dict[str, Any],
                            request_handler: Callable) -> Dict[str, Any]:
        """Execute a request with full anti-detection coordination."""
        
        request_id = f"{session_id}_{int(time.time() * 1000)}"
        behavior_result = {}
        
        try:
            # 1. Traffic Distribution - Schedule the request
            if self.enable_traffic_distribution:
                priority = RequestPriority(request_info.get('priority', 'normal'))
                await self.traffic_distributor.schedule_request(
                    request_id=request_id,
                    session_id=session_id,
                    request_type=request_info.get('type', 'general'),
                    priority=priority
                )
            
            # 2. Behavioral Simulation - Calculate human-like delays
            if self.enable_behavioral_simulation:
                behavior_result = await self.behavioral_simulator.simulate_page_interaction(
                    session_id=session_id,
                    page_content=request_info.get('page_content', {}),
                    interaction_type=request_info.get('interaction_type', 'general')
                )
                
                # Apply pre-interaction delay
                if behavior_result['pre_delay'] > 0:
                    await asyncio.sleep(behavior_result['pre_delay'])
            
            # 3. Browser Simulation - Use Playwright for more realistic behavior
            if self.enable_browser_simulation and request_info.get('use_browser', False):
                return await self._execute_with_browser(session_id, request_info, request_handler)
            
            # 4. Proxy Management - Get optimal proxy
            proxy = None
            if self.enable_proxy_rotation:
                proxy = await self.proxy_manager.get_proxy()
            
            # 5. Request Obfuscation - Generate headers
            headers = await self.request_obfuscator.obfuscate_request(
                session_id=session_id,
                base_headers=request_info.get('headers', {}),
                request_type=request_info.get('type', 'general')
            )
            
            # 6. Execute the actual request
            start_time = time.time()
            
            try:
                request_config = {
                    'headers': headers,
                    'proxy': proxy,
                    'timeout': request_info.get('timeout', 30),
                    **request_info.get('config', {})
                }
                
                result = await request_handler(**request_config)
                response_time = time.time() - start_time
                
                # Mark success in all components
                await self._handle_request_success(
                    request_id, session_id, proxy, response_time, result
                )
                
                return {
                    'success': True,
                    'result': result,
                    'response_time': response_time,
                    'proxy_used': proxy.endpoint if proxy else None,
                    'detection_level': self.detection_level,
                    'behavioral_flags': behavior_result.get('behavioral_flags', {})
                }
                
            except Exception as e:
                response_time = time.time() - start_time
                
                # Handle request failure
                await self._handle_request_failure(
                    request_id, session_id, proxy, str(e)
                )
                
                # Check if we should retry with different strategy
                should_retry = await self._should_retry_request(request_info, str(e))
                
                if should_retry:
                    # Apply adaptive strategy and retry
                    await self._adapt_strategy(str(e))
                    return await self.execute_request(session_id, request_info, request_handler)
                
                raise e
        
        except Exception as e:
            self.logger.error(
                "Anti-detection request execution failed",
                request_id=request_id,
                session_id=session_id,
                error=str(e)
            )
            raise
    
    async def _execute_with_browser(self,
                                  session_id: str,
                                  request_info: Dict[str, Any],
                                  request_handler: Callable) -> Dict[str, Any]:
        """Execute a request using the Playwright browser simulator."""
        request_id = f"{session_id}_browser_{int(time.time() * 1000)}"
        
        try:
            # Get URL from request info
            url = request_info.get('url')
            if not url:
                raise ValueError("URL is required for browser-based requests")
            
            # Navigate to page using browser simulator
            content = await self.browser_simulator.navigate_to_page(session_id, url)
            
            # If this is a form submission, handle form filling
            form_data = request_info.get('form_data')
            if form_data:
                form_selector = request_info.get('form_selector', 'form')
                await self.browser_simulator.fill_form(session_id, form_data)
                
                # Submit form if submit selector is provided
                submit_selector = request_info.get('submit_selector')
                if submit_selector:
                    await self.browser_simulator.click_element(session_id, submit_selector)
                    
                    # Wait for navigation after form submission
                    await asyncio.sleep(random.uniform(1.0, 3.0))
                    
                    # Get updated content
                    content = await self.browser_simulator.page.content()
            
            # Handle any additional clicks
            clicks = request_info.get('clicks', [])
            for click_selector in clicks:
                await self.browser_simulator.click_element(session_id, click_selector)
            
            response_time = time.time() - request_info.get('start_time', time.time())
            
            # Process the result with the request handler
            result = await request_handler(content=content)
            
            return {
                'success': True,
                'result': result,
                'response_time': response_time,
                'proxy_used': None,  # Browser handles proxy internally
                'detection_level': self.detection_level,
                'method': 'browser_simulation'
            }
            
        except Exception as e:
            self.logger.error(
                "Browser-based request execution failed",
                request_id=request_id,
                session_id=session_id,
                error=str(e)
            )
            raise
    
    async def start_session(self,
                          session_id: str,
                          behavior_type: BehaviorType = BehaviorType.CASUAL_BROWSING,
                          goals: List[str] = None) -> Dict[str, Any]:
        """Start a new coordinated anti-detection session."""
        
        if goals is None:
            goals = []
        
        # Initialize behavioral simulation session
        behavior_session = None
        if self.enable_behavioral_simulation:
            behavior_session = await self.behavioral_simulator.start_session(
                session_id=session_id,
                behavior_type=behavior_type,
                goals=goals
            )
        
        # Track session state
        self.active_sessions[session_id] = {
            'start_time': time.time(),
            'behavior_type': behavior_type,
            'goals': goals,
            'request_count': 0,
            'success_count': 0,
            'failure_count': 0,
            'current_proxy': None,
            'behavior_session': behavior_session
        }
        
        self.logger.info(
            "Anti-detection session started",
            session_id=session_id,
            behavior_type=behavior_type.value if behavior_type else None,
            goals_count=len(goals)
        )
        
        return {
            'session_id': session_id,
            'strategy': self.current_strategy,
            'detection_level': self.detection_level,
            'components_active': {
                'proxy_rotation': self.enable_proxy_rotation,
                'behavioral_simulation': self.enable_behavioral_simulation,
                'traffic_distribution': self.enable_traffic_distribution,
                'browser_simulation': self.enable_browser_simulation
            }
        }
    
    async def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all anti-detection components."""
        
        status = {
            'coordinator': {
                'strategy': self.current_strategy,
                'detection_level': self.detection_level,
                'active_sessions': len(self.active_sessions),
                'global_metrics': self.global_metrics.copy()
            }
        }
        
        # Proxy manager status
        if self.enable_proxy_rotation:
            proxy_analytics = await self.proxy_manager.get_proxy_analytics()
            status['proxy_management'] = proxy_analytics
        
        # Traffic distributor status
        if self.enable_traffic_distribution:
            traffic_status = await self.traffic_distributor.get_traffic_status()
            status['traffic_distribution'] = traffic_status
        
        # Behavioral simulation status
        if self.enable_behavioral_simulation:
            behavior_status = {}
            for session_id in self.active_sessions:
                session_summary = await self.behavioral_simulator.get_session_summary(session_id)
                if session_summary:
                    behavior_status[session_id] = session_summary
            status['behavioral_simulation'] = behavior_status
        
        return status
    
    async def adapt_detection_strategy(self, threat_level: str = None) -> None:
        """Manually adapt anti-detection strategy based on threat level."""
        
        if threat_level:
            self.detection_level = threat_level
        
        # Apply strategy based on detection level
        strategies = {
            'low': 'balanced',
            'medium': 'cautious', 
            'high': 'stealth',
            'critical': 'maximum_evasion'
        }
        
        new_strategy = strategies.get(self.detection_level, 'balanced')
        
        if new_strategy != self.current_strategy:
            await self._apply_strategy(new_strategy)
            
            self.logger.info(
                "Anti-detection strategy adapted",
                old_strategy=self.current_strategy,
                new_strategy=new_strategy,
                detection_level=self.detection_level
            )
    
    async def cleanup(self) -> None:
        """Cleanup all anti-detection components."""
        self.logger.info("Cleaning up anti-detection coordinator")
        
        # Cleanup components
        await self.proxy_manager.cleanup()
        await self.traffic_distributor.stop()
        
        # Clear session state
        self.active_sessions.clear()
        
        self.logger.info("Anti-detection coordinator cleanup completed")
    
    async def _apply_initial_strategy(self) -> None:
        """Apply initial anti-detection strategy."""
        # Get strategy from config, defaulting to 'balanced'
        strategy = getattr(self.config, 'initial_strategy', 'balanced')
        await self._apply_strategy(strategy)
    
    async def _apply_strategy(self, strategy: str) -> None:
        """Apply a specific anti-detection strategy."""
        
        self.current_strategy = strategy
        self.strategy_start_time = time.time()
        
        if strategy == 'balanced':
            await self._apply_balanced_strategy()
        elif strategy == 'cautious':
            await self._apply_cautious_strategy()
        elif strategy == 'stealth':
            await self._apply_stealth_strategy()
        elif strategy == 'maximum_evasion':
            await self._apply_maximum_evasion_strategy()
    
    async def _apply_balanced_strategy(self) -> None:
        """Apply balanced anti-detection settings."""
        # Moderate proxy rotation
        self.proxy_manager.config.rotation_interval = 1800  # 30 minutes
        
        # Normal traffic distribution
        await self.traffic_distributor.set_traffic_pattern(TrafficPattern.ADAPTIVE)
    
    async def _apply_cautious_strategy(self) -> None:
        """Apply cautious anti-detection settings."""
        # Slower proxy rotation
        self.proxy_manager.config.rotation_interval = 2700  # 45 minutes
        
        # Slower, more deliberate traffic
        await self.traffic_distributor.set_traffic_pattern(
            TrafficPattern.GRADUAL_RAMP_UP,
            ramp_duration=900
        )
    
    async def _apply_stealth_strategy(self) -> None:
        """Apply stealth anti-detection settings."""
        # Frequent proxy rotation
        self.proxy_manager.config.rotation_interval = 900  # 15 minutes
        
        # Burst and quiet patterns
        await self.traffic_distributor.set_traffic_pattern(
            TrafficPattern.BURST_THEN_QUIET,
            burst_duration=120,
            quiet_duration=600
        )
    
    async def _apply_maximum_evasion_strategy(self) -> None:
        """Apply maximum evasion settings."""
        # Very frequent proxy rotation
        self.proxy_manager.config.rotation_interval = 600  # 10 minutes
        
        # Random intervals for unpredictability
        await self.traffic_distributor.set_traffic_pattern(TrafficPattern.RANDOM_INTERVALS)
    
    async def _handle_request_success(self,
                                    request_id: str,
                                    session_id: str,
                                    proxy: Optional[ProxyConfig],
                                    response_time: float,
                                    result: Any) -> None:
        """Handle successful request completion."""
        
        # Update global metrics
        self.global_metrics['total_requests'] += 1
        success_count = self.global_metrics['total_requests'] * self.global_metrics['success_rate'] + 1
        self.global_metrics['success_rate'] = success_count / (self.global_metrics['total_requests'])
        
        # Update session metrics
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session['request_count'] += 1
            session['success_count'] += 1
        
        # Update component metrics
        if proxy and self.enable_proxy_rotation:
            await self.proxy_manager.mark_proxy_success(proxy, response_time)
        
        if self.enable_traffic_distribution:
            await self.traffic_distributor.mark_request_completed(
                request_id, True, response_time
            )
    
    async def _handle_request_failure(self,
                                    request_id: str,
                                    session_id: str,
                                    proxy: Optional[ProxyConfig],
                                    error: str) -> None:
        """Handle failed request."""
        
        # Update global metrics
        self.global_metrics['total_requests'] += 1
        success_count = self.global_metrics['total_requests'] * self.global_metrics['success_rate']
        self.global_metrics['success_rate'] = success_count / self.global_metrics['total_requests']
        
        # Check for detection indicators
        if self._is_detection_error(error):
            self.global_metrics['detection_events'] += 1
        
        # Update session metrics
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session['request_count'] += 1
            session['failure_count'] += 1
        
        # Update component metrics
        if proxy and self.enable_proxy_rotation:
            await self.proxy_manager.mark_proxy_failure(proxy, Exception(error))
        
        if self.enable_traffic_distribution:
            error_type = self._classify_error_type(error)
            await self.traffic_distributor.mark_request_completed(
                request_id, False, 0.0, error_type
            )
    
    async def _should_retry_request(self, request_info: Dict[str, Any], error: str) -> bool:
        """Determine if request should be retried with adapted strategy."""
        
        retry_count = request_info.get('retry_count', 0)
        max_retries = request_info.get('max_retries', 2)
        
        if retry_count >= max_retries:
            return False
        
        # Retry on detection-related errors
        if self._is_detection_error(error):
            return True
        
        # Retry on network-related errors
        network_errors = ['timeout', 'connection', 'proxy']
        if any(err_type in error.lower() for err_type in network_errors):
            return True
        
        return False
    
    async def _adapt_strategy(self, error: str) -> None:
        """Adapt strategy based on error type."""
        
        if not self.enable_adaptive_strategies:
            return
        
        self.global_metrics['adaptive_adjustments'] += 1
        
        if self._is_detection_error(error):
            # Detection detected - increase evasion level
            current_levels = ['low', 'medium', 'high', 'critical']
            current_index = current_levels.index(self.detection_level)
            
            if current_index < len(current_levels) - 1:
                new_level = current_levels[current_index + 1]
                await self.adapt_detection_strategy(new_level)
        
        elif 'rate_limit' in error.lower():
            # Rate limiting - slow down traffic
            await self.traffic_distributor.set_traffic_pattern(
                TrafficPattern.GRADUAL_RAMP_UP,
                ramp_duration=1200
            )
    
    def _is_detection_error(self, error: str) -> bool:
        """Check if error indicates detection."""
        detection_indicators = [
            'captcha', 'blocked', 'forbidden', 'access denied',
            'suspicious activity', 'bot detected', 'rate limit'
        ]
        
        error_lower = error.lower()
        return any(indicator in error_lower for indicator in detection_indicators)
    
    def _classify_error_type(self, error: str) -> str:
        """Classify error type for component handling."""
        error_lower = error.lower()
        
        if 'rate' in error_lower and 'limit' in error_lower:
            return 'rate_limit'
        elif any(term in error_lower for term in ['blocked', 'forbidden', 'captcha']):
            return 'blocked'
        elif any(term in error_lower for term in ['timeout', 'connection']):
            return 'network'
        else:
            return 'unknown'