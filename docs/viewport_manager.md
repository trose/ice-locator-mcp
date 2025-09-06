# Viewport Manager Documentation

## Overview

The ViewportManager module provides advanced viewport and screen simulation capabilities to avoid detection based on display characteristics. It implements realistic screen dimensions, device emulation, and dynamic viewport resizing to make browser sessions appear more human-like.

## Key Features

- Realistic viewport dimension generation
- Device-specific viewport profiles (desktop, laptop, mobile, tablet)
- Screen property spoofing
- Dynamic viewport resizing capabilities
- Device category detection
- Integration with Playwright browser contexts

## Installation

The ViewportManager is part of the ICE Locator MCP Server and requires no additional installation steps.

## Usage

### Basic Usage

```python
from ice_locator_mcp.anti_detection.viewport_manager import ViewportManager

# Create a viewport manager instance
viewport_manager = ViewportManager()

# Generate a realistic viewport
viewport = viewport_manager.generate_realistic_viewport()

# Get a random desktop viewport
desktop_viewport = viewport_manager.get_random_viewport("desktop")

# Get a random device profile
device_profile = viewport_manager.get_random_device_profile()
```

### Applying Viewport to Browser Context

```python
import asyncio
from playwright.async_api import async_playwright
from ice_locator_mcp.anti_detection.viewport_manager import ViewportManager

async def example():
    viewport_manager = ViewportManager()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        
        # Apply a realistic viewport to the context
        await viewport_manager.apply_viewport_to_context(context)
        
        # Or apply a specific viewport
        viewport = viewport_manager.get_random_viewport("mobile")
        await viewport_manager.apply_viewport_to_context(context, viewport)
        
        page = await context.new_page()
        await page.goto("https://example.com")
        
        await browser.close()

# Run the example
asyncio.run(example())
```

## API Reference

### ViewportManager Class

#### `__init__()`
Initializes the ViewportManager with predefined viewport configurations for different device types.

#### `get_random_viewport(device_type: str) -> ViewportProfile`
Get a random viewport configuration based on device type.

**Parameters:**
- `device_type` (str): Type of device ("desktop", "laptop", "mobile", "tablet")

**Returns:**
- `ViewportProfile`: ViewportProfile with realistic properties

#### `get_random_device_profile() -> DeviceProfile`
Get a random device profile with realistic properties.

**Returns:**
- `DeviceProfile`: DeviceProfile with realistic viewport and browser properties

#### `generate_realistic_viewport() -> ViewportProfile`
Generate a completely realistic viewport with natural variations.

**Returns:**
- `ViewportProfile`: ViewportProfile with realistic properties

#### `apply_viewport_to_context(context: BrowserContext, viewport: Optional[ViewportProfile] = None) -> None`
Apply viewport and screen properties to a browser context.

**Parameters:**
- `context` (BrowserContext): Playwright BrowserContext to apply viewport to
- `viewport` (Optional[ViewportProfile]): ViewportProfile to apply, or None to generate a random one

#### `get_viewport_dimensions(viewport: ViewportProfile) -> Tuple[int, int]`
Get viewport dimensions as a tuple.

**Parameters:**
- `viewport` (ViewportProfile): ViewportProfile to get dimensions from

**Returns:**
- `Tuple[int, int]`: Tuple of (width, height)

#### `get_screen_dimensions(viewport: ViewportProfile) -> Tuple[int, int]`
Get screen dimensions as a tuple.

**Parameters:**
- `viewport` (ViewportProfile): ViewportProfile to get dimensions from

**Returns:**
- `Tuple[int, int]`: Tuple of (width, height)

#### `is_mobile_viewport(viewport: ViewportProfile) -> bool`
Check if viewport is mobile-sized.

**Parameters:**
- `viewport` (ViewportProfile): ViewportProfile to check

**Returns:**
- `bool`: True if viewport is mobile-sized, False otherwise

#### `is_tablet_viewport(viewport: ViewportProfile) -> bool`
Check if viewport is tablet-sized.

**Parameters:**
- `viewport` (ViewportProfile): ViewportProfile to check

