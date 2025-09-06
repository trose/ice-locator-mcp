"""
Proxy management system for anti-detection and IP rotation.
"""

import asyncio
import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Any
import httpx
import structlog
from fake_useragent import UserAgent

from ..core.config import ProxyConfig


class ProxyStatus(Enum):
    """Proxy status enumeration."""
    HEALTHY = "healthy"
    FAILED = "failed" 
    TESTING = "testing"
    COOLING_DOWN = "cooling_down"


@dataclass 
class ProxyMetrics:
    """Metrics for proxy performance tracking."""
    request_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    last_used: float = 0.0
    last_success: float = 0.0
    last_failure: float = 0.0
    average_response_time: float = 0.0
    consecutive_failures: int = 0
    reputation_score: float = 0.5  # Normalized score (0-1)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.request_count == 0:
            return 0.0
        return self.success_count / self.request_count
    
    @property
    def is_healthy(self) -> bool:
        """Check if proxy is considered healthy."""
        # Consider unhealthy if more than 3 consecutive failures
        if self.consecutive_failures >= 3:
            return False
        
        # Consider unhealthy if success rate below 70% with at least 5 requests
        if self.request_count >= 5 and self.success_rate < 0.7:
            return False
            
        # Consider unhealthy if reputation score is too low
        if self.reputation_score < 0.3:
            return False
            
        return True


@dataclass 
class ProxyConfig:
    """Configuration for a single proxy."""
    endpoint: str
    proxy_type: str = "http"  # http, https, socks4, socks5
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    is_residential: bool = False
    
    @property
    def url(self) -> str:
        """Get properly formatted proxy URL."""
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"
        else:
            auth = ""
        
        return f"{self.proxy_type}://{auth}{self.endpoint}"
    
    def __hash__(self) -> int:
        return hash(self.endpoint)


