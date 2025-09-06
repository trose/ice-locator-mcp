"""
Timezone and Locale Manager for ICE Locator MCP Server.

This module provides advanced timezone and locale simulation capabilities to avoid 
detection based on geographic inconsistencies. It implements realistic geolocation, 
timezone handling, and dynamic locale switching.
"""

import random
import structlog
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any
from playwright.async_api import BrowserContext
import json


@dataclass
class TimezoneProfile:
    """Represents a timezone configuration with realistic properties."""
    timezone_id: str
    offset: int  # in minutes
    locale: str
    language: str
    country_code: str
    geolocation: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timezone_id": self.timezone_id,
            "offset": self.offset,
            "locale": self.locale,
            "language": self.language,
            "country_code": self.country_code,
            "geolocation": self.geolocation
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimezoneProfile':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class LocaleProfile:
    """Represents a locale configuration with realistic properties."""
    locale: str
    language: str
    country_code: str
    currency: str
    numbering_system: str
    calendar: str
    text_direction: str  # ltr or rtl
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "locale": self.locale,
            "language": self.language,
            "country_code": self.country_code,
            "currency": self.currency,
            "numbering_system": self.numbering_system,
            "calendar": self.calendar,
            "text_direction": self.text_direction
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LocaleProfile':
        """Create from dictionary."""
        return cls(**data)


