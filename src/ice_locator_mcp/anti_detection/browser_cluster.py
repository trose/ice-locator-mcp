"""
Browser clustering manager for distributing requests across multiple browser instances.

This module implements browser clustering to improve resource management and redundancy
by distributing requests across multiple browser instances.
"""

import asyncio
import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import structlog
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

from ..core.config import SearchConfig
from .browser_simulator import BrowserSimulator, BrowserSession
from .request_obfuscator import BrowserProfile


@dataclass
class BrowserInstance:
    """Represents a browser instance in the cluster."""
    instance_id: str
    simulator: BrowserSimulator
    is_available: bool = True
    last_used: float = 0.0
    request_count: int = 0
    error_count: int = 0
    consecutive_failures: int = 0
    created_at: float = time.time()
    
    def mark_as_used(self):
        """Mark instance as used."""
        self.is_available = False
        self.last_used = time.time()
        self.request_count += 1
    
    def mark_as_available(self):
        """Mark instance as available."""
        self.is_available = True
        self.last_used = time.time()
    
    def mark_as_failed(self):
        """Mark instance as failed."""
        self.is_available = False
        self.error_count += 1
        self.consecutive_failures += 1
    
    def mark_as_successful(self):
        """Mark instance as successful (resets consecutive failures)."""
        self.consecutive_failures = 0
    
    @property
    def health_score(self) -> float:
        """Calculate health score for load balancing (0.0 to 1.0)."""
        # Base score from success rate
        if self.request_count == 0:
            success_rate = 1.0
        else:
            success_rate = max(0.0, 1.0 - (self.error_count / max(1, self.request_count)))
        
        # Penalty for consecutive failures
        consecutive_failure_penalty = max(0.0, 1.0 - (self.consecutive_failures * 0.1))
        
        # Bonus for recent usage (more recent = higher score)
        time_since_use = time.time() - self.last_used
        recency_bonus = max(0.0, 1.0 - (time_since_use / 300.0))  # 5 minutes
        
        # Combine factors
        score = (success_rate * 0.7) + (consecutive_failure_penalty * 0.2) + (recency_bonus * 0.1)
        return max(0.0, min(1.0, score))
    
    @property
    def is_healthy(self) -> bool:
        """Check if instance is healthy."""
        return self.consecutive_failures < 3


