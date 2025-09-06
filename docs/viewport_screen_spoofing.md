# Viewport and Screen Dimension Spoofing Manager

## Overview

The ViewportScreenSpoofingManager provides advanced spoofing of viewport and screen dimensions to prevent browser fingerprinting based on display characteristics. It implements realistic spoofing of screen properties, viewport dimensions, and device pixel ratios.

## Features

- Realistic screen dimension spoofing
- Viewport and outer dimension spoofing
- Device pixel ratio spoofing
- Screen orientation spoofing
- Device-specific dimension configurations
- Consistency validation for dimension profiles

## Installation

The ViewportScreenSpoofingManager is part of the ICE Locator MCP Server and requires no additional installation.

## Usage

### Basic Usage

```python
from ice_locator_mcp.anti_detection.viewport_screen_spoofing import ViewportScreenSpoofingManager

# Create manager instance
viewport_manager = ViewportScreenSpoofingManager()

# Generate a random viewport profile
profile = viewport_manager.get_random_profile()

# Apply spoofing to a browser context
await viewport_manager.apply_viewport_screen_spoofing(context, profile)
```

### Device-Specific Profiles

```python
# Generate device-specific profiles
desktop_4k_profile = viewport_manager.get_device_specific_profile("desktop_4k")
laptop_fhd_profile = viewport_manager.get_device_specific_profile("laptop_fhd")
mobile_profile = viewport_manager.get_device_specific_profile("mobile_high_end")
tablet_profile = viewport_manager.get_device_specific_profile("tablet")
```

### Custom Profiles

```python
from ice_locator_mcp.anti_detection.viewport_screen_spoofing import ViewportScreenProfile

# Create a custom profile
custom_profile = ViewportScreenProfile(
    screen_width=2560,
    screen_height=1440,
    avail_width=2560,
    avail_height=1400,
    color_depth=32,
    pixel_depth=32,
    viewport_width=2560,
    viewport_height=1400,
    outer_width=2560,
    outer_height=1440,
    device_pixel_ratio=1.5,
    orientation_type="landscape-primary",
    orientation_angle=0,
    device_type="desktop_wqhd",
    is_consistent=True
)
```

## API Reference

### ViewportScreenSpoofingManager Class

#### `get_random_profile() -> ViewportScreenProfile`
Generate a random viewport and screen dimension profile with realistic properties.

**Returns:**
- `ViewportScreenProfile`: ViewportScreenProfile with realistic properties

#### `get_device_specific_profile(device_type: str) -> ViewportScreenProfile`
Get a device-specific viewport and screen dimension profile.

**Parameters:**
- `device_type` (str): Type of device (desktop_4k, desktop_wqhd, desktop_fhd, desktop_hd, laptop_fhd, laptop_hd, mobile_high_end, mobile_mid_range, mobile_low_end, tablet)

**Returns:**
- `ViewportScreenProfile`: ViewportScreenProfile with device-specific properties

#### `apply_viewport_screen_spoofing(context: BrowserContext, profile: Optional[ViewportScreenProfile] = None) -> None`
Apply advanced viewport and screen dimension spoofing to a browser context.

**Parameters:**
- `context` (BrowserContext): Playwright BrowserContext to apply spoofing to
- `profile` (Optional[ViewportScreenProfile]): ViewportScreenProfile object, or None to generate random

#### `generate_fingerprint(profile: ViewportScreenProfile) -> str`
Generate a fingerprint based on viewport and screen dimension profile.

**Parameters:**
- `profile` (ViewportScreenProfile): ViewportScreenProfile object

**Returns:**
- `str`: Viewport fingerprint hash

#### `are_profiles_consistent(profile: ViewportScreenProfile) -> bool`
Check if viewport and screen dimension profile is consistent.

**Parameters:**
- `profile` (ViewportScreenProfile): ViewportScreenProfile object

**Returns:**
- `bool`: True if profile is consistent, False otherwise

#### `_generate_spoofing_js(profile: ViewportScreenProfile) -> str`
Generate JavaScript to spoof viewport and screen dimension properties.

**Parameters:**
- `profile` (ViewportScreenProfile): ViewportScreenProfile object

**Returns:**
- `str`: JavaScript code string

### ViewportScreenProfile Dataclass

Represents a viewport and screen dimension configuration with realistic properties.

**Attributes:**
- `screen_width` (int): Screen width in pixels
- `screen_height` (int): Screen height in pixels
- `avail_width` (int): Available screen width in pixels
- `avail_height` (int): Available screen height in pixels
- `color_depth` (int): Screen color depth in bits
- `pixel_depth` (int): Screen pixel depth in bits
- `viewport_width` (int): Viewport width in pixels
- `viewport_height` (int): Viewport height in pixels
- `outer_width` (int): Outer width in pixels
- `outer_height` (int): Outer height in pixels
- `device_pixel_ratio` (float): Device pixel ratio
- `orientation_type` (str): Screen orientation type (landscape-primary, portrait-primary, etc.)
- `orientation_angle` (int): Screen orientation angle (0, 90, 180, 270)
- `device_type` (str): Type of device (desktop, mobile, tablet)
- `is_consistent` (bool): Whether the profile is internally consistent

## Device Configurations

The ViewportScreenSpoofingManager includes predefined configurations for:

### Desktop Devices
- 4K: 3840x2160, 3440x1440, 2560x1440 screen dimensions
- WQHD: 2560x1440, 2560x1080, 3440x1440 screen dimensions
- FHD: 1920x1080, 1920x1200, 1680x1050 screen dimensions
- HD: 1366x768, 1280x1024, 1440x900 screen dimensions

### Laptop Devices
- FHD: 1920x1080, 1600x900, 1366x768 screen dimensions
- HD: 1366x768, 1280x800, 1440x900 screen dimensions

### Mobile Devices
- High-end: 412x892, 414x896, 375x812, 414x736 screen dimensions
- Mid-range: 412x732, 360x740, 360x640, 412x844 screen dimensions
- Low-end: 360x640, 320x568, 375x667, 360x720 screen dimensions

### Tablet Devices
- 768x1024, 800x1280, 834x1194, 1024x1366 screen dimensions

## Integration with Browser Simulator

The ViewportScreenSpoofingManager integrates seamlessly with the BrowserSimulator to provide realistic viewport and screen dimension spoofing:

```python
from ice_locator_mcp.anti_detection.browser_simulator import BrowserSimulator
from ice_locator_mcp.anti_detection.viewport_screen_spoofing import ViewportScreenSpoofingManager
from ice_locator_mcp.core.config import SearchConfig

# Create browser simulator
config = SearchConfig()
browser_sim = BrowserSimulator(config)
viewport_manager = ViewportScreenSpoofingManager()

# The ViewportScreenSpoofingManager can be used to create realistic 
# viewport and screen configurations for each session
```

## Best Practices

1. **Use realistic profiles**: Choose viewport profiles that match real devices
2. **Vary profiles**: Use different profiles to avoid detection patterns
3. **Apply early**: Apply viewport spoofing to contexts before creating pages
4. **Check consistency**: Verify that profiles are consistent and realistic
5. **Update regularly**: Change viewport profiles periodically to avoid fingerprinting

## Testing

The ViewportScreenSpoofingManager includes comprehensive tests to ensure functionality:

```bash
python -m pytest tests/test_viewport_screen_spoofing.py -v
```

## Contributing

Contributions to improve viewport and screen dimension spoofing or add new simulation techniques are welcome. Please ensure all tests pass before submitting pull requests.

## License

This module is part of the ICE Locator MCP Server and is licensed under the project's license.