# Font and Media Manager Documentation

## Overview

The FontMediaManager module provides advanced font and media simulation capabilities to avoid fingerprinting based on system resources. It implements font enumeration protection and media capability spoofing to make browser sessions appear more human-like and reduce detection risk.

## Key Features

- Realistic font enumeration protection
- Media capability spoofing
- WebGL extension and parameter spoofing
- Audio/video codec support simulation
- Media device enumeration protection
- Integration with Playwright browser contexts

## Installation

The FontMediaManager is part of the ICE Locator MCP Server and requires no additional installation steps.

## Usage

### Basic Usage

```python
from ice_locator_mcp.anti_detection.font_media_manager import FontMediaManager

# Create a font media manager instance
font_media_manager = FontMediaManager()

# Generate a random font list
font_list = font_media_manager.get_random_font_list(15)

# Generate a random media profile
media_profile = font_media_manager.get_random_media_profile()

# Get font names from font profile
font_names = font_media_manager.get_font_names(font_list)
```

### Applying Font and Media Simulation to Browser Context

```python
import asyncio
from playwright.async_api import async_playwright
from ice_locator_mcp.anti_detection.font_media_manager import FontMediaManager

async def example():
    font_media_manager = FontMediaManager()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        
        # Apply font and media simulation to the context
        await font_media_manager.apply_font_media_simulation(context)
        
        # Or apply specific font and media profiles
        font_profile = font_media_manager.get_random_font_list(10)
        media_profile = font_media_manager.get_random_media_profile()
        await font_media_manager.apply_font_media_simulation(context, font_profile, media_profile)
        
        page = await context.new_page()
        await page.goto("https://example.com")
        
        await browser.close()

# Run the example
asyncio.run(example())
```

## API Reference

### FontMediaManager Class

#### `__init__()`
Initializes the FontMediaManager with predefined font and media configurations.

#### `get_random_font_list(count: int = 20) -> List[FontProfile]`
Get a random list of fonts to simulate realistic font enumeration.

**Parameters:**
- `count` (int): Number of fonts to include in the list (default: 20)

**Returns:**
- `List[FontProfile]`: List of FontProfile objects

#### `get_random_media_profile() -> MediaProfile`
Get a random media profile with realistic properties.

**Returns:**
- `MediaProfile`: MediaProfile with realistic media capabilities

#### `apply_font_media_simulation(context: BrowserContext, font_profile: Optional[List[FontProfile]] = None, media_profile: Optional[MediaProfile] = None) -> None`
Apply font and media simulation to a browser context.

**Parameters:**
- `context` (BrowserContext): Playwright BrowserContext to apply simulation to
- `font_profile` (Optional[List[FontProfile]]): List of FontProfile objects, or None to generate random
- `media_profile` (Optional[MediaProfile]): MediaProfile object, or None to generate random

#### `get_font_names(font_profile: List[FontProfile]) -> List[str]`
Get font names from a font profile.

**Parameters:**
- `font_profile` (List[FontProfile]): List of FontProfile objects

**Returns:**
- `List[str]`: List of font names

#### `is_monospace_font(font: FontProfile) -> bool`
Check if a font is monospace.

**Parameters:**
- `font` (FontProfile): FontProfile to check

**Returns:**
- `bool`: True if font is monospace, False otherwise

#### `is_serif_font(font: FontProfile) -> bool`
Check if a font is serif.

**Parameters:**
- `font` (FontProfile): FontProfile to check

**Returns:**
- `bool`: True if font is serif, False otherwise

### FontProfile Dataclass

Represents a font configuration with realistic properties.

**Attributes:**
- `name` (str): Font name
- `generic_family` (str): Generic CSS font family
- `is_monospace` (bool): Whether the font is monospace
- `is_serif` (bool): Whether the font is serif
- `is_sans_serif` (bool): Whether the font is sans-serif
- `is_display` (bool): Whether the font is a display font
- `is_handwriting` (bool): Whether the font is a handwriting font

### MediaProfile Dataclass

Represents a media configuration with realistic properties.