class BrowserClusterManager:
    """Manages a cluster of browser instances for load balancing and redundancy."""
    
    def __init__(self, config: SearchConfig, max_instances: int = 5):
        self.config = config
        self.max_instances = max_instances
        self.logger = structlog.get_logger(__name__)
        
        # Instance management
        self.instances: Dict[str, BrowserInstance] = {}
        self.available_instances: List[str] = []
        self.busy_instances: List[str] = []
        
        # Cluster state
        self.initialized = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_monitoring = False
        
        self.logger.info(
            "Browser cluster manager initialized",
            max_instances=max_instances
        )
    
    async def initialize(self) -> None:
        """Initialize the browser cluster."""
        if self.initialized:
            return
        
        self.logger.info("Initializing browser cluster")
        
        # Create initial browser instances
        for i in range(min(self.max_instances, 3)):  # Start with 3 instances
            await self.create_instance()
        
        # Start health monitoring
        await self._start_monitoring()
        
        self.initialized = True
        self.logger.info(
            "Browser cluster initialized",
            instance_count=len(self.instances)
        )
    
    async def create_instance(self) -> str:
        """Create a new browser instance and add it to the cluster."""
        instance_id = f"browser_{len(self.instances) + 1}_{int(time.time() * 1000)}"
        
        try:
            # Create browser simulator for this instance
            simulator = BrowserSimulator(self.config)
            await simulator.initialize()
            
            # Create browser instance
            instance = BrowserInstance(
                instance_id=instance_id,
                simulator=simulator
            )
            
            # Add to cluster
            self.instances[instance_id] = instance
            self.available_instances.append(instance_id)
            
            self.logger.debug(
                "Created browser instance",
                instance_id=instance_id,
                total_instances=len(self.instances)
            )
            
            return instance_id
            
        except Exception as e:
            self.logger.error(
                "Failed to create browser instance",
                instance_id=instance_id,
                error=str(e)
            )
            raise
    
    async def get_available_instance(self) -> Optional[BrowserInstance]:
        """Get an available browser instance, creating new ones if needed."""
        # First try to find an existing available instance
        if self.available_instances:
            instance_id = self.available_instances.pop(0)
            instance = self.instances[instance_id]
            instance.mark_as_used()
            self.busy_instances.append(instance_id)
            return instance
        
        # If no available instances and we haven't reached max, create a new one
        if len(self.instances) < self.max_instances:
            instance_id = await self.create_instance()
            instance = self.instances[instance_id]
            instance.mark_as_used()
            self.busy_instances.append(instance_id)
            return instance
        
        # No instances available and at max capacity
        return None
    
    def release_instance(self, instance_id: str) -> None:
        """Release a browser instance back to the pool."""
        if instance_id in self.busy_instances:
            self.busy_instances.remove(instance_id)
            self.available_instances.append(instance_id)
            
            if instance_id in self.instances:
                self.instances[instance_id].mark_as_available()
    
    def select_instance_for_request(self) -> Optional[BrowserInstance]:
        """Select the best instance for a request using load balancing."""
        # Get healthy instances
        healthy_instances = [
            instance for instance in self.instances.values() 
            if instance.is_healthy
        ]
        
        if not healthy_instances:
            return None
        
        # Weighted selection based on health score
        weights = [instance.health_score for instance in healthy_instances]
        selected_instance = random.choices(healthy_instances, weights=weights)[0]
        
        return selected_instance
    
    async def handle_request(self, session_id: str, url: str, **kwargs) -> str:
        """Handle a request using the browser cluster with load balancing."""
        # Get an available instance
        instance = await self.get_available_instance()
        
        if not instance:
            # Try to select any healthy instance even if busy (overload)
            instance = self.select_instance_for_request()
            
            if not instance:
                raise RuntimeError("No healthy browser instances available")
        
        try:
            # Create session if it doesn't exist
            if session_id not in instance.simulator.sessions:
                await instance.simulator.create_session(session_id)
            
            # Navigate to page
            content = await instance.simulator.navigate_to_page(session_id, url)
            
            # Mark as successful
            instance.mark_as_successful()
            
            return content
            
        except Exception as e:
            self.logger.error(
                "Request failed on browser instance",
                instance_id=instance.instance_id,
                session_id=session_id,
                url=url,
                error=str(e)
            )
            
            # Mark as failed
            instance.mark_as_failed()
            
            # Try failover if possible
            return await self._handle_failover(session_id, url, **kwargs)
            
        finally:
            # Release instance back to pool
            self.release_instance(instance.instance_id)
    
    async def _handle_failover(self, session_id: str, url: str, **kwargs) -> str:
        """Handle failover to another browser instance."""
        self.logger.info(
            "Attempting failover for request",
            session_id=session_id,
            url=url
        )
        
        # Try to get a different healthy instance
        original_instance = None
        for instance in self.instances.values():
            if (instance.is_healthy and 
                session_id in instance.simulator.sessions):
                original_instance = instance
                break
        
        # Get a new instance for failover
        failover_instance = self.select_instance_for_request()
        
        if not failover_instance:
            raise RuntimeError("No healthy instances available for failover")
        
        try:
            # Create session on failover instance
            if session_id not in failover_instance.simulator.sessions:
                await failover_instance.simulator.create_session(session_id)
            
            # Navigate to page
            content = await failover_instance.simulator.navigate_to_page(session_id, url)
            
            # Mark as successful
            failover_instance.mark_as_successful()
            
            self.logger.info(
                "Failover successful",
                original_instance=original_instance.instance_id if original_instance else "unknown",
                failover_instance=failover_instance.instance_id
            )
            
            return content
            
        except Exception as e:
            self.logger.error(
                "Failover also failed",
                failover_instance=failover_instance.instance_id,
                error=str(e)
            )
            
            # Mark failover instance as failed
            failover_instance.mark_as_failed()
            
            raise
    
    async def check_instance_health(self, instance_id: str) -> bool:
        """Check the health of a specific browser instance."""
        if instance_id not in self.instances:
            return False
        
        instance = self.instances[instance_id]
        
        try:
            # Simple health check - try to create a session
            test_session_id = f"health_check_{int(time.time() * 1000)}"
            await instance.simulator.create_session(test_session_id)
            await instance.simulator.close_session(test_session_id)
            
            instance.mark_as_successful()
            return True
            
        except Exception as e:
            self.logger.debug(
                "Health check failed for instance",
                instance_id=instance_id,
                error=str(e)
            )
            instance.mark_as_failed()
            return False
    
    async def restart_instance(self, instance_id: str) -> bool:
        """Restart a specific browser instance."""
        if instance_id not in self.instances:
            return False
        
        instance = self.instances[instance_id]
        
        try:
            # Close all sessions
            await instance.simulator.close_all_sessions()
            
            # Reinitialize simulator
            await instance.simulator.initialize()
            
            # Reset instance state
            instance.error_count = 0
            instance.consecutive_failures = 0
            instance.request_count = 0
            instance.is_available = True
            
            self.logger.info(
                "Successfully restarted browser instance",
                instance_id=instance_id
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "Failed to restart browser instance",
                instance_id=instance_id,
                error=str(e)
            )
            return False
    
    async def _start_monitoring(self) -> None:
        """Start background health monitoring."""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_task = asyncio.create_task(self._monitor_loop())
    
    async def _monitor_loop(self) -> None:
        """Background loop for health monitoring."""
        while self.is_monitoring:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(
                    "Health monitoring error",
                    error=str(e)
                )
                await asyncio.sleep(60)
    
    async def _perform_health_checks(self) -> None:
        """Perform health checks on all instances."""
        for instance_id in list(self.instances.keys()):
            # Skip very recently used instances
            instance = self.instances[instance_id]
            if time.time() - instance.last_used < 30:
                continue
            
            is_healthy = await self.check_instance_health(instance_id)
            
            if not is_healthy and instance.consecutive_failures >= 2:
                self.logger.warning(
                    "Restarting unhealthy instance",
                    instance_id=instance_id,
                    consecutive_failures=instance.consecutive_failures
                )
                await self.restart_instance(instance_id)
    
    async def cleanup(self) -> None:
        """Clean up all browser instances and resources."""
        self.logger.info("Cleaning up browser cluster")
        
        # Stop monitoring
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        # Close all instances
        cleanup_tasks = []
        for instance in self.instances.values():
            try:
                task = asyncio.create_task(instance.simulator.close_all_sessions())
                cleanup_tasks.append(task)
            except Exception as e:
                self.logger.debug(
                    "Error during instance cleanup",
                    instance_id=instance.instance_id,
                    error=str(e)
                )
        
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        # Clear instance lists
        self.instances.clear()
        self.available_instances.clear()
        self.busy_instances.clear()
        
        self.initialized = False
        self.logger.info("Browser cluster cleanup completed")