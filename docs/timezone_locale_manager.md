# Timezone and Locale Manager Documentation

## Overview

The TimezoneLocaleManager module provides advanced timezone and locale simulation capabilities to avoid detection based on geographic inconsistencies. It implements realistic geolocation, timezone handling, and dynamic locale switching to make browser sessions appear more human-like and geographically consistent.

## Key Features

- Realistic timezone and locale generation
- Geolocation spoofing with consistent coordinates
- Dynamic locale switching capabilities
- HTTP header customization for different locales
- Integration with Playwright browser contexts
- Consistency checking between timezone and locale profiles

## Installation

The TimezoneLocaleManager is part of the ICE Locator MCP Server and requires no additional installation steps.

## Usage

### Basic Usage

```python
from ice_locator_mcp.anti_detection.timezone_locale_manager import TimezoneLocaleManager

# Create a timezone locale manager instance
timezone_locale_manager = TimezoneLocaleManager()

# Generate a random timezone profile
timezone_profile = timezone_locale_manager.get_random_timezone_profile()

# Generate a random locale profile
locale_profile = timezone_locale_manager.get_random_locale_profile()

# Generate a completely realistic timezone/locale combination
realistic_timezone, realistic_locale = timezone_locale_manager.generate_realistic_timezone_locale()
```

### Applying Timezone and Locale to Browser Context

```python
import asyncio
from playwright.async_api import async_playwright
from ice_locator_mcp.anti_detection.timezone_locale_manager import TimezoneLocaleManager

async def example():
    timezone_locale_manager = TimezoneLocaleManager()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        
        # Apply timezone and locale simulation to the context
        await timezone_locale_manager.apply_timezone_locale_to_context(context)
        
        # Or apply specific profiles
        timezone_profile = timezone_locale_manager.get_random_timezone_profile()
        locale_profile = timezone_locale_manager.get_random_locale_profile()
        await timezone_locale_manager.apply_timezone_locale_to_context(
            context, timezone_profile, locale_profile
        )
        
        page = await context.new_page()
        await page.goto("https://example.com")
        
        await browser.close()

# Run the example
asyncio.run(example())
```

## API Reference

### TimezoneLocaleManager Class

#### `__init__()`
Initializes the TimezoneLocaleManager with predefined timezone and locale configurations.

#### `get_random_timezone_profile() -> TimezoneProfile`
Get a random timezone profile with realistic properties.

**Returns:**
- `TimezoneProfile`: TimezoneProfile with realistic properties

#### `get_random_locale_profile() -> LocaleProfile`
Get a random locale profile with realistic properties.

**Returns:**
- `LocaleProfile`: LocaleProfile with realistic properties

#### `generate_realistic_timezone_locale() -> Tuple[TimezoneProfile, LocaleProfile]`
Generate a completely realistic timezone and locale combination with consistent properties.

**Returns:**
- `Tuple[TimezoneProfile, LocaleProfile]`: Consistent timezone and locale profiles

#### `apply_timezone_locale_to_context(context: BrowserContext, timezone_profile: Optional[TimezoneProfile] = None, locale_profile: Optional[LocaleProfile] = None) -> None`
Apply timezone and locale properties to a browser context.

**Parameters:**
- `context` (BrowserContext): Playwright BrowserContext to apply timezone/locale to
- `timezone_profile` (Optional[TimezoneProfile]): TimezoneProfile to apply, or None to generate a random one
- `locale_profile` (Optional[LocaleProfile]): LocaleProfile to apply, or None to generate a random one

#### `get_timezone_headers(locale: str = "en-US") -> Dict[str, str]`
Get appropriate HTTP headers for a given locale.

**Parameters:**
- `locale` (str): Locale string (e.g., "en-US")

**Returns:**
- `Dict[str, str]`: Dictionary of HTTP headers

#### `get_timezone_offset(timezone_profile: TimezoneProfile) -> int`
Get timezone offset in minutes.

**Parameters:**
- `timezone_profile` (TimezoneProfile): TimezoneProfile to get offset from

**Returns:**
- `int`: Timezone offset in minutes

#### `get_geolocation(timezone_profile: TimezoneProfile) -> Dict[str, float]`
Get geolocation coordinates.

**Parameters:**
- `timezone_profile` (TimezoneProfile): TimezoneProfile to get geolocation from

