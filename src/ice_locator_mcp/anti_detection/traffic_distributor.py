"""
Traffic distribution manager for intelligent request spacing and pattern management.

Implements sophisticated traffic distribution strategies including:
- Adaptive request timing based on success/failure rates
- Natural traffic patterns that mimic human behavior
- Load balancing across proxy pools
- Peak/off-peak scheduling
- Burst detection and mitigation
"""

import asyncio
import random
import time
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Callable
import structlog
from collections import deque, defaultdict


class TrafficPattern(Enum):
    """Types of traffic patterns to simulate."""
    STEADY_STATE = "steady_state"
    BURST_THEN_QUIET = "burst_then_quiet"
    GRADUAL_RAMP_UP = "gradual_ramp_up"
    RANDOM_INTERVALS = "random_intervals"
    BUSINESS_HOURS = "business_hours"
    ADAPTIVE = "adaptive"


class RequestPriority(Enum):
    """Request priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


@dataclass
class TrafficMetrics:
    """Metrics for traffic analysis and optimization."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    blocked_requests: int = 0
    average_response_time: float = 0.0
    current_rps: float = 0.0  # Requests per second
    peak_rps: float = 0.0
    success_rate: float = 1.0
    last_success_time: float = 0.0
    last_failure_time: float = 0.0
    consecutive_failures: int = 0
    rate_limit_hits: int = 0
    
    def update_success(self, response_time: float) -> None:
        """Update metrics for successful request."""
        self.successful_requests += 1
        self.total_requests += 1
        self.last_success_time = time.time()
        self.consecutive_failures = 0
        
        # Update average response time with exponential moving average
        if self.average_response_time == 0:
            self.average_response_time = response_time
        else:
            self.average_response_time = (self.average_response_time * 0.8 + 
                                        response_time * 0.2)
        
        self._update_success_rate()
    
    def update_failure(self, error_type: str = "unknown") -> None:
        """Update metrics for failed request."""
        self.failed_requests += 1
        self.total_requests += 1
        self.last_failure_time = time.time()
        self.consecutive_failures += 1
        
        if error_type == "rate_limit":
            self.rate_limit_hits += 1
        elif error_type == "blocked":
            self.blocked_requests += 1
        
        self._update_success_rate()
    
    def _update_success_rate(self) -> None:
        """Update success rate calculation."""
        if self.total_requests > 0:
            self.success_rate = self.successful_requests / self.total_requests


@dataclass
class QueuedRequest:
    """Represents a queued request with metadata."""
    request_id: str
    priority: RequestPriority
    scheduled_time: float
    session_id: str
    request_type: str
    retry_count: int = 0
    max_retries: int = 3
    timeout: float = 30.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_due(self) -> bool:
        """Check if request is due for execution."""
        return time.time() >= self.scheduled_time
    
    @property
    def can_retry(self) -> bool:
        """Check if request can be retried."""
        return self.retry_count < self.max_retries


