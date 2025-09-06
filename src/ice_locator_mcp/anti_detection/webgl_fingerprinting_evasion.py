"""
Advanced WebGL Fingerprinting Evasion Manager for ICE Locator MCP Server.

This module provides advanced techniques to prevent WebGL-based browser fingerprinting.
It implements sophisticated WebGL vendor and renderer spoofing, debug renderer info protection,
and other advanced techniques to avoid detection based on WebGL fingerprints.
"""

import random
import structlog
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from playwright.async_api import BrowserContext
import hashlib


@dataclass
class AdvancedWebGLProfile:
    """Represents an advanced WebGL configuration with realistic properties for fingerprinting evasion."""
    vendor: str
    renderer: str
    unmasked_vendor: str
    unmasked_renderer: str
    version: str
    shading_language_version: str
    extensions: List[str]
    parameters: Dict[str, Any]
    max_texture_size: int
    max_viewport_dims: Tuple[int, int]
    red_bits: int
    green_bits: int
    blue_bits: int
    alpha_bits: int
    depth_bits: int
    stencil_bits: int
    antialiasing: str
    preferred_webgl_version: int  # 1 or 2
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "vendor": self.vendor,
            "renderer": self.renderer,
            "unmasked_vendor": self.unmasked_vendor,
            "unmasked_renderer": self.unmasked_renderer,
            "version": self.version,
            "shading_language_version": self.shading_language_version,
            "extensions": self.extensions,
            "parameters": self.parameters,
            "max_texture_size": self.max_texture_size,
            "max_viewport_dims": list(self.max_viewport_dims),
            "red_bits": self.red_bits,
            "green_bits": self.green_bits,
            "blue_bits": self.blue_bits,
            "alpha_bits": self.alpha_bits,
            "depth_bits": self.depth_bits,
            "stencil_bits": self.stencil_bits,
            "antialiasing": self.antialiasing,
            "preferred_webgl_version": self.preferred_webgl_version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AdvancedWebGLProfile':
        """Create from dictionary."""
        data["max_viewport_dims"] = tuple(data["max_viewport_dims"])
        return cls(**data)


