"""
Rate limiting utilities for ICE Locator MCP Server.
"""

import asyncio
import time
from typing import Dict, Optional
import structlog


class RateLimiter:
    """Rate limiter with burst allowance and smart backoff."""
    
    def __init__(self, 
                 requests_per_minute: int = 10,
                 burst_allowance: int = 20):
        self.requests_per_minute = requests_per_minute
        self.burst_allowance = burst_allowance
        self.logger = structlog.get_logger(__name__)
        
        # Rate limiting state
        self.request_times: list = []
        self.burst_count = 0
        self.last_reset = time.time()
        self.lock = asyncio.Lock()
        
        # Adaptive rate limiting
        self.success_count = 0
        self.error_count = 0
        self.current_rate_multiplier = 1.0
        
    async def acquire(self) -> None:
        """Acquire permission to make a request."""
        async with self.lock:
            current_time = time.time()
            
            # Clean old request times (older than 1 minute)
            self.request_times = [
                t for t in self.request_times 
                if current_time - t < 60
            ]
            
            # Reset burst count every minute
            if current_time - self.last_reset > 60:
                self.burst_count = 0
                self.last_reset = current_time
            
            # Calculate current rate limit
            effective_rate = int(self.requests_per_minute * self.current_rate_multiplier)
            
            # Check if we need to wait
            if len(self.request_times) >= effective_rate:
                # Check if we can use burst allowance
                if self.burst_count < self.burst_allowance:
                    self.burst_count += 1
                    self.logger.debug("Using burst allowance", burst_count=self.burst_count)
                else:
                    # Calculate wait time
                    oldest_request = min(self.request_times)
                    wait_time = 60 - (current_time - oldest_request)
                    
                    if wait_time > 0:
                        self.logger.info("Rate limit reached, waiting", wait_time=wait_time)
                        await asyncio.sleep(wait_time)
            
            # Record this request
            self.request_times.append(current_time)
    
    async def mark_success(self) -> None:
        """Mark a successful request for adaptive rate limiting."""
        self.success_count += 1
        await self._adjust_rate_multiplier()
    
    async def mark_error(self, error_type: str = "general") -> None:
        """Mark a failed request for adaptive rate limiting."""
        self.error_count += 1
        
        # Reduce rate more aggressively for certain errors
        if error_type in ["rate_limit", "captcha", "blocked"]:
            self.error_count += 2  # Count these as worse errors
        
        await self._adjust_rate_multiplier()
    
    async def _adjust_rate_multiplier(self) -> None:
        """Adjust rate multiplier based on success/error ratio."""
        total_requests = self.success_count + self.error_count
        
        if total_requests < 10:
            return  # Not enough data yet
        
        success_rate = self.success_count / total_requests
        
        # Adjust multiplier based on success rate
        if success_rate > 0.9:
            # High success rate, can be more aggressive
            self.current_rate_multiplier = min(1.5, self.current_rate_multiplier + 0.1)
        elif success_rate > 0.7:
            # Good success rate, maintain current rate
            pass
        elif success_rate > 0.5:
            # Moderate success rate, be more conservative
            self.current_rate_multiplier = max(0.5, self.current_rate_multiplier - 0.1)
        else:
            # Poor success rate, be very conservative
            self.current_rate_multiplier = max(0.3, self.current_rate_multiplier - 0.2)
        
        self.logger.debug(
            "Rate multiplier adjusted",
            success_rate=success_rate,
            multiplier=self.current_rate_multiplier
        )
        
        # Reset counters periodically
        if total_requests > 100:
            self.success_count = int(self.success_count * 0.8)
            self.error_count = int(self.error_count * 0.8)