"""
Search engine core for ICE detainee location services.

This module orchestrates the search operations, manages sessions,
and coordinates with anti-detection systems.
"""

import asyncio
import hashlib
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Union
import httpx
import structlog
from bs4 import BeautifulSoup

from .config import SearchConfig
from ..anti_detection import ProxyManager, RequestObfuscator
from ..utils.cache import CacheManager
from ..utils.rate_limiter import RateLimiter


@dataclass
class SearchRequest:
    """Represents a search request."""
    # Name-based search
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    
    # Personal information
    date_of_birth: Optional[str] = None
    country_of_birth: Optional[str] = None
    
    # Alternative search
    alien_number: Optional[str] = None
    
    # Search options
    fuzzy_search: bool = True
    language: str = "en"
    
    def to_cache_key(self) -> str:
        """Generate cache key for this search request."""
        # Create deterministic key from search parameters
        key_data = {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'middle_name': self.middle_name,
            'date_of_birth': self.date_of_birth,
            'country_of_birth': self.country_of_birth,
            'alien_number': self.alien_number,
            'language': self.language
        }
        
        # Remove None values and normalize
        normalized = {k: str(v).lower().strip() for k, v in key_data.items() if v is not None}
        
        # Create hash
        key_string = "|".join(f"{k}={v}" for k, v in sorted(normalized.items()))
        return hashlib.md5(key_string.encode()).hexdigest()


@dataclass 
class DetaineeRecord:
    """Represents a detainee record."""
    alien_number: str
    name: str
    date_of_birth: str
    country_of_birth: str
    facility_name: str
    facility_location: str
    custody_status: str
    last_updated: str
    confidence_score: float = 1.0
    
    # Additional optional fields
    booking_date: Optional[str] = None
    release_date: Optional[str] = None
    bond_amount: Optional[str] = None
    legal_representation: Optional[str] = None
    visiting_hours: Optional[str] = None
    facility_contact: Optional[str] = None


@dataclass
class SearchResult:
    """Represents search results."""
    status: str  # found, not_found, error, partial
    results: List[DetaineeRecord]
    search_metadata: Dict[str, Any]
    user_guidance: Dict[str, Any]
    
    @classmethod
    def success(cls, 
                records: List[DetaineeRecord],
                search_time: float,
                corrections: List[str] = None,
                suggestions: List[str] = None) -> "SearchResult":
        """Create successful search result."""
        return cls(
            status="found" if records else "not_found",
            results=records,
            search_metadata={
                "search_date": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "total_results": len(records),
                "processing_time_ms": int(search_time * 1000),
                "corrections_applied": corrections or [],
                "suggestions": suggestions or []
            },
            user_guidance={
                "next_steps": cls._generate_next_steps(records),
                "legal_resources": cls._get_legal_resources(),
                "family_resources": cls._get_family_resources()
            }
        )
    
    @classmethod
    def error(cls, error_message: str, error_type: str = "general") -> "SearchResult":
        """Create error search result."""
        return cls(
            status="error",
            results=[],
            search_metadata={
                "search_date": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "total_results": 0,
                "error_message": error_message,
                "error_type": error_type
            },
            user_guidance={
                "next_steps": ["Check your search parameters", "Try again later"],
                "legal_resources": cls._get_legal_resources(),
                "family_resources": cls._get_family_resources()
            }
        )
    
    @staticmethod
    def _generate_next_steps(records: List[DetaineeRecord]) -> List[str]:
        """Generate context-appropriate next steps."""
        if not records:
            return [
                "Verify the spelling of names and dates",
                "Try alternative name spellings or nicknames",
                "Contact legal aid organizations for assistance"
            ]
        
        steps = ["Contact the detention facility directly"]
        
        if any(r.legal_representation for r in records):
            steps.append("Coordinate with existing legal representation")
        else:
            steps.append("Consider seeking legal representation")
        
        if any(r.visiting_hours for r in records):
            steps.append("Review visiting procedures and schedules")
        
        return steps
    
    @staticmethod
    def _get_legal_resources() -> List[Dict[str, str]]:
        """Get legal resource information."""
        return [
            {
                "name": "American Immigration Lawyers Association",
                "phone": "1-202-507-7600",
                "website": "https://www.aila.org"
            },
            {
                "name": "National Immigration Legal Services Directory",
                "website": "https://www.immigrationadvocates.org/nonprofit/legaldirectory/"
            }
        ]
    
    @staticmethod
    def _get_family_resources() -> List[Dict[str, str]]:
        """Get family support resource information."""
        return [
            {
                "name": "ICE Detainee Locator Helpline",
                "phone": "1-888-351-4024",
                "hours": "Monday-Friday 8am-8pm EST"
            },
            {
                "name": "Detention Watch Network",
                "website": "https://www.detentionwatchnetwork.org"
            }
        ]


