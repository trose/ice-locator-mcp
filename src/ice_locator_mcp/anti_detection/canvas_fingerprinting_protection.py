"""
Canvas Fingerprinting Protection Manager for ICE Locator MCP Server.

This module provides advanced canvas fingerprinting protection techniques to prevent
browser fingerprinting based on HTML5 canvas rendering capabilities. It implements
realistic rendering patterns, noise injection, and other techniques to avoid detection.
"""

import random
import structlog
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
from playwright.async_api import BrowserContext


@dataclass
class AdvancedCanvasProfile:
    """Represents an advanced canvas configuration with realistic properties for fingerprinting protection."""
    # Text rendering variations
    text_rendering_noise: float  # Amount of noise in text rendering (0.0-1.0)
    text_baseline_variation: float  # Variation in text baseline positioning
    font_smoothing_variation: bool  # Whether to vary font smoothing
    
    # Pixel manipulation protection
    pixel_data_noise_level: float  # Level of noise to add to pixel data (0.0-1.0)
    pixel_data_rounding: int  # Number of decimal places to round pixel data
    color_depth_variation: bool  # Whether to vary color depth representation
    
    # Rendering timing variations
    rendering_delay_min: float  # Minimum rendering delay in milliseconds
    rendering_delay_max: float  # Maximum rendering delay in milliseconds
    timing_jitter: float  # Amount of timing jitter to add
    
    # Image data protection
    image_data_transformation: str  # Type of transformation to apply (none, shift, noise)
    image_data_block_size: int  # Block size for image data transformations
    
    # Path rendering protection
    path_rendering_noise: float  # Noise level for path rendering operations
    line_cap_variation: bool  # Whether to vary line cap styles
    line_join_variation: bool  # Whether to vary line join styles
    
    # Composite operation protection
    composite_operation_variations: bool  # Whether to vary composite operations
    global_alpha_variation: float  # Variation in global alpha values
    
    # Gradient and pattern protection
    gradient_noise_level: float  # Noise level for gradient operations
    pattern_distortion_level: float  # Distortion level for pattern operations
    
    # WebGL context protection (for canvas WebGL contexts)
    webgl_context_protection: bool  # Whether to protect WebGL contexts within canvas
    webgl_parameter_noise: float  # Noise level for WebGL parameters
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AdvancedCanvasProfile':
        """Create from dictionary."""
        return cls(**data)


