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
        
        # Check for access denied or blocked responses
        if self._detect_access_denied(soup):
            return SearchResult.error("Access denied - IP may be blocked", "access_denied")
        
        # Check for maintenance pages
        if self._detect_maintenance(soup):
            return SearchResult.error("Website is currently under maintenance", "maintenance")
        
        # Check for session expiration
        if self._detect_session_expired(soup):
            return SearchResult.error("Session expired - please try again", "session_expired")
        
        # Check for no results found
        if self._detect_no_results(soup):
            return SearchResult.success([], 0.0)  # Return empty results but success status
        
        # Extract detainee records
        records = await self._extract_detainee_records(soup)
        
        return SearchResult.success(records, 0.0)  # Time will be set by caller
    
    def _detect_captcha(self, soup: BeautifulSoup) -> bool:
        """Detect if response contains CAPTCHA challenge."""
        captcha_indicators = [
            'captcha', 'recaptcha', 'hcaptcha', 'verification', 
            'robot', 'human verification', 'prove you are human'
        ]
        
        page_text = soup.get_text().lower()
        return any(indicator in page_text for indicator in captcha_indicators)
    
    def _detect_rate_limit(self, soup: BeautifulSoup) -> bool:
        """Detect if response indicates rate limiting."""
        rate_limit_indicators = [
            'too many requests', 'rate limit', 'slow down',
            'try again later', 'temporarily unavailable',
            '429', 'request limit'
        ]
        
        page_text = soup.get_text().lower()
        title = soup.title.get_text().lower() if soup.title else ""
        
        return (any(indicator in page_text for indicator in rate_limit_indicators) or
                any(indicator in title for indicator in rate_limit_indicators))
    
    def _detect_access_denied(self, soup: BeautifulSoup) -> bool:
        """Detect if response indicates access denied."""
        access_denied_indicators = [
            'access denied', 'forbidden', '403', 'not authorized',
            'blocked', 'ip blocked', 'suspicious activity',
            'security check', 'unusual traffic'
        ]
        
        page_text = soup.get_text().lower()
        title = soup.title.get_text().lower() if soup.title else ""
        
        return (any(indicator in page_text for indicator in access_denied_indicators) or
                any(indicator in title for indicator in access_denied_indicators))
    
    def _detect_maintenance(self, soup: BeautifulSoup) -> bool:
        """Detect if response indicates website maintenance."""
        maintenance_indicators = [
            'maintenance', 'down for maintenance', 'scheduled maintenance',
            'site unavailable', 'temporarily offline', 'system maintenance'
        ]
        
        page_text = soup.get_text().lower()
        title = soup.title.get_text().lower() if soup.title else ""
        
        return (any(indicator in page_text for indicator in maintenance_indicators) or
                any(indicator in title for indicator in maintenance_indicators))
    
    def _detect_session_expired(self, soup: BeautifulSoup) -> bool:
        """Detect if response indicates session expiration."""
        session_expired_indicators = [
            'session expired', 'login required', 'authentication required',
            'session timeout', 'please log in', 'login again'
        ]
        
        page_text = soup.get_text().lower()
        title = soup.title.get_text().lower() if soup.title else ""
        
        return (any(indicator in page_text for indicator in session_expired_indicators) or
                any(indicator in title for indicator in session_expired_indicators))
    
    def _detect_no_results(self, soup: BeautifulSoup) -> bool:
        """Detect if response indicates no results found."""
        no_results_indicators = [
            'no results found', 'no records found', 'no matches',
            'nothing found', '0 results', 'zero results',
            'no detainees found', 'no individuals found'
        ]
        
        page_text = soup.get_text().lower()
        title = soup.title.get_text().lower() if soup.title else ""
        
        return (any(indicator in page_text for indicator in no_results_indicators) or
                any(indicator in title for indicator in no_results_indicators))
    
    async def _extract_detainee_records(self, soup: BeautifulSoup) -> List[DetaineeRecord]:
        """Extract detainee records from search results."""
        records = []
        
        # Look for result tables or divs with more specific selectors
        result_containers = (
            soup.find_all('tr', class_='result-row') or
            soup.find_all('div', class_='detainee-record') or
            soup.find_all('div', class_='search-result') or
            soup.find_all('tbody', class_='results') or
            soup.find_all('div', {'data-record': True}) or
            soup.find_all('table')  # Fallback to any table
        )
        
        for container in result_containers:
            record = self._parse_detainee_record(container)
            if record:
                records.append(record)
        
        # If no records found, try a more general approach
        if not records:
            records = await self._extract_records_general(soup)
            
        # If still no records, try to parse any table that might contain results
        if not records:
            records = await self._extract_records_from_any_table(soup)
        
        return records
    
    async def _extract_records_from_any_table(self, soup: BeautifulSoup) -> List[DetaineeRecord]:
        """Extract detainee records from any table that might contain results."""
        records = []
        
        # Look for any table with potential detainee data
        tables = soup.find_all('table')
        for table in tables:
            # Check if this looks like a detainee table
            headers = table.find_all('th')
            if headers:
                header_texts = [h.get_text(strip=True).lower() for h in headers]
                # Look for common header names in detainee records
                common_headers = ['alien', 'number', 'name', 'birth', 'country', 'facility', 'status', 'location']
                matching_headers = [h for h in header_texts if any(ch in h for ch in common_headers)]
                
                if len(matching_headers) >= 3:  # At least 3 matching headers
                    # Look for rows with data
                    rows = table.find_all('tr')[1:]  # Skip header row
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 3:
                            # Try to extract basic information
                            record = await self._parse_table_row_as_record(cells, header_texts)
                            if record:
                                records.append(record)
            else:
                # No headers, try to parse based on cell content
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        # Try to extract basic information
                        record = self._parse_row_as_record(cells)
                        if record:
                            records.append(record)
        
        return records
    
    async def _parse_table_row_as_record(self, cells, header_texts: List[str]) -> Optional[DetaineeRecord]:
        """Parse a table row as a detainee record using header information."""
        try:
            # Create a mapping from header names to cell values
            cell_values = [cell.get_text(strip=True) for cell in cells]
            
            # Initialize fields
            alien_number = ""
            name = ""
            dob = ""
            country = ""
            facility = ""
            location = ""
            status = ""
            
            # Map header names to fields
            for i, header in enumerate(header_texts):
                if i < len(cell_values):
                    cell_value = cell_values[i]
                    header_lower = header.lower()
                    
                    if 'alien' in header_lower or 'number' in header_lower:
                        # Check if this looks like an alien number
                        if cell_value.startswith('A') and len(cell_value) >= 9 and cell_value[1:].isdigit():
                            alien_number = cell_value
                        elif not alien_number and 'A' in cell_value and len(cell_value) >= 9:
                            # Try to extract alien number from mixed text
                            import re
                            alien_match = re.search(r'A\d{8,9}', cell_value)
                            if alien_match:
                                alien_number = alien_match.group(0)
                    elif 'name' in header_lower:
                        name = cell_value
                    elif 'birth' in header_lower or 'dob' in header_lower:
                        dob = cell_value
                    elif 'country' in header_lower:
                        country = cell_value
                    elif 'facility' in header_lower:
                        facility = cell_value
                    elif 'location' in header_lower:
                        location = cell_value
                    elif 'status' in header_lower:
                        status = cell_value
            
            # If we couldn't match by headers, try content-based matching
            if not alien_number or not name:
                for cell_value in cell_values:
                    if not alien_number and cell_value.startswith('A') and len(cell_value) >= 9 and cell_value[1:].isdigit():
                        alien_number = cell_value
                    elif not alien_number and 'A' in cell_value and len(cell_value) >= 9:
                        import re
                        alien_match = re.search(r'A\d{8,9}', cell_value)
                        if alien_match:
                            alien_number = alien_match.group(0)
                    elif not name and ',' in cell_value and len(cell_value.split()) >= 2:
                        name = cell_value  # Assume name format is "Last, First"
            
            # Create a record if we have at least an alien number or name
            if alien_number or name:
                return DetaineeRecord(
                    alien_number=alien_number or "Unknown",
                    name=name or "Unknown",
                    date_of_birth=dob or "",
                    country_of_birth=country or "",
                    facility_name=facility or "",
                    facility_location=location or "",
                    custody_status=status or "Unknown",
                    last_updated=time.strftime("%Y-%m-%dT%H:%M:%S")
                )
        except Exception as e:
            self.logger.warning("Failed to parse table row as record", error=str(e))
        
        return None
    
    async def _extract_records_general(self, soup: BeautifulSoup) -> List[DetaineeRecord]:
        """General approach to extract detainee records when specific selectors fail."""
        records = []
        
        # Look for any table with potential detainee data
        tables = soup.find_all('table')
        for table in tables:
            # Check if this looks like a detainee table
            headers = table.find_all('th')
            if headers and len(headers) >= 3:  # At least 3 columns for basic info
                # Look for rows with data
                rows = table.find_all('tr')[1:]  # Skip header row
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        # Try to extract basic information
                        record = self._parse_row_as_record(cells)
                        if record:
                            records.append(record)
        
        return records
    
    def _parse_row_as_record(self, cells) -> Optional[DetaineeRecord]:
        """Parse a table row as a detainee record."""
        try:
            # This is a very basic parser that would need to be refined
            # based on the actual ICE website structure
            if len(cells) >= 3:
                # Try to identify which cell contains what information
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                # Look for patterns that might indicate an alien number
                alien_number = ""
                name = ""
                dob = ""
                country = ""
                facility = ""
                location = ""
                status = ""
                
                for text in cell_texts:
                    if text.startswith('A') and len(text) >= 9 and text[1:].isdigit():
                        alien_number = text
                    elif ',' in text and len(text.split()) >= 2:
                        name = text  # Assume name format is "Last, First"
                
                # Create a basic record if we have at least an alien number or name
                if alien_number or name:
                    return DetaineeRecord(
                        alien_number=alien_number or "Unknown",
                        name=name or "Unknown",
                        date_of_birth=dob or "",
                        country_of_birth=country or "",
                        facility_name=facility or "",
                        facility_location=location or "",
                        custody_status=status or "Unknown",
                        last_updated=time.strftime("%Y-%m-%dT%H:%M:%S")
                    )
        except Exception as e:
            self.logger.warning("Failed to parse row as record", error=str(e))
        
        return None
    
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
                page_content = await browser_sim.navigate_to_page(session_id, search_url)
                
                # Parse the page to understand the form structure
                soup = BeautifulSoup(page_content, 'html.parser')
                
                # Try to find the search form
                form = soup.find('form', {'action': lambda x: x and 'search' in x.lower()}) or soup.find('form')
                if not form:
                    return SearchResult.error("Could not find search form on page", "form_not_found")
                
                # Extract form action
                form_action = form.get('action', '/search')
                if not form_action.startswith('http'):
                    form_action = f"{self.config.base_url}{form_action}"
                
                # Fill form and submit with enhanced human-like behavior
                form_fields = {}
                
                # Try to map our search data to form fields
                # This is a simplified approach - in reality, we'd need to inspect the actual form
                input_mapping = {
                    'first_name': ['first_name', 'firstName', 'first-name'],
                    'last_name': ['last_name', 'lastName', 'last-name'],
                    'date_of_birth': ['date_of_birth', 'dob', 'date-of-birth', 'birth_date'],
                    'country_of_birth': ['country_of_birth', 'country', 'country-of-birth'],
                    'middle_name': ['middle_name', 'middleName', 'middle-name']
                }
                
                # Find form inputs and map them
                form_inputs = form.find_all('input')
                for field_name, possible_names in input_mapping.items():
                    if field_name in search_data and search_data[field_name]:
                        # Look for matching input
                        for input_elem in form_inputs:
                            input_name = input_elem.get('name', '').lower()
                            if any(name in input_name for name in possible_names):
                                form_fields[f'input[name="{input_elem.get("name")}"]'] = search_data[field_name]
                                break
                
                # Special handling for alien number search
                if 'alien_number' in search_data and search_data['alien_number']:
                    for input_elem in form_inputs:
                        input_name = input_elem.get('name', '').lower()
                        if 'alien' in input_name or 'a_number' in input_name:
                            form_fields[f'input[name="{input_elem.get("name")}"]'] = search_data['alien_number']
                
                if form_fields:
                    # Use enhanced human-like form filling
                    await browser_sim.simulate_human_form_filling(session_id, form_fields)
                    
                    # Try to find and click submit button with human-like behavior
                    submit_selectors = [
                        'input[type="submit"]',
                        'button[type="submit"]',
                        'input[value*="search" i]',
                        'button:has-text("Search")'
                    ]
                    
                    submit_clicked = False
                    for selector in submit_selectors:
                        try:
                            await browser_sim.click_element(session_id, selector)
                            submit_clicked = True
                            break
                        except:
                            continue  # Try next selector
                    
                    if not submit_clicked:
                        return SearchResult.error("Could not find submit button", "submit_not_found")
                    
                    # Wait for results and get page content
                    await asyncio.sleep(2)  # Wait for page to load
                    results_content = await browser_sim.navigate_to_page(session_id, form_action)
                    
                    # Parse results
                    results_soup = BeautifulSoup(results_content, 'html.parser')
                    records = await self._extract_detainee_records(results_soup)
                    
                    return SearchResult.success(records, 0.0)
                else:
                    return SearchResult.error("Could not map search fields to form inputs", "field_mapping_error")
                
            finally:
                await browser_sim.close_all_sessions()
                
        except Exception as e:
            self.logger.error("Browser-based search failed", error=str(e))
            return SearchResult.error(f"Browser search failed: {str(e)}")
    
    async def _search_by_alien_number_with_browser(self, request: SearchRequest) -> SearchResult:
        """Perform alien number-based search using browser simulation."""
        # For now, we can use the same implementation as name search
        # since the browser simulation handles both cases
        return await self._search_by_name_with_browser(request)
