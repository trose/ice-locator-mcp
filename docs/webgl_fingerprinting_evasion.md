# WebGL Fingerprinting Evasion Manager Documentation

## Overview

The WebGLFingerprintingEvasionManager module provides advanced techniques to prevent WebGL-based browser fingerprinting. It implements sophisticated WebGL vendor and renderer spoofing, debug renderer info protection, and other advanced techniques to avoid detection based on WebGL fingerprints.

## Key Features

- Advanced WebGL vendor and renderer spoofing
- WebGL debug renderer info protection
- WebGL extension spoofing
- WebGL parameter spoofing
- WebGL version spoofing (WebGL 1 and WebGL 2)
- Unmasked vendor and renderer protection
- Realistic WebGL capability simulation
- Integration with Playwright browser contexts

## Installation

The WebGLFingerprintingEvasionManager is part of the ICE Locator MCP Server and requires no additional installation steps.

## Usage

### Basic Usage

```python
from ice_locator_mcp.anti_detection.webgl_fingerprinting_evasion import WebGLFingerprintingEvasionManager

# Create a WebGL fingerprinting evasion manager instance
webgl_evasion_manager = WebGLFingerprintingEvasionManager()

# Generate a random WebGL profile
webgl_profile = webgl_evasion_manager.get_random_webgl_profile()

# Generate a WebGL 1 profile
webgl1_profile = webgl_evasion_manager.get_random_webgl_profile(1)

# Generate a WebGL 2 profile
webgl2_profile = webgl_evasion_manager.get_random_webgl_profile(2)
```

### Applying WebGL Fingerprinting Evasion to Browser Context

```python
import asyncio
from playwright.async_api import async_playwright
from ice_locator_mcp.anti_detection.webgl_fingerprinting_evasion import WebGLFingerprintingEvasionManager

async def example():
    webgl_evasion_manager = WebGLFingerprintingEvasionManager()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        
        # Apply WebGL fingerprinting evasion to the context
        await webgl_evasion_manager.apply_webgl_fingerprinting_evasion(context)
        
        # Or apply a specific WebGL profile
        webgl_profile = webgl_evasion_manager.get_random_webgl_profile()
        await webgl_evasion_manager.apply_webgl_fingerprinting_evasion(context, webgl_profile)
        
        page = await context.new_page()
        await page.goto("https://example.com")
        
        await browser.close()

# Run the example
asyncio.run(example())
```

## API Reference

### WebGLFingerprintingEvasionManager Class

#### `__init__()`
Initializes the WebGLFingerprintingEvasionManager with predefined WebGL configurations.

#### `get_random_webgl_profile(webgl_version: Optional[int] = None) -> AdvancedWebGLProfile`
Get a random advanced WebGL profile with realistic properties.

**Parameters:**
- `webgl_version` (Optional[int]): WebGL version (1 or 2), or None for random

**Returns:**
- `AdvancedWebGLProfile`: AdvancedWebGLProfile with realistic WebGL properties

#### `apply_webgl_fingerprinting_evasion(context: BrowserContext, webgl_profile: Optional[AdvancedWebGLProfile] = None) -> None`
Apply advanced WebGL fingerprinting evasion to a browser context.

**Parameters:**
- `context` (BrowserContext): Playwright BrowserContext to apply evasion to
- `webgl_profile` (Optional[AdvancedWebGLProfile]): AdvancedWebGLProfile object, or None to generate random

#### `generate_webgl_fingerprint(webgl_profile: AdvancedWebGLProfile) -> str`
Generate a WebGL fingerprint based on the profile.

**Parameters:**
- `webgl_profile` (AdvancedWebGLProfile): AdvancedWebGLProfile object

**Returns:**
- `str`: String fingerprint hash

#### `is_webgl_profile_consistent(webgl_profile: AdvancedWebGLProfile) -> bool`
Check if a WebGL profile is consistent and realistic.

**Parameters:**
- `webgl_profile` (AdvancedWebGLProfile): AdvancedWebGLProfile object

**Returns:**
- `bool`: True if profile is consistent, False otherwise

#### `_generate_webgl_evasion_js(webgl_profile: AdvancedWebGLProfile) -> str`
Generate JavaScript to implement advanced WebGL fingerprinting evasion.

**Parameters:**
- `webgl_profile` (AdvancedWebGLProfile): AdvancedWebGLProfile object

**Returns:**
- `str`: JavaScript code string

### AdvancedWebGLProfile Dataclass

Represents an advanced WebGL configuration with realistic properties for fingerprinting evasion.

**Attributes:**
- `vendor` (str): WebGL vendor string
- `renderer` (str): WebGL renderer string
- `unmasked_vendor` (str): Unmasked WebGL vendor string
- `unmasked_renderer` (str): Unmasked WebGL renderer string
- `version` (str): WebGL version string
- `shading_language_version` (str): WebGL shading language version
- `extensions` (List[str]): Supported WebGL extensions
- `parameters` (Dict[str, Any]): WebGL parameters
- `max_texture_size` (int): Maximum texture size
- `max_viewport_dims` (Tuple[int, int]): Maximum viewport dimensions
- `red_bits` (int): Red color bits
- `green_bits` (int): Green color bits
- `blue_bits` (int): Blue color bits
- `alpha_bits` (int): Alpha color bits
- `depth_bits` (int): Depth buffer bits
- `stencil_bits` (int): Stencil buffer bits
- `antialiasing` (str): Antialiasing support
- `preferred_webgl_version` (int): Preferred WebGL version (1 or 2)

## WebGL Configurations

The WebGLFingerprintingEvasionManager includes predefined WebGL configurations for:

