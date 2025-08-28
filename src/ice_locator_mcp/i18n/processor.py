"""
Multi-language support for ICE Locator MCP Server.

Provides comprehensive Spanish language support including interface translations,
natural language processing, and localized resources.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import structlog

from ..core.config import Config


@dataclass
class TranslationEntry:
    """Translation entry with context and metadata."""
    key: str
    english: str
    spanish: str
    context: str = ""
    legal_verified: bool = False


class LanguageProcessor:
    """Handles language detection, translation, and localization."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = structlog.get_logger(__name__)
        
        # Supported languages
        self.supported_languages = ["en", "es"]
        self.default_language = "en"
        
        # Translation dictionaries
        self.translations: Dict[str, Dict[str, str]] = {}
        self.legal_translations: Dict[str, Dict[str, str]] = {}
        
        # Language detection patterns
        self.language_patterns = {
            "es": [
                r"\bbuscar\b", r"\bencontrar\b", r"\bdónde\b", r"\bestá\b",
                r"\bdetenido\b", r"\bcárcel\b", r"\binmigración\b", r"\bICE\b",
                r"\bnúmero\b", r"\balien\b", r"\bfacilidad\b", r"\bcentro\b"
            ],
            "en": [
                r"\bfind\b", r"\bsearch\b", r"\bwhere\b", r"\bis\b",
                r"\bdetained\b", r"\bprison\b", r"\bimmigration\b", r"\bICE\b",
                r"\bnumber\b", r"\balien\b", r"\bfacility\b", r"\bcenter\b"
            ]
        }
        
        # Name processing patterns for Spanish/Latino names
        self.hispanic_name_patterns = {
            "compound_first": r"^(Ana|José|Juan|María|Luis|Carmen)\s+(.*)",
            "compound_last": r"(.+)\s+(de\s+la|de\s+los|de|del|van\s+der|von)\s+(.+)",
            "maternal_surname": r"(.+)\s+(.+)\s+(.+)$",  # First Middle Paternal Maternal
            "hyphenated": r"(.+)-(.+)",
            "particles": ["de", "del", "de la", "de los", "de las", "da", "do", "dos", "van", "von"]
        }
    
    async def initialize(self) -> None:
        """Initialize language processor with translations."""
        await self._load_translations()
        self.logger.info("Language processor initialized", languages=self.supported_languages)
    
    async def detect_language(self, text: str) -> str:
        """Detect language of input text."""
        if not text:
            return self.default_language
        
        text_lower = text.lower()
        
        # Count pattern matches for each language
        scores = {}
        for lang, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                score += matches
            scores[lang] = score
        
        # Return language with highest score
        if scores:
            detected = max(scores, key=scores.get)
            if scores[detected] > 0:
                return detected
        
        return self.default_language
    
    async def translate_text(self, text: str, target_language: str, context: str = "") -> str:
        """Translate text to target language."""
        if target_language not in self.supported_languages:
            return text
        
        # Check for direct translation
        key = text.lower().strip()
        if target_language in self.translations and key in self.translations[target_language]:
            return self.translations[target_language][key]
        
        # Check legal translations for legal context
        if context == "legal" and target_language in self.legal_translations:
            if key in self.legal_translations[target_language]:
                return self.legal_translations[target_language][key]
        
        # Return original text if no translation found
        return text
    
    async def translate_interface(self, interface_dict: Dict[str, Any], target_language: str) -> Dict[str, Any]:
        """Translate interface elements to target language."""
        if target_language == "en":
            return interface_dict
        
        translated = {}
        for key, value in interface_dict.items():
            if isinstance(value, str):
                translated[key] = await self.translate_text(value, target_language, "interface")
            elif isinstance(value, dict):
                translated[key] = await self.translate_interface(value, target_language)
            elif isinstance(value, list):
                translated[key] = []
                for item in value:
                    if isinstance(item, str):
                        translated[key].append(await self.translate_text(item, target_language, "interface"))
                    else:
                        translated[key].append(item)
            else:
                translated[key] = value
        
        return translated
    
    async def process_spanish_name(self, name: str) -> Dict[str, List[str]]:
        """Process Spanish/Latino names for better matching."""
        name = name.strip()
        variations = []
        
        # Handle compound first names (José Luis -> José, Luis, José Luis)
        compound_first = re.match(self.hispanic_name_patterns["compound_first"], name)
        if compound_first:
            first_part = compound_first.group(1)
            second_part = compound_first.group(2)
            variations.extend([first_part, second_part, f"{first_part} {second_part}"])
        
        # Handle particles (de la Cruz -> Cruz, de la Cruz)
        for particle in self.hispanic_name_patterns["particles"]:
            if f" {particle} " in name.lower():
                # Extract name without particle
                without_particle = re.sub(f"\\s+{re.escape(particle)}\\s+", " ", name, flags=re.IGNORECASE)
                variations.append(without_particle.strip())
        
        # Handle hyphenated names (García-López -> García, López, García-López)
        if "-" in name:
            parts = name.split("-")
            variations.extend(parts)
            variations.append(name)
        
        # Handle maternal surnames (Juan Carlos Pérez González -> various combinations)
        parts = name.split()
        if len(parts) >= 3:
            # First + Paternal
            variations.append(f"{parts[0]} {parts[-2]}")
            # First + Maternal  
            variations.append(f"{parts[0]} {parts[-1]}")
            # First + Middle + Paternal
            if len(parts) >= 4:
                variations.append(f"{parts[0]} {parts[1]} {parts[-2]}")
        
        # Remove duplicates and empty strings
        variations = list(set(v.strip() for v in variations if v.strip()))
        
        return {
            "original": [name],
            "variations": variations,
            "phonetic_variants": await self._generate_phonetic_variants(name)
        }
    
    async def translate_search_query(self, query: str, source_lang: str = None) -> Tuple[str, Dict[str, Any]]:
        """Translate and parse natural language search query."""
        if source_lang is None:
            source_lang = await self.detect_language(query)
        
        # Normalize query for parsing
        normalized_query = query.lower().strip()
        
        # Spanish to English translation patterns for search
        if source_lang == "es":
            translations = {
                r"buscar\s+(a\s+)?": "find ",
                r"encontrar\s+(a\s+)?": "find ",
                r"dónde\s+está": "where is",
                r"en\s+el\s+centro": "at facility",
                r"en\s+la\s+cárcel": "at detention center",
                r"número\s+alien": "alien number",
                r"número\s+de\s+alien": "alien number",
                r"facilidad": "facility",
                r"centro\s+de\s+detención": "detention center",
                r"nacido\s+en": "born in",
                r"nacido\s+alrededor\s+de": "born around",
                r"años?": "years old"
            }
            
            translated_query = normalized_query
            for pattern, replacement in translations.items():
                translated_query = re.sub(pattern, replacement, translated_query, flags=re.IGNORECASE)
        else:
            translated_query = normalized_query
        
        # Extract search parameters
        parameters = await self._extract_search_parameters(translated_query, source_lang)
        
        return translated_query, parameters
    
    async def localize_response(self, response: Dict[str, Any], language: str) -> Dict[str, Any]:
        """Localize response data to specified language."""
        if language == "en":
            return response
        
        localized = response.copy()
        
        # Translate status messages
        if "status" in localized:
            localized["status"] = await self.translate_text(
                localized["status"], language, "status"
            )
        
        # Translate error messages
        if "error" in localized:
            localized["error"] = await self.translate_text(
                localized["error"], language, "error"
            )
        
        # Translate guidance and recommendations
        if "user_guidance" in localized:
            localized["user_guidance"] = await self.translate_interface(
                localized["user_guidance"], language
            )
        
        # Translate facility information
        if "results" in localized and isinstance(localized["results"], list):
            for result in localized["results"]:
                if "custody_status" in result:
                    result["custody_status"] = await self.translate_text(
                        result["custody_status"], language, "legal"
                    )
        
        return localized
    
    async def get_localized_resources(self, language: str) -> List[Dict[str, str]]:
        """Get localized resources and support contacts."""
        if language == "es":
            return [
                {
                    "name": "Línea Nacional de Inmigración",
                    "phone": "1-855-234-1317",
                    "description": "Asistencia legal gratuita en español",
                    "type": "legal_aid"
                },
                {
                    "name": "Unidos US (anteriormente UnidosUS)",
                    "url": "https://unidosus.org",
                    "description": "Recursos y apoyo para la comunidad latina",
                    "type": "advocacy"
                },
                {
                    "name": "Asociación Americana de Abogados de Inmigración (AILA)",
                    "url": "https://aila.org",
                    "description": "Encuentra abogados de inmigración calificados",
                    "type": "legal"
                },
                {
                    "name": "Directorio Nacional de Servicios Legales de Inmigración",
                    "url": "https://nipnlg.org/PILdirectory",
                    "description": "Servicios legales gratuitos y de bajo costo",
                    "type": "legal_aid"
                },
                {
                    "name": "Localizador de Detenidos de ICE",
                    "url": "https://locator.ice.gov",
                    "description": "Base de datos oficial de ICE para localizar detenidos",
                    "type": "official"
                }
            ]
        else:
            return [
                {
                    "name": "ICE Online Detainee Locator",
                    "url": "https://locator.ice.gov",
                    "description": "Official ICE database for locating detainees",
                    "type": "official"
                },
                {
                    "name": "American Immigration Lawyers Association",
                    "url": "https://aila.org",
                    "description": "Find qualified immigration attorneys",
                    "type": "legal"
                },
                {
                    "name": "National Immigration Legal Services Directory",
                    "url": "https://nipnlg.org/PILdirectory",
                    "description": "Free and low-cost legal services",
                    "type": "legal_aid"
                },
                {
                    "name": "National Immigration Hotline",
                    "phone": "1-855-234-1317",
                    "description": "Free legal assistance hotline",
                    "type": "legal_aid"
                }
            ]
    
    async def _load_translations(self) -> None:
        """Load translation dictionaries."""
        # Interface translations
        self.translations = {
            "es": {
                # Search interface
                "search": "buscar",
                "find": "encontrar",
                "results": "resultados",
                "no results found": "no se encontraron resultados",
                "search by name": "buscar por nombre",
                "search by alien number": "buscar por número alien",
                "first name": "nombre",
                "last name": "apellido",
                "alien number": "número alien",
                "facility": "facilidad",
                "detention center": "centro de detención",
                
                # Status messages
                "found": "encontrado",
                "not found": "no encontrado",
                "in custody": "bajo custodia",
                "released": "liberado",
                "transferred": "transferido",
                
                # Error messages
                "invalid input": "entrada inválida",
                "rate limit exceeded": "límite de velocidad excedido",
                "server error": "error del servidor",
                "connection failed": "falló la conexión",
                
                # Interface elements
                "loading": "cargando",
                "please wait": "por favor espere",
                "try again": "inténtelo de nuevo",
                "help": "ayuda",
                "contact": "contacto",
                "resources": "recursos"
            }
        }
        
        # Legal terminology translations
        self.legal_translations = {
            "es": {
                "detention": "detención",
                "immigration court": "corte de inmigración",
                "deportation": "deportación",
                "removal proceedings": "procedimientos de deportación",
                "bond hearing": "audiencia de fianza",
                "legal representation": "representación legal",
                "attorney": "abogado",
                "interpreter": "intérprete",
                "due process": "debido proceso",
                "asylum": "asilo",
                "refugee": "refugiado",
                "temporary protected status": "estatus de protección temporal",
                "withholding of removal": "suspensión de deportación"
            }
        }
    
    async def _extract_search_parameters(self, query: str, language: str) -> Dict[str, Any]:
        """Extract search parameters from natural language query."""
        parameters = {}
        
        # Name extraction patterns
        name_patterns = {
            "en": [
                r"find\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
                r"search\s+for\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
                r"locate\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
            ],
            "es": [
                r"buscar\s+(?:a\s+)?([A-ZÁÉÍÓÚÑa-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑa-záéíóúñ]+)*)",
                r"encontrar\s+(?:a\s+)?([A-ZÁÉÍÓÚÑa-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑa-záéíóúñ]+)*)"
            ]
        }
        
        # Extract names
        for pattern in name_patterns.get(language, name_patterns["en"]):
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                full_name = match.group(1)
                name_parts = full_name.split()
                if len(name_parts) >= 2:
                    parameters["first_name"] = name_parts[0]
                    parameters["last_name"] = " ".join(name_parts[1:])
                elif len(name_parts) == 1:
                    parameters["last_name"] = name_parts[0]
                break
        
        # Extract A-number
        alien_patterns = [
            r"(?:alien\s+number|a-number|a\s*number)[\s:]+([a-z]?\d{8,9})",
            r"\b[aA]\d{8,9}\b"
        ]
        
        for pattern in alien_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                parameters["alien_number"] = match.group(1).upper()
                if not parameters["alien_number"].startswith("A"):
                    parameters["alien_number"] = "A" + parameters["alien_number"]
                break
        
        # Extract facility/location
        facility_patterns = {
            "en": [
                r"(?:at|in|facility)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:facility|center|detention))?)",
                r"(?:detention\s+center|facility)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
            ],
            "es": [
                r"en\s+(?:el\s+)?(?:centro|facilidad)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑa-záéíóúñ]+)*)",
                r"en\s+([A-ZÁÉÍÓÚÑa-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑa-záéíóúñ]+)*)"
            ]
        }
        
        for pattern in facility_patterns.get(language, facility_patterns["en"]):
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                parameters["facility_name"] = match.group(1)
                break
        
        return parameters
    
    async def _generate_phonetic_variants(self, name: str) -> List[str]:
        """Generate phonetic variants for Spanish names."""
        variants = []
        
        # Common Spanish phonetic substitutions
        substitutions = [
            ("b", "v"), ("v", "b"),  # B/V confusion
            ("j", "h"), ("h", "j"),  # J/H confusion in some regions
            ("ll", "y"), ("y", "ll"),  # LL/Y yeísmo
            ("s", "z"), ("z", "s"),  # S/Z seseo
            ("ce", "se"), ("ci", "si"),  # C/S before i,e
            ("que", "ke"), ("qui", "ki"),  # QU/K
            ("gu", "g")  # GU/G before e,i
        ]
        
        name_lower = name.lower()
        for old, new in substitutions:
            if old in name_lower:
                variant = name_lower.replace(old, new)
                variants.append(variant.title())
        
        return list(set(variants))


