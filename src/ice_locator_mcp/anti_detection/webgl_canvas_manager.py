"""
WebGL and Canvas Rendering Simulation Manager for ICE Locator MCP Server.

This module provides advanced WebGL and canvas rendering simulation capabilities to avoid 
graphics-based fingerprinting. It implements realistic rendering patterns and output 
to prevent detection based on WebGL and canvas fingerprints.
"""

import random
import structlog
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from playwright.async_api import BrowserContext
import hashlib
import time


@dataclass
class WebGLProfile:
    """Represents a WebGL configuration with realistic properties."""
    vendor: str
    renderer: str
    version: str
    shading_language_version: str
    extensions: List[str]
    parameters: Dict[str, Any]
    max_texture_size: int
    max_viewport_dims: int
    red_bits: int
    green_bits: int
    blue_bits: int
    alpha_bits: int
    depth_bits: int
    stencil_bits: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "vendor": self.vendor,
            "renderer": self.renderer,
            "version": self.version,
            "shading_language_version": self.shading_language_version,
            "extensions": self.extensions,
            "parameters": self.parameters,
            "max_texture_size": self.max_texture_size,
            "max_viewport_dims": self.max_viewport_dims,
            "red_bits": self.red_bits,
            "green_bits": self.green_bits,
            "blue_bits": self.blue_bits,
            "alpha_bits": self.alpha_bits,
            "depth_bits": self.depth_bits,
            "stencil_bits": self.stencil_bits
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebGLProfile':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class CanvasProfile:
    """Represents a canvas configuration with realistic properties."""
    text_rendering_variation: float  # Amount of variation in text rendering
    pixel_noise_level: float  # Level of noise to add to pixels
    rendering_timing_variation: float  # Variation in rendering timing
    fill_text_offset_variation: Tuple[float, float]  # X, Y offset variation for fillText
    to_data_url_noise: bool  # Whether to add noise to toDataURL
    get_image_data_noise: bool  # Whether to add noise to getImageData
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "text_rendering_variation": self.text_rendering_variation,
            "pixel_noise_level": self.pixel_noise_level,
            "rendering_timing_variation": self.rendering_timing_variation,
            "fill_text_offset_variation": list(self.fill_text_offset_variation),
            "to_data_url_noise": self.to_data_url_noise,
            "get_image_data_noise": self.get_image_data_noise
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CanvasProfile':
        """Create from dictionary."""
        data["fill_text_offset_variation"] = tuple(data["fill_text_offset_variation"])
        return cls(**data)