class TimezoneLocaleManager:
    """Manages advanced timezone and locale simulation to avoid detection based on geographic inconsistencies."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        
        # Common timezone configurations with realistic geolocations
        self.timezone_profiles = [
            TimezoneProfile(
                timezone_id="America/New_York",
                offset=-300,  # EST
                locale="en-US",
                language="en",
                country_code="US",
                geolocation={"latitude": 40.7128, "longitude": -74.0060}  # New York
            ),
            TimezoneProfile(
                timezone_id="America/Chicago",
                offset=-360,  # CST
                locale="en-US",
                language="en",
                country_code="US",
                geolocation={"latitude": 41.8781, "longitude": -87.6298}  # Chicago
            ),
            TimezoneProfile(
                timezone_id="America/Denver",
                offset=-420,  # MST
                locale="en-US",
                language="en",
                country_code="US",
                geolocation={"latitude": 39.7392, "longitude": -104.9903}  # Denver
            ),
            TimezoneProfile(
                timezone_id="America/Los_Angeles",
                offset=-480,  # PST
                locale="en-US",
                language="en",
                country_code="US",
                geolocation={"latitude": 34.0522, "longitude": -118.2437}  # Los Angeles
            ),
            TimezoneProfile(
                timezone_id="Europe/London",
                offset=0,  # GMT
                locale="en-GB",
                language="en",
                country_code="GB",
                geolocation={"latitude": 51.5074, "longitude": -0.1278}  # London
            ),
            TimezoneProfile(
                timezone_id="Europe/Paris",
                offset=60,  # CET
                locale="fr-FR",
                language="fr",
                country_code="FR",
                geolocation={"latitude": 48.8566, "longitude": 2.3522}  # Paris
            ),
            TimezoneProfile(
                timezone_id="Europe/Berlin",
                offset=60,  # CET
                locale="de-DE",
                language="de",
                country_code="DE",
                geolocation={"latitude": 52.5200, "longitude": 13.4050}  # Berlin
            ),
            TimezoneProfile(
                timezone_id="Asia/Tokyo",
                offset=540,  # JST
                locale="ja-JP",
                language="ja",
                country_code="JP",
                geolocation={"latitude": 35.6762, "longitude": 139.6503}  # Tokyo
            ),
            TimezoneProfile(
                timezone_id="Asia/Shanghai",
                offset=480,  # CST
                locale="zh-CN",
                language="zh",
                country_code="CN",
                geolocation={"latitude": 31.2304, "longitude": 121.4737}  # Shanghai
            ),
            TimezoneProfile(
                timezone_id="Australia/Sydney",
                offset=600,  # AEST
                locale="en-AU",
                language="en",
                country_code="AU",
                geolocation={"latitude": -33.8688, "longitude": 151.2093}  # Sydney
            )
        ]
        
        # Common locale configurations
        self.locale_profiles = [
            LocaleProfile(
                locale="en-US",
                language="en",
                country_code="US",
                currency="USD",
                numbering_system="latn",
                calendar="gregory",
                text_direction="ltr"
            ),
            LocaleProfile(
                locale="en-GB",
                language="en",
                country_code="GB",
                currency="GBP",
                numbering_system="latn",
                calendar="gregory",
                text_direction="ltr"
            ),
            LocaleProfile(
                locale="fr-FR",
                language="fr",
                country_code="FR",
                currency="EUR",
                numbering_system="latn",
                calendar="gregory",
                text_direction="ltr"
            ),
            LocaleProfile(
                locale="de-DE",
                language="de",
                country_code="DE",
                currency="EUR",
                numbering_system="latn",
                calendar="gregory",
                text_direction="ltr"
            ),
            LocaleProfile(
                locale="es-ES",
                language="es",
                country_code="ES",
                currency="EUR",
                numbering_system="latn",
                calendar="gregory",
                text_direction="ltr"
            ),
            LocaleProfile(
                locale="ja-JP",
                language="ja",
                country_code="JP",
                currency="JPY",
                numbering_system="latn",
                calendar="gregory",
                text_direction="ltr"
            ),
            LocaleProfile(
                locale="zh-CN",
                language="zh",
                country_code="CN",
                currency="CNY",
                numbering_system="latn",
                calendar="gregory",
                text_direction="ltr"
            ),
            LocaleProfile(
                locale="ar-SA",
                language="ar",
                country_code="SA",
                currency="SAR",
                numbering_system="latn",
                calendar="gregory",
                text_direction="rtl"
            )
        ]
        
        # Header variations for different locales
        self.locale_headers = {
            "en-US": {
                "accept-language": "en-US,en;q=0.9",
                "accept-charset": "utf-8, iso-8859-1;q=0.5"
            },
            "en-GB": {
                "accept-language": "en-GB,en;q=0.9,en-US;q=0.8",
                "accept-charset": "utf-8, iso-8859-1;q=0.5"
            },
            "fr-FR": {
                "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                "accept-charset": "utf-8, iso-8859-1;q=0.5"
            },
            "de-DE": {
                "accept-language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
                "accept-charset": "utf-8, iso-8859-1;q=0.5"
            },
            "es-ES": {
                "accept-language": "es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7",
                "accept-charset": "utf-8, iso-8859-1;q=0.5"
            },
            "ja-JP": {
                "accept-language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
                "accept-charset": "utf-8, shift_jis;q=0.7, iso-2022-jp;q=0.7"
            },
            "zh-CN": {
                "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "accept-charset": "utf-8, gb2312;q=0.7, gbk;q=0.7"
            },
            "ar-SA": {
                "accept-language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
                "accept-charset": "utf-8, windows-1256;q=0.7, iso-8859-6;q=0.7"
            }
        }
    
    def get_random_timezone_profile(self) -> TimezoneProfile:
        """
        Get a random timezone profile with realistic properties.
        
        Returns:
            TimezoneProfile with realistic properties
        """
        return random.choice(self.timezone_profiles)
    
    def get_random_locale_profile(self) -> LocaleProfile:
        """
        Get a random locale profile with realistic properties.
        
        Returns:
            LocaleProfile with realistic properties
        """
        return random.choice(self.locale_profiles)
    
    def generate_realistic_timezone_locale(self) -> Tuple[TimezoneProfile, LocaleProfile]:
        """
        Generate a completely realistic timezone and locale combination.
        
        Returns:
            Tuple of (TimezoneProfile, LocaleProfile) with consistent properties
        """
        # Choose a timezone profile
        timezone_profile = self.get_random_timezone_profile()
        
        # Find a matching locale profile
        matching_locale = None
        for locale_profile in self.locale_profiles:
            if locale_profile.locale == timezone_profile.locale:
                matching_locale = locale_profile
                break
        
        # If no exact match, find a language match
        if matching_locale is None:
            for locale_profile in self.locale_profiles:
                if locale_profile.language == timezone_profile.language:
                    matching_locale = locale_profile
                    break
        
        # If still no match, use a random locale
        if matching_locale is None:
            matching_locale = self.get_random_locale_profile()
        
        self.logger.debug(
            "Generated realistic timezone/locale combination",
            timezone=timezone_profile.timezone_id,
            locale=matching_locale.locale
        )
        
        return (timezone_profile, matching_locale)
    
    async def apply_timezone_locale_to_context(
        self, 
        context: BrowserContext, 
        timezone_profile: Optional[TimezoneProfile] = None, 
        locale_profile: Optional[LocaleProfile] = None
    ) -> None:
        """
        Apply timezone and locale properties to a browser context.
        
        Args:
            context: Playwright BrowserContext to apply timezone/locale to
            timezone_profile: TimezoneProfile to apply, or None to generate a random one
            locale_profile: LocaleProfile to apply, or None to generate a random one
        """
        if timezone_profile is None or locale_profile is None:
            tz_profile, loc_profile = self.generate_realistic_timezone_locale()
            if timezone_profile is None:
                timezone_profile = tz_profile
            if locale_profile is None:
                locale_profile = loc_profile
        
        try:
            # Set timezone and locale in context options
            await context.set_extra_http_headers(self.locale_headers.get(locale_profile.locale, self.locale_headers["en-US"]))
            
            # Add JavaScript to spoof timezone and locale properties
            await context.add_init_script(f"""
                // Override Intl.DateTimeFormat to spoof timezone
                const originalDateTimeFormat = Intl.DateTimeFormat;
                Intl.DateTimeFormat = function() {{
                    const original = new originalDateTimeFormat(...arguments);
                    const originalResolvedOptions = original.resolvedOptions;
                    original.resolvedOptions = function() {{
                        const options = originalResolvedOptions.call(this);
                        options.timeZone = '{timezone_profile.timezone_id}';
                        options.locale = '{locale_profile.locale}';
                        return options;
                    }};
                    return original;
                }};
                
                // Override navigator.language and navigator.languages
                Object.defineProperty(navigator, 'language', {{
                    get: () => '{locale_profile.locale}'
                }});
                
                Object.defineProperty(navigator, 'languages', {{
                    get: () => ['{locale_profile.locale}', '{locale_profile.language}']
                }});
                
                // Override navigator.locale if it exists
                if (navigator.locale) {{
                    Object.defineProperty(navigator, 'locale', {{
                        get: () => '{locale_profile.locale}'
                    }});
                }}
                
                // Override toLocaleString and related methods
                const dateProto = Date.prototype;
                const originalToLocaleString = dateProto.toLocaleString;
                const originalToLocaleDateString = dateProto.toLocaleDateString;
                const originalToLocaleTimeString = dateProto.toLocaleTimeString;
                
                dateProto.toLocaleString = function(locales, options) {{
                    const effectiveLocales = locales || '{locale_profile.locale}';
                    const effectiveOptions = options || {{}};
                    effectiveOptions.timeZone = '{timezone_profile.timezone_id}';
                    return originalToLocaleString.call(this, effectiveLocales, effectiveOptions);
                }};
                
                dateProto.toLocaleDateString = function(locales, options) {{
                    const effectiveLocales = locales || '{locale_profile.locale}';
                    const effectiveOptions = options || {{}};
                    effectiveOptions.timeZone = '{timezone_profile.timezone_id}';
                    return originalToLocaleDateString.call(this, effectiveLocales, effectiveOptions);
                }};
                
                dateProto.toLocaleTimeString = function(locales, options) {{
                    const effectiveLocales = locales || '{locale_profile.locale}';
                    const effectiveOptions = options || {{}};
                    effectiveOptions.timeZone = '{timezone_profile.timezone_id}';
                    return originalToLocaleTimeString.call(this, effectiveLocales, effectiveOptions);
                }};
                
                // Override performance.timeOrigin to be timezone consistent
                if (performance && performance.timeOrigin) {{
                    const originalTimeOrigin = performance.timeOrigin;
                    Object.defineProperty(performance, 'timeOrigin', {{
                        get: () => {{
                            // Adjust timeOrigin to match timezone
                            const now = Date.now();
                            const localNow = new Date(now).toLocaleString('en-US', {{timeZone: '{timezone_profile.timezone_id}'}});
                            const localTime = new Date(localNow).getTime();
                            return originalTimeOrigin + (localTime - now);
                        }}
                    }});
                }}
                
                // Override Date methods that might reveal timezone
                const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
                Date.prototype.getTimezoneOffset = function() {{
                    return {timezone_profile.offset};
                }};
            """)
            
            self.logger.debug(
                "Applied timezone/locale to context",
                timezone=timezone_profile.timezone_id,
                locale=locale_profile.locale
            )
            
        except Exception as e:
            self.logger.error("Failed to apply timezone/locale to context", error=str(e))
            raise
    
    def get_timezone_headers(self, locale: str = "en-US") -> Dict[str, str]:
        """
        Get appropriate HTTP headers for a given locale.
        
        Args:
            locale: Locale string (e.g., "en-US")
            
        Returns:
            Dictionary of HTTP headers
        """
        return self.locale_headers.get(locale, self.locale_headers["en-US"])
    
    def get_timezone_offset(self, timezone_profile: TimezoneProfile) -> int:
        """
        Get timezone offset in minutes.
        
        Args:
            timezone_profile: TimezoneProfile to get offset from
            
        Returns:
            Timezone offset in minutes
        """
        return timezone_profile.offset
    
    def get_geolocation(self, timezone_profile: TimezoneProfile) -> Dict[str, float]:
        """
        Get geolocation coordinates.
        
        Args:
            timezone_profile: TimezoneProfile to get geolocation from
            
        Returns:
            Dictionary with latitude and longitude
        """
        return timezone_profile.geolocation
    
    def is_consistent_timezone_locale(self, timezone_profile: TimezoneProfile, locale_profile: LocaleProfile) -> bool:
        """
        Check if timezone and locale profiles are consistent.
        
        Args:
            timezone_profile: TimezoneProfile to check
            locale_profile: LocaleProfile to check
            
        Returns:
            True if profiles are consistent, False otherwise
        """
        # Check if locale matches timezone locale
        if timezone_profile.locale == locale_profile.locale:
            return True
        
        # Check if language matches
        if timezone_profile.language == locale_profile.language:
            return True
        
        # For some common combinations, allow mismatch
        compatible_combinations = [
            ("en-US", "en-GB"),
            ("en-GB", "en-US"),
            ("fr-FR", "fr-CA"),
            ("es-ES", "es-MX")
        ]
        
        locale_pair = (timezone_profile.locale, locale_profile.locale)
        reverse_pair = (locale_profile.locale, timezone_profile.locale)
        
        return locale_pair in compatible_combinations or reverse_pair in compatible_combinations