class TrafficDistributor:
    """Manages intelligent traffic distribution and request scheduling."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.logger = structlog.get_logger(__name__)
        self.config = config or {}
        
        # Traffic metrics and state
        self.metrics = TrafficMetrics()
        self.current_pattern = TrafficPattern.ADAPTIVE
        
        # Request queuing
        self.request_queue: Dict[RequestPriority, deque] = {
            priority: deque() for priority in RequestPriority
        }
        self.active_requests: Dict[str, QueuedRequest] = {}
        
        # Rate limiting and timing
        self.base_request_interval = 2.0  # Base seconds between requests
        self.current_interval = self.base_request_interval
        self.last_request_time = 0.0
        self.request_history = deque(maxlen=100)  # Last 100 request times
        
        # Adaptive parameters
        self.adaptation_enabled = True
        self.success_threshold = 0.8
        self.failure_threshold = 0.3
        self.adaptation_factor = 0.1
        
        # Pattern-specific state
        self.pattern_state = {}
        self.pattern_start_time = time.time()
        
        # Scheduling task
        self.scheduler_task: Optional[asyncio.Task] = None
        self.running = False
    
    async def start(self) -> None:
        """Start the traffic distribution system."""
        if self.running:
            return
        
        self.running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        self.logger.info(
            "Traffic distributor started",
            pattern=self.current_pattern.value,
            base_interval=self.base_request_interval
        )
    
    async def stop(self) -> None:
        """Stop the traffic distribution system."""
        self.running = False
        
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Traffic distributor stopped")
    
    async def schedule_request(self,
                             request_id: str,
                             session_id: str,
                             request_type: str,
                             priority: RequestPriority = RequestPriority.NORMAL,
                             delay: Optional[float] = None,
                             metadata: Dict[str, Any] = None) -> str:
        """Schedule a request for execution."""
        
        if metadata is None:
            metadata = {}
        
        # Calculate when request should be executed
        if delay is not None:
            scheduled_time = time.time() + delay
        else:
            scheduled_time = await self._calculate_next_slot(priority, request_type)
        
        # Create queued request
        queued_request = QueuedRequest(
            request_id=request_id,
            priority=priority,
            scheduled_time=scheduled_time,
            session_id=session_id,
            request_type=request_type,
            metadata=metadata
        )
        
        # Add to appropriate queue
        self.request_queue[priority].append(queued_request)
        
        self.logger.debug(
            "Request scheduled",
            request_id=request_id,
            priority=priority.value,
            delay=scheduled_time - time.time(),
            queue_size=len(self.request_queue[priority])
        )
        
        return request_id
    
    async def mark_request_completed(self,
                                   request_id: str,
                                   success: bool,
                                   response_time: float = 0.0,
                                   error_type: str = "unknown") -> None:
        """Mark request as completed and update metrics."""
        
        request = self.active_requests.pop(request_id, None)
        if not request:
            return
        
        # Update metrics
        if success:
            self.metrics.update_success(response_time)
        else:
            self.metrics.update_failure(error_type)
        
        # Record request completion time
        self.request_history.append(time.time())
        
        # Trigger adaptation if enabled
        if self.adaptation_enabled:
            await self._adapt_timing()
        
        self.logger.debug(
            "Request completed",
            request_id=request_id,
            success=success,
            response_time=response_time,
            success_rate=self.metrics.success_rate
        )
    
    async def set_traffic_pattern(self, pattern: TrafficPattern, **kwargs) -> None:
        """Change traffic distribution pattern."""
        
        self.current_pattern = pattern
        self.pattern_start_time = time.time()
        self.pattern_state = kwargs
        
        # Reset adaptation for new pattern
        if pattern != TrafficPattern.ADAPTIVE:
            self.adaptation_enabled = False
        else:
            self.adaptation_enabled = True
        
        self.logger.info(
            "Traffic pattern changed",
            pattern=pattern.value,
            kwargs=kwargs
        )
    
    async def get_traffic_status(self) -> Dict[str, Any]:
        """Get current traffic distribution status."""
        
        current_time = time.time()
        
        # Calculate current RPS
        recent_requests = [t for t in self.request_history 
                          if current_time - t <= 60]  # Last minute
        current_rps = len(recent_requests) / 60 if recent_requests else 0
        
        # Queue sizes
        queue_sizes = {
            priority.value: len(queue) 
            for priority, queue in self.request_queue.items()
        }
        
        return {
            'pattern': self.current_pattern.value,
            'current_interval': self.current_interval,
            'current_rps': current_rps,
            'metrics': {
                'total_requests': self.metrics.total_requests,
                'success_rate': self.metrics.success_rate,
                'average_response_time': self.metrics.average_response_time,
                'consecutive_failures': self.metrics.consecutive_failures,
                'rate_limit_hits': self.metrics.rate_limit_hits
            },
            'queue_sizes': queue_sizes,
            'active_requests': len(self.active_requests),
            'adaptation_enabled': self.adaptation_enabled
        }
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop for processing queued requests."""
        
        while self.running:
            try:
                # Process due requests by priority
                await self._process_due_requests()
                
                # Update traffic pattern if needed
                await self._update_pattern()
                
                # Calculate current RPS
                await self._update_current_rps()
                
                # Sleep briefly before next iteration
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Scheduler loop error", error=str(e))
                await asyncio.sleep(1.0)
    
    async def _process_due_requests(self) -> None:
        """Process requests that are due for execution."""
        
        processed_count = 0
        
        # Process by priority order
        for priority in RequestPriority:
            queue = self.request_queue[priority]
            
            while queue and processed_count < 5:  # Limit per iteration
                request = queue[0]
                
                if not request.is_due:
                    break
                
                # Remove from queue and mark as active
                queue.popleft()
                self.active_requests[request.request_id] = request
                
                # Execute request (would trigger actual HTTP request)
                asyncio.create_task(self._execute_request(request))
                
                processed_count += 1
                
                # Update last request time
                self.last_request_time = time.time()
                
                # Respect minimum interval
                if processed_count > 0 and queue:
                    await asyncio.sleep(0.1)
    
    async def _execute_request(self, request: QueuedRequest) -> None:
        """Execute a queued request (placeholder for actual execution)."""
        
        # This would normally trigger the actual HTTP request
        # For now, we just simulate the execution
        
        self.logger.debug(
            "Executing request",
            request_id=request.request_id,
            type=request.request_type,
            priority=request.priority.value
        )
        
        # Simulate execution (replace with actual request execution)
        try:
            # Placeholder: would call actual request handler here
            await asyncio.sleep(0.1)  # Simulate network request
            
            # Simulate success/failure based on current success rate
            success = random.random() < max(0.7, self.metrics.success_rate)
            response_time = random.uniform(0.5, 3.0)
            
            await self.mark_request_completed(
                request.request_id,
                success,
                response_time,
                "timeout" if not success else None
            )
            
        except Exception as e:
            await self.mark_request_completed(
                request.request_id,
                False,
                0.0,
                "exception"
            )
    
    async def _calculate_next_slot(self,
                                 priority: RequestPriority,
                                 request_type: str) -> float:
        """Calculate when the next request should be executed."""
        
        current_time = time.time()
        
        # Base delay from current interval
        base_delay = await self._get_pattern_interval()
        
        # Priority adjustments
        priority_multipliers = {
            RequestPriority.CRITICAL: 0.1,
            RequestPriority.HIGH: 0.5,
            RequestPriority.NORMAL: 1.0,
            RequestPriority.LOW: 1.5,
            RequestPriority.BACKGROUND: 3.0
        }
        
        priority_delay = base_delay * priority_multipliers[priority]
        
        # Request type adjustments
        type_multipliers = {
            'search': 1.0,
            'form_submit': 1.2,
            'page_load': 0.8,
            'health_check': 0.5
        }
        
        type_delay = priority_delay * type_multipliers.get(request_type, 1.0)
        
        # Add randomization to avoid predictable patterns
        randomization = random.uniform(0.8, 1.2)
        final_delay = type_delay * randomization
        
        # Ensure minimum spacing from last request
        min_spacing = 0.5
        time_since_last = current_time - self.last_request_time
        if time_since_last < min_spacing:
            additional_delay = min_spacing - time_since_last
            final_delay = max(final_delay, additional_delay)
        
        return current_time + final_delay
    
    async def _get_pattern_interval(self) -> float:
        """Get current interval based on active traffic pattern."""
        
        if self.current_pattern == TrafficPattern.STEADY_STATE:
            return self.current_interval
        
        elif self.current_pattern == TrafficPattern.BURST_THEN_QUIET:
            elapsed = time.time() - self.pattern_start_time
            burst_duration = self.pattern_state.get('burst_duration', 60)
            quiet_duration = self.pattern_state.get('quiet_duration', 300)
            
            cycle_time = burst_duration + quiet_duration
            cycle_position = elapsed % cycle_time
            
            if cycle_position < burst_duration:
                # Burst phase - faster requests
                return self.current_interval * 0.3
            else:
                # Quiet phase - slower requests
                return self.current_interval * 3.0
        
        elif self.current_pattern == TrafficPattern.GRADUAL_RAMP_UP:
            elapsed = time.time() - self.pattern_start_time
            ramp_duration = self.pattern_state.get('ramp_duration', 600)
            
            if elapsed < ramp_duration:
                # Gradually increase speed
                progress = elapsed / ramp_duration
                speed_multiplier = 0.1 + (0.9 * progress)
                return self.current_interval / speed_multiplier
            else:
                return self.current_interval
        
        elif self.current_pattern == TrafficPattern.RANDOM_INTERVALS:
            min_interval = self.current_interval * 0.5
            max_interval = self.current_interval * 2.0
            return random.uniform(min_interval, max_interval)
        
        elif self.current_pattern == TrafficPattern.BUSINESS_HOURS:
            # Simulate business hours pattern (9 AM - 5 PM)
            current_hour = time.localtime().tm_hour
            if 9 <= current_hour <= 17:
                return self.current_interval * 0.7  # More active during business hours
            else:
                return self.current_interval * 2.0  # Less active outside business hours
        
        else:  # ADAPTIVE
            return self.current_interval
    
    async def _adapt_timing(self) -> None:
        """Adapt request timing based on success/failure patterns."""
        
        if not self.adaptation_enabled:
            return
        
        success_rate = self.metrics.success_rate
        consecutive_failures = self.metrics.consecutive_failures
        
        # Adapt based on success rate
        if success_rate < self.failure_threshold:
            # Low success rate - slow down significantly
            adaptation = 1.0 + (self.adaptation_factor * 3)
            self.current_interval *= adaptation
            
        elif consecutive_failures >= 3:
            # Multiple consecutive failures - slow down
            adaptation = 1.0 + (self.adaptation_factor * 2)
            self.current_interval *= adaptation
            
        elif success_rate > self.success_threshold and consecutive_failures == 0:
            # High success rate - can speed up slightly
            adaptation = 1.0 - (self.adaptation_factor * 0.5)
            self.current_interval *= adaptation
        
        # Ensure reasonable bounds
        min_interval = 0.5
        max_interval = 30.0
        self.current_interval = max(min_interval, min(self.current_interval, max_interval))
        
        # Rate limit detection - slow down more if hitting limits
        if self.metrics.rate_limit_hits > 0:
            recent_hits = self.metrics.rate_limit_hits
            if recent_hits >= 3:
                self.current_interval *= 2.0
        
        self.logger.debug(
            "Timing adapted",
            success_rate=success_rate,
            consecutive_failures=consecutive_failures,
            new_interval=self.current_interval
        )
    
    async def _update_pattern(self) -> None:
        """Update pattern-specific state if needed."""
        
        # Pattern-specific updates can be added here
        # For example, transitioning between pattern phases
        pass
    
    async def _update_current_rps(self) -> None:
        """Update current requests per second calculation."""
        
        current_time = time.time()
        recent_requests = [t for t in self.request_history 
                          if current_time - t <= 10]  # Last 10 seconds
        
        self.metrics.current_rps = len(recent_requests) / 10 if recent_requests else 0
        
        # Update peak RPS
        if self.metrics.current_rps > self.metrics.peak_rps:
            self.metrics.peak_rps = self.metrics.current_rps