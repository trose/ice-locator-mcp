"""
Font and Media Simulation Manager for ICE Locator MCP Server.

This module provides advanced font and media simulation capabilities to avoid 
fingerprinting based on system resources. It implements font enumeration protection 
and media capability spoofing.
"""

import random
import structlog
from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Any
from playwright.async_api import BrowserContext


@dataclass
class FontProfile:
    """Represents a font configuration with realistic properties."""
    name: str
    generic_family: str
    is_monospace: bool
    is_serif: bool
    is_sans_serif: bool
    is_display: bool
    is_handwriting: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "generic_family": self.generic_family,
            "is_monospace": self.is_monospace,
            "is_serif": self.is_serif,
            "is_sans_serif": self.is_sans_serif,
            "is_display": self.is_display,
            "is_handwriting": self.is_handwriting
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FontProfile':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class MediaProfile:
    """Represents a media configuration with realistic properties."""
    audio_codecs: List[str]
    video_codecs: List[str]
    media_devices: List[Dict[str, str]]
    webgl_extensions: List[str]
    webgl_parameters: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "audio_codecs": self.audio_codecs,
            "video_codecs": self.video_codecs,
            "media_devices": self.media_devices,
            "webgl_extensions": self.webgl_extensions,
            "webgl_parameters": self.webgl_parameters
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MediaProfile':
        """Create from dictionary."""
        return cls(**data)


