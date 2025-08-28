"""
Natural Language Query Processor for ICE Locator MCP Server.

This module handles parsing of natural language queries into structured
search parameters with intelligent extraction and auto-correction.
"""

import re
import calendar
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import structlog


@dataclass
class ParsedQuery:
    """Result of natural language query parsing."""
    search_type: str  # name_based, alien_number, facility
    parameters: Dict[str, Any]
    confidence: float
    suggestions: List[str]
    corrections_applied: List[str]
    ambiguities: List[str]


class DateParser:
    """Parse various date formats and expressions."""
    
    def __init__(self):
        self.current_year = datetime.now().year
        self.month_names = {
            month.lower(): i for i, month in enumerate(calendar.month_name[1:], 1)
        }
        self.month_abbrev = {
            month.lower(): i for i, month in enumerate(calendar.month_abbr[1:], 1)
        }
        
    def parse_date(self, date_str: str) -> Optional[str]:
        """Parse natural language date into YYYY-MM-DD format."""
        date_str = date_str.lower().strip()
        
        # Exact date patterns
        patterns = [
            # YYYY-MM-DD
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', self._parse_ymd),
            # MM/DD/YYYY
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', self._parse_mdy),
            # DD/MM/YYYY (European)
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', self._parse_dmy),
            # Month DD, YYYY
            (r'([a-z]+)\s+(\d{1,2}),?\s+(\d{4})', self._parse_month_day_year),
            # DD Month YYYY
            (r'(\d{1,2})\s+([a-z]+)\s+(\d{4})', self._parse_day_month_year),
            # Just year
            (r'^(\d{4})$', self._parse_year_only),
            # "born around 1990"
            (r'(?:around|about|circa)\s+(\d{4})', self._parse_approximate_year),
            # "born in 1990"
            (r'(?:in|during)\s+(\d{4})', self._parse_year_only),
        ]
        
        for pattern, parser in patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    return parser(match)
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def _parse_ymd(self, match) -> str:
        """Parse YYYY-MM-DD format."""
        year, month, day = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    
    def _parse_mdy(self, match) -> str:
        """Parse MM/DD/YYYY format."""
        month, day, year = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    
    def _parse_dmy(self, match) -> str:
        """Parse DD/MM/YYYY format (European)."""
        day, month, year = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    
    def _parse_month_day_year(self, match) -> str:
        """Parse 'Month DD, YYYY' format."""
        month_str, day, year = match.groups()
        month_num = self._parse_month_name(month_str)
        if month_num:
            return f"{year}-{month_num:02d}-{int(day):02d}"
        raise ValueError("Invalid month name")
    
    def _parse_day_month_year(self, match) -> str:
        """Parse 'DD Month YYYY' format."""
        day, month_str, year = match.groups()
        month_num = self._parse_month_name(month_str)
        if month_num:
            return f"{year}-{month_num:02d}-{int(day):02d}"
        raise ValueError("Invalid month name")
    
    def _parse_year_only(self, match) -> str:
        """Parse year only, default to January 1st."""
        year = match.groups()[0]
        return f"{year}-01-01"
    
    def _parse_approximate_year(self, match) -> str:
        """Parse approximate year."""
        year = match.groups()[0]
        return f"{year}-01-01"
    
    def _parse_month_name(self, month_str: str) -> Optional[int]:
        """Parse month name or abbreviation."""
        month_str = month_str.lower()
        return self.month_names.get(month_str) or self.month_abbrev.get(month_str)


