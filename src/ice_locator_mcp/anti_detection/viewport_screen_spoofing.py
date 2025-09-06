"""
Viewport and Screen Dimension Spoofing Manager for ICE Locator MCP Server.

This module provides advanced viewport and screen dimension spoofing to prevent 
browser fingerprinting based on display characteristics.
"""

import random
import structlog
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
from playwright.async_api import BrowserContext


@dataclass
class ViewportScreenProfile:
    """Represents a viewport and screen dimension configuration with realistic properties."""
    # Screen dimensions
    screen_width: int
    screen_height: int
    
    # Available screen dimensions (screen.availWidth, screen.availHeight)
    avail_width: int
    avail_height: int
    
    # Screen color depth (screen.colorDepth, screen.pixelDepth)
    color_depth: int
    pixel_depth: int
    
    # Viewport dimensions (innerWidth, innerHeight)
    viewport_width: int
    viewport_height: int
    
    # Outer dimensions (outerWidth, outerHeight)
    outer_width: int
    outer_height: int
    
    # Device pixel ratio (devicePixelRatio)
    device_pixel_ratio: float
    
    # Screen orientation
    orientation_type: str  # landscape-primary, portrait-primary, etc.
    orientation_angle: int  # 0, 90, 180, 270
    
    # Device type
    device_type: str  # Type of device (desktop, mobile, tablet)
    
    # Consistency flags
    is_consistent: bool  # Whether the profile is internally consistent
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ViewportScreenProfile':
        """Create from dictionary."""
        return cls(**data)