class WebGLFingerprintingEvasionManager:
    """Manages advanced WebGL fingerprinting evasion techniques."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        
        # Realistic WebGL vendor/renderer combinations
        self.webgl_vendor_renderer_pairs = [
            ("Intel Inc.", "Intel Iris OpenGL Engine"),
            ("Intel Inc.", "Intel HD Graphics 630"),
            ("NVIDIA Corporation", "NVIDIA GeForce GTX 1080 OpenGL Engine"),
            ("NVIDIA Corporation", "NVIDIA GeForce RTX 3080"),
            ("ATI Technologies Inc.", "AMD Radeon Pro 560 OpenGL Engine"),
            ("ATI Technologies Inc.", "AMD Radeon RX 6800 XT"),
            ("ARM", "Mali-G78"),
            ("Qualcomm", "Adreno (TM) 660"),
            ("Google Inc. (Apple)", "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)"),
            ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce GTX 1080 Direct3D11 vs_5_0 ps_5_0)"),
            ("Google Inc. (AMD)", "ANGLE (AMD, AMD Radeon(TM) Graphics Direct3D11 vs_5_0 ps_5_0)"),
            ("Apple", "Apple GPU"),
            ("Apple Inc.", "Apple M1"),
            ("Microsoft", "Direct3D11"),
        ]
        
        # WebGL 1 extensions
        self.webgl1_extensions = [
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
        
        # WebGL 2 extensions
        self.webgl2_extensions = [
            'EXT_color_buffer_float',
            'EXT_disjoint_timer_query_webgl2',
            'EXT_float_blend',
            'EXT_texture_compression_bptc',
            'EXT_texture_compression_rgtc',
            'EXT_texture_filter_anisotropic',
            'EXT_texture_norm16',
            'KHR_parallel_shader_compile',
            'OES_texture_float_linear',
            'WEBGL_compressed_texture_s3tc',
            'WEBGL_compressed_texture_s3tc_srgb',
            'WEBGL_debug_renderer_info',
            'WEBGL_debug_shaders',
            'WEBGL_lose_context',
            'WEBGL_multi_draw'
        ]
        
        # WebGL parameters with realistic values
        self.webgl_parameters = {
            0x1F00: 'VERSION',
            0x1F01: 'SHADING_LANGUAGE_VERSION',
            0x1F02: 'VENDOR',
            0x1F03: 'RENDERER',
            0x821B: 'MAX_TEXTURE_SIZE',
            0x0D3A: 'MAX_VIEWPORT_DIMS',
            0x0D52: 'RED_BITS',
            0x0D53: 'GREEN_BITS',
            0x0D54: 'BLUE_BITS',
            0x0D55: 'ALPHA_BITS',
            0x0D56: 'DEPTH_BITS',
            0x0D57: 'STENCIL_BITS',
            0x8892: 'ARRAY_BUFFER_BINDING',
            0x8893: 'ELEMENT_ARRAY_BUFFER_BINDING',
            0x8872: 'CURRENT_PROGRAM',
            0x8CA6: 'FRAMEBUFFER_BINDING',
            0x8D40: 'RENDERBUFFER_BINDING',
            0x84E8: 'TEXTURE_BINDING_2D',
            0x8514: 'TEXTURE_BINDING_CUBE_MAP',
            0x846D: 'MAX_VERTEX_ATTRIBS',
            0x8869: 'MAX_VERTEX_UNIFORM_VECTORS',
            0x8DFB: 'MAX_VARYING_VECTORS',
            0x8B4D: 'MAX_COMBINED_TEXTURE_IMAGE_UNITS',
            0x8871: 'MAX_VERTEX_TEXTURE_IMAGE_UNITS',
            0x8B4C: 'MAX_TEXTURE_IMAGE_UNITS',
            0x886A: 'MAX_FRAGMENT_UNIFORM_VECTORS',
            0x86A2: 'MAX_RENDERBUFFER_SIZE',
            0x821D: 'MAX_CUBE_MAP_TEXTURE_SIZE',
            0x851C: 'MAX_ARRAY_TEXTURE_LAYERS',
            0x8C8D: 'MAX_UNIFORM_BUFFER_BINDINGS',
            0x8A30: 'MAX_UNIFORM_BLOCK_SIZE'
        }
    
    def get_random_webgl_profile(self, webgl_version: Optional[int] = None) -> AdvancedWebGLProfile:
        """
        Get a random advanced WebGL profile with realistic properties.
        
        Args:
            webgl_version: WebGL version (1 or 2), or None for random
            
        Returns:
            AdvancedWebGLProfile with realistic WebGL properties
        """
        if webgl_version is None:
            webgl_version = random.choice([1, 2])
        
        # Select a realistic vendor/renderer pair
        vendor, renderer = random.choice(self.webgl_vendor_renderer_pairs)
        
        # For unmasked values, we might want to show different values to simulate
        # the difference between masked and unmasked values
        unmasked_vendor = vendor
        unmasked_renderer = renderer
        
        # In some cases, we might want to simulate the difference between
        # masked and unmasked values
        if random.random() < 0.3:  # 30% chance of having different unmasked values
            # Select a different vendor/renderer for unmasked values
            unmasked_vendor, unmasked_renderer = random.choice(self.webgl_vendor_renderer_pairs)
        
        # Select extensions based on WebGL version
        if webgl_version == 2:
            extensions = random.sample(
                self.webgl2_extensions, 
                random.randint(10, min(15, len(self.webgl2_extensions)))
            )
            version = "WebGL 2.0"
            shading_language_version = "WebGL GLSL ES 3.00"
        else:
            extensions = random.sample(
                self.webgl1_extensions, 
                random.randint(15, min(25, len(self.webgl1_extensions)))
            )
            version = "WebGL 1.0"
            shading_language_version = "WebGL GLSL ES 1.0"
        
        # Determine realistic hardware capabilities
        is_mobile = any(mobile_vendor in vendor.lower() for mobile_vendor in ["arm", "qualcomm", "adreno", "mali"])
        is_apple = any(apple_vendor in vendor.lower() for apple_vendor in ["apple"])
        
        if is_mobile:
            max_texture_size = random.choice([4096, 8192, 8192, 16384])  # Mobile GPUs typically max at 8192 or 16384
            max_viewport_dims = (random.choice([4096, 8192]), random.choice([4096, 8192]))
        elif is_apple:
            max_texture_size = random.choice([8192, 16384, 16384, 32768])  # Apple GPUs often have higher limits
            max_viewport_dims = (random.choice([8192, 16384]), random.choice([8192, 16384]))
        else:
            max_texture_size = random.choice([8192, 16384, 16384, 32768])  # Desktop GPUs typically max at 16384 or 32768
            max_viewport_dims = (random.choice([8192, 16384, 32768]), random.choice([8192, 16384, 32768]))
        
        # Color depth bits
        red_bits = green_bits = blue_bits = alpha_bits = random.choice([8, 8, 8, 10])  # Usually 8, sometimes 10
        depth_bits = random.choice([16, 24, 24, 32])  # Usually 24, sometimes 16 or 32
        stencil_bits = random.choice([0, 0, 0, 8])  # Usually 0, sometimes 8
        
        # Antialiasing support
        antialiasing = random.choice(["available", "available", "available", "not supported"])
        
        # Create parameters
        parameters = {
            "VERSION": version,
            "SHADING_LANGUAGE_VERSION": shading_language_version,
            "VENDOR": vendor,
            "RENDERER": renderer,
            "UNMASKED_VENDOR_WEBGL": unmasked_vendor,
            "UNMASKED_RENDERER_WEBGL": unmasked_renderer,
            "MAX_TEXTURE_SIZE": str(max_texture_size),
            "MAX_VIEWPORT_DIMS": f"{max_viewport_dims[0]}, {max_viewport_dims[1]}",
            "RED_BITS": str(red_bits),
            "GREEN_BITS": str(green_bits),
            "BLUE_BITS": str(blue_bits),
            "ALPHA_BITS": str(alpha_bits),
            "DEPTH_BITS": str(depth_bits),
            "STENCIL_BITS": str(stencil_bits),
            "MAX_VERTEX_ATTRIBS": str(random.choice([16, 16, 16, 32])),
            "MAX_VERTEX_UNIFORM_VECTORS": str(random.choice([256, 256, 256, 512])),
            "MAX_VARYING_VECTORS": str(random.choice([15, 15, 15, 30])),
            "MAX_COMBINED_TEXTURE_IMAGE_UNITS": str(random.choice([32, 32, 32, 64])),
            "MAX_VERTEX_TEXTURE_IMAGE_UNITS": str(random.choice([16, 16, 16, 32])),
            "MAX_TEXTURE_IMAGE_UNITS": str(random.choice([16, 16, 16, 32])),
            "MAX_FRAGMENT_UNIFORM_VECTORS": str(random.choice([256, 256, 256, 512])),
            "MAX_RENDERBUFFER_SIZE": str(max_texture_size),
            "MAX_CUBE_MAP_TEXTURE_SIZE": str(max_texture_size // 2),
            "MAX_ARRAY_TEXTURE_LAYERS": str(random.choice([256, 512, 1024, 2048])),
            "MAX_UNIFORM_BUFFER_BINDINGS": str(random.choice([36, 36, 36, 72])),
            "MAX_UNIFORM_BLOCK_SIZE": str(random.choice([16384, 16384, 16384, 32768]))
        }
        
        return AdvancedWebGLProfile(
            vendor=vendor,
            renderer=renderer,
            unmasked_vendor=unmasked_vendor,
            unmasked_renderer=unmasked_renderer,
            version=version,
            shading_language_version=shading_language_version,
            extensions=extensions,
            parameters=parameters,
            max_texture_size=max_texture_size,
            max_viewport_dims=max_viewport_dims,
            red_bits=red_bits,
            green_bits=green_bits,
            blue_bits=blue_bits,
            alpha_bits=alpha_bits,
            depth_bits=depth_bits,
            stencil_bits=stencil_bits,
            antialiasing=antialiasing,
            preferred_webgl_version=webgl_version
        )
    
    async def apply_webgl_fingerprinting_evasion(self, context: BrowserContext,
                                                 webgl_profile: Optional[AdvancedWebGLProfile] = None) -> None:
        """
        Apply advanced WebGL fingerprinting evasion to a browser context.
        
        Args:
            context: Playwright BrowserContext to apply evasion to
            webgl_profile: AdvancedWebGLProfile object, or None to generate random
        """
        if webgl_profile is None:
            webgl_profile = self.get_random_webgl_profile()
        
        try:
            # Generate JavaScript to spoof WebGL rendering
            webgl_js = self._generate_webgl_evasion_js(webgl_profile)
            
            # Add JavaScript to context
            await context.add_init_script(webgl_js)
            
            self.logger.debug(
                "Applied advanced WebGL fingerprinting evasion to context",
                webgl_vendor=webgl_profile.vendor,
                webgl_renderer=webgl_profile.renderer,
                webgl_version=webgl_profile.version,
                extensions_count=len(webgl_profile.extensions)
            )
            
        except Exception as e:
            self.logger.error("Failed to apply advanced WebGL fingerprinting evasion to context", error=str(e))
            raise
    
    def _generate_webgl_evasion_js(self, webgl_profile: AdvancedWebGLProfile) -> str:
        """
        Generate JavaScript to implement advanced WebGL fingerprinting evasion.
        
        Args:
            webgl_profile: AdvancedWebGLProfile object
            
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
        unmasked_vendor = webgl_profile.unmasked_vendor.replace('"', '\\"')
        unmasked_renderer = webgl_profile.unmasked_renderer.replace('"', '\\"')
        version = webgl_profile.version.replace('"', '\\"')
        sl_version = webgl_profile.shading_language_version.replace('"', '\\"')
        
        js_code = f"""
        // Advanced WebGL fingerprinting evasion
        (function() {{
            // Enhanced WebGL fingerprinting protection
            if (window.WebGLRenderingContext || window.WebGL2RenderingContext) {{
                // Override getParameter for both WebGL 1 and 2
                const overrideGetParameter = function(glContext) {{
                    const originalGetParameter = glContext.prototype.getParameter;
                    glContext.prototype.getParameter = function(parameter) {{
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
                                return new Int32Array([{webgl_profile.max_viewport_dims[0]}, {webgl_profile.max_viewport_dims[1]}]);
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
                            case 0x9245: // UNMASKED_VENDOR_WEBGL (extension)
                                return "{unmasked_vendor}";
                            case 0x9246: // UNMASKED_RENDERER_WEBGL (extension)
                                return "{unmasked_renderer}";
                            default:
                                return originalGetParameter.apply(this, [parameter]);
                        }}
                    }};
                }};
                
                // Apply to WebGL 1 if available
                if (window.WebGLRenderingContext) {{
                    overrideGetParameter(WebGLRenderingContext);
                }}
                
                // Apply to WebGL 2 if available
                if (window.WebGL2RenderingContext) {{
                    overrideGetParameter(WebGL2RenderingContext);
                }}
                
                // Hide WebGL debug renderer info extension
                const overrideGetExtension = function(glContext) {{
                    const originalGetExtension = glContext.prototype.getExtension;
                    glContext.prototype.getExtension = function(name) {{
                        if (name === 'WEBGL_debug_renderer_info') {{
                            // Return a mock object that provides our controlled values
                            return {{
                                UNMASKED_VENDOR_WEBGL: 0x9245,
                                UNMASKED_RENDERER_WEBGL: 0x9246,
                                toString: function() {{ return '[object WebGLDebugRendererInfo]'; }}
                            }};
                        }}
                        // For other extensions, return a mock object if in our list
                        const extensions = {extensions_json};
                        if (extensions.includes(name)) {{
                            return {{
                                name: name,
                                toString: function() {{ return '[object WebGLExtension]'; }}
                            }};
                        }}
                        return originalGetExtension.apply(this, [name]);
                    }};
                }};
                
                // Apply to WebGL 1 if available
                if (window.WebGLRenderingContext) {{
                    overrideGetExtension(WebGLRenderingContext);
                }}
                
                // Apply to WebGL 2 if available
                if (window.WebGL2RenderingContext) {{
                    overrideGetExtension(WebGL2RenderingContext);
                }}
                
                // Override getSupportedExtensions to return our list
                const overrideGetSupportedExtensions = function(glContext) {{
                    const originalGetSupportedExtensions = glContext.prototype.getSupportedExtensions;
                    glContext.prototype.getSupportedExtensions = function() {{
                        return {extensions_json};
                    }};
                }};
                
                // Apply to WebGL 1 if available
                if (window.WebGLRenderingContext) {{
                    overrideGetSupportedExtensions(WebGLRenderingContext);
                }}
                
                // Apply to WebGL 2 if available
                if (window.WebGL2RenderingContext) {{
                    overrideGetSupportedExtensions(WebGL2RenderingContext);
                }}
                
                // Add realistic timing variations to WebGL operations
                const overrideCreateBuffer = function(glContext) {{
                    const originalCreateBuffer = glContext.prototype.createBuffer;
                    glContext.prototype.createBuffer = function() {{
                        // Add slight delay to simulate real WebGL operation
                        const delay = Math.random() * 0.1; // 0-100ms
                        const result = originalCreateBuffer.apply(this, arguments);
                        return result;
                    }};
                }};
                
                // Apply to WebGL 1 if available
                if (window.WebGLRenderingContext) {{
                    overrideCreateBuffer(WebGLRenderingContext);
                }}
                
                // Apply to WebGL 2 if available
                if (window.WebGL2RenderingContext) {{
                    overrideCreateBuffer(WebGL2RenderingContext);
                }}
                
                // Override readPixels to add slight variations
                const overrideReadPixels = function(glContext) {{
                    const originalReadPixels = glContext.prototype.readPixels;
                    glContext.prototype.readPixels = function(x, y, width, height, format, type, pixels) {{
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
                }};
                
                // Apply to WebGL 1 if available
                if (window.WebGLRenderingContext) {{
                    overrideReadPixels(WebGLRenderingContext);
                }}
                
                // Apply to WebGL 2 if available
                if (window.WebGL2RenderingContext) {{
                    overrideReadPixels(WebGL2RenderingContext);
                }}
                
                // Override getShaderPrecisionFormat to add variations
                const overrideGetShaderPrecisionFormat = function(glContext) {{
                    const originalGetShaderPrecisionFormat = glContext.prototype.getShaderPrecisionFormat;
                    glContext.prototype.getShaderPrecisionFormat = function(shaderType, precisionType) {{
                        const result = originalGetShaderPrecisionFormat.apply(this, arguments);
                        // Add slight variations to precision format
                        if (result) {{
                            // Create a new object to avoid modifying the original
                            return {{
                                rangeMin: result.rangeMin,
                                rangeMax: result.rangeMax,
                                precision: result.precision + Math.floor(Math.random() * 3) - 1 // Small variation
                            }};
                        }}
                        return result;
                    }};
                }};
                
                // Apply to WebGL 1 if available
                if (window.WebGLRenderingContext) {{
                    overrideGetShaderPrecisionFormat(WebGLRenderingContext);
                }}
                
                // Apply to WebGL 2 if available
                if (window.WebGL2RenderingContext) {{
                    overrideGetShaderPrecisionFormat(WebGL2RenderingContext);
                }}
            }}
            
            // Hide missing WebGL contexts
            if (!window.WebGLRenderingContext) {{
                window.WebGLRenderingContext = function() {{}};
            }}
            
            if (!window.WebGL2RenderingContext) {{
                window.WebGL2RenderingContext = function() {{}};
            }}
            
            // Override WebGL context creation to ensure consistent behavior
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(contextType, contextAttributes) {{
                const context = originalGetContext.apply(this, [contextType, contextAttributes]);
                
                // If requesting WebGL context, ensure our evasion is applied
                if (context && (contextType === 'webgl' || contextType === 'experimental-webgl')) {{
                    // Apply any additional context-specific overrides here
                }} else if (context && contextType === 'webgl2') {{
                    // Apply any WebGL 2 specific overrides here
                }}
                
                return context;
            }};
        }})();
        """
        
        return js_code
    
    def generate_webgl_fingerprint(self, webgl_profile: AdvancedWebGLProfile) -> str:
        """
        Generate a WebGL fingerprint based on the profile.
        
        Args:
            webgl_profile: AdvancedWebGLProfile object
            
        Returns:
            String fingerprint hash
        """
        # Create a string representation of the profile
        fingerprint_data = (
            f"{webgl_profile.vendor}|{webgl_profile.renderer}|"
            f"{webgl_profile.unmasked_vendor}|{webgl_profile.unmasked_renderer}|"
            f"{webgl_profile.version}|{len(webgl_profile.extensions)}|"
            f"{webgl_profile.max_texture_size}|{webgl_profile.red_bits}|"
            f"{webgl_profile.green_bits}|{webgl_profile.blue_bits}|"
            f"{webgl_profile.alpha_bits}|{webgl_profile.depth_bits}|"
            f"{webgl_profile.stencil_bits}|{webgl_profile.preferred_webgl_version}"
        )
        
        # Generate a hash of the fingerprint data
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    def is_webgl_profile_consistent(self, webgl_profile: AdvancedWebGLProfile) -> bool:
        """
        Check if a WebGL profile is consistent and realistic.
        
        Args:
            webgl_profile: AdvancedWebGLProfile object
            
        Returns:
            True if profile is consistent, False otherwise
        """
        # Check that vendor and renderer are not empty
        if not webgl_profile.vendor or not webgl_profile.renderer:
            return False
        
        # Check that extensions list is not empty
        if not webgl_profile.extensions:
            return False
        
        # Check that max texture size is reasonable
        if webgl_profile.max_texture_size < 2048 or webgl_profile.max_texture_size > 65536:
            return False
        
        # Check that color bits are reasonable
        if (webgl_profile.red_bits < 4 or webgl_profile.red_bits > 16 or
            webgl_profile.green_bits < 4 or webgl_profile.green_bits > 16 or
            webgl_profile.blue_bits < 4 or webgl_profile.blue_bits > 16 or
            webgl_profile.alpha_bits < 0 or webgl_profile.alpha_bits > 16):
            return False
        
        # Check that depth and stencil bits are reasonable
        if webgl_profile.depth_bits not in [0, 16, 24, 32]:
            return False
        
        if webgl_profile.stencil_bits not in [0, 1, 4, 8]:
            return False
        
        # Check that WebGL version is valid
        if webgl_profile.preferred_webgl_version not in [1, 2]:
            return False
        
        # Check consistency between vendor and max texture size
        is_mobile = any(mobile_vendor in webgl_profile.vendor.lower() 
                       for mobile_vendor in ["arm", "qualcomm", "adreno", "mali"])
        
        if is_mobile and webgl_profile.max_texture_size > 16384:
            return False  # Mobile GPUs typically don't have such high limits
        
        return True