class NameExtractor:
    """Extract and normalize names from natural language."""
    
    def __init__(self):
        self.common_prefixes = {
            'mr', 'mrs', 'ms', 'miss', 'dr', 'prof', 'sr', 'jr'
        }
        self.spanish_articles = {
            'de', 'del', 'de la', 'van', 'von', 'da', 'do', 'dos'
        }
        
    def extract_name(self, text: str) -> Optional[Dict[str, str]]:
        """Extract name components from text."""
        # Common patterns for name extraction
        patterns = [
            # "find John Doe"
            r'(?:find|search|locate)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            # "looking for Maria Garcia"
            r'(?:looking for|seeking)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            # Direct name patterns
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b',
            # Quoted names
            r'"([^"]+)"',
            r"'([^']+)'"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                name_parts = self._parse_name_components(match)
                if name_parts and len(name_parts.get('tokens', [])) >= 2:
                    return name_parts
        
        return None
    
    def _parse_name_components(self, full_name: str) -> Optional[Dict[str, str]]:
        """Parse full name into components."""
        full_name = full_name.strip()
        if not full_name:
            return None
        
        # Split into tokens and clean
        tokens = [token.strip() for token in full_name.split()]
        tokens = [token for token in tokens if token and token.lower() not in self.common_prefixes]
        
        if len(tokens) < 2:
            return None
        
        # Handle compound last names (e.g., "de la Cruz")
        processed_tokens = []
        i = 0
        while i < len(tokens):
            if tokens[i].lower() in self.spanish_articles and i + 1 < len(tokens):
                # Combine article with next token
                compound = tokens[i] + " " + tokens[i + 1]
                if i + 2 < len(tokens) and tokens[i + 2].lower() in self.spanish_articles:
                    # Handle "de la" style compounds
                    compound += " " + tokens[i + 2]
                    i += 3
                else:
                    i += 2
                processed_tokens.append(compound)
            else:
                processed_tokens.append(tokens[i])
                i += 1
        
        # Assign components
        if len(processed_tokens) == 2:
            return {
                'first_name': processed_tokens[0],
                'last_name': processed_tokens[1],
                'tokens': processed_tokens
            }
        elif len(processed_tokens) == 3:
            return {
                'first_name': processed_tokens[0],
                'middle_name': processed_tokens[1],
                'last_name': processed_tokens[2],
                'tokens': processed_tokens
            }
        elif len(processed_tokens) > 3:
            # Multiple middle names or compound names
            return {
                'first_name': processed_tokens[0],
                'middle_name': ' '.join(processed_tokens[1:-1]),
                'last_name': processed_tokens[-1],
                'tokens': processed_tokens
            }
        
        return None


class LocationExtractor:
    """Extract location and country information."""
    
    def __init__(self):
        self.country_aliases = self._load_country_aliases()
        self.us_states = self._load_us_states()
        
    def extract_country(self, text: str) -> Optional[str]:
        """Extract country from text."""
        text = text.lower()
        
        # Direct country mentions
        for country, aliases in self.country_aliases.items():
            for alias in aliases:
                if alias.lower() in text:
                    return country
        
        # Pattern-based extraction
        patterns = [
            r'from\s+([A-Za-z\s]+?)(?:\s+born|\s+detained|$)',
            r'born\s+in\s+([A-Za-z\s]+?)(?:\s+on|\s+in|\s+around|$)',
            r'citizen\s+of\s+([A-Za-z\s]+?)(?:\s|$)',
            r'native\s+of\s+([A-Za-z\s]+?)(?:\s|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Try to map to known country
                normalized = self._normalize_country(location)
                if normalized:
                    return normalized
        
        return None
    
    def extract_facility_location(self, text: str) -> Optional[str]:
        """Extract facility or detention location."""
        patterns = [
            r'(?:detained|held)\s+(?:at|in)\s+([A-Za-z\s,]+?)(?:\s|$)',
            r'(?:facility|center)\s+(?:in|at)\s+([A-Za-z\s,]+?)(?:\s|$)',
            r'(?:prison|jail)\s+(?:in|at)\s+([A-Za-z\s,]+?)(?:\s|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _normalize_country(self, location: str) -> Optional[str]:
        """Normalize location to standard country name."""
        location = location.lower().strip()
        
        for country, aliases in self.country_aliases.items():
            if location in [alias.lower() for alias in aliases]:
                return country
        
        return None
    
    def _load_country_aliases(self) -> Dict[str, List[str]]:
        """Load country aliases and variations."""
        return {
            'Mexico': ['mexico', 'méxico', 'mexican', 'mx'],
            'Guatemala': ['guatemala', 'guatemalan', 'gt'],
            'El Salvador': ['el salvador', 'salvador', 'salvadoran', 'sv'],
            'Honduras': ['honduras', 'honduran', 'hn'],
            'Nicaragua': ['nicaragua', 'nicaraguan', 'ni'],
            'Costa Rica': ['costa rica', 'costarrican', 'cr'],
            'Panama': ['panama', 'panamá', 'panamanian', 'pa'],
            'Colombia': ['colombia', 'colombian', 'co'],
            'Venezuela': ['venezuela', 'venezuelan', 've'],
            'Ecuador': ['ecuador', 'ecuadorian', 'ec'],
            'Peru': ['peru', 'perú', 'peruvian', 'pe'],
            'Bolivia': ['bolivia', 'bolivian', 'bo'],
            'Brazil': ['brazil', 'brasil', 'brazilian', 'br'],
            'Argentina': ['argentina', 'argentinian', 'ar'],
            'Chile': ['chile', 'chilean', 'cl'],
            'Uruguay': ['uruguay', 'uruguayan', 'uy'],
            'Paraguay': ['paraguay', 'paraguayan', 'py'],
            'Cuba': ['cuba', 'cuban', 'cu'],
            'Dominican Republic': ['dominican republic', 'dominican', 'dr', 'rd'],
            'Haiti': ['haiti', 'haitian', 'ht'],
            'Jamaica': ['jamaica', 'jamaican', 'jm'],
            'Puerto Rico': ['puerto rico', 'pr'],
            'China': ['china', 'chinese', 'cn'],
            'India': ['india', 'indian', 'in'],
            'Philippines': ['philippines', 'filipino', 'ph'],
            'Vietnam': ['vietnam', 'vietnamese', 'vn'],
            'South Korea': ['south korea', 'korea', 'korean', 'kr'],
            'Nigeria': ['nigeria', 'nigerian', 'ng'],
            'Ethiopia': ['ethiopia', 'ethiopian', 'et'],
            'Somalia': ['somalia', 'somali', 'so'],
            'Ukraine': ['ukraine', 'ukrainian', 'ua'],
            'Russia': ['russia', 'russian', 'ru'],
            'Poland': ['poland', 'polish', 'pl']
        }
    
    def _load_us_states(self) -> Dict[str, str]:
        """Load US state names and abbreviations."""
        return {
            'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
            'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
            'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
            'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
            'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
            'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
            'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
            'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
            'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
            'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
            'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
            'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
            'wisconsin': 'WI', 'wyoming': 'WY'
        }


class NaturalLanguageQueryProcessor:
    """Main processor for natural language queries."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        self.date_parser = DateParser()
        self.name_extractor = NameExtractor()
        self.location_extractor = LocationExtractor()
        
    def parse_query(self, query: str, context: Optional[str] = None) -> ParsedQuery:
        """Parse natural language query into structured parameters."""
        query = query.strip()
        full_text = f"{query} {context or ''}".lower()
        
        self.logger.debug("Parsing natural language query", query=query)
        
        # Detect query type
        search_type = self._detect_search_type(full_text)
        
        if search_type == "alien_number":
            return self._parse_alien_number_query(full_text)
        elif search_type == "facility":
            return self._parse_facility_query(full_text)
        else:
            return self._parse_name_based_query(full_text)
    
    def _detect_search_type(self, text: str) -> str:
        """Detect the type of search from the query."""
        # Alien number patterns
        if re.search(r'a\d{8,9}|\b\d{8,9}\b', text, re.IGNORECASE):
            return "alien_number"
        
        # Facility search patterns
        facility_keywords = [
            'facility', 'center', 'detention', 'prison', 'jail',
            'processing center', 'correctional', 'holding'
        ]
        if any(keyword in text for keyword in facility_keywords):
            return "facility"
        
        # Default to name-based search
        return "name_based"
    
    def _parse_alien_number_query(self, text: str) -> ParsedQuery:
        """Parse alien number query."""
        # Extract alien number
        patterns = [
            r'(a\d{8,9})',
            r'\b(\d{8,9})\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                alien_number = match.group(1).upper()
                if not alien_number.startswith('A'):
                    alien_number = 'A' + alien_number
                
                return ParsedQuery(
                    search_type="alien_number",
                    parameters={'alien_number': alien_number},
                    confidence=1.0,
                    suggestions=[],
                    corrections_applied=[],
                    ambiguities=[]
                )
        
        return ParsedQuery(
            search_type="alien_number",
            parameters={},
            confidence=0.0,
            suggestions=["Please provide a valid alien number (A followed by 8-9 digits)"],
            corrections_applied=[],
            ambiguities=["Could not extract alien number from query"]
        )
    
    def _parse_facility_query(self, text: str) -> ParsedQuery:
        """Parse facility-based query."""
        facility_location = self.location_extractor.extract_facility_location(text)
        
        if facility_location:
            return ParsedQuery(
                search_type="facility",
                parameters={'facility_location': facility_location},
                confidence=0.8,
                suggestions=[],
                corrections_applied=[],
                ambiguities=[]
            )
        
        return ParsedQuery(
            search_type="facility",
            parameters={},
            confidence=0.0,
            suggestions=["Please specify a facility name or location"],
            corrections_applied=[],
            ambiguities=["Could not extract facility information"]
        )
    
    def _parse_name_based_query(self, text: str) -> ParsedQuery:
        """Parse name-based query."""
        parameters = {}
        suggestions = []
        corrections_applied = []
        ambiguities = []
        confidence = 0.0
        
        # Extract name
        name_info = self.name_extractor.extract_name(text)
        if name_info:
            parameters.update({
                'first_name': name_info['first_name'],
                'last_name': name_info['last_name']
            })
            if 'middle_name' in name_info:
                parameters['middle_name'] = name_info['middle_name']
            confidence += 0.4
        else:
            ambiguities.append("Could not extract name from query")
            suggestions.append("Please provide first and last name")
        
        # Extract date of birth
        date_match = self._extract_date_from_text(text)
        if date_match:
            parameters['date_of_birth'] = date_match
            confidence += 0.3
        else:
            suggestions.append("Consider adding date of birth for better results")
        
        # Extract country
        country = self.location_extractor.extract_country(text)
        if country:
            parameters['country_of_birth'] = country
            confidence += 0.3
        else:
            suggestions.append("Consider adding country of birth for better results")
        
        # Auto-corrections
        corrected_params = self._apply_auto_corrections(parameters)
        if corrected_params != parameters:
            corrections_applied.extend(self._find_corrections(parameters, corrected_params))
            parameters = corrected_params
        
        return ParsedQuery(
            search_type="name_based",
            parameters=parameters,
            confidence=min(confidence, 1.0),
            suggestions=suggestions,
            corrections_applied=corrections_applied,
            ambiguities=ambiguities
        )
    
    def _extract_date_from_text(self, text: str) -> Optional[str]:
        """Extract date from text using various patterns."""
        # Date-related patterns
        date_patterns = [
            r'born\s+(?:on\s+)?([^,]+?)(?:\s+in|\s+at|,|$)',
            r'birth\s+(?:date\s+)?([^,]+?)(?:\s+in|\s+at|,|$)',
            r'dob\s+([^,\s]+)',
            r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
            r'(\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2})',
            r'((?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4})',
            r'(\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4})',
            r'(?:around|about|circa)\s+(\d{4})',
            r'(?:in|during)\s+(\d{4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                parsed_date = self.date_parser.parse_date(date_str)
                if parsed_date:
                    return parsed_date
        
        return None
    
    def _apply_auto_corrections(self, parameters: Dict[str, str]) -> Dict[str, str]:
        """Apply auto-corrections to extracted parameters."""
        corrected = parameters.copy()
        
        # Name corrections
        name_corrections = {
            'jose': 'José',
            'maria': 'María',
            'carlos': 'Carlos',
            'juan': 'Juan',
            'luis': 'Luis',
            'ana': 'Ana',
            'garcia': 'García',
            'rodriguez': 'Rodríguez',
            'martinez': 'Martínez',
            'lopez': 'López',
            'gonzalez': 'González',
            'hernandez': 'Hernández',
            'perez': 'Pérez',
            'sanchez': 'Sánchez'
        }
        
        for field in ['first_name', 'last_name', 'middle_name']:
            if field in corrected:
                original = corrected[field].lower()
                if original in name_corrections:
                    corrected[field] = name_corrections[original]
        
        # Country corrections
        if 'country_of_birth' in corrected:
            country_corrections = {
                'mexico': 'Mexico',
                'méxico': 'Mexico',
                'guatemala': 'Guatemala',
                'el salvador': 'El Salvador',
                'salvador': 'El Salvador',
                'honduras': 'Honduras',
                'nicaragua': 'Nicaragua'
            }
            
            original = corrected['country_of_birth'].lower()
            if original in country_corrections:
                corrected['country_of_birth'] = country_corrections[original]
        
        return corrected
    
    def _find_corrections(self, original: Dict[str, str], corrected: Dict[str, str]) -> List[str]:
        """Find what corrections were applied."""
        corrections = []
        
        for key in original:
            if key in corrected and original[key] != corrected[key]:
                corrections.append(f"{key}: '{original[key]}' → '{corrected[key]}'")
        
        return corrections