"""
Viewport and Screen Simulation Manager for ICE Locator MCP Server.

This module provides advanced viewport and screen simulation capabilities to avoid 
detection based on display characteristics. It implements realistic screen dimensions, 
device emulation, and dynamic viewport resizing.
"""

import random
import structlog
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any
from playwright.async_api import BrowserContext


@dataclass
class ViewportProfile:
    """Represents a viewport configuration with realistic properties."""
    width: int
    height: int
    device_scale_factor: float
    is_mobile: bool
    has_touch: bool
    screen_width: int
    screen_height: int
    avail_width: int
    avail_height: int
    color_depth: int
    pixel_depth: int
    orientation_type: str
    orientation_angle: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "width": self.width,
            "height": self.height,
            "device_scale_factor": self.device_scale_factor,
            "is_mobile": self.is_mobile,
            "has_touch": self.has_touch,
            "screen_width": self.screen_width,
            "screen_height": self.screen_height,
            "avail_width": self.avail_width,
            "avail_height": self.avail_height,
            "color_depth": self.color_depth,
            "pixel_depth": self.pixel_depth,
            "orientation_type": self.orientation_type,
            "orientation_angle": self.orientation_angle
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ViewportProfile':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class DeviceProfile:
    """Represents a device with specific screen and viewport characteristics."""
    name: str
    viewport: ViewportProfile
    user_agent: str
    platform: str