**Attributes:**
- `audio_codecs` (List[str]): Supported audio codecs
- `video_codecs` (List[str]): Supported video codecs
- `media_devices` (List[Dict[str, str]]): Media device configurations
- `webgl_extensions` (List[str]): Supported WebGL extensions
- `webgl_parameters` (Dict[str, str]): WebGL parameter values

## Font Configurations

The FontMediaManager includes a comprehensive list of common fonts found on different platforms:

### Sans-serif Fonts
- Arial, Helvetica, Verdana, Tahoma, Segoe UI, Geneva, Calibri, Candara, Optima, Futura, Gill Sans, Franklin Gothic, Myriad Pro, Lucida Grande, Century Gothic, Apple Gothic, Apple SD Gothic Neo, Nanum Gothic, Malgun Gothic, SimHei, Microsoft YaHei

### Serif Fonts
- Times New Roman, Times, Georgia, Palatino, Garamond, Century Schoolbook

### Monospace Fonts
- Courier New, Courier, Lucida Console, Monaco

### Display Fonts
- Arial Black, Impact

### Handwriting Fonts
- Comic Sans MS

## Media Capabilities

The FontMediaManager simulates realistic media capabilities including:

### Audio Codecs
- audio/mp3, audio/mp4, audio/aac, audio/ogg, audio/wav, audio/webm, audio/flac, audio/x-m4a, audio/x-aac, audio/x-wav

### Video Codecs
- video/mp4, video/webm, video/ogg, video/quicktime, video/x-msvideo, video/x-flv, video/3gpp, video/3gpp2, video/h264, video/x-m4v

### WebGL Extensions
- ANGLE_instanced_arrays, EXT_blend_minmax, EXT_color_buffer_half_float, EXT_disjoint_timer_query, EXT_float_blend, EXT_frag_depth, EXT_shader_texture_lod, EXT_texture_compression_bptc, EXT_texture_compression_rgtc, EXT_texture_filter_anisotropic, EXT_sRGB, KHR_parallel_shader_compile, OES_element_index_uint, OES_fbo_render_mipmap, OES_standard_derivatives, OES_texture_float, OES_texture_float_linear, OES_texture_half_float, OES_texture_half_float_linear, OES_vertex_array_object, WEBGL_color_buffer_float, WEBGL_compressed_texture_s3tc, WEBGL_compressed_texture_s3tc_srgb, WEBGL_debug_renderer_info, WEBGL_debug_shaders, WEBGL_depth_texture, WEBGL_draw_buffers, WEBGL_lose_context

### Media Devices
- Audio input devices (microphones)
- Audio output devices (speakers)
- Video input devices (cameras)

## Integration with Browser Simulator

The FontMediaManager integrates seamlessly with the BrowserSimulator to provide realistic font and media simulation:

```python
from ice_locator_mcp.anti_detection.browser_simulator import BrowserSimulator
from ice_locator_mcp.anti_detection.font_media_manager import FontMediaManager
from ice_locator_mcp.core.config import SearchConfig

# Create browser simulator and font media manager
config = SearchConfig()
browser_sim = BrowserSimulator(config)
font_media_manager = FontMediaManager()

# The font media manager can be used to enhance browser simulation
# by adding realistic font and media capabilities
```

## Best Practices

1. **Use realistic font lists**: Choose fonts that are commonly found on the target platform
2. **Match media capabilities**: Ensure media capabilities match the device type
3. **Vary configurations**: Use different font and media configurations to avoid detection patterns
4. **Apply early**: Apply font and media simulation to contexts before creating pages
5. **Combine with other evasion techniques**: Use font and media simulation in conjunction with other anti-detection measures

## Testing

The FontMediaManager includes comprehensive tests to ensure functionality:

```bash
python -m pytest tests/test_font_media_manager.py -v
```

## Contributing

Contributions to improve font configurations or add new media capabilities are welcome. Please ensure all tests pass before submitting pull requests.

## License

This module is part of the ICE Locator MCP Server and is licensed under the project's license.