class ProxyManager:
    """Manages proxy pool with rotation and health monitoring."""
    
    def __init__(self, config: ProxyConfig):
        self.config = config
        self.logger = structlog.get_logger(__name__)
        
        # Proxy pool management
        self.proxy_pool: List[ProxyConfig] = []
        self.proxy_metrics: Dict[str, ProxyMetrics] = {}
        self.proxy_status: Dict[str, ProxyStatus] = {}
        self.failed_proxies: Set[str] = set()
        
        # Rotation state
        self.current_proxy_index = 0
        self.last_rotation_time = 0.0
        self.rotation_lock = asyncio.Lock()
        
        # Health monitoring
        self.health_check_task: Optional[asyncio.Task] = None
        self.monitoring_active = False
        
    async def initialize(self) -> None:
        """Initialize proxy manager and load proxy pool."""
        self.logger.info("Initializing proxy manager")
        
        if not self.config.enabled:
            self.logger.warning(
                "Proxy management DISABLED - Direct access to ICE website will likely fail with 403 errors. "
                "The ICE website implements anti-bot measures that require proxy usage for bypassing. "
                "To enable proxies, set ICE_LOCATOR_PROXY_ENABLED=true"
            )
            return
        
        # Load initial proxy pool
        await self._load_proxy_pool()
        
        # Start health monitoring
        if self.proxy_pool:
            await self._start_health_monitoring()
            self.logger.info(
                "Proxy manager initialized", 
                proxy_count=len(self.proxy_pool)
            )
        else:
            self.logger.warning("No proxies available, running without proxy")
    
    async def get_proxy(self) -> Optional[ProxyConfig]:
        """Get next available proxy with rotation logic."""
        if not self.config.enabled or not self.proxy_pool:
            return None
        
        async with self.rotation_lock:
            # Check if rotation is needed
            current_time = time.time()
            if (current_time - self.last_rotation_time) >= self.config.rotation_interval:
                await self._rotate_proxy()
                self.last_rotation_time = current_time
            
            # Get current proxy
            healthy_proxies = self._get_healthy_proxies()
            if not healthy_proxies:
                self.logger.warning("No healthy proxies available")
                await self._refresh_proxy_pool()
                healthy_proxies = self._get_healthy_proxies()
                
                if not healthy_proxies:
                    return None
            
            # Select proxy based on strategy
            selected_proxy = await self._select_proxy(healthy_proxies)
            
            # Update usage metrics
            await self._update_proxy_usage(selected_proxy)
            
            return selected_proxy
    
    async def mark_proxy_success(self, proxy: ProxyConfig, response_time: float) -> None:
        """Mark proxy as successful and update metrics."""
        metrics = self.proxy_metrics.get(proxy.endpoint, ProxyMetrics())
        
        metrics.success_count += 1
        metrics.last_success = time.time()
        metrics.consecutive_failures = 0
        
        # Update average response time
        if metrics.average_response_time == 0:
            metrics.average_response_time = response_time
        else:
            # Exponential moving average
            metrics.average_response_time = (
                metrics.average_response_time * 0.8 + response_time * 0.2
            )
        
        self.proxy_metrics[proxy.endpoint] = metrics
        self.proxy_status[proxy.endpoint] = ProxyStatus.HEALTHY
        
        # Remove from failed set if it was there
        self.failed_proxies.discard(proxy.endpoint)
        
        self.logger.debug(
            "Proxy success recorded",
            proxy=proxy.endpoint,
            response_time=response_time,
            success_rate=metrics.success_rate
        )
    
    async def mark_proxy_failure(self, proxy: ProxyConfig, error: Exception) -> None:
        """Mark proxy as failed and update metrics."""
        metrics = self.proxy_metrics.get(proxy.endpoint, ProxyMetrics())
        
        metrics.failure_count += 1
        metrics.last_failure = time.time()
        metrics.consecutive_failures += 1
        
        self.proxy_metrics[proxy.endpoint] = metrics
        
        # Mark as failed if too many consecutive failures
        if metrics.consecutive_failures >= 3:
            self.proxy_status[proxy.endpoint] = ProxyStatus.FAILED
            self.failed_proxies.add(proxy.endpoint)
            
            self.logger.warning(
                "Proxy marked as failed",
                proxy=proxy.endpoint,
                consecutive_failures=metrics.consecutive_failures,
                error=str(error)
            )
        else:
            self.proxy_status[proxy.endpoint] = ProxyStatus.COOLING_DOWN
            
            self.logger.debug(
                "Proxy failure recorded",
                proxy=proxy.endpoint,
                consecutive_failures=metrics.consecutive_failures,
                error=str(error)
            )
    
    async def cleanup(self) -> None:
        """Cleanup proxy manager resources."""
        self.logger.info("Cleaning up proxy manager")
        
        self.monitoring_active = False
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
    
    def _get_healthy_proxies(self) -> List[ProxyConfig]:
        """Get list of currently healthy proxies."""
        healthy = []
        
        for proxy in self.proxy_pool:
            status = self.proxy_status.get(proxy.endpoint, ProxyStatus.HEALTHY)
            metrics = self.proxy_metrics.get(proxy.endpoint, ProxyMetrics())
            
            if (status == ProxyStatus.HEALTHY and 
                proxy.endpoint not in self.failed_proxies and
                metrics.is_healthy):
                healthy.append(proxy)
        
        return healthy
    
    async def _select_proxy(self, healthy_proxies: List[ProxyConfig]) -> ProxyConfig:
        """Select proxy based on configured strategy."""
        if len(healthy_proxies) == 1:
            return healthy_proxies[0]
        
        # Performance-based selection (prefer faster, more reliable proxies)
        def proxy_score(proxy: ProxyConfig) -> float:
            metrics = self.proxy_metrics.get(proxy.endpoint, ProxyMetrics())
            
            # Base score from success rate (0-1 scale)
            score = metrics.success_rate
            
            # Bonus for residential proxies (0-0.1)
            if proxy.is_residential:
                score += 0.1
            
            # Bonus for good reputation score (0-0.2)
            if hasattr(metrics, 'reputation_score'):
                score += metrics.reputation_score * 0.2
            
            # Bonus for faster response times (lower is better) (0-0.2)
            if metrics.average_response_time > 0:
                # Normalize response time (assume 5s is very slow)
                time_score = max(0, 1 - (metrics.average_response_time / 5.0))
                score += time_score * 0.2
            
            # Penalty for recent usage (load balancing) (-0.1)
            time_since_use = time.time() - metrics.last_used
            if time_since_use < 60:  # Used within last minute
                score -= 0.1
            
            # Bonus for geolocation verification (0-0.1)
            if hasattr(metrics, 'geolocation_verified') and metrics.geolocation_verified:
                score += 0.1
            
            # Bonus for anonymity verification (0-0.1)
            if hasattr(metrics, 'anonymity_verified') and metrics.anonymity_verified:
                score += 0.1
            
            # Bonus for consistent performance (0-0.15)
            if hasattr(metrics, 'performance_history') and len(metrics.performance_history) > 3:
                # Calculate consistency (lower variance = higher score)
                import statistics
                try:
                    variance = statistics.variance(metrics.performance_history)
                    consistency_score = max(0, 1 - (variance / 10))  # Normalize
                    score += consistency_score * 0.15
                except statistics.StatisticsError:
                    pass  # Not enough data for variance calculation
            
            return max(0, score)  # Ensure non-negative score
        
        # Sort by score and add some randomness
        sorted_proxies = sorted(healthy_proxies, key=proxy_score, reverse=True)
        
        # Select from top 3 with weighted randomness
        top_proxies = sorted_proxies[:min(3, len(sorted_proxies))]
        weights = [3, 2, 1][:len(top_proxies)]
        
        return random.choices(top_proxies, weights=weights)[0]
    
    async def _update_proxy_usage(self, proxy: ProxyConfig) -> None:
        """Update proxy usage statistics."""
        metrics = self.proxy_metrics.get(proxy.endpoint, ProxyMetrics())
        
        metrics.request_count += 1
        metrics.last_used = time.time()
        
        self.proxy_metrics[proxy.endpoint] = metrics
    
    async def _rotate_proxy(self) -> None:
        """Perform proxy rotation logic."""
        # This is called automatically based on rotation_interval
        # The actual rotation happens in get_proxy() method
        self.logger.debug("Proxy rotation triggered")
    
    async def _load_proxy_pool(self) -> None:
        """Load proxy pool from configured sources."""
        if self.config.proxy_list_file and self.config.proxy_list_file.exists():
            await self._load_from_file()
        else:
            await self._load_from_sources()
    
    async def _load_from_file(self) -> None:
        """Load proxies from file."""
        try:
            with open(self.config.proxy_list_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        proxy = self._parse_proxy_line(line)
                        if proxy:
                            self.proxy_pool.append(proxy)
                            self.proxy_status[proxy.endpoint] = ProxyStatus.HEALTHY
            
            self.logger.info(
                "Loaded proxies from file",
                file=str(self.config.proxy_list_file),
                count=len(self.proxy_pool)
            )
        except Exception as e:
            self.logger.error("Failed to load proxies from file", error=str(e))
    
    async def _load_from_sources(self) -> None:
        """Load proxies from configured sources."""
        # Try to load from actual proxy providers
        loaded_proxies = await self._fetch_from_proxy_providers()
        
        if loaded_proxies:
            for proxy in loaded_proxies:
                self.proxy_pool.append(proxy)
                self.proxy_status[proxy.endpoint] = ProxyStatus.HEALTHY
            
            self.logger.info("Loaded real proxy pool", count=len(self.proxy_pool))
        else:
            # Fall back to direct connections if no proxies available
            self.logger.warning(
                "No real proxies available, system will use direct connections. "
                "For production use, configure real proxy sources for better anti-detection."
            )
            
            # Add a warning to the proxy status
            self.proxy_status["DIRECT_CONNECTION"] = ProxyStatus.HEALTHY
    
    async def _fetch_from_proxy_providers(self) -> List[ProxyConfig]:
        """Fetch proxies from actual providers."""
        proxies = []
        
        # Try multiple proxy sources
        try:
            # Fetch from various proxy sources
            free_proxies = await self._fetch_from_free_proxy_sources()
            proxies.extend(free_proxies)
            
            # Fetch from premium sources if configured
            premium_proxies = await self._fetch_from_premium_sources()
            proxies.extend(premium_proxies)
            
            # Validate and filter proxies
            validated_proxies = await self._validate_proxies(proxies)
            
            self.logger.info(
                "Fetched proxies from providers",
                total=len(proxies),
                validated=len(validated_proxies)
            )
            
            return validated_proxies
            
        except Exception as e:
            self.logger.debug("Failed to fetch proxies from providers", error=str(e))
        
        return proxies
    
    async def _fetch_from_free_proxy_sources(self) -> List[ProxyConfig]:
        """Fetch proxies from free proxy sources."""
        proxies = []
        
        # Common free proxy sources
        sources = [
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://www.proxy-list.download/api/v1/get?type=https",
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all",
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all"
        ]
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            for source in sources:
                try:
                    response = await client.get(source)
                    if response.status_code == 200:
                        # Parse proxy list (format varies by source)
                        proxy_lines = response.text.strip().split('\n')
                        for line in proxy_lines:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                proxy = self._parse_proxy_line(line)
                                if proxy:
                                    proxies.append(proxy)
                    
                    await asyncio.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    self.logger.debug(
                        "Failed to fetch from proxy source",
                        source=source,
                        error=str(e)
                    )
        
        return proxies
    
    async def _fetch_from_premium_sources(self) -> List[ProxyConfig]:
        """Fetch proxies from premium sources (if API keys configured)."""
        proxies = []
        
        # Premium proxy services that require API keys
        # These would be configured through environment variables
        import os
        
        # ScraperAPI
        scraperapi_key = os.getenv("SCRAPERAPI_KEY")
        if scraperapi_key:
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.get(
                        f"http://api.scraperapi.com?api_key={scraperapi_key}&url=https://httpbin.org/ip"
                    )
                    if response.status_code == 200:
                        # ScraperAPI works as a proxy endpoint
                        proxy = ProxyConfig(
                            endpoint=f"proxy-server.scraperapi.com:8001",
                            proxy_type="http",
                            username=scraperapi_key,
                            password="scraperapi",
                            is_residential=True
                        )
                        proxies.append(proxy)
            except Exception as e:
                self.logger.debug(
                    "Failed to fetch from ScraperAPI",
                    error=str(e)
                )
        
        # BrightData (formerly BrightData)
        brightdata_username = os.getenv("BRIGHTDATA_USERNAME")
        brightdata_password = os.getenv("BRIGHTDATA_PASSWORD")
        brightdata_zone = os.getenv("BRIGHTDATA_ZONE", "zone")
        if brightdata_username and brightdata_password:
            try:
                # BrightData residential proxy
                proxy = ProxyConfig(
                    endpoint="brd.superproxy.io:22225",
                    proxy_type="http",
                    username=brightdata_username,
                    password=brightdata_password,
                    is_residential=True
                )
                proxies.append(proxy)
            except Exception as e:
                self.logger.debug(
                    "Failed to configure BrightData proxy",
                    error=str(e)
                )
        
        # SmartProxy
        smartproxy_username = os.getenv("SMARTPROXY_USERNAME")
        smartproxy_password = os.getenv("SMARTPROXY_PASSWORD")
        if smartproxy_username and smartproxy_password:
            try:
                # SmartProxy residential proxy
                proxy = ProxyConfig(
                    endpoint="us.smartproxy.com:10000",
                    proxy_type="http",
                    username=smartproxy_username,
                    password=smartproxy_password,
                    is_residential=True
                )
                proxies.append(proxy)
            except Exception as e:
                self.logger.debug(
                    "Failed to configure SmartProxy",
                    error=str(e)
                )
        
        # NetNut
        netnut_username = os.getenv("NETNUT_USERNAME")
        netnut_password = os.getenv("NETNUT_PASSWORD")
        if netnut_username and netnut_password:
            try:
                # NetNut residential proxy
                proxy = ProxyConfig(
                    endpoint="gw.netnut.io:8888",
                    proxy_type="http",
                    username=netnut_username,
                    password=netnut_password,
                    is_residential=True
                )
                proxies.append(proxy)
            except Exception as e:
                self.logger.debug(
                    "Failed to configure NetNut proxy",
                    error=str(e)
                )
        
        # Oxylabs
        oxylabs_username = os.getenv("OXYLABS_USERNAME")
        oxylabs_password = os.getenv("OXYLABS_PASSWORD")
        if oxylabs_username and oxylabs_password:
            try:
                # Oxylabs residential proxy
                proxy = ProxyConfig(
                    endpoint="pr.oxylabs.io:7777",
                    proxy_type="http",
                    username=oxylabs_username,
                    password=oxylabs_password,
                    is_residential=True
                )
                proxies.append(proxy)
            except Exception as e:
                self.logger.debug(
                    "Failed to configure Oxylabs proxy",
                    error=str(e)
                )
        
        # GeoSurf
        geosurf_token = os.getenv("GEOSURF_TOKEN")
        if geosurf_token:
            try:
                # GeoSurf residential proxy
                proxy = ProxyConfig(
                    endpoint="gw.geosurf.io:8000",
                    proxy_type="http",
                    username="token",
                    password=geosurf_token,
                    is_residential=True
                )
                proxies.append(proxy)
            except Exception as e:
                self.logger.debug(
                    "Failed to configure GeoSurf proxy",
                    error=str(e)
                )
        
        # Infatica
        infatica_key = os.getenv("INFATICA_KEY")
        if infatica_key:
            try:
                # Infatica residential proxy
                proxy = ProxyConfig(
                    endpoint="proxy.infatica.io:8080",
                    proxy_type="http",
                    username=infatica_key,
                    password=infatica_key,
                    is_residential=True
                )
                proxies.append(proxy)
            except Exception as e:
                self.logger.debug(
                    "Failed to configure Infatica proxy",
                    error=str(e)
                )
        
        # Storm Proxies
        storm_username = os.getenv("STORM_USERNAME")
        storm_password = os.getenv("STORM_PASSWORD")
        if storm_username and storm_password:
            try:
                # Storm Proxies residential proxy
                proxy = ProxyConfig(
                    endpoint="proxy.stormproxies.com:1000",
                    proxy_type="http",
                    username=storm_username,
                    password=storm_password,
                    is_residential=True
                )
                proxies.append(proxy)
            except Exception as e:
                self.logger.debug(
                    "Failed to configure Storm Proxies",
                    error=str(e)
                )
        
        return proxies
    
    async def _validate_proxies(self, proxies: List[ProxyConfig]) -> List[ProxyConfig]:
        """Validate and filter proxies based on connectivity and performance."""
        validated_proxies = []
        
        # Test a sample of proxies to avoid overwhelming the system
        test_proxies = random.sample(proxies, min(20, len(proxies)))
        
        async def test_proxy(proxy: ProxyConfig) -> Optional[ProxyConfig]:
            try:
                async with httpx.AsyncClient(
                    proxies={"http://": proxy.url, "https://": proxy.url},
                    timeout=10.0
                ) as client:
                    # Test basic connectivity
                    response = await client.get("http://httpbin.org/ip", timeout=10.0)
                    if response.status_code == 200:
                        # Test ICE website access
                        ice_response = await client.get("https://locator.ice.gov", timeout=10.0)
                        if ice_response.status_code in [200, 301, 302]:
                            return proxy
            except Exception:
                pass
            return None
        
        # Test proxies concurrently
        tasks = [test_proxy(proxy) for proxy in test_proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, ProxyConfig):
                validated_proxies.append(result)
        
        self.logger.info(
            "Proxy validation completed",
            tested=len(test_proxies),
            validated=len(validated_proxies)
        )
        
        return validated_proxies
    
    def _parse_proxy_line(self, line: str) -> Optional[ProxyConfig]:
        """Parse proxy configuration from line."""
        try:
            # Format: host:port or host:port:username:password
            parts = line.split(':')
            
            if len(parts) >= 2:
                host = parts[0]
                port = parts[1]
                endpoint = f"{host}:{port}"
                
                username = parts[2] if len(parts) > 2 else None
                password = parts[3] if len(parts) > 3 else None
                
                return ProxyConfig(
                    endpoint=endpoint,
                    username=username,
                    password=password
                )
        except Exception as e:
            self.logger.warning("Failed to parse proxy line", line=line, error=str(e))
        
        return None
    
    async def _refresh_proxy_pool(self) -> None:
        """Refresh proxy pool by removing failed proxies and adding new ones."""
        # Remove failed proxies
        self.proxy_pool = [
            proxy for proxy in self.proxy_pool 
            if proxy.endpoint not in self.failed_proxies
        ]
        
        # Reset failed proxies set (give them another chance later)
        old_failed_count = len(self.failed_proxies)
        self.failed_proxies.clear()
        
        # Reset proxy status for cooling down proxies
        for endpoint, status in self.proxy_status.items():
            if status == ProxyStatus.COOLING_DOWN:
                self.proxy_status[endpoint] = ProxyStatus.HEALTHY
        
        self.logger.info(
            "Refreshed proxy pool",
            removed_failed=old_failed_count,
            current_pool_size=len(self.proxy_pool)
        )
    
    async def _start_health_monitoring(self) -> None:
        """Start background health monitoring task."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.health_check_task = asyncio.create_task(self._health_monitor_loop())
    
    async def _health_monitor_loop(self) -> None:
        """Background loop for proxy health monitoring."""
        while self.monitoring_active:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Health monitoring error", error=str(e))
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _perform_health_checks(self) -> None:
        """Perform health checks on proxy pool."""
        if not self.proxy_pool:
            return
        
        # Check a subset of proxies each time to avoid overload
        proxies_to_check = random.sample(
            self.proxy_pool, 
            min(3, len(self.proxy_pool))
        )
        
        for proxy in proxies_to_check:
            try:
                await self._health_check_proxy(proxy)
            except Exception as e:
                self.logger.debug(
                    "Health check failed for proxy",
                    proxy=proxy.endpoint,
                    error=str(e)
                )
    
    async def _perform_basic_connectivity_check(self, proxy: ProxyConfig) -> None:
        """Basic connectivity test."""
        async with httpx.AsyncClient(
            proxies={"http://": proxy.url, "https://": proxy.url},
            timeout=10.0
        ) as client:
            start_time = time.time()
            response = await client.get("http://httpbin.org/ip")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                await self.mark_proxy_success(proxy, response_time)
            else:
                await self.mark_proxy_failure(proxy, Exception(f"HTTP {response.status_code}"))
    
    async def _perform_performance_check(self, proxy: ProxyConfig) -> None:
        """Test proxy performance with multiple requests."""
        performance_metrics = []
        
        for i in range(3):  # Test with 3 requests
            try:
                async with httpx.AsyncClient(
                    proxies={"http://": proxy.url, "https://": proxy.url},
                    timeout=15.0
                ) as client:
                    start_time = time.time()
                    response = await client.get("http://httpbin.org/delay/1")
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        performance_metrics.append(response_time)
                    
                    await asyncio.sleep(0.5)  # Brief pause between tests
                    
            except Exception:
                break  # Stop testing on first failure
        
        if performance_metrics:
            avg_performance = sum(performance_metrics) / len(performance_metrics)
            metrics = self.proxy_metrics.get(proxy.endpoint, ProxyMetrics())
            
            # Update performance data
            if not hasattr(metrics, 'performance_history'):
                metrics.performance_history = deque(maxlen=10)
            metrics.performance_history.append(avg_performance)
            
            self.proxy_metrics[proxy.endpoint] = metrics
    
    async def _perform_anonymity_check(self, proxy: ProxyConfig) -> None:
        """Check if proxy properly hides real IP."""
        try:
            # Get IP without proxy first
            async with httpx.AsyncClient(timeout=10.0) as direct_client:
                direct_response = await direct_client.get("http://httpbin.org/ip")
                real_ip = direct_response.json().get('origin', '')
            
            # Get IP through proxy
            async with httpx.AsyncClient(
                proxies={"http://": proxy.url, "https://": proxy.url},
                timeout=10.0
            ) as proxy_client:
                proxy_response = await proxy_client.get("http://httpbin.org/ip")
                proxy_ip = proxy_response.json().get('origin', '')
            
            # Check if IPs are different (anonymity working)
            metrics = self.proxy_metrics.get(proxy.endpoint, ProxyMetrics())
            if not hasattr(metrics, 'anonymity_verified'):
                metrics.anonymity_verified = False
            
            if proxy_ip != real_ip and proxy_ip:
                metrics.anonymity_verified = True
                self.logger.debug(
                    "Proxy anonymity verified",
                    proxy=proxy.endpoint,
                    real_ip=real_ip[:8] + "...",  # Partial IP for privacy
                    proxy_ip=proxy_ip[:8] + "..."
                )
            else:
                metrics.anonymity_verified = False
                self.logger.warning(
                    "Proxy anonymity failed",
                    proxy=proxy.endpoint
                )
            
            self.proxy_metrics[proxy.endpoint] = metrics
            
        except Exception as e:
            self.logger.debug(
                "Anonymity check failed",
                proxy=proxy.endpoint,
                error=str(e)
            )
    
    async def _perform_geolocation_check(self, proxy: ProxyConfig) -> None:
        """Verify proxy geolocation matches expected region."""
        if not proxy.country:
            return  # Skip if no expected country
        
        try:
            async with httpx.AsyncClient(
                proxies={"http://": proxy.url, "https://": proxy.url},
                timeout=15.0
            ) as client:
                # Use a geolocation service
                response = await client.get("http://ip-api.com/json")
                
                if response.status_code == 200:
                    geo_data = response.json()
                    detected_country = geo_data.get('countryCode', '')
                    
                    metrics = self.proxy_metrics.get(proxy.endpoint, ProxyMetrics())
                    if not hasattr(metrics, 'geolocation_verified'):
                        metrics.geolocation_verified = False
                    
                    if detected_country.upper() == proxy.country.upper():
                        metrics.geolocation_verified = True
                        self.logger.debug(
                            "Proxy geolocation verified",
                            proxy=proxy.endpoint,
                            expected=proxy.country,
                            detected=detected_country
                        )
                    else:
                        metrics.geolocation_verified = False
                        self.logger.warning(
                            "Proxy geolocation mismatch",
                            proxy=proxy.endpoint,
                            expected=proxy.country,
                            detected=detected_country
                        )
                    
                    self.proxy_metrics[proxy.endpoint] = metrics
                    
        except Exception as e:
            self.logger.debug(
                "Geolocation check failed",
                proxy=proxy.endpoint,
                error=str(e)
            )

    async def _perform_ip_reputation_check(self, proxy: ProxyConfig) -> None:
        """Check IP reputation using multiple reputation services."""
        try:
            # Get the proxy's IP address
            async with httpx.AsyncClient(
                proxies={"http://": proxy.url, "https://": proxy.url},
                timeout=15.0
            ) as client:
                response = await client.get("http://httpbin.org/ip")
                if response.status_code == 200:
                    proxy_ip = response.json().get('origin', '').split(',')[0].strip()
                    
                    if proxy_ip:
                        # Check reputation using multiple services
                        reputation_score = await self._check_ip_reputation(proxy_ip)
                        
                        metrics = self.proxy_metrics.get(proxy.endpoint, ProxyMetrics())
                        metrics.reputation_score = reputation_score
                        
                        # Mark as failed if reputation is too low
                        if reputation_score < 0.3:  # Below 30% is considered bad
                            self.logger.warning(
                                "Proxy has poor reputation",
                                proxy=proxy.endpoint,
                                ip=proxy_ip,
                                reputation_score=reputation_score
                            )
                            await self.mark_proxy_failure(proxy, Exception("Poor IP reputation"))
                        else:
                            self.logger.debug(
                                "Proxy reputation check completed",
                                proxy=proxy.endpoint,
                                ip=proxy_ip,
                                reputation_score=reputation_score
                            )
                        
                        self.proxy_metrics[proxy.endpoint] = metrics
        except Exception as e:
            self.logger.debug(
                "IP reputation check failed",
                proxy=proxy.endpoint,
                error=str(e)
            )

    async def _check_ip_reputation(self, ip: str) -> float:
        """Check IP reputation using multiple services and return normalized score (0-1)."""
        scores = []
        
        # Check using ip-api.com for basic info
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"http://ip-api.com/json/{ip}")
                if response.status_code == 200:
                    data = response.json()
                    # Simple heuristic: if ISP is known residential provider, higher score
                    isp = data.get('isp', '').lower()
                    org = data.get('org', '').lower()
                    
                    # Known residential ISPs get higher scores
                    residential_isps = [
                        'comcast', 'verizon', 'att', 'spectrum', 'xfinity', 
                        'cox communications', 'centurylink', 'frontier communications',
                        'charter communications', 'bt', 'virgin media', 'sky broadband',
                        'telefonica', 'orange', 'free', 'sfr', 'bouygues', 'vodafone',
                        'telekom', 't-mobile', 'o2', 'vodafone', 'three', 'ee',
                        'rogers', 'bell', 'telus', 'shaw', 'videotron'
                    ]
                    
                    if any(residential_isp in isp or residential_isp in org 
                          for residential_isp in residential_isps):
                        scores.append(0.9)
                    elif data.get('hosting', False):
                        # Hosting providers get lower scores
                        scores.append(0.2)
                    else:
                        # Unknown gets medium score
                        scores.append(0.5)
        except Exception:
            scores.append(0.5)  # Default score if check fails
        
        # Check using a simple heuristic based on IP ranges
        try:
            # Datacenter IPs often have specific patterns
            octets = ip.split('.')
            if len(octets) == 4:
                first_octet = int(octets[0])
                # Certain ranges are more likely to be residential
                residential_ranges = [
                    (1, 126),   # Class A except special ranges
                    (128, 191), # Class B
                    (192, 223)  # Class C
                ]
                
                is_likely_residential = any(
                    start <= first_octet <= end 
                    for start, end in residential_ranges
                )
                
                if is_likely_residential:
                    scores.append(0.7)
                else:
                    scores.append(0.3)
        except Exception:
            scores.append(0.5)
        
        # Add more sophisticated checks for known datacenter IP ranges
        try:
            # Known datacenter IP ranges get lower scores
            datacenter_ranges = [
                ('172.16.0.0', '172.31.255.255'),  # AWS
                ('10.0.0.0', '10.255.255.255'),     # Private networks
                ('192.168.0.0', '192.168.255.255'), # Private networks
                ('100.64.0.0', '100.127.255.255'),   # Carrier-grade NAT
            ]
            
            def ip_to_int(ip_str):
                """Convert IP string to integer for comparison."""
                parts = ip_str.split('.')
                return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])
            
            ip_int = ip_to_int(ip)
            is_datacenter = any(
                ip_to_int(start) <= ip_int <= ip_to_int(end)
                for start, end in datacenter_ranges
            )
            
            if is_datacenter:
                scores.append(0.2)
            else:
                scores.append(0.6)
        except Exception:
            scores.append(0.5)
        
        # Return average score
        return sum(scores) / len(scores) if scores else 0.5

    async def _health_check_proxy(self, proxy: ProxyConfig) -> None:
        """Perform comprehensive health check on a single proxy."""
        try:
            await self._perform_basic_connectivity_check(proxy)
            await self._perform_performance_check(proxy)
            await self._perform_anonymity_check(proxy)
            await self._perform_geolocation_check(proxy)
            await self._perform_ip_reputation_check(proxy)  # Add reputation check
            
        except Exception as e:
            await self.mark_proxy_failure(proxy, e)

    async def get_proxy_analytics(self) -> Dict[str, Any]:
        """Get comprehensive proxy pool analytics."""
        current_time = time.time()
        
        # Overall statistics
        total_proxies = len(self.proxy_pool)
        healthy_proxies = len(self._get_healthy_proxies())
        failed_proxies = len(self.failed_proxies)
        
        # Performance metrics
        all_metrics = list(self.proxy_metrics.values())
        if all_metrics:
            avg_success_rate = sum(m.success_rate for m in all_metrics) / len(all_metrics)
            avg_response_time = sum(m.average_response_time for m in all_metrics if m.average_response_time > 0) / max(1, len([m for m in all_metrics if m.average_response_time > 0]))
            total_requests = sum(m.request_count for m in all_metrics)
        else:
            avg_success_rate = 0.0
            avg_response_time = 0.0
            total_requests = 0
        
        # Geographic distribution
        country_distribution = {}
        residential_count = 0
        
        for proxy in self.proxy_pool:
            if proxy.country:
                country_distribution[proxy.country] = country_distribution.get(proxy.country, 0) + 1
            if proxy.is_residential:
                residential_count += 1
        
        # Health status breakdown
        status_breakdown = {status.value: 0 for status in ProxyStatus}
        for status in self.proxy_status.values():
            status_breakdown[status.value] += 1
        
        # Recent performance trends
        recent_failures = 0
        recent_successes = 0
        
        for metrics in all_metrics:
            if current_time - metrics.last_failure < 3600:  # Last hour
                recent_failures += 1
            if current_time - metrics.last_success < 3600:  # Last hour
                recent_successes += 1
        
        return {
            'overview': {
                'total_proxies': total_proxies,
                'healthy_proxies': healthy_proxies,
                'failed_proxies': failed_proxies,
                'health_percentage': (healthy_proxies / max(1, total_proxies)) * 100
            },
            'performance': {
                'average_success_rate': avg_success_rate,
                'average_response_time': avg_response_time,
                'total_requests': total_requests,
                'recent_failures': recent_failures,
                'recent_successes': recent_successes
            },
            'distribution': {
                'by_country': country_distribution,
                'residential_proxies': residential_count,
                'datacenter_proxies': total_proxies - residential_count
            },
            'status_breakdown': status_breakdown,
            'rotation_info': {
                'last_rotation': current_time - self.last_rotation_time,
                'rotation_interval': self.config.rotation_interval
            }
        }
    
    async def get_proxy_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations for proxy pool optimization."""
        recommendations = []
        
        analytics = await self.get_proxy_analytics()
        
        # Health-based recommendations
        health_percentage = analytics['overview']['health_percentage']
        if health_percentage < 50:
            recommendations.append({
                'type': 'critical',
                'title': 'Low Proxy Health',
                'description': f'Only {health_percentage:.1f}% of proxies are healthy',
                'action': 'Add more proxies or refresh proxy list',
                'priority': 'high'
            })
        
        # Performance recommendations
        avg_response_time = analytics['performance']['average_response_time']
        if avg_response_time > 5.0:
            recommendations.append({
                'type': 'performance',
                'title': 'Slow Proxy Performance',
                'description': f'Average response time is {avg_response_time:.1f}s',
                'action': 'Consider faster proxy providers or increase timeout',
                'priority': 'medium'
            })
        
        # Geographic diversity
        country_count = len(analytics['distribution']['by_country'])
        if country_count < 3:
            recommendations.append({
                'type': 'diversity',
                'title': 'Limited Geographic Diversity',
                'description': f'Proxies from only {country_count} countries',
                'action': 'Add proxies from different geographic regions',
                'priority': 'low'
            })
        
        # Residential vs datacenter balance
        total_proxies = analytics['overview']['total_proxies']
        residential_count = analytics['distribution']['residential_proxies']
        if total_proxies > 0 and residential_count / total_proxies < 0.3:
            recommendations.append({
                'type': 'quality',
                'title': 'Low Residential Proxy Ratio',
                'description': f'Only {residential_count}/{total_proxies} proxies are residential',
                'action': 'Increase residential proxy ratio for better detection avoidance',
                'priority': 'medium'
            })
        
        return recommendations
    
    async def optimize_proxy_pool(self) -> Dict[str, Any]:
        """Automatically optimize proxy pool based on performance data."""
        optimization_results = {
            'actions_taken': [],
            'proxies_removed': 0,
            'proxies_demoted': 0,
            'settings_adjusted': []
        }
        
        current_time = time.time()
        
        # Remove consistently failing proxies
        proxies_to_remove = []
        for proxy in self.proxy_pool:
            metrics = self.proxy_metrics.get(proxy.endpoint, ProxyMetrics())
            
            # Remove if success rate is very low with sufficient data
            if (metrics.request_count >= 10 and 
                metrics.success_rate < 0.2):
                proxies_to_remove.append(proxy)
            
            # Remove if not used successfully in last 24 hours
            elif (current_time - metrics.last_success > 86400 and 
                  metrics.request_count > 0):
                proxies_to_remove.append(proxy)
        
        for proxy in proxies_to_remove:
            self.proxy_pool.remove(proxy)
            self.failed_proxies.add(proxy.endpoint)
            optimization_results['proxies_removed'] += 1
            optimization_results['actions_taken'].append(
                f"Removed underperforming proxy: {proxy.endpoint}"
            )
        
        # Adjust rotation interval based on success rates
        avg_success_rate = sum(
            m.success_rate for m in self.proxy_metrics.values()
        ) / max(1, len(self.proxy_metrics))
        
        if avg_success_rate < 0.7:
            # Low success rate - increase rotation interval
            old_interval = self.config.rotation_interval
            self.config.rotation_interval = min(3600, old_interval * 1.5)
            optimization_results['settings_adjusted'].append(
                f"Increased rotation interval from {old_interval}s to {self.config.rotation_interval}s"
            )
        
        elif avg_success_rate > 0.9:
            # High success rate - can decrease rotation interval
            old_interval = self.config.rotation_interval
            self.config.rotation_interval = max(300, old_interval * 0.8)
            optimization_results['settings_adjusted'].append(
                f"Decreased rotation interval from {old_interval}s to {self.config.rotation_interval}s"
            )
        
        self.logger.info(
            "Proxy pool optimized",
            **optimization_results
        )
        
        return optimization_results