class FontMediaManager:
    """Manages advanced font and media simulation to avoid fingerprinting based on system resources."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        
        # Common fonts found on different platforms
        self.common_fonts = [
            FontProfile("Arial", "sans-serif", False, False, True, False, False),
            FontProfile("Helvetica", "sans-serif", False, False, True, False, False),
            FontProfile("Times New Roman", "serif", False, True, False, False, False),
            FontProfile("Times", "serif", False, True, False, False, False),
            FontProfile("Courier New", "monospace", True, False, False, False, False),
            FontProfile("Courier", "monospace", True, False, False, False, False),
            FontProfile("Verdana", "sans-serif", False, False, True, False, False),
            FontProfile("Georgia", "serif", False, True, False, False, False),
            FontProfile("Palatino", "serif", False, True, False, False, False),
            FontProfile("Garamond", "serif", False, True, False, False, False),
            FontProfile("Comic Sans MS", "sans-serif", False, False, True, False, False),
            FontProfile("Trebuchet MS", "sans-serif", False, False, True, False, False),
            FontProfile("Arial Black", "sans-serif", False, False, True, True, False),
            FontProfile("Impact", "sans-serif", False, False, True, True, False),
            FontProfile("Lucida Console", "monospace", True, False, False, False, False),
            FontProfile("Lucida Sans Unicode", "sans-serif", False, False, True, False, False),
            FontProfile("Tahoma", "sans-serif", False, False, True, False, False),
            FontProfile("Segoe UI", "sans-serif", False, False, True, False, False),
            FontProfile("Geneva", "sans-serif", False, False, True, False, False),
            FontProfile("Calibri", "sans-serif", False, False, True, False, False),
            FontProfile("Candara", "sans-serif", False, False, True, False, False),
            FontProfile("Optima", "sans-serif", False, False, True, False, False),
            FontProfile("Futura", "sans-serif", False, False, True, True, False),
            FontProfile("Gill Sans", "sans-serif", False, False, True, False, False),
            FontProfile("Franklin Gothic", "sans-serif", False, False, True, False, False),
            FontProfile("Myriad Pro", "sans-serif", False, False, True, False, False),
            FontProfile("Lucida Grande", "sans-serif", False, False, True, False, False),
            FontProfile("Century Gothic", "sans-serif", False, False, True, False, False),
            FontProfile("Apple Gothic", "sans-serif", False, False, True, False, False),
            FontProfile("Apple SD Gothic Neo", "sans-serif", False, False, True, False, False),
            FontProfile("Nanum Gothic", "sans-serif", False, False, True, False, False),
            FontProfile("Malgun Gothic", "sans-serif", False, False, True, False, False),
            FontProfile("SimSun", "serif", False, True, False, False, False),
            FontProfile("SimHei", "sans-serif", False, False, True, False, False),
            FontProfile("Microsoft YaHei", "sans-serif", False, False, True, False, False),
            FontProfile("PMingLiU", "serif", False, True, False, False, False),
            FontProfile("MingLiU", "serif", False, True, False, False, False),
            FontProfile("MS PGothic", "sans-serif", False, False, True, False, False),
            FontProfile("MS Gothic", "monospace", True, False, False, False, False),
            FontProfile("Meiryo", "sans-serif", False, False, True, False, False),
            FontProfile("Yu Gothic", "sans-serif", False, False, True, False, False),
            FontProfile("Osaka", "sans-serif", False, False, True, False, False),
            FontProfile("Hiragino Kaku Gothic Pro", "sans-serif", False, False, True, False, False),
            FontProfile("Hiragino Mincho Pro", "serif", False, True, False, False, False),
        ]
        
        # Common audio codecs
        self.common_audio_codecs = [
            'audio/mp3',
            'audio/mp4',
            'audio/aac',
            'audio/ogg',
            'audio/wav',
            'audio/webm',
            'audio/flac',
            'audio/x-m4a',
            'audio/x-aac',
            'audio/x-wav'
        ]
        
        # Common video codecs
        self.common_video_codecs = [
            'video/mp4',
            'video/webm',
            'video/ogg',
            'video/quicktime',
            'video/x-msvideo',
            'video/x-flv',
            'video/3gpp',
            'video/3gpp2',
            'video/h264',
            'video/x-m4v'
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
        
        # Common WebGL parameters
        self.common_webgl_parameters = {
            'VERSION': 'WebGL 1.0',
            'SHADING_LANGUAGE_VERSION': 'WebGL GLSL ES 1.0',
            'VENDOR': 'WebKit',
            'RENDERER': 'WebKit WebGL',
            'MAX_VERTEX_ATTRIBS': '16',
            'MAX_VERTEX_UNIFORM_VECTORS': '128',
            'MAX_VARYING_VECTORS': '8',
            'MAX_COMBINED_TEXTURE_IMAGE_UNITS': '32',
            'MAX_CUBE_MAP_TEXTURE_SIZE': '16384',
            'MAX_FRAGMENT_UNIFORM_VECTORS': '64',
            'MAX_RENDERBUFFER_SIZE': '16384',
            'MAX_TEXTURE_IMAGE_UNITS': '16',
            'MAX_TEXTURE_SIZE': '16384',
            'MAX_VIEWPORT_DIMS': '16384',
            'RED_BITS': '8',
            'GREEN_BITS': '8',
            'BLUE_BITS': '8',
            'ALPHA_BITS': '8',
            'DEPTH_BITS': '24',
            'STENCIL_BITS': '0'
        }
    
    def get_random_font_list(self, count: int = 20) -> List[FontProfile]:
        """
        Get a random list of fonts to simulate realistic font enumeration.
        
        Args:
            count: Number of fonts to include in the list
            
        Returns:
            List of FontProfile objects
        """
        # Ensure we don't exceed available fonts
        actual_count = min(count, len(self.common_fonts))
        return random.sample(self.common_fonts, actual_count)
    
    def get_random_media_profile(self) -> MediaProfile:
        """
        Get a random media profile with realistic properties.
        
        Returns:
            MediaProfile with realistic media capabilities
        """
        # Randomly select codecs
        audio_codecs = random.sample(self.common_audio_codecs, random.randint(3, 6))
        video_codecs = random.sample(self.common_video_codecs, random.randint(3, 6))
        
        # Generate realistic media devices
        media_devices = self._generate_realistic_media_devices()
        
        # Randomly select WebGL extensions
        webgl_extensions = random.sample(self.common_webgl_extensions, random.randint(10, 20))
        
        # Use common WebGL parameters
        webgl_parameters = self.common_webgl_parameters.copy()
        
        return MediaProfile(
            audio_codecs=audio_codecs,
            video_codecs=video_codecs,
            media_devices=media_devices,
            webgl_extensions=webgl_extensions,
            webgl_parameters=webgl_parameters
        )
    
    def _generate_realistic_media_devices(self) -> List[Dict[str, str]]:
        """
        Generate realistic media device configurations.
        
        Returns:
            List of media device dictionaries
        """
        devices = []
        
        # Add audio input devices
        audio_inputs = [
            {"deviceId": self._generate_device_id(), "kind": "audioinput", "label": "Default - Microphone", "groupId": self._generate_group_id()},
            {"deviceId": self._generate_device_id(), "kind": "audioinput", "label": "Built-in Microphone", "groupId": self._generate_group_id()}
        ]
        devices.extend(audio_inputs)
        
        # Add audio output devices
        audio_outputs = [
            {"deviceId": self._generate_device_id(), "kind": "audiooutput", "label": "Default - Speakers", "groupId": self._generate_group_id()},
            {"deviceId": self._generate_device_id(), "kind": "audiooutput", "label": "Built-in Speakers", "groupId": self._generate_group_id()}
        ]
        devices.extend(audio_outputs)
        
        # Add video input devices
        video_inputs = [
            {"deviceId": self._generate_device_id(), "kind": "videoinput", "label": "FaceTime HD Camera", "groupId": self._generate_group_id()},
            {"deviceId": self._generate_device_id(), "kind": "videoinput", "label": "USB Camera", "groupId": self._generate_group_id()}
        ]
        devices.extend(video_inputs)
        
        return devices
    
    def _generate_device_id(self) -> str:
        """Generate a realistic device ID."""
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(random.choice(chars) for _ in range(32))
    
    def _generate_group_id(self) -> str:
        """Generate a realistic group ID."""
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(random.choice(chars) for _ in range(16))
    
    async def apply_font_media_simulation(self, context: BrowserContext, 
                                        font_profile: Optional[List[FontProfile]] = None,
                                        media_profile: Optional[MediaProfile] = None) -> None:
        """
        Apply font and media simulation to a browser context.
        
        Args:
            context: Playwright BrowserContext to apply simulation to
            font_profile: List of FontProfile objects, or None to generate random
            media_profile: MediaProfile object, or None to generate random
        """
        if font_profile is None:
            font_profile = self.get_random_font_list()
        
        if media_profile is None:
            media_profile = self.get_random_media_profile()
        
        try:
            # Generate JavaScript to spoof font enumeration
            font_js = self._generate_font_spoofing_js(font_profile)
            
            # Generate JavaScript to spoof media capabilities
            media_js = self._generate_media_spoofing_js(media_profile)
            
            # Add JavaScript to context
            await context.add_init_script(font_js + media_js)
            
            self.logger.debug(
                "Applied font and media simulation to context",
                font_count=len(font_profile),
                audio_codecs=len(media_profile.audio_codecs),
                video_codecs=len(media_profile.video_codecs)
            )
            
        except Exception as e:
            self.logger.error("Failed to apply font and media simulation to context", error=str(e))
            raise
    
    def _generate_font_spoofing_js(self, font_profile: List[FontProfile]) -> str:
        """
        Generate JavaScript to spoof font enumeration.
        
        Args:
            font_profile: List of FontProfile objects
            
        Returns:
            JavaScript code string
        """
        # Create font list as JSON
        font_names = [font.name for font in font_profile]
        font_json = str(font_names).replace("'", "\\'")
        
        js_code = f"""
        // Font enumeration spoofing
        (function() {{
            // Override document.fonts.ready
            if (document.fonts && document.fonts.ready) {{
                Object.defineProperty(document.fonts, 'ready', {{
                    get: () => Promise.resolve(document.fonts)
                }});
            }}
            
            // Override CSS.supports for font features
            const originalCSSSupports = CSS.supports;
            CSS.supports = function() {{
                // Return random results for font-related queries
                if (arguments.length === 2 && typeof arguments[0] === 'string' && arguments[0].includes('font')) {{
                    return Math.random() > 0.3;
                }}
                return originalCSSSupports.apply(this, arguments);
            }};
            
            // Override CanvasRenderingContext2D.measureText with realistic font variations
            if (window.CanvasRenderingContext2D && CanvasRenderingContext2D.prototype.measureText) {{
                const originalMeasureText = CanvasRenderingContext2D.prototype.measureText;
                CanvasRenderingContext2D.prototype.measureText = function(text) {{
                    const result = originalMeasureText.apply(this, arguments);
                    // Add slight random variation to text measurements based on font
                    if (result.width && this.font) {{
                        // Extract font size from font string
                        const fontSizeMatch = this.font.match(/(\\d+(\\.\\d+)?)px/);
                        if (fontSizeMatch) {{
                            const fontSize = parseFloat(fontSizeMatch[1]);
                            // Add variation based on font size (larger fonts have more variation)
                            const variation = (Math.random() * 0.2 - 0.1) * (fontSize / 16);
                            result.width += variation;
                        }}
                    }}
                    return result;
                }};
            }}
            
            // Override offsetWidth/offsetHeight to add slight variations
            const originalOffsetWidth = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'offsetWidth');
            if (originalOffsetWidth && originalOffsetWidth.get) {{
                Object.defineProperty(HTMLElement.prototype, 'offsetWidth', {{
                    get: function() {{
                        const original = originalOffsetWidth.get.call(this);
                        // Add tiny random variation
                        return original + (Math.random() * 2 - 1);
                    }}
                }});
            }}
            
            const originalOffsetHeight = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'offsetHeight');
            if (originalOffsetHeight && originalOffsetHeight.get) {{
                Object.defineProperty(HTMLElement.prototype, 'offsetHeight', {{
                    get: function() {{
                        const original = originalOffsetHeight.get.call(this);
                        // Add tiny random variation
                        return original + (Math.random() * 2 - 1);
                    }}
                }});
            }}
        }})();
        """
        
        return js_code
    
    def _generate_media_spoofing_js(self, media_profile: MediaProfile) -> str:
        """
        Generate JavaScript to spoof media capabilities.
        
        Args:
            media_profile: MediaProfile object
            
        Returns:
            JavaScript code string
        """
        # Create media devices JSON
        devices_json = str(media_profile.media_devices).replace("'", "\\'")
        
        # Create codec lists
        audio_codecs_json = str(media_profile.audio_codecs).replace("'", "\\'")
        video_codecs_json = str(media_profile.video_codecs).replace("'", "\\'")
        
        # Create WebGL extensions JSON
        webgl_extensions_json = str(media_profile.webgl_extensions).replace("'", "\\'")
        
        # Create WebGL parameters JSON
        webgl_params_json = str(media_profile.webgl_parameters).replace("'", "\\'").replace('"', '\\"')
        
        js_code = f"""
        // Media capability spoofing
        (function() {{
            // Override media devices enumeration
            if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {{
                const originalEnumerateDevices = navigator.mediaDevices.enumerateDevices;
                navigator.mediaDevices.enumerateDevices = function() {{
                    return Promise.resolve({devices_json});
                }};
            }}
            
            // Override media device permissions
            if (navigator.permissions && navigator.permissions.query) {{
                const originalPermissionsQuery = navigator.permissions.query;
                navigator.permissions.query = function(descriptor) {{
                    if (descriptor && descriptor.name === 'camera') {{
                        return Promise.resolve({{state: 'granted'}});
                    }} else if (descriptor && descriptor.name === 'microphone') {{
                        return Promise.resolve({{state: 'granted'}});
                    }}
                    return originalPermissionsQuery.apply(this, arguments);
                }};
            }}
            
            // Override media capabilities API
            if (HTMLMediaElement) {{
                // Audio codec support
                const audioCodecs = {audio_codecs_json};
                const originalCanPlayType = HTMLAudioElement.prototype.canPlayType;
                HTMLAudioElement.prototype.canPlayType = function(type) {{
                    if (audioCodecs.includes(type)) {{
                        return 'probably';
                    }}
                    return originalCanPlayType.apply(this, arguments);
                }};
                
                // Video codec support
                const videoCodecs = {video_codecs_json};
                const originalVideoCanPlayType = HTMLVideoElement.prototype.canPlayType;
                HTMLVideoElement.prototype.canPlayType = function(type) {{
                    if (videoCodecs.includes(type)) {{
                        return 'probably';
                    }}
                    return originalVideoCanPlayType.apply(this, arguments);
                }};
            }}
            
            // WebGL extension spoofing
            if (window.WebGLRenderingContext) {{
                const webglExtensions = {webgl_extensions_json};
                const originalGetExtension = WebGLRenderingContext.prototype.getExtension;
                WebGLRenderingContext.prototype.getExtension = function(name) {{
                    if (webglExtensions.includes(name)) {{
                        // Return a mock extension object
                        return {{
                            name: name,
                            toString: function() {{ return '[object WebGLExtension]'; }}
                        }};
                    }}
                    return originalGetExtension.apply(this, arguments);
                }};
                
                // WebGL parameter spoofing
                const webglParams = {webgl_params_json};
                const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(pname) {{
                    // Handle common parameters
                    if (pname === 0x1F00) {{ // VERSION
                        return webglParams.VERSION || 'WebGL 1.0';
                    }} else if (pname === 0x1F01) {{ // SHADING_LANGUAGE_VERSION
                        return webglParams.SHADING_LANGUAGE_VERSION || 'WebGL GLSL ES 1.0';
                    }} else if (pname === 0x1F02) {{ // VENDOR
                        return webglParams.VENDOR || 'WebKit';
                    }} else if (pname === 0x1F03) {{ // RENDERER
                        return webglParams.RENDERER || 'WebKit WebGL';
                    }}
                    return originalGetParameter.apply(this, arguments);
                }};
            }}
        }})();
        """
        
        return js_code
    
    def get_font_names(self, font_profile: List[FontProfile]) -> List[str]:
        """
        Get font names from a font profile.
        
        Args:
            font_profile: List of FontProfile objects
            
        Returns:
            List of font names
        """
        return [font.name for font in font_profile]
    
    def is_monospace_font(self, font: FontProfile) -> bool:
        """
        Check if a font is monospace.
        
        Args:
            font: FontProfile to check
            
        Returns:
            True if font is monospace, False otherwise
        """
        return font.is_monospace
    
    def is_serif_font(self, font: FontProfile) -> bool:
        """
        Check if a font is serif.
        
        Args:
            font: FontProfile to check
            
        Returns:
            True if font is serif, False otherwise
        """
        return font.is_serif