**Returns:**
- `Dict[str, float]`: Dictionary with latitude and longitude

#### `is_consistent_timezone_locale(timezone_profile: TimezoneProfile, locale_profile: LocaleProfile) -> bool`
Check if timezone and locale profiles are consistent.

**Parameters:**
- `timezone_profile` (TimezoneProfile): TimezoneProfile to check
- `locale_profile` (LocaleProfile): LocaleProfile to check

**Returns:**
- `bool`: True if profiles are consistent, False otherwise

### TimezoneProfile Dataclass

Represents a timezone configuration with realistic properties.

**Attributes:**
- `timezone_id` (str): Timezone identifier (e.g., "America/New_York")
- `offset` (int): Timezone offset in minutes
- `locale` (str): Locale string (e.g., "en-US")
- `language` (str): Language code (e.g., "en")
- `country_code` (str): Country code (e.g., "US")
- `geolocation` (Dict[str, float]): Geolocation coordinates with latitude and longitude

### LocaleProfile Dataclass

Represents a locale configuration with realistic properties.

**Attributes:**
- `locale` (str): Locale string (e.g., "en-US")
- `language` (str): Language code (e.g., "en")
- `country_code` (str): Country code (e.g., "US")
- `currency` (str): Currency code (e.g., "USD")
- `numbering_system` (str): Numbering system (e.g., "latn")
- `calendar` (str): Calendar system (e.g., "gregory")
- `text_direction` (str): Text direction ("ltr" or "rtl")

## Timezone Configurations

The TimezoneLocaleManager includes predefined timezone configurations for major global cities:

### North America
- America/New_York (EST)
- America/Chicago (CST)
- America/Denver (MST)
- America/Los_Angeles (PST)

### Europe
- Europe/London (GMT)
- Europe/Paris (CET)
- Europe/Berlin (CET)

### Asia
- Asia/Tokyo (JST)
- Asia/Shanghai (CST)

### Oceania
- Australia/Sydney (AEST)

Each timezone configuration includes realistic geolocation coordinates that match the city location.

## Locale Configurations

The TimezoneLocaleManager includes realistic locale configurations for major languages:

### English
- en-US (United States)
- en-GB (United Kingdom)

### European Languages
- fr-FR (French, France)
- de-DE (German, Germany)
- es-ES (Spanish, Spain)

### Asian Languages
- ja-JP (Japanese, Japan)
- zh-CN (Chinese, China)

### Middle Eastern Languages
- ar-SA (Arabic, Saudi Arabia)

Each locale configuration includes realistic currency, numbering system, calendar, and text direction properties.

## HTTP Header Customization

The TimezoneLocaleManager includes predefined HTTP headers for different locales:

- Accept-Language headers that match the locale
- Accept-Charset headers appropriate for the language
- Other headers that vary by locale for realistic simulation

## Integration with Browser Simulator

The TimezoneLocaleManager integrates seamlessly with the BrowserSimulator to provide realistic timezone and locale simulation:

```python
from ice_locator_mcp.anti_detection.browser_simulator import BrowserSimulator
from ice_locator_mcp.anti_detection.timezone_locale_manager import TimezoneLocaleManager
from ice_locator_mcp.core.config import SearchConfig

# Create browser simulator
config = SearchConfig()
browser_sim = BrowserSimulator(config)
timezone_locale_manager = TimezoneLocaleManager()

# The timezone locale manager can be used by the browser simulator
# to create realistic timezone and locale configurations for each session
```

## Best Practices

1. **Use realistic combinations**: Choose timezone and locale combinations that make geographic sense
2. **Vary profiles**: Use different timezone/locale combinations to avoid detection patterns
3. **Apply early**: Apply timezone and locale simulation to contexts before creating pages
4. **Check consistency**: Verify that timezone and locale profiles are consistent
5. **Update regularly**: Change timezone and locale profiles periodically to avoid fingerprinting

## Testing

The TimezoneLocaleManager includes comprehensive tests to ensure functionality:

```bash
python -m pytest tests/test_timezone_locale_manager.py -v
```

## Contributing

Contributions to improve timezone and locale configurations or add new simulation techniques are welcome. Please ensure all tests pass before submitting pull requests.

## License

This module is part of the ICE Locator MCP Server and is licensed under the project's license.