class CanvasFingerprintingProtectionManager:
    """Manages advanced canvas fingerprinting protection to avoid browser fingerprinting."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        
        # Common canvas rendering characteristics for different device types
        self.common_canvas_configs = [
            {
                "device_type": "desktop",
                "text_rendering_noise": 0.02,
                "text_baseline_variation": 0.01,
                "font_smoothing_variation": True,
                "pixel_data_noise_level": 0.005,
                "pixel_data_rounding": 2,
                "color_depth_variation": True,
                "rendering_delay_min": 1.0,
                "rendering_delay_max": 5.0,
                "timing_jitter": 0.5,
                "image_data_transformation": "shift",
                "image_data_block_size": 4,
                "path_rendering_noise": 0.01,
                "line_cap_variation": True,
                "line_join_variation": True,
                "composite_operation_variations": True,
                "global_alpha_variation": 0.02,
                "gradient_noise_level": 0.01,
                "pattern_distortion_level": 0.01,
                "webgl_context_protection": True,
                "webgl_parameter_noise": 0.005
            },
            {
                "device_type": "mobile",
                "text_rendering_noise": 0.03,
                "text_baseline_variation": 0.02,
                "font_smoothing_variation": False,
                "pixel_data_noise_level": 0.01,
                "pixel_data_rounding": 1,
                "color_depth_variation": False,
                "rendering_delay_min": 2.0,
                "rendering_delay_max": 8.0,
                "timing_jitter": 1.0,
                "image_data_transformation": "noise",
                "image_data_block_size": 8,
                "path_rendering_noise": 0.02,
                "line_cap_variation": False,
                "line_join_variation": False,
                "composite_operation_variations": False,
                "global_alpha_variation": 0.05,
                "gradient_noise_level": 0.02,
                "pattern_distortion_level": 0.03,
                "webgl_context_protection": True,
                "webgl_parameter_noise": 0.01
            },
            {
                "device_type": "tablet",
                "text_rendering_noise": 0.025,
                "text_baseline_variation": 0.015,
                "font_smoothing_variation": True,
                "pixel_data_noise_level": 0.008,
                "pixel_data_rounding": 2,
                "color_depth_variation": True,
                "rendering_delay_min": 1.5,
                "rendering_delay_max": 6.0,
                "timing_jitter": 0.8,
                "image_data_transformation": "shift",
                "image_data_block_size": 6,
                "path_rendering_noise": 0.015,
                "line_cap_variation": True,
                "line_join_variation": True,
                "composite_operation_variations": True,
                "global_alpha_variation": 0.03,
                "gradient_noise_level": 0.015,
                "pattern_distortion_level": 0.02,
                "webgl_context_protection": True,
                "webgl_parameter_noise": 0.008
            }
        ]
    
    def get_random_canvas_profile(self) -> AdvancedCanvasProfile:
        """
        Get a random advanced canvas profile with realistic properties.
        
        Returns:
            AdvancedCanvasProfile with realistic canvas properties
        """
        config = random.choice(self.common_canvas_configs)
        
        # Add some random variation to make it more realistic
        variation_factor = random.uniform(0.8, 1.2)
        
        return AdvancedCanvasProfile(
            text_rendering_noise=config["text_rendering_noise"] * variation_factor,
            text_baseline_variation=config["text_baseline_variation"] * variation_factor,
            font_smoothing_variation=config["font_smoothing_variation"],
            pixel_data_noise_level=config["pixel_data_noise_level"] * variation_factor,
            pixel_data_rounding=config["pixel_data_rounding"],
            color_depth_variation=config["color_depth_variation"],
            rendering_delay_min=config["rendering_delay_min"] * variation_factor,
            rendering_delay_max=config["rendering_delay_max"] * variation_factor,
            timing_jitter=config["timing_jitter"] * variation_factor,
            image_data_transformation=config["image_data_transformation"],
            image_data_block_size=config["image_data_block_size"],
            path_rendering_noise=config["path_rendering_noise"] * variation_factor,
            line_cap_variation=config["line_cap_variation"],
            line_join_variation=config["line_join_variation"],
            composite_operation_variations=config["composite_operation_variations"],
            global_alpha_variation=config["global_alpha_variation"] * variation_factor,
            gradient_noise_level=config["gradient_noise_level"] * variation_factor,
            pattern_distortion_level=config["pattern_distortion_level"] * variation_factor,
            webgl_context_protection=config["webgl_context_protection"],
            webgl_parameter_noise=config["webgl_parameter_noise"] * variation_factor
        )
    
    def get_device_specific_profile(self, device_type: str) -> AdvancedCanvasProfile:
        """
        Get a device-specific canvas profile.
        
        Args:
            device_type: Type of device ("desktop", "mobile", or "tablet")
            
        Returns:
            AdvancedCanvasProfile with device-specific properties
        """
        for config in self.common_canvas_configs:
            if config["device_type"] == device_type:
                # Create a copy of the config without the device_type key
                config_copy = config.copy()
                del config_copy["device_type"]
                return AdvancedCanvasProfile(**config_copy)
        
        # If device type not found, return a random profile
        return self.get_random_canvas_profile()
    
    async def apply_canvas_fingerprinting_protection(self, context: BrowserContext,
                                                   canvas_profile: Optional[AdvancedCanvasProfile] = None) -> None:
        """
        Apply advanced canvas fingerprinting protection to a browser context.
        
        Args:
            context: Playwright BrowserContext to apply protection to
            canvas_profile: AdvancedCanvasProfile object, or None to generate random
        """
        if canvas_profile is None:
            canvas_profile = self.get_random_canvas_profile()
        
        try:
            # Generate JavaScript to protect against canvas fingerprinting
            canvas_js = self._generate_canvas_protection_js(canvas_profile)
            
            # Add JavaScript to context
            await context.add_init_script(canvas_js)
            
            self.logger.debug(
                "Applied advanced canvas fingerprinting protection to context",
                text_rendering_noise=canvas_profile.text_rendering_noise,
                pixel_data_noise_level=canvas_profile.pixel_data_noise_level
            )
            
        except Exception as e:
            self.logger.error("Failed to apply canvas fingerprinting protection to context", error=str(e))
            raise
    
    def _generate_canvas_protection_js(self, canvas_profile: AdvancedCanvasProfile) -> str:
        """
        Generate JavaScript to protect against canvas fingerprinting.
        
        Args:
            canvas_profile: AdvancedCanvasProfile object
            
        Returns:
            JavaScript code string
        """
        # Convert profile values to JavaScript-friendly format
        text_rendering_noise = canvas_profile.text_rendering_noise
        text_baseline_variation = canvas_profile.text_baseline_variation
        pixel_data_noise_level = canvas_profile.pixel_data_noise_level
        pixel_data_rounding = canvas_profile.pixel_data_rounding
        rendering_delay_min = canvas_profile.rendering_delay_min
        rendering_delay_max = canvas_profile.rendering_delay_max
        timing_jitter = canvas_profile.timing_jitter
        image_data_transformation = canvas_profile.image_data_transformation
        image_data_block_size = canvas_profile.image_data_block_size
        path_rendering_noise = canvas_profile.path_rendering_noise
        global_alpha_variation = canvas_profile.global_alpha_variation
        gradient_noise_level = canvas_profile.gradient_noise_level
        
        js_code = f"""
        // Advanced Canvas Fingerprinting Protection
        (function() {{
            // Protect HTML5 Canvas API
            if (window.HTMLCanvasElement) {{
                // Override getContext to add protection for 2D contexts
                const originalGetContext = HTMLCanvasElement.prototype.getContext;
                HTMLCanvasElement.prototype.getContext = function(contextType, contextAttributes) {{
                    const context = originalGetContext.apply(this, [contextType, contextAttributes]);
                    
                    if (contextType === '2d' && context) {{
                        // Protect fillText method
                        const originalFillText = context.fillText;
                        context.fillText = function(text, x, y, maxWidth) {{
                            // Add noise to text rendering
                            const noiseX = (Math.random() - 0.5) * 2 * {text_rendering_noise};
                            const noiseY = (Math.random() - 0.5) * 2 * {text_rendering_noise};
                            
                            // Apply text baseline variation
                            const baselineVariation = (Math.random() - 0.5) * 2 * {text_baseline_variation};
                            
                            return originalFillText.apply(this, [
                                text,
                                parseFloat(x) + noiseX,
                                parseFloat(y) + noiseY + baselineVariation,
                                maxWidth
                            ]);
                        }};
                        
                        // Protect strokeText method
                        const originalStrokeText = context.strokeText;
                        context.strokeText = function(text, x, y, maxWidth) {{
                            const noiseX = (Math.random() - 0.5) * 2 * {text_rendering_noise};
                            const noiseY = (Math.random() - 0.5) * 2 * {text_rendering_noise};
                            const baselineVariation = (Math.random() - 0.5) * 2 * {text_baseline_variation};
                            
                            return originalStrokeText.apply(this, [
                                text,
                                parseFloat(x) + noiseX,
                                parseFloat(y) + noiseY + baselineVariation,
                                maxWidth
                            ]);
                        }};
                        
                        // Protect toDataURL method
                        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                        HTMLCanvasElement.prototype.toDataURL = function(type, quality) {{
                            // Add slight delay to simulate real rendering time
                            const baseDelay = {rendering_delay_min};
                            const maxAdditionalDelay = {rendering_delay_max} - {rendering_delay_min};
                            const jitter = (Math.random() - 0.5) * 2 * {timing_jitter};
                            const totalDelay = Math.max(0, baseDelay + Math.random() * maxAdditionalDelay + jitter);
                            
                            // In a real implementation, we would add the delay here
                            // For now, we just return the original result after potential modifications
                            const result = originalToDataURL.apply(this, [type, quality]);
                            return result;
                        }};
                        
                        // Protect getImageData method
                        const originalGetImageData = context.getImageData;
                        context.getImageData = function(sx, sy, sw, sh) {{
                            const imageData = originalGetImageData.apply(this, [sx, sy, sw, sh]);
                            
                            if (imageData && imageData.data) {{
                                const data = imageData.data;
                                
                                // Apply image data transformation based on profile
                                if ('{image_data_transformation}' === 'noise') {{
                                    // Add noise to pixel data
                                    const noiseLevel = {pixel_data_noise_level};
                                    for (let i = 0; i < data.length; i++) {{
                                        const noise = (Math.random() - 0.5) * 2 * noiseLevel * 255;
                                        data[i] = Math.max(0, Math.min(255, data[i] + noise));
                                    }}
                                }} else if ('{image_data_transformation}' === 'shift') {{
                                    // Shift pixel data in blocks
                                    const blockSize = {image_data_block_size};
                                    for (let i = 0; i < data.length; i += blockSize) {{
                                        const shift = Math.floor(Math.random() * blockSize);
                                        for (let j = 0; j < blockSize && (i + j) < data.length; j++) {{
                                            const targetIndex = i + ((j + shift) % blockSize);
                                            if (targetIndex < data.length) {{
                                                const temp = data[i + j];
                                                data[i + j] = data[targetIndex];
                                                data[targetIndex] = temp;
                                            }}
                                        }}
                                    }}
                                }}
                                
                                // Apply pixel data rounding
                                const roundingFactor = Math.pow(10, {pixel_data_rounding});
                                for (let i = 0; i < data.length; i++) {{
                                    data[i] = Math.round(data[i] * roundingFactor) / roundingFactor;
                                }}
                            }}
                            
                            return imageData;
                        }};
                        
                        // Protect putImageData method
                        const originalPutImageData = context.putImageData;
                        context.putImageData = function(imageData, dx, dy, dirtyX, dirtyY, dirtyWidth, dirtyHeight) {{
                            // Add path rendering noise
                            const pathNoise = (Math.random() - 0.5) * 2 * {path_rendering_noise};
                            
                            // Apply noise to coordinates
                            const noisyDx = dx + pathNoise;
                            const noisyDy = dy + pathNoise;
                            
                            return originalPutImageData.apply(this, [
                                imageData, noisyDx, noisyDy, dirtyX, dirtyY, dirtyWidth, dirtyHeight
                            ]);
                        }};
                        
                        // Protect globalAlpha property
                        const originalGlobalAlpha = Object.getOwnPropertyDescriptor(CanvasRenderingContext2D.prototype, 'globalAlpha');
                        Object.defineProperty(context, 'globalAlpha', {{
                            get: function() {{
                                return originalGlobalAlpha.get.call(this);
                            }},
                            set: function(value) {{
                                // Add variation to global alpha
                                const variation = (Math.random() - 0.5) * 2 * {global_alpha_variation};
                                const newValue = Math.max(0, Math.min(1, parseFloat(value) + variation));
                                return originalGlobalAlpha.set.call(this, newValue);
                            }}
                        }});
                        
                        // Add rendering timing variations
                        const renderingMethods = [
                            'fillRect', 'strokeRect', 'clearRect',
                            'fill', 'stroke', 'clip', 'rotate', 'scale', 'translate'
                        ];
                        
                        renderingMethods.forEach(methodName => {{
                            if (typeof context[methodName] === 'function') {{
                                const originalMethod = context[methodName];
                                context[methodName] = function() {{
                                    // Add slight delay to simulate real rendering time
                                    const baseDelay = {rendering_delay_min};
                                    const maxAdditionalDelay = {rendering_delay_max} - {rendering_delay_min};
                                    const jitter = (Math.random() - 0.5) * 2 * {timing_jitter};
                                    const totalDelay = Math.max(0, baseDelay + Math.random() * maxAdditionalDelay + jitter);
                                    
                                    // In a real implementation, we would add the delay here
                                    // For now, we just call the original method
                                    return originalMethod.apply(this, arguments);
                                }};
                            }}
                        }});
                    }}
                    
                    return context;
                }};
                
                // Protect CanvasGradient API
                if (window.CanvasGradient) {{
                    const originalAddColorStop = CanvasGradient.prototype.addColorStop;
                    CanvasGradient.prototype.addColorStop = function(offset, color) {{
                        // Add noise to gradient color stops
                        const noise = (Math.random() - 0.5) * 2 * {gradient_noise_level};
                        const noisyOffset = Math.max(0, Math.min(1, parseFloat(offset) + noise));
                        return originalAddColorStop.apply(this, [noisyOffset, color]);
                    }};
                }}
            }}
            
            // Protect OffscreenCanvas API if available
            if (window.OffscreenCanvas) {{
                const originalOffscreenGetContext = OffscreenCanvas.prototype.getContext;
                OffscreenCanvas.prototype.getContext = function(contextType, contextAttributes) {{
                    const context = originalOffscreenGetContext.apply(this, [contextType, contextAttributes]);
                    
                    // Apply similar protections to offscreen contexts
                    if (contextType === '2d' && context) {{
                        // Add protection logic similar to HTMLCanvasElement
                        // ... (similar implementation as above)
                    }}
                    
                    return context;
                }};
            }}
        }})();
        """
        
        return js_code
    
    def generate_canvas_fingerprint(self, canvas_profile: AdvancedCanvasProfile) -> str:
        """
        Generate a fingerprint based on canvas profile.
        
        Args:
            canvas_profile: AdvancedCanvasProfile object
            
        Returns:
            String fingerprint
        """
        # Create a string representation of the profile
        fingerprint_data = (
            f"{canvas_profile.text_rendering_noise}|{canvas_profile.pixel_data_noise_level}|"
            f"{canvas_profile.rendering_delay_min}|{canvas_profile.rendering_delay_max}|"
            f"{canvas_profile.image_data_transformation}|{canvas_profile.path_rendering_noise}"
        )
        
        # Generate a hash of the fingerprint data
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    def are_profiles_consistent(self, canvas_profile: AdvancedCanvasProfile) -> bool:
        """
        Check if canvas profile is consistent.
        
        Args:
            canvas_profile: AdvancedCanvasProfile object
            
        Returns:
            True if profile is consistent, False otherwise
        """
        # Check that delay values are reasonable
        if canvas_profile.rendering_delay_min < 0 or canvas_profile.rendering_delay_max < 0:
            return False
        
        if canvas_profile.rendering_delay_min > canvas_profile.rendering_delay_max:
            return False
        
        # Check that noise levels are within reasonable range
        if (canvas_profile.text_rendering_noise < 0 or canvas_profile.text_rendering_noise > 1 or
            canvas_profile.pixel_data_noise_level < 0 or canvas_profile.pixel_data_noise_level > 1 or
            canvas_profile.path_rendering_noise < 0 or canvas_profile.path_rendering_noise > 1 or
            canvas_profile.gradient_noise_level < 0 or canvas_profile.gradient_noise_level > 1 or
            canvas_profile.pattern_distortion_level < 0 or canvas_profile.pattern_distortion_level > 1):
            return False
        
        # Check that rounding is a reasonable value
        if canvas_profile.pixel_data_rounding < 0 or canvas_profile.pixel_data_rounding > 10:
            return False
        
        # Check that block size is reasonable
        if canvas_profile.image_data_block_size < 1 or canvas_profile.image_data_block_size > 100:
            return False
        
        return True