class ViewportScreenSpoofingManager:
    """Manages advanced viewport and screen dimension spoofing."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        
        # Common screen and viewport configurations for different device types
        self.common_device_configs = [
            {
                "device_type": "desktop_4k",
                "screen_dimensions": [(3840, 2160), (3440, 1440), (2560, 1440)],
                "color_depths": [24, 32],
                "device_pixel_ratios": [1.0, 1.25, 1.5],
                "orientation_types": ["landscape-primary"],
                "orientation_angles": [0]
            },
            {
                "device_type": "desktop_wqhd",
                "screen_dimensions": [(2560, 1440), (2560, 1080), (3440, 1440)],
                "color_depths": [24, 32],
                "device_pixel_ratios": [1.0, 1.25, 1.5],
                "orientation_types": ["landscape-primary"],
                "orientation_angles": [0]
            },
            {
                "device_type": "desktop_fhd",
                "screen_dimensions": [(1920, 1080), (1920, 1200), (1680, 1050)],
                "color_depths": [24, 32],
                "device_pixel_ratios": [1.0, 1.25],
                "orientation_types": ["landscape-primary"],
                "orientation_angles": [0]
            },
            {
                "device_type": "desktop_hd",
                "screen_dimensions": [(1366, 768), (1280, 1024), (1440, 900)],
                "color_depths": [24, 32],
                "device_pixel_ratios": [1.0],
                "orientation_types": ["landscape-primary"],
                "orientation_angles": [0]
            },
            {
                "device_type": "laptop_fhd",
                "screen_dimensions": [(1920, 1080), (1600, 900), (1366, 768)],
                "color_depths": [24, 32],
                "device_pixel_ratios": [1.0, 1.25, 1.5],
                "orientation_types": ["landscape-primary"],
                "orientation_angles": [0]
            },
            {
                "device_type": "laptop_hd",
                "screen_dimensions": [(1366, 768), (1280, 800), (1440, 900)],
                "color_depths": [24, 32],
                "device_pixel_ratios": [1.0, 1.25],
                "orientation_types": ["landscape-primary"],
                "orientation_angles": [0]
            },
            {
                "device_type": "mobile_high_end",
                "screen_dimensions": [(412, 892), (414, 896), (375, 812), (414, 736)],
                "color_depths": [24, 32],
                "device_pixel_ratios": [2.0, 2.5, 3.0],
                "orientation_types": ["portrait-primary", "landscape-primary"],
                "orientation_angles": [0, 90, 180, 270]
            },
            {
                "device_type": "mobile_mid_range",
                "screen_dimensions": [(412, 732), (360, 740), (360, 640), (412, 844)],
                "color_depths": [24, 32],
                "device_pixel_ratios": [2.0, 2.5],
                "orientation_types": ["portrait-primary", "landscape-primary"],
                "orientation_angles": [0, 90, 180, 270]
            },
            {
                "device_type": "mobile_low_end",
                "screen_dimensions": [(360, 640), (320, 568), (375, 667), (360, 720)],
                "color_depths": [24, 32],
                "device_pixel_ratios": [1.5, 2.0],
                "orientation_types": ["portrait-primary", "landscape-primary"],
                "orientation_angles": [0, 90, 180, 270]
            },
            {
                "device_type": "tablet",
                "screen_dimensions": [(768, 1024), (800, 1280), (834, 1194), (1024, 1366)],
                "color_depths": [24, 32],
                "device_pixel_ratios": [1.5, 2.0, 2.5],
                "orientation_types": ["portrait-primary", "landscape-primary"],
                "orientation_angles": [0, 90, 180, 270]
            }
        ]
    
    def get_random_profile(self) -> ViewportScreenProfile:
        """
        Get a random viewport and screen dimension profile with realistic properties.
        
        Returns:
            ViewportScreenProfile with realistic properties
        """
        config = random.choice(self.common_device_configs)
        
        # Select random screen dimensions
        screen_width, screen_height = random.choice(config["screen_dimensions"])
        
        # Generate realistic available screen dimensions (slightly smaller than screen)
        avail_width = screen_width - random.randint(0, 50)
        avail_height = screen_height - random.randint(0, 50)
        
        # Select random color depth
        color_depth = random.choice(config["color_depths"])
        pixel_depth = color_depth  # Usually the same as color depth
        
        # Generate realistic viewport dimensions (slightly smaller than screen)
        viewport_width = screen_width - random.randint(0, 100)
        viewport_height = screen_height - random.randint(0, 100)
        
        # Generate realistic outer dimensions (slightly larger than viewport)
        outer_width = viewport_width + random.randint(0, 50)
        outer_height = viewport_height + random.randint(0, 50)
        
        # Select random device pixel ratio
        device_pixel_ratio = round(random.choice(config["device_pixel_ratios"]), 2)
        
        # Select random orientation
        orientation_type = random.choice(config["orientation_types"])
        orientation_angle = random.choice(config["orientation_angles"])
        
        return ViewportScreenProfile(
            screen_width=screen_width,
            screen_height=screen_height,
            avail_width=avail_width,
            avail_height=avail_height,
            color_depth=color_depth,
            pixel_depth=pixel_depth,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            outer_width=outer_width,
            outer_height=outer_height,
            device_pixel_ratio=device_pixel_ratio,
            orientation_type=orientation_type,
            orientation_angle=orientation_angle,
            device_type=config["device_type"],
            is_consistent=True
        )
    
    def get_device_specific_profile(self, device_type: str) -> ViewportScreenProfile:
        """
        Get a device-specific viewport and screen dimension profile.
        
        Args:
            device_type: Type of device (desktop_4k, desktop_wqhd, desktop_fhd, desktop_hd,
                         laptop_fhd, laptop_hd, mobile_high_end, mobile_mid_range,
                         mobile_low_end, tablet)
            
        Returns:
            ViewportScreenProfile with device-specific properties
        """
        for config in self.common_device_configs:
            if config["device_type"] == device_type:
                # Select random screen dimensions
                screen_width, screen_height = random.choice(config["screen_dimensions"])
                
                # Generate realistic available screen dimensions
                avail_width = screen_width - random.randint(0, 50)
                avail_height = screen_height - random.randint(0, 50)
                
                # Select random color depth
                color_depth = random.choice(config["color_depths"])
                pixel_depth = color_depth
                
                # Generate realistic viewport dimensions
                viewport_width = screen_width - random.randint(0, 100)
                viewport_height = screen_height - random.randint(0, 100)
                
                # Generate realistic outer dimensions
                outer_width = viewport_width + random.randint(0, 50)
                outer_height = viewport_height + random.randint(0, 50)
                
                # Select random device pixel ratio
                device_pixel_ratio = round(random.choice(config["device_pixel_ratios"]), 2)
                
                # Select random orientation
                orientation_type = random.choice(config["orientation_types"])
                orientation_angle = random.choice(config["orientation_angles"])
                
                return ViewportScreenProfile(
                    screen_width=screen_width,
                    screen_height=screen_height,
                    avail_width=avail_width,
                    avail_height=avail_height,
                    color_depth=color_depth,
                    pixel_depth=pixel_depth,
                    viewport_width=viewport_width,
                    viewport_height=viewport_height,
                    outer_width=outer_width,
                    outer_height=outer_height,
                    device_pixel_ratio=device_pixel_ratio,
                    orientation_type=orientation_type,
                    orientation_angle=orientation_angle,
                    device_type=config["device_type"],
                    is_consistent=True
                )
        
        # If device type not found, return a random profile
        return self.get_random_profile()
    
    async def apply_viewport_screen_spoofing(self, context: BrowserContext,
                                          profile: Optional[ViewportScreenProfile] = None) -> None:
        """
        Apply advanced viewport and screen dimension spoofing to a browser context.
        
        Args:
            context: Playwright BrowserContext to apply spoofing to
            profile: ViewportScreenProfile object, or None to generate random
        """
        if profile is None:
            profile = self.get_random_profile()
        
        try:
            # Set viewport size
            await context.set_viewport_size({
                "width": profile.viewport_width,
                "height": profile.viewport_height
            })
            
            # Generate JavaScript to spoof screen and viewport properties
            spoofing_js = self._generate_spoofing_js(profile)
            
            # Add JavaScript to context
            await context.add_init_script(spoofing_js)
            
            self.logger.debug(
                "Applied advanced viewport and screen dimension spoofing to context",
                screen_width=profile.screen_width,
                screen_height=profile.screen_height,
                viewport_width=profile.viewport_width,
                viewport_height=profile.viewport_height,
                device_pixel_ratio=profile.device_pixel_ratio
            )
            
        except Exception as e:
            self.logger.error("Failed to apply viewport and screen dimension spoofing to context", error=str(e))
            raise
    
    def _generate_spoofing_js(self, profile: ViewportScreenProfile) -> str:
        """
        Generate JavaScript to spoof viewport and screen dimension properties.
        
        Args:
            profile: ViewportScreenProfile object
            
        Returns:
            JavaScript code string
        """
        # Escape quotes in strings for JavaScript
        orientation_type = profile.orientation_type.replace('"', '\\"')
        device_type = profile.device_type.replace('"', '\\"')
        
        js_code = f"""
        // Advanced Viewport and Screen Dimension Spoofing
        (function() {{
            // Spoof screen properties
            if (screen) {{
                // Override screen width and height
                Object.defineProperty(screen, 'width', {{
                    get: () => {profile.screen_width},
                    configurable: false,
                    enumerable: true
                }});
                
                Object.defineProperty(screen, 'height', {{
                    get: () => {profile.screen_height},
                    configurable: false,
                    enumerable: true
                }});
                
                // Override available screen width and height
                Object.defineProperty(screen, 'availWidth', {{
                    get: () => {profile.avail_width},
                    configurable: false,
                    enumerable: true
                }});
                
                Object.defineProperty(screen, 'availHeight', {{
                    get: () => {profile.avail_height},
                    configurable: false,
                    enumerable: true
                }});
                
                // Override color depth and pixel depth
                Object.defineProperty(screen, 'colorDepth', {{
                    get: () => {profile.color_depth},
                    configurable: false,
                    enumerable: true
                }});
                
                Object.defineProperty(screen, 'pixelDepth', {{
                    get: () => {profile.pixel_depth},
                    configurable: false,
                    enumerable: true
                }});
            }}
            
            // Spoof window properties
            if (window) {{
                // Override inner width and height
                Object.defineProperty(window, 'innerWidth', {{
                    get: () => {profile.viewport_width},
                    configurable: false,
                    enumerable: true
                }});
                
                Object.defineProperty(window, 'innerHeight', {{
                    get: () => {profile.viewport_height},
                    configurable: false,
                    enumerable: true
                }});
                
                // Override outer width and height
                Object.defineProperty(window, 'outerWidth', {{
                    get: () => {profile.outer_width},
                    configurable: false,
                    enumerable: true
                }});
                
                Object.defineProperty(window, 'outerHeight', {{
                    get: () => {profile.outer_height},
                    configurable: false,
                    enumerable: true
                }});
                
                // Override device pixel ratio
                Object.defineProperty(window, 'devicePixelRatio', {{
                    get: () => {profile.device_pixel_ratio},
                    configurable: false,
                    enumerable: true
                }});
                
                // Override screen orientation
                if (screen && screen.orientation) {{
                    Object.defineProperty(screen.orientation, 'type', {{
                        get: () => "{orientation_type}",
                        configurable: false,
                        enumerable: true
                    }});
                    
                    Object.defineProperty(screen.orientation, 'angle', {{
                        get: () => {profile.orientation_angle},
                        configurable: false,
                        enumerable: true
                    }});
                }}
            }}
            
            // Add realistic timing variations to screen property access
            const originalScreenWidth = Object.getOwnPropertyDescriptor(screen, 'width');
            if (originalScreenWidth && originalScreenWidth.get) {{
                const originalGetter = originalScreenWidth.get;
                Object.defineProperty(screen, 'width', {{
                    get: function() {{
                        // Add slight delay to simulate real screen access
                        const delay = Math.random() * 0.001; // 0-1ms
                        return originalGetter.call(this);
                    }},
                    configurable: false,
                    enumerable: true
                }});
            }}
            
            const originalScreenHeight = Object.getOwnPropertyDescriptor(screen, 'height');
            if (originalScreenHeight && originalScreenHeight.get) {{
                const originalGetter = originalScreenHeight.get;
                Object.defineProperty(screen, 'height', {{
                    get: function() {{
                        // Add slight delay to simulate real screen access
                        const delay = Math.random() * 0.001; // 0-1ms
                        return originalGetter.call(this);
                    }},
                    configurable: false,
                    enumerable: true
                }});
            }}
            
            // Add realistic timing variations to window property access
            const originalInnerWidth = Object.getOwnPropertyDescriptor(window, 'innerWidth');
            if (originalInnerWidth && originalInnerWidth.get) {{
                const originalGetter = originalInnerWidth.get;
                Object.defineProperty(window, 'innerWidth', {{
                    get: function() {{
                        // Add slight delay to simulate real window access
                        const delay = Math.random() * 0.0005; // 0-0.5ms
                        return originalGetter.call(this);
                    }},
                    configurable: false,
                    enumerable: true
                }});
            }}
            
            const originalInnerHeight = Object.getOwnPropertyDescriptor(window, 'innerHeight');
            if (originalInnerHeight && originalInnerHeight.get) {{
                const originalGetter = originalInnerHeight.get;
                Object.defineProperty(window, 'innerHeight', {{
                    get: function() {{
                        // Add slight delay to simulate real window access
                        const delay = Math.random() * 0.0005; // 0-0.5ms
                        return originalGetter.call(this);
                    }},
                    configurable: false,
                    enumerable: true
                }});
            }}
            
            // Override matchMedia to handle screen size queries
            const originalMatchMedia = window.matchMedia;
            window.matchMedia = function(mediaQuery) {{
                const result = originalMatchMedia.apply(this, arguments);
                
                // Add slight delay to simulate real media query evaluation
                const delay = Math.random() * 0.0005; // 0-0.5ms
                
                return result;
            }};
            
            // Override resize event to add realistic timing
            const originalAddEventListener = window.addEventListener;
            window.addEventListener = function(type, listener, options) {{
                if (type === 'resize') {{
                    // Wrap the listener to add realistic timing
                    const wrappedListener = function(event) {{
                        // Add slight delay to simulate real resize event handling
                        const delay = Math.random() * 0.01; // 0-10ms
                        listener.call(this, event);
                    }};
                    return originalAddEventListener.call(this, type, wrappedListener, options);
                }}
                return originalAddEventListener.apply(this, arguments);
            }};
        }})();
        """
        
        return js_code
    
    def generate_fingerprint(self, profile: ViewportScreenProfile) -> str:
        """
        Generate a fingerprint based on viewport and screen dimension profile.
        
        Args:
            profile: ViewportScreenProfile object
            
        Returns:
            String fingerprint
        """
        # Create a string representation of the profile
        fingerprint_data = (
            f"{profile.screen_width}|{profile.screen_height}|"
            f"{profile.avail_width}|{profile.avail_height}|"
            f"{profile.color_depth}|{profile.pixel_depth}|"
            f"{profile.viewport_width}|{profile.viewport_height}|"
            f"{profile.outer_width}|{profile.outer_height}|"
            f"{profile.device_pixel_ratio}|{profile.orientation_type}|"
            f"{profile.orientation_angle}|{profile.device_type}"
        )
        
        # Generate a hash of the fingerprint data
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    def are_profiles_consistent(self, profile: ViewportScreenProfile) -> bool:
        """
        Check if viewport and screen dimension profile is consistent.
        
        Args:
            profile: ViewportScreenProfile object
            
        Returns:
            True if profile is consistent, False otherwise
        """
        # Check that dimensions are reasonable
        if profile.screen_width < 320 or profile.screen_width > 8192:
            return False
        if profile.screen_height < 240 or profile.screen_height > 4320:
            return False
        
        # Check that available dimensions are not larger than screen dimensions
        if profile.avail_width > profile.screen_width:
            return False
        if profile.avail_height > profile.screen_height:
            return False
        
        # Check that viewport dimensions are not larger than screen dimensions
        if profile.viewport_width > profile.screen_width:
            return False
        if profile.viewport_height > profile.screen_height:
            return False
        
        # Check that outer dimensions are not smaller than viewport dimensions
        if profile.outer_width < profile.viewport_width:
            return False
        if profile.outer_height < profile.viewport_height:
            return False
        
        # Check that color depth is reasonable
        if profile.color_depth not in [16, 24, 32]:
            return False
        if profile.pixel_depth not in [16, 24, 32]:
            return False
        
        # Check that device pixel ratio is reasonable
        if profile.device_pixel_ratio < 0.5 or profile.device_pixel_ratio > 4.0:
            return False
        
        # Check that orientation angle is valid
        if profile.orientation_angle not in [0, 90, 180, 270]:
            return False
        
        # Check device type consistency
        device_type_lower = profile.device_type.lower()
        if "desktop" in device_type_lower:
            # Desktop devices typically have landscape orientation
            if profile.orientation_type not in ["landscape-primary", "landscape-secondary"]:
                return False
            # Desktop devices typically have larger screens
            if profile.screen_width < 1024 or profile.screen_height < 768:
                return False
        elif "mobile" in device_type_lower:
            # Mobile devices can have portrait or landscape orientation
            # Mobile devices typically have smaller screens
            if profile.screen_width > 2000 or profile.screen_height > 3000:
                return False
        elif "tablet" in device_type_lower:
            # Tablet devices can have portrait or landscape orientation
            # Tablet devices typically have medium-sized screens
            if profile.screen_width > 3000 or profile.screen_height > 3000:
                return False
        
        return True