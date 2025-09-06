# Font Enumeration Protection Manager

## Overview

The FontEnumerationProtectionManager provides advanced protection against font enumeration-based browser fingerprinting techniques. It implements realistic spoofing of font measurement methods and adds variations to prevent detection through font-based fingerprinting.

## Features

- Realistic font measurement protection
- Device-specific font configurations
- Font family randomization
- Text measurement noise injection
- Canvas rendering protection
- Consistency validation for font profiles

## Installation

The FontEnumerationProtectionManager is part of the ICE Locator MCP Server and requires no additional installation.

## Usage

### Basic Usage

```python
from ice_locator_mcp.anti_detection.font_enumeration_protection import FontEnumerationProtectionManager

# Create manager instance
font_manager = FontEnumerationProtectionManager()

# Generate a random font profile
profile = font_manager.get_random_profile()

# Apply protection to a browser context
await font_manager.apply_font_enumeration_protection(context, profile)
```

### Device-Specific Profiles

```python
# Generate device-specific profiles
windows_profile = font_manager.get_device_specific_profile("desktop_windows")
mac_profile = font_manager.get_device_specific_profile("desktop_macos")
linux_profile = font_manager.get_device_specific_profile("desktop_linux")
ios_profile = font_manager.get_device_specific_profile("mobile_ios")
android_profile = font_manager.get_device_specific_profile("mobile_android")
tablet_profile = font_manager.get_device_specific_profile("tablet")
```

### Custom Profiles

```python
from ice_locator_mcp.anti_detection.font_enumeration_protection import FontEnumerationProfile

# Create a custom profile
custom_profile = FontEnumerationProfile(
    font_families=["Custom Font 1", "Custom Font 2", "Custom Font 3"],
    include_emoji_fonts=True,
    include_monospace_fonts=False,
    include_serif_fonts=True,
    include_sans_serif_fonts=True,
    include_cursive_fonts=False,
    include_fantasy_fonts=True,
    device_type="desktop_custom",
    is_consistent=True
)
```

## API Reference

### FontEnumerationProtectionManager Class

#### `get_random_profile() -> FontEnumerationProfile`
Generate a random font enumeration protection profile with realistic properties.

**Returns:**
- `FontEnumerationProfile`: FontEnumerationProfile with realistic properties

#### `get_device_specific_profile(device_type: str) -> FontEnumerationProfile`
Get a device-specific font enumeration protection profile.

**Parameters:**
- `device_type` (str): Type of device (desktop_windows, desktop_macos, desktop_linux, mobile_ios, mobile_android, tablet)

**Returns:**
- `FontEnumerationProfile`: FontEnumerationProfile with device-specific properties

#### `apply_font_enumeration_protection(context: BrowserContext, profile: Optional[FontEnumerationProfile] = None) -> None`
Apply advanced font enumeration protection to a browser context.

**Parameters:**
- `context` (BrowserContext): Playwright BrowserContext to apply protection to
- `profile` (Optional[FontEnumerationProfile]): FontEnumerationProfile object, or None to generate random

#### `generate_fingerprint(profile: FontEnumerationProfile) -> str`
Generate a fingerprint based on font enumeration profile.

**Parameters:**
- `profile` (FontEnumerationProfile): FontEnumerationProfile object

**Returns:**
- `str`: Font fingerprint hash

#### `are_profiles_consistent(profile: FontEnumerationProfile) -> bool`
Check if font enumeration profile is consistent.

**Parameters:**
- `profile` (FontEnumerationProfile): FontEnumerationProfile object

**Returns:**
- `bool`: True if profile is consistent, False otherwise

#### `_generate_protection_js(profile: FontEnumerationProfile) -> str`
Generate JavaScript to protect against font enumeration fingerprinting.

**Parameters:**
- `profile` (FontEnumerationProfile): FontEnumerationProfile object

**Returns:**
- `str`: JavaScript code string

### FontEnumerationProfile Dataclass

Represents a font enumeration protection configuration with realistic properties.

**Attributes:**
- `font_families` (List[str]): Font families to include in enumeration results
- `include_emoji_fonts` (bool): Whether to include emoji fonts
- `include_monospace_fonts` (bool): Whether to include monospace fonts
- `include_serif_fonts` (bool): Whether to include serif fonts
- `include_sans_serif_fonts` (bool): Whether to include sans-serif fonts
- `include_cursive_fonts` (bool): Whether to include cursive fonts
- `include_fantasy_fonts` (bool): Whether to include fantasy fonts
- `device_type` (str): Type of device (desktop, mobile, tablet)
- `is_consistent` (bool): Whether the profile is internally consistent

## Font Configurations

The FontEnumerationProtectionManager includes predefined font configurations for:

### Desktop Devices
- Windows: Arial, Times New Roman, Courier New, Verdana, Georgia, etc.
- macOS: Helvetica, Times, Courier, Arial, Verdana, Geneva, etc.
- Linux: DejaVu Sans, Liberation Sans, Noto Sans, Ubuntu, etc.

### Mobile Devices
- iOS: San Francisco, Helvetica Neue, Times New Roman, Courier, etc.
- Android: Roboto, Droid Sans, Noto Sans, etc.

### Tablet Devices
- Mixed font sets from desktop and mobile platforms

## Integration with Browser Simulator

The FontEnumerationProtectionManager integrates seamlessly with the BrowserSimulator to provide realistic font enumeration protection:

```python
from ice_locator_mcp.anti_detection.browser_simulator import BrowserSimulator
from ice_locator_mcp.anti_detection.font_enumeration_protection import FontEnumerationProtectionManager
from ice_locator_mcp.core.config import SearchConfig

# Create browser simulator
config = SearchConfig()
browser_sim = BrowserSimulator(config)
font_manager = FontEnumerationProtectionManager()

# The FontEnumerationProtectionManager can be used to create realistic 
# font configurations for each session
```

## Best Practices

1. **Use realistic profiles**: Choose font profiles that match real devices
2. **Vary profiles**: Use different profiles to avoid detection patterns
3. **Apply early**: Apply font enumeration protection to contexts before creating pages
4. **Check consistency**: Verify that profiles are consistent and realistic
5. **Update regularly**: Change font profiles periodically to avoid fingerprinting

## Testing

The FontEnumerationProtectionManager includes comprehensive tests to ensure functionality:

```bash
python -m pytest tests/test_font_enumeration_protection.py -v
```

## Contributing

Contributions to improve font enumeration protection or add new simulation techniques are welcome. Please ensure all tests pass before submitting pull requests.

## License

This module is part of the ICE Locator MCP Server and is licensed under the project's license.