### Realistic WebGL Vendor/Renderer Pairs
- Intel Inc. / Intel Iris OpenGL Engine
- NVIDIA Corporation / NVIDIA GeForce GTX 1080 OpenGL Engine
- ATI Technologies Inc. / AMD Radeon Pro 560 OpenGL Engine
- ARM / Mali-G78
- Qualcomm / Adreno (TM) 660
- Google Inc. (Apple) / ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)
- Apple / Apple GPU
- Microsoft / Direct3D11

### WebGL Extensions
The manager includes realistic WebGL extensions for both WebGL 1 and WebGL 2:

#### WebGL 1 Extensions
- ANGLE_instanced_arrays
- EXT_blend_minmax
- EXT_color_buffer_half_float
- EXT_disjoint_timer_query
- EXT_float_blend
- EXT_frag_depth
- EXT_shader_texture_lod
- EXT_texture_compression_bptc
- EXT_texture_compression_rgtc
- EXT_texture_filter_anisotropic
- EXT_sRGB
- KHR_parallel_shader_compile
- OES_element_index_uint
- OES_fbo_render_mipmap
- OES_standard_derivatives
- OES_texture_float
- OES_texture_float_linear
- OES_texture_half_float
- OES_texture_half_float_linear
- OES_vertex_array_object
- WEBGL_color_buffer_float
- WEBGL_compressed_texture_s3tc
- WEBGL_compressed_texture_s3tc_srgb
- WEBGL_debug_renderer_info
- WEBGL_debug_shaders
- WEBGL_depth_texture
- WEBGL_draw_buffers
- WEBGL_lose_context

#### WebGL 2 Extensions
- EXT_color_buffer_float
- EXT_disjoint_timer_query_webgl2
- EXT_float_blend
- EXT_texture_compression_bptc
- EXT_texture_compression_rgtc
- EXT_texture_filter_anisotropic
- EXT_texture_norm16
- KHR_parallel_shader_compile
- OES_texture_float_linear
- WEBGL_compressed_texture_s3tc
- WEBGL_compressed_texture_s3tc_srgb
- WEBGL_debug_renderer_info
- WEBGL_debug_shaders
- WEBGL_lose_context
- WEBGL_multi_draw

### WebGL Parameters
The manager simulates realistic WebGL parameters including:
- VERSION
- SHADING_LANGUAGE_VERSION
- VENDOR
- RENDERER
- UNMASKED_VENDOR_WEBGL
- UNMASKED_RENDERER_WEBGL
- MAX_TEXTURE_SIZE
- MAX_VIEWPORT_DIMS
- RED_BITS
- GREEN_BITS
- BLUE_BITS
- ALPHA_BITS
- DEPTH_BITS
- STENCIL_BITS
- MAX_VERTEX_ATTRIBS
- MAX_VERTEX_UNIFORM_VECTORS
- MAX_VARYING_VECTORS
- MAX_COMBINED_TEXTURE_IMAGE_UNITS
- MAX_VERTEX_TEXTURE_IMAGE_UNITS
- MAX_TEXTURE_IMAGE_UNITS
- MAX_FRAGMENT_UNIFORM_VECTORS
- MAX_RENDERBUFFER_SIZE
- MAX_CUBE_MAP_TEXTURE_SIZE
- MAX_ARRAY_TEXTURE_LAYERS
- MAX_UNIFORM_BUFFER_BINDINGS
- MAX_UNIFORM_BLOCK_SIZE

## Advanced Techniques

### Unmasked Vendor and Renderer Protection
The manager implements protection against unmasked vendor and renderer detection by:
- Providing different values for masked and unmasked properties
- Simulating the difference between what websites can see normally vs. through debug extensions
- Ensuring consistency between vendor/renderer pairs

### WebGL Version Spoofing
The manager supports both WebGL 1 and WebGL 2 spoofing:
- Realistic extension lists for each version
- Appropriate version strings and shading language versions
- Consistent parameter values for each version

### Hardware Capability Simulation
The manager simulates realistic hardware capabilities:
- Appropriate max texture sizes for different GPU types (mobile vs. desktop)
- Realistic color depth values
- Consistent depth and stencil buffer configurations
- Antialiasing support simulation

## Integration with Browser Simulator

The WebGLFingerprintingEvasionManager integrates seamlessly with the BrowserSimulator to provide realistic WebGL fingerprinting evasion:

```python
from ice_locator_mcp.anti_detection.browser_simulator import BrowserSimulator
from ice_locator_mcp.anti_detection.webgl_fingerprinting_evasion import WebGLFingerprintingEvasionManager
from ice_locator_mcp.core.config import SearchConfig

# Create browser simulator
config = SearchConfig()
browser_sim = BrowserSimulator(config)
webgl_evasion_manager = WebGLFingerprintingEvasionManager()

# The WebGL fingerprinting evasion manager can be used by the browser simulator
# to create realistic WebGL configurations for each session
```

## Best Practices

1. **Use realistic profiles**: Choose WebGL profiles that match real devices
2. **Vary profiles**: Use different profiles to avoid detection patterns
3. **Apply early**: Apply WebGL fingerprinting evasion to contexts before creating pages
4. **Check consistency**: Verify that profiles are consistent and realistic
5. **Update regularly**: Change WebGL profiles periodically to avoid fingerprinting

## Testing

The WebGLFingerprintingEvasionManager includes comprehensive tests to ensure functionality:

```bash
python -m pytest tests/test_webgl_fingerprinting_evasion.py -v
```

## Contributing

Contributions to improve WebGL fingerprinting evasion techniques or add new simulation methods are welcome. Please ensure all tests pass before submitting pull requests.

## License

This module is part of the ICE Locator MCP Server and is licensed under the project's license.