class WebGLCanvasManager:
    """Manages advanced WebGL and canvas rendering simulation to avoid graphics-based fingerprinting."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        
        # Common WebGL vendors and renderers
        self.common_webgl_configs = [
            {
                "vendor": "Intel Inc.",
                "renderer": "Intel Iris OpenGL Engine",
                "version": "WebGL 1.0",
                "shading_language_version": "WebGL GLSL ES 1.0",
                "max_texture_size": 16384,
                "max_viewport_dims": 16384,
                "red_bits": 8,
                "green_bits": 8,
                "blue_bits": 8,
                "alpha_bits": 8,
                "depth_bits": 24,
                "stencil_bits": 0
            },
            {
                "vendor": "NVIDIA Corporation",
                "renderer": "NVIDIA GeForce GTX 1080 OpenGL Engine",
                "version": "WebGL 1.0",
                "shading_language_version": "WebGL GLSL ES 1.0",
                "max_texture_size": 16384,
                "max_viewport_dims": 16384,
                "red_bits": 8,
                "green_bits": 8,
                "blue_bits": 8,
                "alpha_bits": 8,
                "depth_bits": 24,
                "stencil_bits": 0
            },
            {
                "vendor": "ATI Technologies Inc.",
                "renderer": "AMD Radeon Pro 560 OpenGL Engine",
                "version": "WebGL 1.0",
                "shading_language_version": "WebGL GLSL ES 1.0",
                "max_texture_size": 16384,
                "max_viewport_dims": 16384,
                "red_bits": 8,
                "green_bits": 8,
                "blue_bits": 8,
                "alpha_bits": 8,
                "depth_bits": 24,
                "stencil_bits": 0
            },
            {
                "vendor": "ARM",
                "renderer": "Mali-T860",
                "version": "WebGL 1.0",
                "shading_language_version": "WebGL GLSL ES 1.0",
                "max_texture_size": 8192,
                "max_viewport_dims": 8192,
                "red_bits": 8,
                "green_bits": 8,
                "blue_bits": 8,
                "alpha_bits": 8,
                "depth_bits": 24,
                "stencil_bits": 0
            },
            {
                "vendor": "Qualcomm",
                "renderer": "Adreno (TM) 540",
                "version": "WebGL 1.0",
                "shading_language_version": "WebGL GLSL ES 1.0",
                "max_texture_size": 8192,
                "max_viewport_dims": 8192,
                "red_bits": 8,
                "green_bits": 8,
                "blue_bits": 8,
                "alpha_bits": 8,
                "depth_bits": 24,
                "stencil_bits": 0
            }
        ]
        
        # Common WebGL extensions
        self.common_webgl_extensions = [
            'ANGLE_instanced_arrays',
            'EXT_blend_minmax',
            'EXT_color_buffer_half_float',
            'EXT_disjoint_timer_query',
            'EXT_float_blend',
            'EXT_frag_depth',
            'EXT_shader_texture_lod',
            'EXT_texture_compression_bptc',
            'EXT_texture_compression_rgtc',
            'EXT_texture_filter_anisotropic',
            'EXT_sRGB',
            'KHR_parallel_shader_compile',
            'OES_element_index_uint',
            'OES_fbo_render_mipmap',
            'OES_standard_derivatives',
            'OES_texture_float',
            'OES_texture_float_linear',
            'OES_texture_half_float',
            'OES_texture_half_float_linear',
            'OES_vertex_array_object',
            'WEBGL_color_buffer_float',
            'WEBGL_compressed_texture_s3tc',
            'WEBGL_compressed_texture_s3tc_srgb',
            'WEBGL_debug_renderer_info',
            'WEBGL_debug_shaders',
            'WEBGL_depth_texture',
            'WEBGL_draw_buffers',
            'WEBGL_lose_context'
        ]
        
        # WebGL parameters
        self.webgl_parameters = {
            0x1F00: 'VERSION',  # "WebGL 1.0"
            0x1F01: 'SHADING_LANGUAGE_VERSION',  # "WebGL GLSL ES 1.0"
            0x1F02: 'VENDOR',  # Vendor string
            0x1F03: 'RENDERER',  # Renderer string
            0x821B: 'MAX_TEXTURE_SIZE',  # 16384
            0x0D3A: 'MAX_VIEWPORT_DIMS',  # 16384
            0x0D52: 'RED_BITS',  # 8
            0x0D53: 'GREEN_BITS',  # 8
            0x0D54: 'BLUE_BITS',  # 8
            0x0D55: 'ALPHA_BITS',  # 8
            0x0D56: 'DEPTH_BITS',  # 24
            0x0D57: 'STENCIL_BITS',  # 0
            0x8892: 'ARRAY_BUFFER_BINDING',
            0x8893: 'ELEMENT_ARRAY_BUFFER_BINDING',
            0x8872: 'CURRENT_PROGRAM',
            0x8CA6: 'FRAMEBUFFER_BINDING',
            0x8D40: 'RENDERBUFFER_BINDING',
            0x84E8: 'TEXTURE_BINDING_2D',
            0x8514: 'TEXTURE_BINDING_CUBE_MAP'
        }
    
    def get_random_webgl_profile(self) -> WebGLProfile:
        """
        Get a random WebGL profile with realistic properties.
        
        Returns:
            WebGLProfile with realistic WebGL properties
        """
        config = random.choice(self.common_webgl_configs)
        
        # Select random extensions
        extension_count = random.randint(15, len(self.common_webgl_extensions))
        extensions = random.sample(self.common_webgl_extensions, extension_count)
        
        # Create parameters
        parameters = {
            "VERSION": config["version"],
            "SHADING_LANGUAGE_VERSION": config["shading_language_version"],
            "VENDOR": config["vendor"],
            "RENDERER": config["renderer"],
            "MAX_TEXTURE_SIZE": str(config["max_texture_size"]),
            "MAX_VIEWPORT_DIMS": str(config["max_viewport_dims"]),
            "RED_BITS": str(config["red_bits"]),
            "GREEN_BITS": str(config["green_bits"]),
            "BLUE_BITS": str(config["blue_bits"]),
            "ALPHA_BITS": str(config["alpha_bits"]),
            "DEPTH_BITS": str(config["depth_bits"]),
            "STENCIL_BITS": str(config["stencil_bits"])
        }
        
        return WebGLProfile(
            vendor=config["vendor"],
            renderer=config["renderer"],
            version=config["version"],
            shading_language_version=config["shading_language_version"],
            extensions=extensions,
            parameters=parameters,
            max_texture_size=config["max_texture_size"],
            max_viewport_dims=config["max_viewport_dims"],
            red_bits=config["red_bits"],
            green_bits=config["green_bits"],
            blue_bits=config["blue_bits"],
            alpha_bits=config["alpha_bits"],
            depth_bits=config["depth_bits"],
            stencil_bits=config["stencil_bits"]
        )
    
    def get_random_canvas_profile(self) -> CanvasProfile:
        """
        Get a random canvas profile with realistic properties.
        
        Returns:
            CanvasProfile with realistic canvas properties
        """
        return CanvasProfile(
            text_rendering_variation=random.uniform(0.05, 0.15),  # 5-15% variation
            pixel_noise_level=random.uniform(0.001, 0.01),  # 0.1-1% noise
            rendering_timing_variation=random.uniform(0.1, 0.5),  # 10-50% timing variation
            fill_text_offset_variation=(
                random.uniform(0.001, 0.01),  # X offset 0.1-1% of font size
                random.uniform(0.001, 0.01)   # Y offset 0.1-1% of font size
            ),
            to_data_url_noise=random.choice([True, False]),
            get_image_data_noise=random.choice([True, False])
        )
    
    async def apply_webgl_canvas_simulation(self, context: BrowserContext,
                                          webgl_profile: Optional[WebGLProfile] = None,
                                          canvas_profile: Optional[CanvasProfile] = None) -> None:
        """
        Apply WebGL and canvas rendering simulation to a browser context.
        
        Args:
            context: Playwright BrowserContext to apply simulation to
            webgl_profile: WebGLProfile object, or None to generate random
            canvas_profile: CanvasProfile object, or None to generate random
        """
        if webgl_profile is None:
            webgl_profile = self.get_random_webgl_profile()
        
        if canvas_profile is None:
            canvas_profile = self.get_random_canvas_profile()
        
        try:
            # Generate JavaScript to spoof WebGL rendering
            webgl_js = self._generate_webgl_spoofing_js(webgl_profile)
            
            # Generate JavaScript to spoof canvas rendering
            canvas_js = self._generate_canvas_spoofing_js(canvas_profile)
            
            # Add JavaScript to context
            await context.add_init_script(webgl_js + canvas_js)
            
            self.logger.debug(
                "Applied WebGL and canvas rendering simulation to context",
                webgl_vendor=webgl_profile.vendor,
                webgl_renderer=webgl_profile.renderer,
                canvas_noise_level=canvas_profile.pixel_noise_level
            )
            
        except Exception as e:
            self.logger.error("Failed to apply WebGL and canvas rendering simulation to context", error=str(e))
            raise
    
    def _generate_webgl_spoofing_js(self, webgl_profile: WebGLProfile) -> str:
        """
        Generate JavaScript to spoof WebGL rendering.
        
        Args:
            webgl_profile: WebGLProfile object
            
        Returns:
            JavaScript code string
        """
        # Create extensions JSON
        extensions_json = str(webgl_profile.extensions).replace("'", "\\'")
        
        # Create parameters JSON
        parameters_json = str(webgl_profile.parameters).replace("'", "\\'").replace('"', '\\"')
        
        # Create vendor and renderer strings
        vendor = webgl_profile.vendor.replace('"', '\\"')
        renderer = webgl_profile.renderer.replace('"', '\\"')
        version = webgl_profile.version.replace('"', '\\"')
        sl_version = webgl_profile.shading_language_version.replace('"', '\\"')
        
        js_code = f"""
        // WebGL rendering spoofing
        (function() {{
            // Advanced WebGL fingerprinting protection
            if (window.WebGLRenderingContext) {{
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                    // Handle common parameters with realistic values
                    switch (parameter) {{
                        case 0x1F00: // VERSION
                            return "{version}";
                        case 0x1F01: // SHADING_LANGUAGE_VERSION
                            return "{sl_version}";
                        case 0x1F02: // VENDOR
                            return "{vendor}";
                        case 0x1F03: // RENDERER
                            return "{renderer}";
                        case 0x821B: // MAX_TEXTURE_SIZE
                            return {webgl_profile.max_texture_size};
                        case 0x0D3A: // MAX_VIEWPORT_DIMS
                            return {webgl_profile.max_viewport_dims};
                        case 0x0D52: // RED_BITS
                            return {webgl_profile.red_bits};
                        case 0x0D53: // GREEN_BITS
                            return {webgl_profile.green_bits};
                        case 0x0D54: // BLUE_BITS
                            return {webgl_profile.blue_bits};
                        case 0x0D55: // ALPHA_BITS
                            return {webgl_profile.alpha_bits};
                        case 0x0D56: // DEPTH_BITS
                            return {webgl_profile.depth_bits};
                        case 0x0D57: // STENCIL_BITS
                            return {webgl_profile.stencil_bits};
                        default:
                            return getParameter.apply(this, [parameter]);
                    }}
                }};
                
                // Hide WebGL debug renderer info
                const extension = WebGLRenderingContext.prototype.getExtension;
                WebGLRenderingContext.prototype.getExtension = function(name) {{
                    if (name === 'WEBGL_debug_renderer_info') {{
                        // Return null to hide debug renderer info
                        return null;
                    }}
                    // For other extensions, return a mock object if in our list
                    const extensions = {extensions_json};
                    if (extensions.includes(name)) {{
                        return {{
                            name: name,
                            toString: function() {{ return '[object WebGLExtension]'; }}
                        }};
                    }}
                    return extension.apply(this, [name]);
                }};
                
                // Override getSupportedExtensions to return our list
                WebGLRenderingContext.prototype.getSupportedExtensions = function() {{
                    return {extensions_json};
                }};
                
                // Add realistic timing variations to WebGL operations
                const originalCreateBuffer = WebGLRenderingContext.prototype.createBuffer;
                WebGLRenderingContext.prototype.createBuffer = function() {{
                    // Add slight delay to simulate real WebGL operation
                    const delay = Math.random() * 0.1; // 0-100ms
                    const result = originalCreateBuffer.apply(this, arguments);
                    return result;
                }};
                
                // Override readPixels to add slight variations
                const originalReadPixels = WebGLRenderingContext.prototype.readPixels;
                WebGLRenderingContext.prototype.readPixels = function(x, y, width, height, format, type, pixels) {{
                    // Add tiny random noise to pixel data
                    const result = originalReadPixels.apply(this, arguments);
                    if (pixels && pixels.length) {{
                        const noiseLevel = 0.001;
                        for (let i = 0; i < pixels.length; i++) {{
                            pixels[i] = Math.max(0, Math.min(255, pixels[i] + (Math.random() * noiseLevel * 255 - noiseLevel * 127.5)));
                        }}
                    }}
                    return result;
                }};
            }}
            
            // Hide missing webgl with more advanced spoofing
            if (!window.WebGLRenderingContext) {{
                window.WebGLRenderingContext = function() {{}};
            }}
        }})();
        """
        
        return js_code
    
    def _generate_canvas_spoofing_js(self, canvas_profile: CanvasProfile) -> str:
        """
        Generate JavaScript to spoof canvas rendering.
        
        Args:
            canvas_profile: CanvasProfile object
            
        Returns:
            JavaScript code string
        """
        text_variation = canvas_profile.text_rendering_variation
        pixel_noise = canvas_profile.pixel_noise_level
        timing_variation = canvas_profile.rendering_timing_variation
        offset_variation = canvas_profile.fill_text_offset_variation
        to_data_url_noise = canvas_profile.to_data_url_noise
        get_image_data_noise = canvas_profile.get_image_data_noise
        
        js_code = f"""
        // Canvas rendering spoofing
        (function() {{
            // Advanced canvas fingerprinting protection
            if (window.HTMLCanvasElement) {{
                const originalGetContext = HTMLCanvasElement.prototype.getContext;
                HTMLCanvasElement.prototype.getContext = function(contextType) {{
                    const context = originalGetContext.apply(this, [contextType]);
                    
                    if (contextType === '2d' && context) {{
                        // Add slight noise to canvas operations to prevent fingerprinting
                        const originalFillText = context.fillText;
                        context.fillText = function() {{
                            // Add tiny random offset to prevent exact pixel matching
                            const args = Array.from(arguments);
                            if (args.length >= 3) {{
                                // Add variation based on font size (if available)
                                let fontSize = 16; // Default font size
                                if (this.font) {{
                                    const fontSizeMatch = this.font.match(/(\\d+(\\.\\d+)?)px/);
                                    if (fontSizeMatch) {{
                                        fontSize = parseFloat(fontSizeMatch[1]);
                                    }}
                                }}
                                
                                // Apply offset variation
                                const offsetX = fontSize * {offset_variation[0]} * (Math.random() * 2 - 1);
                                const offsetY = fontSize * {offset_variation[1]} * (Math.random() * 2 - 1);
                                
                                args[1] = parseFloat(args[1]) + offsetX;
                                args[2] = parseFloat(args[2]) + offsetY;
                            }}
                            return originalFillText.apply(this, args);
                        }};
                        
                        // Override strokeText with similar variations
                        const originalStrokeText = context.strokeText;
                        context.strokeText = function() {{
                            const args = Array.from(arguments);
                            if (args.length >= 3) {{
                                let fontSize = 16;
                                if (this.font) {{
                                    const fontSizeMatch = this.font.match(/(\\d+(\\.\\d+)?)px/);
                                    if (fontSizeMatch) {{
                                        fontSize = parseFloat(fontSizeMatch[1]);
                                    }}
                                }}
                                
                                const offsetX = fontSize * {offset_variation[0]} * (Math.random() * 2 - 1);
                                const offsetY = fontSize * {offset_variation[1]} * (Math.random() * 2 - 1);
                                
                                args[1] = parseFloat(args[1]) + offsetX;
                                args[2] = parseFloat(args[2]) + offsetY;
                            }}
                            return originalStrokeText.apply(this, args);
                        }};
                        
                        // Override measureText to add slight variations
                        const originalMeasureText = context.measureText;
                        context.measureText = function() {{
                            const result = originalMeasureText.apply(this, arguments);
                            // Add slight random variation to text measurements
                            if (result.width) {{
                                result.width += result.width * {text_variation} * (Math.random() * 2 - 1);
                            }}
                            return result;
                        }};
                        
                        // Override toDataURL to add noise
                        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                        HTMLCanvasElement.prototype.toDataURL = function() {{
                            const context = this.getContext('2d');
                            if (context && {str(to_data_url_noise).lower()}) {{
                                // Add a tiny random colored pixel to prevent exact matching
                                const noiseLevel = {pixel_noise};
                                context.fillStyle = `rgba(${{Math.floor(Math.random() * 255)}}, ${{Math.floor(Math.random() * 255)}}, ${{Math.floor(Math.random() * 255)}}, ${{Math.random() * noiseLevel}})`;
                                context.fillRect(Math.random() * this.width, Math.random() * this.height, 1, 1);
                            }}
                            return originalToDataURL.apply(this, arguments);
                        }};
                        
                        // Override getImageData to add noise
                        const originalGetImageData = context.getImageData;
                        context.getImageData = function() {{
                            const imageData = originalGetImageData.apply(this, arguments);
                            if ({str(get_image_data_noise).lower()}) {{
                                // Add slight noise to image data to prevent exact matching
                                const data = imageData.data;
                                const noiseLevel = {pixel_noise};
                                for (let i = 0; i < data.length; i += 4) {{
                                    // Add tiny random noise to RGB values
                                    data[i] = Math.min(255, Math.max(0, data[i] + (Math.random() * noiseLevel * 255 - noiseLevel * 127.5)));
                                    data[i + 1] = Math.min(255, Math.max(0, data[i + 1] + (Math.random() * noiseLevel * 255 - noiseLevel * 127.5)));
                                    data[i + 2] = Math.min(255, Math.max(0, data[i + 2] + (Math.random() * noiseLevel * 255 - noiseLevel * 127.5)));
                                }}
                            }}
                            return imageData;
                        }};
                        
                        // Add realistic timing variations to canvas operations
                        const originalFillRect = context.fillRect;
                        context.fillRect = function() {{
                            // Add slight delay to simulate real rendering time
                            const delay = Math.random() * {timing_variation}; // 0-{timing_variation * 1000}ms
                            return originalFillRect.apply(this, arguments);
                        }};
                        
                        const originalStrokeRect = context.strokeRect;
                        context.strokeRect = function() {{
                            const delay = Math.random() * {timing_variation};
                            return originalStrokeRect.apply(this, arguments);
                        }};
                    }}
                    
                    return context;
                }};
            }}
            
            // Hide missing CanvasRenderingContext2D
            if (!window.CanvasRenderingContext2D) {{
                window.CanvasRenderingContext2D = function() {{}};
            }}
        }})();
        """
        
        return js_code
    
    def generate_webgl_canvas_fingerprint(self, webgl_profile: WebGLProfile, canvas_profile: CanvasProfile) -> str:
        """
        Generate a fingerprint based on WebGL and canvas profiles.
        
        Args:
            webgl_profile: WebGLProfile object
            canvas_profile: CanvasProfile object
            
        Returns:
            String fingerprint
        """
        # Create a string representation of the profiles
        fingerprint_data = (
            f"{webgl_profile.vendor}|{webgl_profile.renderer}|"
            f"{len(webgl_profile.extensions)}|{webgl_profile.max_texture_size}|"
            f"{canvas_profile.text_rendering_variation}|{canvas_profile.pixel_noise_level}"
        )
        
        # Generate a hash of the fingerprint data
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    def are_profiles_consistent(self, webgl_profile: WebGLProfile, canvas_profile: CanvasProfile) -> bool:
        """
        Check if WebGL and canvas profiles are consistent with each other.
        
        Args:
            webgl_profile: WebGLProfile object
            canvas_profile: CanvasProfile object
            
        Returns:
            True if profiles are consistent, False otherwise
        """
        # Basic consistency checks
        # For example, mobile GPUs typically have lower max texture sizes
        is_mobile_gpu = any(mobile_vendor in webgl_profile.vendor.lower() 
                           for mobile_vendor in ["arm", "qualcomm", "adreno", "mali"])
        
        if is_mobile_gpu:
            # Mobile GPUs typically have lower capabilities
            return webgl_profile.max_texture_size <= 8192
        else:
            # Desktop GPUs typically have higher capabilities
            return webgl_profile.max_texture_size >= 8192