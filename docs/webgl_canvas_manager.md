# WebGL and Canvas Manager Documentation

## Overview

The WebGLCanvasManager module provides advanced WebGL and canvas rendering simulation capabilities to avoid graphics-based fingerprinting. It implements realistic rendering patterns, WebGL vendor/renderer spoofing, canvas noise injection, and other techniques to prevent detection based on graphics capabilities.

## Key Features

- Realistic WebGL rendering simulation
- Canvas rendering spoofing with noise injection
- WebGL vendor and renderer spoofing
- WebGL extension and parameter spoofing
- Canvas text rendering variations
- Pixel noise injection
- Rendering timing variations
- Integration with Playwright browser contexts

## Installation

The WebGLCanvasManager is part of the ICE Locator MCP Server and requires no additional installation steps.

## Usage

### Basic Usage

```python
from ice_locator_mcp.anti_detection.webgl_canvas_manager import WebGLCanvasManager

# Create a WebGLCanvasManager instance
webgl_canvas_manager = WebGLCanvasManager()

# Generate a random WebGL profile
webgl_profile = webgl_canvas_manager.get_random_webgl_profile()

# Generate a random canvas profile
canvas_profile = webgl_canvas_manager.get_random_canvas_profile()

# Generate completely realistic profiles
realistic_webgl = webgl_canvas_manager.generate_realistic_webgl_profile()
realistic_canvas = webgl_canvas_manager.generate_realistic_canvas_profile()
```

### Applying WebGL and Canvas Simulation to Browser Context

```python
import asyncio
from playwright.async_api import async_playwright
from ice_locator_mcp.anti_detection.webgl_canvas_manager import WebGLCanvasManager

async def example():
    webgl_canvas_manager = WebGLCanvasManager()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        
        # Apply WebGL and canvas simulation to the context
        await webgl_canvas_manager.apply_webgl_canvas_simulation(context)
        
        # Or apply specific profiles
        webgl_profile = webgl_canvas_manager.get_random_webgl_profile()
        canvas_profile = webgl_canvas_manager.get_random_canvas_profile()
        await webgl_canvas_manager.apply_webgl_canvas_simulation(context, webgl_profile, canvas_profile)
        
        page = await context.new_page()
        await page.goto("https://example.com")
        
        await browser.close()

# Run the example
asyncio.run(example())
```

## API Reference

### WebGLCanvasManager Class

#### `__init__()`
Initializes the WebGLCanvasManager with predefined WebGL and canvas configurations.

#### `get_random_webgl_profile() -> WebGLProfile`
Get a random WebGL profile with realistic properties.

**Returns:**
- `WebGLProfile`: WebGLProfile with realistic properties

#### `get_random_canvas_profile() -> CanvasProfile`
Get a random canvas profile with realistic properties.

**Returns:**
- `CanvasProfile`: CanvasProfile with realistic properties

#### `generate_realistic_webgl_profile() -> WebGLProfile`
Generate a completely realistic WebGL profile with natural variations.

**Returns:**
- `WebGLProfile`: WebGLProfile with realistic properties

#### `generate_realistic_canvas_profile() -> CanvasProfile`
Generate a completely realistic canvas profile with natural variations.

**Returns:**
- `CanvasProfile`: CanvasProfile with realistic properties

#### `generate_webgl_fingerprint(profile: WebGLProfile) -> str`
Generate a WebGL fingerprint hash from a profile.

**Parameters:**
- `profile` (WebGLProfile): WebGL profile to generate fingerprint from

**Returns:**
- `str`: WebGL fingerprint hash

#### `generate_canvas_fingerprint(profile: CanvasProfile) -> str`
Generate a canvas fingerprint hash from a profile.

**Parameters:**
- `profile` (CanvasProfile): Canvas profile to generate fingerprint from

**Returns:**
- `str`: Canvas fingerprint hash

#### `is_webgl_profile_consistent(profile: WebGLProfile) -> bool`
Check if a WebGL profile is consistent and realistic.

**Parameters:**
- `profile` (WebGLProfile): WebGL profile to check

**Returns:**
- `bool`: True if profile is consistent, False otherwise

#### `is_canvas_profile_consistent(profile: CanvasProfile) -> bool`
Check if a canvas profile is consistent and realistic.

**Parameters:**
- `profile` (CanvasProfile): Canvas profile to check

**Returns:**
- `bool`: True if profile is consistent, False otherwise