**Returns:**
- `bool`: True if viewport is tablet-sized, False otherwise

#### `get_device_category(viewport: ViewportProfile) -> str`
Get device category based on viewport properties.

**Parameters:**
- `viewport` (ViewportProfile): ViewportProfile to categorize

**Returns:**
- `str`: Device category ("mobile", "tablet", "laptop", "desktop")

### ViewportProfile Dataclass

Represents a viewport configuration with realistic properties.

**Attributes:**
- `width` (int): Viewport width in pixels
- `height` (int): Viewport height in pixels
- `device_scale_factor` (float): Device pixel ratio
- `is_mobile` (bool): Whether this is a mobile viewport
- `has_touch` (bool): Whether this device has touch capabilities
- `screen_width` (int): Screen width in pixels
- `screen_height` (int): Screen height in pixels
- `avail_width` (int): Available screen width in pixels
- `avail_height` (int): Available screen height in pixels
- `color_depth` (int): Screen color depth
- `pixel_depth` (int): Screen pixel depth
- `orientation_type` (str): Screen orientation type
- `orientation_angle` (int): Screen orientation angle

### DeviceProfile Dataclass

Represents a device with specific screen and viewport characteristics.

**Attributes:**
- `name` (str): Device name
- `viewport` (ViewportProfile): Viewport configuration
- `user_agent` (str): Browser user agent string
- `platform` (str): Browser platform string

## Viewport Configurations

The ViewportManager includes predefined viewport configurations for:

### Desktop Viewports
- 1920x1080 (Full HD)
- 1366x768 (Common laptop)
- 1536x864 (Common laptop with high DPI)
- 1440x900 (Common desktop)
- 1600x900 (Common desktop)
- 1280x1024 (Common desktop)
- 1280x800 (Common laptop)
- 1680x1050 (Common desktop)
- 1920x1200 (Common desktop)

### Laptop Viewports
- 1366x768 (Common laptop)
- 1536x864 (Common laptop with high DPI)
- 1440x900 (Common laptop)
- 1280x800 (Common laptop)
- 1600x900 (Common laptop)

### Mobile Viewports
- 375x667 (iPhone-sized)
- 414x896 (iPhone-sized)
- 360x640 (Android-sized)
- 414x736 (iPhone-sized)
- 360x780 (Android-sized)

### Tablet Viewports
- 768x1024 (iPad-sized)
- 834x1112 (iPad-sized)
- 810x1080 (iPad-sized)
- 1024x1366 (iPad-sized in landscape)

## Device Profiles

The ViewportManager includes realistic device profiles for:

- MacBook Pro 13", 14", 16"
- Dell XPS 13, 15
- iPhone 14 Pro
- iPad Pro 12.9"

## Integration with Browser Simulator

The ViewportManager integrates seamlessly with the BrowserSimulator to provide realistic viewport simulation:

```python
from ice_locator_mcp.anti_detection.browser_simulator import BrowserSimulator
from ice_locator_mcp.anti_detection.viewport_manager import ViewportManager
from ice_locator_mcp.core.config import SearchConfig

# Create browser simulator
config = SearchConfig()
browser_sim = BrowserSimulator(config)
viewport_manager = ViewportManager()

# The viewport manager is automatically used by the browser simulator
# to create realistic viewport configurations for each session
```

## Best Practices

1. **Use realistic viewport sizes**: Choose viewport dimensions that match real devices
2. **Match device characteristics**: Ensure viewport properties match the device type
3. **Vary viewport sizes**: Use different viewport sizes to avoid detection patterns
4. **Apply to contexts early**: Apply viewport configurations before creating pages
5. **Use device profiles**: Leverage predefined device profiles for consistency

## Testing

The ViewportManager includes comprehensive tests to ensure functionality:

```bash
python -m pytest tests/test_viewport_manager.py -v
```

## Contributing

Contributions to improve viewport configurations or add new device profiles are welcome. Please ensure all tests pass before submitting pull requests.

## License

This module is part of the ICE Locator MCP Server and is licensed under the project's license.