class MultiLanguageInterface:
    """Provides multi-language interface for MCP tools."""
    
    def __init__(self, language_processor: LanguageProcessor):
        self.processor = language_processor
        self.logger = structlog.get_logger(__name__)
    
    async def process_multilingual_query(self, query: str) -> Dict[str, Any]:
        """Process query with automatic language detection and translation."""
        # Detect language
        detected_language = await self.processor.detect_language(query)
        
        # Translate to English for processing if needed
        if detected_language != "en":
            english_query, parameters = await self.processor.translate_search_query(query, detected_language)
        else:
            english_query = query
            parameters = await self.processor._extract_search_parameters(query, "en")
        
        return {
            "original_query": query,
            "detected_language": detected_language,
            "english_query": english_query,
            "extracted_parameters": parameters,
            "needs_translation": detected_language != "en"
        }
    
    async def format_multilingual_response(
        self, 
        response: Dict[str, Any], 
        target_language: str
    ) -> Dict[str, Any]:
        """Format response for target language."""
        if target_language == "en":
            return response
        
        # Localize the response
        localized_response = await self.processor.localize_response(response, target_language)
        
        # Add language-specific resources
        resources = await self.processor.get_localized_resources(target_language)
        if "user_guidance" not in localized_response:
            localized_response["user_guidance"] = {}
        localized_response["user_guidance"]["resources"] = resources
        
        return localized_response