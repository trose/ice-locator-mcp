"""
Search tools implementation for ICE Locator MCP Server.

This module implements the actual MCP tools that handle search requests.
"""

import asyncio
import json
import re
import time
from typing import Any, Dict, List, Optional
import structlog
from fuzzywuzzy import fuzz
from phonetics import metaphone, soundex

from ..core.search_engine import SearchEngine, SearchRequest, SearchResult, DetaineeRecord
from ..utils.logging import PerformanceLogger


class SearchTools:
    """Implementation of MCP search tools."""
    
    def __init__(self, search_engine: SearchEngine):
        self.search_engine = search_engine
        self.logger = structlog.get_logger(__name__)
        self.performance_logger = PerformanceLogger()
        
        # Fuzzy matching components
        self.name_variations = self._load_name_variations()
        self.country_mappings = self._load_country_mappings()
        
    async def search_by_name(self,
                           first_name: str,
                           last_name: str,
                           date_of_birth: str,
                           country_of_birth: str,
                           middle_name: Optional[str] = None,
                           language: str = "en",
                           fuzzy_search: bool = True,
                           birth_date_range: int = 0) -> str:
        """Search for detainee by name and personal information."""
        
        start_time = time.time()
        
        try:
            # Validate and normalize input
            request = await self._build_name_search_request(
                first_name=first_name,
                last_name=last_name,
                date_of_birth=date_of_birth,
                country_of_birth=country_of_birth,
                middle_name=middle_name,
                language=language,
                fuzzy_search=fuzzy_search,
                birth_date_range=birth_date_range
            )
            
            # Perform search
            result = await self.search_engine.search(request)
            
            # Apply fuzzy matching if enabled and no exact matches
            if fuzzy_search and result.status == "not_found":
                result = await self._apply_fuzzy_search(request, result)
            
            # Log performance
            processing_time = time.time() - start_time
            await self.performance_logger.log_search_performance(
                search_type="name_search",
                processing_time=processing_time,
                cache_hit=False,  # Would need to track this
                results_count=len(result.results)
            )
            
            return self._format_search_response(result, language)
            
        except Exception as e:
            self.logger.error("Name search failed", error=str(e), first_name=first_name, last_name=last_name)
            return self._format_error_response(str(e), language)
    
    async def search_by_alien_number(self,
                                   alien_number: str,
                                   language: str = "en") -> str:
        """Search for detainee by alien registration number."""
        
        start_time = time.time()
        
        try:
            # Validate alien number format
            if not self._validate_alien_number(alien_number):
                return self._format_error_response(
                    "Invalid alien number format. Should be A followed by 8-9 digits.",
                    language
                )
            
            # Build search request
            request = SearchRequest(
                alien_number=alien_number,
                language=language
            )
            
            # Perform search
            result = await self.search_engine.search(request)
            
            # Log performance
            processing_time = time.time() - start_time
            await self.performance_logger.log_search_performance(
                search_type="alien_number_search",
                processing_time=processing_time,
                cache_hit=False,
                results_count=len(result.results)
            )
            
            return self._format_search_response(result, language)
            
        except Exception as e:
            self.logger.error("Alien number search failed", error=str(e), alien_number=alien_number)
            return self._format_error_response(str(e), language)
    
    async def smart_search(self,
                         query: str,
                         context: Optional[str] = None,
                         suggest_corrections: bool = True,
                         language: str = "en") -> str:
        """AI-powered natural language search."""
        
        start_time = time.time()
        
        try:
            # Parse natural language query
            parsed_params = await self._parse_natural_language_query(query, context)
            
            if not parsed_params:
                return self._format_error_response(
                    "Could not understand the search query. Please provide more specific information.",
                    language
                )
            
            # Apply auto-corrections if enabled
            if suggest_corrections:
                parsed_params = await self._apply_auto_corrections(parsed_params)
            
            # Build search request
            if 'alien_number' in parsed_params:
                request = SearchRequest(
                    alien_number=parsed_params['alien_number'],
                    language=language
                )
            else:
                request = SearchRequest(
                    first_name=parsed_params.get('first_name'),
                    last_name=parsed_params.get('last_name'),
                    middle_name=parsed_params.get('middle_name'),
                    date_of_birth=parsed_params.get('date_of_birth'),
                    country_of_birth=parsed_params.get('country_of_birth'),
                    language=language,
                    fuzzy_search=True
                )
            
            # Perform search
            result = await self.search_engine.search(request)
            
            # Log performance
            processing_time = time.time() - start_time
            await self.performance_logger.log_search_performance(
                search_type="smart_search",
                processing_time=processing_time,
                cache_hit=False,
                results_count=len(result.results)
            )
            
            return self._format_search_response(result, language)
            
        except Exception as e:
            self.logger.error("Smart search failed", error=str(e), query=query)
            return self._format_error_response(str(e), language)
    
    async def bulk_search(self,
                        search_requests: List[Dict[str, Any]],
                        max_concurrent: int = 3,
                        continue_on_error: bool = True) -> str:
        """Search multiple detainees simultaneously."""
        
        start_time = time.time()
        
        try:
            # Validate concurrent limit
            max_concurrent = min(max_concurrent, 5)  # Cap at 5 for safety
            
            # Convert to SearchRequest objects
            requests = []
            for req_data in search_requests:
                if 'alien_number' in req_data:
                    request = SearchRequest(
                        alien_number=req_data['alien_number'],
                        language=req_data.get('language', 'en')
                    )
                else:
                    request = SearchRequest(
                        first_name=req_data.get('first_name'),
                        last_name=req_data.get('last_name'),
                        middle_name=req_data.get('middle_name'),
                        date_of_birth=req_data.get('date_of_birth'),
                        country_of_birth=req_data.get('country_of_birth'),
                        language=req_data.get('language', 'en'),
                        fuzzy_search=req_data.get('fuzzy_search', True)
                    )
                requests.append(request)
            
            # Execute searches with concurrency control
            semaphore = asyncio.Semaphore(max_concurrent)
            results = []
            errors = []
            
            async def process_single_request(request: SearchRequest) -> Optional[SearchResult]:
                async with semaphore:
                    try:
                        return await self.search_engine.search(request)
                    except Exception as e:
                        error_info = {
                            'request': request.__dict__,
                            'error': str(e)
                        }
                        errors.append(error_info)
                        if not continue_on_error:
                            raise
                        return None
            
            # Execute all searches
            tasks = [process_single_request(req) for req in requests]
            completed_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful results
            successful_results = [r for r in completed_results if isinstance(r, SearchResult)]
            
            # Compile bulk result
            bulk_result = {
                'status': 'completed' if not errors else 'partial',
                'total_searches': len(requests),
                'successful_searches': len(successful_results),
                'failed_searches': len(errors),
                'results': [result.__dict__ for result in successful_results],
                'errors': errors if errors else None,
                'processing_time_ms': int((time.time() - start_time) * 1000)
            }
            
            # Log performance
            await self.performance_logger.log_search_performance(
                search_type="bulk_search",
                processing_time=time.time() - start_time,
                cache_hit=False,
                results_count=len(successful_results)
            )
            
            return json.dumps(bulk_result, indent=2)
            
        except Exception as e:
            self.logger.error("Bulk search failed", error=str(e))
            return self._format_error_response(str(e))
    
    async def generate_report(self,
                            search_criteria: Dict[str, Any],
                            results: List[Dict[str, Any]],
                            report_type: str = "legal",
                            format: str = "markdown") -> str:
        """Generate comprehensive reports for legal or advocacy use."""
        
        try:
            if format.lower() == "json":
                return await self._generate_json_report(search_criteria, results, report_type)
            else:
                return await self._generate_markdown_report(search_criteria, results, report_type)
                
        except Exception as e:
            self.logger.error("Report generation failed", error=str(e))
            return self._format_error_response(str(e))
    
    async def _build_name_search_request(self, **kwargs) -> SearchRequest:
        """Build and validate name search request."""
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'date_of_birth', 'country_of_birth']
        for field in required_fields:
            if not kwargs.get(field):
                raise ValueError(f"Missing required field: {field}")
        
        # Normalize names
        first_name = self._normalize_name(kwargs['first_name'])
        last_name = self._normalize_name(kwargs['last_name'])
        middle_name = self._normalize_name(kwargs.get('middle_name')) if kwargs.get('middle_name') else None
        
        # Validate and normalize date
        date_of_birth = self._normalize_date(kwargs['date_of_birth'])
        
        # Normalize country
        country_of_birth = self._normalize_country(kwargs['country_of_birth'])
        
        return SearchRequest(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            date_of_birth=date_of_birth,
            country_of_birth=country_of_birth,
            language=kwargs.get('language', 'en'),
            fuzzy_search=kwargs.get('fuzzy_search', True)
        )
    
    async def _apply_fuzzy_search(self, request: SearchRequest, result: SearchResult) -> SearchResult:
        """Apply fuzzy matching to expand search results."""
        
        # Generate name variations
        name_variations = await self._generate_name_variations(
            request.first_name, request.last_name, request.middle_name
        )
        
        # Try searches with variations
        for first_var, last_var in name_variations[:3]:  # Limit to top 3 variations
            var_request = SearchRequest(
                first_name=first_var,
                last_name=last_var,
                middle_name=request.middle_name,
                date_of_birth=request.date_of_birth,
                country_of_birth=request.country_of_birth,
                language=request.language,
                fuzzy_search=False  # Avoid infinite recursion
            )
            
            var_result = await self.search_engine.search(var_request)
            if var_result.status == "found":
                # Add confidence scores for fuzzy matches
                for record in var_result.results:
                    record.confidence_score = self._calculate_confidence_score(
                        request, record
                    )
                
                # Update metadata to indicate fuzzy match
                var_result.search_metadata["corrections_applied"] = [
                    f"'{request.first_name} {request.last_name}' → '{first_var} {last_var}'"
                ]
                
                return var_result
        
        return result
    
    async def _parse_natural_language_query(self, query: str, context: Optional[str]) -> Optional[Dict[str, str]]:
        """Parse natural language query into search parameters."""
        
        params = {}
        query_lower = query.lower()
        
        # Look for alien number pattern
        alien_pattern = r'a\d{8,9}|\b\d{8,9}\b'
        alien_match = re.search(alien_pattern, query, re.IGNORECASE)
        if alien_match:
            alien_num = alien_match.group()
            if not alien_num.startswith('A'):
                alien_num = 'A' + alien_num
            params['alien_number'] = alien_num
            return params
        
        # Extract names
        name_patterns = [
            r'(?:find|search|locate)\s+([A-Za-z]+(?:\s+[A-Za-z]+)*?)(?:\s+from|\s+born|\s+detained|$)',
            r'([A-Za-z]+\s+[A-Za-z]+)(?:\s+from|\s+born)',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                full_name = match.group(1).strip()
                name_parts = full_name.split()
                if len(name_parts) >= 2:
                    params['first_name'] = name_parts[0]
                    params['last_name'] = name_parts[-1]
                    if len(name_parts) > 2:
                        params['middle_name'] = ' '.join(name_parts[1:-1])
                break
        
        # Extract country
        country_pattern = r'from\s+([A-Za-z\s]+?)(?:\s+born|\s+detained|$)'
        country_match = re.search(country_pattern, query, re.IGNORECASE)
        if country_match:
            params['country_of_birth'] = country_match.group(1).strip()
        
        # Extract birth year/date
        year_pattern = r'(?:born|birth)\s+(?:around\s+)?(\d{4})'
        year_match = re.search(year_pattern, query, re.IGNORECASE)
        if year_match:
            year = year_match.group(1)
            # Use January 1st as default
            params['date_of_birth'] = f"{year}-01-01"
        
        # Full date pattern
        date_pattern = r'(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})'
        date_match = re.search(date_pattern, query)
        if date_match:
            date_str = date_match.group(1)
            params['date_of_birth'] = self._normalize_date(date_str)
        
        return params if len(params) >= 2 else None  # Need at least 2 parameters
    
    async def _apply_auto_corrections(self, params: Dict[str, str]) -> Dict[str, str]:
        """Apply auto-corrections to search parameters."""
        
        corrected = params.copy()
        
        # Name corrections
        for name_field in ['first_name', 'last_name', 'middle_name']:
            if name_field in corrected:
                corrected[name_field] = await self._correct_name(corrected[name_field])
        
        # Country corrections
        if 'country_of_birth' in corrected:
            corrected['country_of_birth'] = await self._correct_country(corrected['country_of_birth'])
        
        return corrected
    
    async def _generate_name_variations(self, first_name: str, last_name: str, middle_name: Optional[str]) -> List[tuple]:
        """Generate variations of names for fuzzy matching."""
        
        variations = []
        
        # Phonetic variations
        first_soundex = soundex(first_name)
        last_soundex = soundex(last_name)
        first_metaphone = metaphone(first_name)
        last_metaphone = metaphone(last_name)
        
        # Common name variations from database
        first_variations = self.name_variations.get(first_name.lower(), [first_name])
        last_variations = self.name_variations.get(last_name.lower(), [last_name])
        
        # Generate combinations
        for first_var in first_variations[:3]:
            for last_var in last_variations[:3]:
                if (first_var, last_var) != (first_name, last_name):
                    variations.append((first_var, last_var))
        
        return variations
    
    def _calculate_confidence_score(self, request: SearchRequest, record: DetaineeRecord) -> float:
        """Calculate confidence score for fuzzy matches."""
        
        score = 0.0
        weights = {'name': 0.4, 'date': 0.3, 'country': 0.3}
        
        # Name similarity
        request_name = f"{request.first_name} {request.last_name}".lower()
        record_name = record.name.lower()
        name_similarity = fuzz.ratio(request_name, record_name) / 100.0
        score += name_similarity * weights['name']
        
        # Date similarity (exact match or close)
        if request.date_of_birth and record.date_of_birth:
            if request.date_of_birth == record.date_of_birth:
                score += weights['date']
            else:
                # Partial credit for similar dates
                date_similarity = 0.5  # Simplified
                score += date_similarity * weights['date']
        
        # Country similarity
        if request.country_of_birth and record.country_of_birth:
            country_similarity = fuzz.ratio(
                request.country_of_birth.lower(),
                record.country_of_birth.lower()
            ) / 100.0
            score += country_similarity * weights['country']
        
        return min(score, 1.0)
    
    def _normalize_name(self, name: str) -> str:
        """Normalize name format."""
        return ' '.join(word.capitalize() for word in name.strip().split())
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date to YYYY-MM-DD format."""
        # Handle various date formats
        date_str = date_str.strip()
        
        # Already in YYYY-MM-DD format
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str
        
        # MM/DD/YYYY format
        if re.match(r'^\d{2}/\d{2}/\d{4}$', date_str):
            month, day, year = date_str.split('/')
            return f"{year}-{month}-{day}"
        
        # DD-MM-YYYY format
        if re.match(r'^\d{2}-\d{2}-\d{4}$', date_str):
            day, month, year = date_str.split('-')
            return f"{year}-{month}-{day}"
        
        raise ValueError(f"Invalid date format: {date_str}")
    
    def _normalize_country(self, country: str) -> str:
        """Normalize country name."""
        country = country.strip()
        return self.country_mappings.get(country.lower(), country)
    
    def _validate_alien_number(self, alien_number: str) -> bool:
        """Validate alien number format."""
        # Should be A followed by 8-9 digits
        pattern = r'^A\d{8,9}$'
        return bool(re.match(pattern, alien_number.upper()))
    
    async def _correct_name(self, name: str) -> str:
        """Apply name corrections."""
        # This would use the auto-correction database
        return self.name_variations.get(name.lower(), [name])[0]
    
    async def _correct_country(self, country: str) -> str:
        """Apply country name corrections."""
        return self.country_mappings.get(country.lower(), country)
    
    def _load_name_variations(self) -> Dict[str, List[str]]:
        """Load name variations database."""
        # In practice, this would load from a file or database
        return {
            'jose': ['josé', 'joseph', 'joe'],
            'maria': ['maría', 'mary', 'marie'],
            'gonzalez': ['gonzález', 'gonzales'],
            'rodriguez': ['rodríguez', 'rodrigues'],
            'martinez': ['martínez', 'martines'],
            'garcia': ['garcía'],
            'lopez': ['lópez'],
            'hernandez': ['hernández'],
            'perez': ['pérez'],
            'sanchez': ['sánchez']
        }
    
    def _load_country_mappings(self) -> Dict[str, str]:
        """Load country name mappings."""
        return {
            'mexico': 'Mexico',
            'méxico': 'Mexico',
            'guatemala': 'Guatemala',
            'el salvador': 'El Salvador',
            'salvador': 'El Salvador',
            'honduras': 'Honduras',
            'nicaragua': 'Nicaragua',
            'costa rica': 'Costa Rica',
            'panama': 'Panama',
            'panamá': 'Panama',
            'colombia': 'Colombia',
            'venezuela': 'Venezuela',
            'ecuador': 'Ecuador',
            'peru': 'Peru',
            'perú': 'Peru',
            'bolivia': 'Bolivia',
            'brazil': 'Brazil',
            'brasil': 'Brazil',
            'argentina': 'Argentina',
            'chile': 'Chile',
            'uruguay': 'Uruguay',
            'paraguay': 'Paraguay'
        }
    
    def _format_search_response(self, result: SearchResult, language: str = "en") -> str:
        """Format search response for MCP client."""
        return json.dumps(result.__dict__, indent=2, default=str)
    
    def _format_error_response(self, error_message: str, language: str = "en") -> str:
        """Format error response."""
        error_response = {
            "status": "error",
            "error_message": error_message,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "language": language
        }
        return json.dumps(error_response, indent=2)
    
    async def _generate_markdown_report(self, criteria: Dict, results: List[Dict], report_type: str) -> str:
        """Generate markdown format report."""
        
        report = f"""# ICE Detainee Search Report

## Search Information
- **Date**: {time.strftime("%Y-%m-%d %H:%M:%S")}
- **Report Type**: {report_type.title()}
- **Search Criteria**: {json.dumps(criteria, indent=2)}

## Results Summary
- **Total Results**: {len(results)}
- **Search Status**: {'Found' if results else 'Not Found'}

"""
        
        if results:
            report += "## Detainee Information\n\n"
            for i, result in enumerate(results, 1):
                for record in result.get('results', []):
                    report += f"""### Record {i}
- **Name**: {record.get('name', 'N/A')}
- **Alien Number**: {record.get('alien_number', 'N/A')}
- **Date of Birth**: {record.get('date_of_birth', 'N/A')}
- **Country of Birth**: {record.get('country_of_birth', 'N/A')}
- **Facility**: {record.get('facility_name', 'N/A')}
- **Location**: {record.get('facility_location', 'N/A')}
- **Status**: {record.get('custody_status', 'N/A')}
- **Last Updated**: {record.get('last_updated', 'N/A')}

"""
        
        if report_type == "legal":
            report += """## Legal Considerations
- Verify all information independently
- Contact facility directly for current status
- Consider legal representation if needed

## Next Steps
1. Contact the detention facility
2. Gather required documentation
3. Consider visiting procedures
4. Seek legal counsel if appropriate

"""
        
        report += """---
*This report was generated by ICE Locator MCP Server*
*Information is subject to change - verify independently*
"""
        
        return report
    
    async def _generate_json_report(self, criteria: Dict, results: List[Dict], report_type: str) -> str:
        """Generate JSON format report."""
        
        report = {
            "report_metadata": {
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "report_type": report_type,
                "search_criteria": criteria,
                "total_results": len(results)
            },
            "results": results,
            "recommendations": self._get_recommendations_for_report_type(report_type),
            "legal_resources": SearchResult._get_legal_resources(),
            "family_resources": SearchResult._get_family_resources()
        }
        
        return json.dumps(report, indent=2, default=str)
    
    def _get_recommendations_for_report_type(self, report_type: str) -> List[str]:
        """Get recommendations based on report type."""
        
        if report_type == "legal":
            return [
                "Verify all information independently with the detention facility",
                "Gather required documentation for legal proceedings",
                "Consider immediate legal representation",
                "Review visiting procedures and restrictions",
                "Document all communications with facilities"
            ]
        elif report_type == "advocacy":
            return [
                "Contact local immigration advocacy organizations",
                "Document conditions and treatment",
                "Coordinate with other affected families",
                "Engage with media if appropriate",
                "Monitor policy changes and advocacy opportunities"
            ]
        else:  # family
            return [
                "Contact the facility to arrange visits",
                "Gather necessary identification for visiting",
                "Consider contacting legal aid organizations",
                "Connect with family support groups",
                "Stay informed about the case status"
            ]