class ViewportManager:
    """Manages advanced viewport and screen simulation to avoid detection based on display characteristics."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        
        # Common desktop viewport configurations
        self.desktop_viewports = [
            ViewportProfile(1920, 1080, 1.0, False, False, 1920, 1080, 1920, 1040, 24, 24, "landscape-primary", 0),
            ViewportProfile(1366, 768, 1.0, False, False, 1366, 768, 1366, 728, 24, 24, "landscape-primary", 0),
            ViewportProfile(1536, 864, 1.25, False, False, 1536, 864, 1536, 824, 24, 24, "landscape-primary", 0),
            ViewportProfile(1440, 900, 1.0, False, False, 1440, 900, 1440, 860, 24, 24, "landscape-primary", 0),
            ViewportProfile(1600, 900, 1.0, False, False, 1600, 900, 1600, 860, 24, 24, "landscape-primary", 0),
            ViewportProfile(1280, 1024, 1.0, False, False, 1280, 1024, 1280, 984, 24, 24, "landscape-primary", 0),
            ViewportProfile(1280, 800, 1.0, False, False, 1280, 800, 1280, 760, 24, 24, "landscape-primary", 0),
            ViewportProfile(1680, 1050, 1.0, False, False, 1680, 1050, 1680, 1010, 24, 24, "landscape-primary", 0),
            ViewportProfile(1920, 1200, 1.0, False, False, 1920, 1200, 1920, 1160, 24, 24, "landscape-primary", 0),
        ]
        
        # Common laptop viewport configurations
        self.laptop_viewports = [
            ViewportProfile(1366, 768, 1.0, False, False, 1366, 768, 1366, 728, 24, 24, "landscape-primary", 0),
            ViewportProfile(1536, 864, 1.25, False, False, 1536, 864, 1536, 824, 24, 24, "landscape-primary", 0),
            ViewportProfile(1440, 900, 1.0, False, False, 1440, 900, 1440, 860, 24, 24, "landscape-primary", 0),
            ViewportProfile(1280, 800, 1.0, False, False, 1280, 800, 1280, 760, 24, 24, "landscape-primary", 0),
            ViewportProfile(1600, 900, 1.0, False, False, 1600, 900, 1600, 860, 24, 24, "landscape-primary", 0),
        ]
        
        # Common mobile viewport configurations
        self.mobile_viewports = [
            ViewportProfile(375, 667, 2.0, True, True, 375, 667, 375, 627, 32, 32, "portrait-primary", 0),
            ViewportProfile(414, 896, 2.0, True, True, 414, 896, 414, 856, 32, 32, "portrait-primary", 0),
            ViewportProfile(360, 640, 2.5, True, True, 360, 640, 360, 600, 32, 32, "portrait-primary", 0),
            ViewportProfile(414, 736, 3.0, True, True, 414, 736, 414, 696, 32, 32, "portrait-primary", 0),
            ViewportProfile(360, 780, 2.0, True, True, 360, 780, 360, 740, 32, 32, "portrait-primary", 0),
        ]
        
        # Common tablet viewport configurations
        self.tablet_viewports = [
            ViewportProfile(768, 1024, 2.0, True, True, 768, 1024, 768, 1024, 32, 32, "portrait-primary", 0),
            ViewportProfile(834, 1112, 2.0, True, True, 834, 1112, 834, 1112, 32, 32, "portrait-primary", 0),
            ViewportProfile(810, 1080, 2.0, True, True, 810, 1080, 810, 1080, 32, 32, "portrait-primary", 0),
            ViewportProfile(1024, 1366, 2.0, True, True, 1024, 1366, 1024, 1366, 32, 32, "landscape-primary", 90),
        ]
        
        # Device profiles for realistic simulation
        self.device_profiles = [
            DeviceProfile(
                name="MacBook Pro 13\"",
                viewport=ViewportProfile(1280, 800, 2.0, False, False, 1280, 800, 1280, 760, 24, 24, "landscape-primary", 0),
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                platform="MacIntel"
            ),
            DeviceProfile(
                name="MacBook Pro 14\"",
                viewport=ViewportProfile(1512, 982, 2.0, False, False, 1512, 982, 1512, 942, 24, 24, "landscape-primary", 0),
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                platform="MacIntel"
            ),
            DeviceProfile(
                name="MacBook Pro 16\"",
                viewport=ViewportProfile(1728, 1117, 2.0, False, False, 1728, 1117, 1728, 1077, 24, 24, "landscape-primary", 0),
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                platform="MacIntel"
            ),
            DeviceProfile(
                name="Dell XPS 13",
                viewport=ViewportProfile(1280, 720, 1.25, False, False, 1280, 720, 1280, 680, 24, 24, "landscape-primary", 0),
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                platform="Win32"
            ),
            DeviceProfile(
                name="Dell XPS 15",
                viewport=ViewportProfile(1920, 1080, 1.25, False, False, 1920, 1080, 1920, 1040, 24, 24, "landscape-primary", 0),
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                platform="Win32"
            ),
            DeviceProfile(
                name="iPhone 14 Pro",
                viewport=ViewportProfile(393, 852, 3.0, True, True, 393, 852, 393, 812, 32, 32, "portrait-primary", 0),
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                platform="iPhone"
            ),
            DeviceProfile(
                name="iPad Pro 12.9\"",
                viewport=ViewportProfile(1024, 1366, 2.0, True, True, 1024, 1366, 1024, 1366, 32, 32, "portrait-primary", 0),
                user_agent="Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                platform="iPad"
            ),
        ]
    
    def get_random_viewport(self, device_type: str = "desktop") -> ViewportProfile:
        """
        Get a random viewport configuration based on device type.
        
        Args:
            device_type: Type of device ("desktop", "laptop", "mobile", "tablet")
            
        Returns:
            ViewportProfile with realistic properties
        """
        if device_type == "laptop":
            return random.choice(self.laptop_viewports)
        elif device_type == "mobile":
            return random.choice(self.mobile_viewports)
        elif device_type == "tablet":
            return random.choice(self.tablet_viewports)
        else:  # desktop
            return random.choice(self.desktop_viewports)
    
    def get_random_device_profile(self) -> DeviceProfile:
        """
        Get a random device profile with realistic properties.
        
        Returns:
            DeviceProfile with realistic viewport and browser properties
        """
        return random.choice(self.device_profiles)
    
    def generate_realistic_viewport(self) -> ViewportProfile:
        """
        Generate a completely realistic viewport with natural variations.
        
        Returns:
            ViewportProfile with realistic properties
        """
        # Choose device type with realistic distribution
        device_type_weights = [("desktop", 0.6), ("laptop", 0.25), ("mobile", 0.1), ("tablet", 0.05)]
        device_type = random.choices(
            [item[0] for item in device_type_weights],
            weights=[item[1] for item in device_type_weights]
        )[0]
        
        # Get base viewport
        viewport = self.get_random_viewport(device_type)
        
        # Add natural variations
        viewport.width = max(800, min(2560, viewport.width + random.randint(-100, 100)))
        viewport.height = max(600, min(1600, viewport.height + random.randint(-100, 100)))
        
        # Natural device scale factor variations
        if device_type in ["mobile", "tablet"]:
            viewport.device_scale_factor = random.choice([2.0, 2.5, 3.0, 3.5])
        elif device_type == "laptop":
            viewport.device_scale_factor = random.choice([1.0, 1.25, 1.5, 2.0])
        else:  # desktop
            viewport.device_scale_factor = random.choice([1.0, 1.25, 1.5])
        
        # Update screen dimensions to match viewport with realistic variations
        viewport.screen_width = viewport.width + random.randint(0, 200)
        viewport.screen_height = viewport.height + random.randint(0, 200)
        viewport.avail_width = viewport.screen_width - random.randint(0, 50)
        viewport.avail_height = viewport.screen_height - random.randint(0, 50)
        
        # Random orientation for mobile/tablet
        if device_type in ["mobile", "tablet"]:
            if random.random() < 0.7:  # 70% portrait
                viewport.orientation_type = "portrait-primary"
                viewport.orientation_angle = 0
            else:  # 30% landscape
                viewport.orientation_type = "landscape-primary"
                viewport.orientation_angle = 90
        
        self.logger.debug("Generated realistic viewport", device_type=device_type, width=viewport.width, height=viewport.height)
        return viewport
    
    async def apply_viewport_to_context(self, context: BrowserContext, viewport: Optional[ViewportProfile] = None) -> None:
        """
        Apply viewport and screen properties to a browser context.
        
        Args:
            context: Playwright BrowserContext to apply viewport to
            viewport: ViewportProfile to apply, or None to generate a random one
        """
        if viewport is None:
            viewport = self.generate_realistic_viewport()
        
        try:
            # Set viewport size
            await context.set_viewport_size({
                "width": viewport.width,
                "height": viewport.height
            })
            
            # Add JavaScript to spoof screen properties
            await context.add_init_script(f"""
                // Override screen properties
                Object.defineProperty(screen, 'width', {{
                    get: () => {viewport.screen_width}
                }});
                
                Object.defineProperty(screen, 'height', {{
                    get: () => {viewport.screen_height}
                }});
                
                Object.defineProperty(screen, 'availWidth', {{
                    get: () => {viewport.avail_width}
                }});
                
                Object.defineProperty(screen, 'availHeight', {{
                    get: () => {viewport.avail_height}
                }});
                
                Object.defineProperty(screen, 'colorDepth', {{
                    get: () => {viewport.color_depth}
                }});
                
                Object.defineProperty(screen, 'pixelDepth', {{
                    get: () => {viewport.pixel_depth}
                }});
                
                // Override window properties
                Object.defineProperty(window, 'devicePixelRatio', {{
                    get: () => {viewport.device_scale_factor}
                }});
                
                // Override outer dimensions
                Object.defineProperty(window, 'outerWidth', {{
                    get: () => {viewport.screen_width}
                }});
                
                Object.defineProperty(window, 'outerHeight', {{
                    get: () => {viewport.screen_height}
                }});
                
                // Override orientation
                if (window.screen && window.screen.orientation) {{
                    Object.defineProperty(window.screen.orientation, 'type', {{
                        get: () => '{viewport.orientation_type}'
                    }});
                    
                    Object.defineProperty(window.screen.orientation, 'angle', {{
                        get: () => {viewport.orientation_angle}
                    }});
                }}
                
                // Override matchMedia for device-pixel-ratio media queries
                const originalMatchMedia = window.matchMedia;
                window.matchMedia = function(query) {{
                    if (query.includes('device-pixel-ratio')) {{
                        const ratio = {viewport.device_scale_factor};
                        const matches = query.includes(`(${{ratio}})`);
                        return {{
                            matches: matches,
                            media: query,
                            addListener: function() {{}},
                            removeListener: function() {{}}
                        }};
                    }}
                    return originalMatchMedia.apply(this, [query]);
                }};
            """)
            
            self.logger.debug(
                "Applied viewport to context",
                width=viewport.width,
                height=viewport.height,
                device_scale_factor=viewport.device_scale_factor
            )
            
        except Exception as e:
            self.logger.error("Failed to apply viewport to context", error=str(e))
            raise
    
    def get_viewport_dimensions(self, viewport: ViewportProfile) -> Tuple[int, int]:
        """
        Get viewport dimensions as a tuple.
        
        Args:
            viewport: ViewportProfile to get dimensions from
            
        Returns:
            Tuple of (width, height)
        """
        return (viewport.width, viewport.height)
    
    def get_screen_dimensions(self, viewport: ViewportProfile) -> Tuple[int, int]:
        """
        Get screen dimensions as a tuple.
        
        Args:
            viewport: ViewportProfile to get dimensions from
            
        Returns:
            Tuple of (width, height)
        """
        return (viewport.screen_width, viewport.screen_height)
    
    def is_mobile_viewport(self, viewport: ViewportProfile) -> bool:
        """
        Check if viewport is mobile-sized.
        
        Args:
            viewport: ViewportProfile to check
            
        Returns:
            True if viewport is mobile-sized, False otherwise
        """
        # Mobile viewports are typically smaller in both dimensions
        return viewport.width <= 800 and viewport.height <= 1000 and viewport.device_scale_factor >= 2.0
    
    def is_tablet_viewport(self, viewport: ViewportProfile) -> bool:
        """
        Check if viewport is tablet-sized.
        
        Args:
            viewport: ViewportProfile to check
            
        Returns:
            True if viewport is tablet-sized, False otherwise
        """
        # Tablet viewports are typically medium-sized with high device scale factor
        return viewport.width > 800 and viewport.width <= 1200 and viewport.device_scale_factor >= 2.0
    
    def get_device_category(self, viewport: ViewportProfile) -> str:
        """
        Get device category based on viewport properties.
        
        Args:
            viewport: ViewportProfile to categorize
            
        Returns:
            Device category ("mobile", "tablet", "laptop", "desktop")
        """
        if self.is_mobile_viewport(viewport):
            return "mobile"
        elif self.is_tablet_viewport(viewport):
            return "tablet"
        elif viewport.device_scale_factor > 1.5:
            return "laptop"
        else:
            return "desktop"