#### `apply_webgl_canvas_simulation(context: BrowserContext, webgl_profile: Optional[WebGLProfile] = None, canvas_profile: Optional[CanvasProfile] = None) -> None`
Apply WebGL and canvas simulation to a browser context.

**Parameters:**
- `context` (BrowserContext): Playwright BrowserContext to apply simulation to
- `webgl_profile` (Optional[WebGLProfile]): WebGLProfile to apply, or None to generate a random one
- `canvas_profile` (Optional[CanvasProfile]): CanvasProfile to apply, or None to generate a random one

### WebGLProfile Dataclass

Represents a WebGL configuration with realistic properties.

**Attributes:**
- `vendor` (str): WebGL vendor string
- `renderer` (str): WebGL renderer string
- `version` (str): WebGL version string
- `shading_language_version` (str): WebGL shading language version
- `extensions` (List[str]): Supported WebGL extensions
- `parameters` (Dict[str, Any]): WebGL parameters
- `unmasked_vendor` (str): Unmasked vendor string
- `unmasked_renderer` (str): Unmasked renderer string

### CanvasProfile Dataclass

Represents a canvas configuration with realistic properties.

**Attributes:**
- `text_rendering_variations` (bool): Whether to add text rendering variations
- `noise_injection_level` (float): Level of noise injection (0.0-1.0)
- `rendering_timing_variation` (float): Rendering timing variation factor
- `pixel_depth` (int): Canvas pixel depth
- `color_space` (str): Canvas color space
- `will_read_frequently` (bool): Whether canvas will be read frequently

## WebGL Configurations

The WebGLCanvasManager includes predefined WebGL configurations for:

### Common WebGL Vendors
- Google Inc.
- Intel Inc.
- NVIDIA Corporation
- AMD
- Apple
- Microsoft

### Common WebGL Renderers
- Intel Iris OpenGL Engine
- ANGLE (Intel, NVIDIA, AMD)
- Mesa
- Direct3D
- Apple GPU

### WebGL Extensions
The manager includes realistic WebGL extensions such as:
- WEBGL_debug_renderer_info
- OES_texture_float
- OES_texture_half_float
- OES_standard_derivatives
- EXT_shader_texture_lod
- WEBGL_depth_texture
- EXT_texture_filter_anisotropic

### WebGL Parameters
The manager simulates realistic WebGL parameters including:
- VERSION
- RENDERER
- VENDOR
- SHADING_LANGUAGE_VERSION
- MAX_TEXTURE_SIZE
- MAX_VIEWPORT_DIMS
- RED_BITS
- GREEN_BITS
- BLUE_BITS
- ALPHA_BITS
- DEPTH_BITS
- STENCIL_BITS

## Canvas Configurations

The WebGLCanvasManager includes realistic canvas configurations with:

### Text Rendering Variations
- Slight variations in text measurements
- Random offsets in text positioning
- Natural variations in font rendering

### Noise Injection
- Pixel-level noise injection
- Subtle color variations
- Random noise patterns

### Rendering Timing Variations
- Variable rendering delays
- Natural timing fluctuations
- Human-like rendering patterns

## Integration with Browser Simulator

The WebGLCanvasManager integrates seamlessly with the BrowserSimulator to provide realistic WebGL and canvas simulation:

```python
from ice_locator_mcp.anti_detection.browser_simulator import BrowserSimulator
from ice_locator_mcp.anti_detection.webgl_canvas_manager import WebGLCanvasManager
from ice_locator_mcp.core.config import SearchConfig

# Create browser simulator
config = SearchConfig()
browser_sim = BrowserSimulator(config)
webgl_canvas_manager = WebGLCanvasManager()

# The WebGLCanvasManager is automatically used by the browser simulator
# to create realistic WebGL and canvas configurations for each session
```

## Best Practices

1. **Use realistic profiles**: Choose WebGL and canvas profiles that match real devices
2. **Vary profiles**: Use different profiles to avoid detection patterns
3. **Apply early**: Apply WebGL and canvas simulation to contexts before creating pages
4. **Check consistency**: Verify that profiles are consistent and realistic
5. **Update regularly**: Change WebGL and canvas profiles periodically to avoid fingerprinting

## Testing

The WebGLCanvasManager includes comprehensive tests to ensure functionality:

```bash
python -m pytest tests/test_webgl_canvas_manager.py -v
```

## Contributing

Contributions to improve WebGL and canvas configurations or add new simulation techniques are welcome. Please ensure all tests pass before submitting pull requests.

## License

This module is part of the ICE Locator MCP Server and is licensed under the project's license.