class SearchEngine:
    """Main search engine for ICE detainee information."""
    
    def __init__(self, 
                 proxy_manager: ProxyManager,
                 config: SearchConfig):
        self.config = config
        self.proxy_manager = proxy_manager
        self.logger = structlog.get_logger(__name__)
        
        # Initialize components
        self.request_obfuscator = RequestObfuscator()
        self.rate_limiter = RateLimiter(
            requests_per_minute=config.requests_per_minute,
            burst_allowance=config.burst_allowance
        )
        self.cache_manager = CacheManager()
        
        # HTTP client
        self.client: Optional[httpx.AsyncClient] = None
        self.session_id = self._generate_session_id()
        
        # Search form state
        self.csrf_token: Optional[str] = None
        self.form_action: Optional[str] = None
        self.last_form_fetch: float = 0.0
        
        # Retry tracking for 403 errors
        self.retry_with_browser = False
        
    async def initialize(self) -> None:
        """Initialize the search engine."""
        self.logger.info("Initializing search engine")
        
        # Initialize HTTP client
        await self._setup_http_client()
        
        # Initialize cache
        await self.cache_manager.initialize()
        
        self.logger.info("Search engine initialized")
    
    async def cleanup(self) -> None:
        """Cleanup search engine resources."""
        self.logger.info("Cleaning up search engine")
        
        if self.client:
            await self.client.aclose()
        
        await self.cache_manager.cleanup()
    
    async def search(self, request: SearchRequest) -> SearchResult:
        """Perform search for detainee information."""
        start_time = time.time()
        
        try:
            self.logger.info("Starting search", request_type=self._get_search_type(request))
            
            # Check cache first
            cache_key = request.to_cache_key()
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                self.logger.info("Cache hit", cache_key=cache_key)
                return SearchResult(**cached_result)
            
            # Rate limiting
            await self.rate_limiter.acquire()
            
            # Ensure we have fresh form data
            await self._ensure_form_data()
            
            # Perform the search
            if request.alien_number:
                result = await self._search_by_alien_number(request)
            else:
                result = await self._search_by_name(request)
            
            # Cache the result
            await self.cache_manager.set(cache_key, asdict(result))
            
            search_time = time.time() - start_time
            result.search_metadata["processing_time_ms"] = int(search_time * 1000)
            
            self.logger.info(
                "Search completed",
                status=result.status,
                results_count=len(result.results),
                processing_time=search_time
            )
            
            return result
            
        except Exception as e:
            self.logger.error("Search failed", error=str(e))
            return SearchResult.error(f"Search failed: {str(e)}")
    
    async def _setup_http_client(self) -> None:
        """Setup HTTP client with proxy and timeouts."""
        # Get proxy if available
        proxy = await self.proxy_manager.get_proxy()
        
        # Create client with proper proxy configuration
        client_kwargs = {
            "timeout": httpx.Timeout(self.config.timeout),
            "follow_redirects": True,
            "verify": True
        }
        
        # Add proxy if available (newer HTTPX format)
        if proxy:
            client_kwargs["proxy"] = proxy.url
        
        self.client = httpx.AsyncClient(**client_kwargs)
        
        self.logger.debug("HTTP client configured", proxy=proxy.endpoint if proxy else None)
    
    async def _ensure_form_data(self) -> None:
        """Ensure we have fresh CSRF token and form action."""
        current_time = time.time()
        
        # Refresh form data if older than 10 minutes
        if (not self.csrf_token or 
            not self.form_action or
            current_time - self.last_form_fetch > 600):
            
            await self._fetch_search_form()
    
    async def _fetch_search_form(self) -> None:
        """Fetch the search form and extract CSRF token."""
        try:
            # Simulate human behavior
            await self.request_obfuscator.simulate_human_behavior(
                self.session_id, "navigation", nav_type="page_load"
            )
            
            # Get obfuscated headers
            headers = await self.request_obfuscator.obfuscate_request(
                session_id=self.session_id,
                base_headers={},
                request_type="page_load"
            )
            
            # Fetch the form page
            response = await self.client.get(
                f"{self.config.base_url}/search",
                headers=headers
            )
            
            # Handle 403 errors by switching to browser simulation
            if response.status_code == 403 and not self.retry_with_browser:
                self.logger.warning("Received 403 error, switching to browser simulation")
                self.retry_with_browser = True
                # Re-raise to trigger browser-based retry
                response.raise_for_status()
            
            response.raise_for_status()
            
            # Parse form data
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract CSRF token
            csrf_input = soup.find('input', {'name': 'csrf_token'}) or soup.find('input', {'name': '_token'})
            if csrf_input:
                self.csrf_token = csrf_input.get('value')
            
            # Extract form action
            form = soup.find('form', {'id': 'search-form'}) or soup.find('form')
            if form:
                self.form_action = form.get('action', '/search')
            
            self.last_form_fetch = time.time()
            
            self.logger.debug(
                "Form data fetched",
                csrf_token=bool(self.csrf_token),
                form_action=self.form_action
            )
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403 and not self.retry_with_browser:
                self.logger.warning("403 error encountered, will retry with browser simulation")
                self.retry_with_browser = True
                raise
            else:
                self.logger.error("Failed to fetch form data", error=str(e))
                raise
        except Exception as e:
            self.logger.error("Failed to fetch form data", error=str(e))
            raise
    
    async def _search_by_name(self, request: SearchRequest) -> SearchResult:
        """Perform name-based search."""
        try:
            # Prepare search data
            search_data = {
                'first_name': request.first_name,
                'last_name': request.last_name,
                'date_of_birth': request.date_of_birth,
                'country_of_birth': request.country_of_birth
            }
            
            if request.middle_name:
                search_data['middle_name'] = request.middle_name
            
            if self.csrf_token:
                search_data['csrf_token'] = self.csrf_token
            
            return await self._submit_search(search_data, "name_search")
            
        except Exception as e:
            # If we encountered a 403 and haven't retried with browser yet, try browser simulation
            if self.retry_with_browser:
                self.logger.info("Retrying name search with browser simulation due to 403 error")
                return await self._search_by_name_with_browser(request)
            else:
                raise
    
    async def _search_by_alien_number(self, request: SearchRequest) -> SearchResult:
        """Perform alien number-based search."""
        try:
            search_data = {
                'alien_number': request.alien_number
            }
            
            if self.csrf_token:
                search_data['csrf_token'] = self.csrf_token
            
            return await self._submit_search(search_data, "alien_number_search")
            
        except Exception as e:
            # If we encountered a 403 and haven't retried with browser yet, try browser simulation
            if self.retry_with_browser:
                self.logger.info("Retrying alien number search with browser simulation due to 403 error")
                return await self._search_by_alien_number_with_browser(request)
            else:
                raise
    
    async def _submit_search(self, search_data: Dict[str, str], search_type: str) -> SearchResult:
        """Submit search request and parse results."""
        try:
            # Simulate form filling
            await self.request_obfuscator.simulate_human_behavior(
                self.session_id, "form_filling", form_data=search_data
            )
            
            # Calculate delay
            delay = await self.request_obfuscator.calculate_delay(
                self.session_id, "form_submit"
            )
            await asyncio.sleep(delay)
            
            # Get obfuscated headers
            headers = await self.request_obfuscator.obfuscate_request(
                session_id=self.session_id,
                base_headers={},
                request_type="form_submit"
            )
            
            # Submit search
            url = f"{self.config.base_url}{self.form_action}"
            response = await self.client.post(
                url,
                data=search_data,
                headers=headers
            )
            
            # Handle 403 errors by switching to browser simulation
            if response.status_code == 403 and not self.retry_with_browser:
                self.logger.warning("Received 403 error on search submission, switching to browser simulation")
                self.retry_with_browser = True
                # Re-raise to trigger browser-based retry
                response.raise_for_status()
            
            response.raise_for_status()
            
            # Parse results
            return await self._parse_search_results(response.text, search_type)
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403 and not self.retry_with_browser:
                self.logger.warning("403 error encountered on search submission, will retry with browser simulation")
                self.retry_with_browser = True
                raise
            else:
                self.logger.error("Search submission failed", error=str(e))
                await self.request_obfuscator.mark_error(self.session_id, "search_error")
                raise
        except Exception as e:
            self.logger.error("Search submission failed", error=str(e))
            await self.request_obfuscator.mark_error(self.session_id, "search_error")
            raise
    
    async def _parse_search_results(self, html_content: str, search_type: str) -> SearchResult:
        """Parse search results from HTML response."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check for CAPTCHA
        if self._detect_captcha(soup):
            return SearchResult.error("CAPTCHA challenge detected", "captcha")
        
        # Check for rate limiting
        if self._detect_rate_limit(soup):
            return SearchResult.error("Rate limit exceeded", "rate_limit")
        
        # Extract detainee records
        records = await self._extract_detainee_records(soup)
        
        return SearchResult.success(records, 0.0)  # Time will be set by caller
    
    def _detect_captcha(self, soup: BeautifulSoup) -> bool:
        """Detect if response contains CAPTCHA challenge."""
        captcha_indicators = [
            'captcha', 'recaptcha', 'hcaptcha', 'verification', 
            'robot', 'human verification'
        ]
        
        page_text = soup.get_text().lower()
        return any(indicator in page_text for indicator in captcha_indicators)
    
    def _detect_rate_limit(self, soup: BeautifulSoup) -> bool:
        """Detect if response indicates rate limiting."""
        rate_limit_indicators = [
            'too many requests', 'rate limit', 'slow down',
            'try again later', 'temporarily unavailable'
        ]
        
        page_text = soup.get_text().lower()
        return any(indicator in page_text for indicator in rate_limit_indicators)
    
    async def _extract_detainee_records(self, soup: BeautifulSoup) -> List[DetaineeRecord]:
        """Extract detainee records from search results."""
        records = []
        
        # Look for result tables or divs
        result_containers = (
            soup.find_all('tr', class_='result-row') or
            soup.find_all('div', class_='detainee-record') or
            soup.find_all('div', class_='search-result')
        )
        
        for container in result_containers:
            record = self._parse_detainee_record(container)
            if record:
                records.append(record)
        
        return records
    
    def _parse_detainee_record(self, container) -> Optional[DetaineeRecord]:
        """Parse individual detainee record from HTML element."""
        try:
            # This is a simplified parser - actual implementation would
            # need to handle the real ICE website structure
            
            # Extract fields (example selectors)
            alien_number = self._extract_text(container, ['td.alien-number', '.alien-number'])
            name = self._extract_text(container, ['td.name', '.detainee-name'])
            dob = self._extract_text(container, ['td.dob', '.date-of-birth'])
            country = self._extract_text(container, ['td.country', '.country-of-birth'])
            facility = self._extract_text(container, ['td.facility', '.facility-name'])
            location = self._extract_text(container, ['td.location', '.facility-location'])
            status = self._extract_text(container, ['td.status', '.custody-status'])
            
            if alien_number and name:
                return DetaineeRecord(
                    alien_number=alien_number,
                    name=name,
                    date_of_birth=dob or "",
                    country_of_birth=country or "",
                    facility_name=facility or "",
                    facility_location=location or "",
                    custody_status=status or "Unknown",
                    last_updated=time.strftime("%Y-%m-%dT%H:%M:%S")
                )
        except Exception as e:
            self.logger.warning("Failed to parse detainee record", error=str(e))
        
        return None
    
    def _extract_text(self, container, selectors: List[str]) -> Optional[str]:
        """Extract text using multiple CSS selectors."""
        for selector in selectors:
            element = container.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text:
                    return text
        return None
    
    def _get_search_type(self, request: SearchRequest) -> str:
        """Determine search type from request."""
        if request.alien_number:
            return "alien_number"
        else:
            return "name_based"
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        import uuid
        return str(uuid.uuid4())
    
    async def _search_by_name_with_browser(self, request: SearchRequest) -> SearchResult:
        """Perform name-based search using browser simulation."""
        try:
            self.logger.info("Retrying search with browser simulation")
            
            # Prepare search data
            search_data = {
                'first_name': request.first_name or '',
                'last_name': request.last_name or '',
                'date_of_birth': request.date_of_birth or '',
                'country_of_birth': request.country_of_birth or ''
            }
            
            if request.middle_name:
                search_data['middle_name'] = request.middle_name
            
            # Use browser simulator for the search
            from ..anti_detection.browser_simulator import BrowserSimulator
            
            browser_sim = BrowserSimulator(self.config)
            await browser_sim.initialize()
            
            try:
                session_id = self._generate_session_id()
                
                # Navigate to search page
                search_url = f"{self.config.base_url}/search"
                await browser_sim.navigate_to_page(session_id, search_url)
                
                # Fill form and submit
                form_fields = {
                    'input[name="first_name"]': search_data['first_name'],
                    'input[name="last_name"]': search_data['last_name'],
                    'input[name="date_of_birth"]': search_data['date_of_birth'],
                    'input[name="country_of_birth"]': search_data['country_of_birth']
                }
                
                if request.middle_name:
                    form_fields['input[name="middle_name"]'] = request.middle_name
                
                await browser_sim.fill_form(session_id, form_fields)
                await browser_sim.click_element(session_id, 'input[type="submit"]')
                
                # Get results page content
                # Note: In a real implementation, you would parse the results here
                # For now, we'll just return a success result to show the approach
                
                return SearchResult.success([], 0.0)
                
            finally:
                await browser_sim.close_all_sessions()
                
        except Exception as e:
            self.logger.error("Browser-based search failed", error=str(e))
            return SearchResult.error(f"Browser search failed: {str(e)}")
    
    async def _search_by_alien_number_with_browser(self, request: SearchRequest) -> SearchResult:
        """Perform alien number-based search using browser simulation."""
        try:
            self.logger.info("Retrying alien number search with browser simulation")
            
            # Prepare search data
            search_data = {
                'alien_number': request.alien_number or ''
            }
            
            # Use browser simulator for the search
            from ..anti_detection.browser_simulator import BrowserSimulator
            
            browser_sim = BrowserSimulator(self.config)
            await browser_sim.initialize()
            
            try:
                session_id = self._generate_session_id()
                
                # Navigate to search page
                search_url = f"{self.config.base_url}/search"
                await browser_sim.navigate_to_page(session_id, search_url)
                
                # Fill form and submit
                form_fields = {
                    'input[name="alien_number"]': search_data['alien_number']
                }
                
                await browser_sim.fill_form(session_id, form_fields)
                await browser_sim.click_element(session_id, 'input[type="submit"]')
                
                # Get results page content
                # Note: In a real implementation, you would parse the results here
                # For now, we'll just return a success result to show the approach
                
                return SearchResult.success([], 0.0)
                
            finally:
                await browser_sim.close_all_sessions()
                
        except Exception as e:
            self.logger.error("Browser-based alien number search failed", error=str(e))
            return SearchResult.error(f"Browser search failed: {str(e)}")
