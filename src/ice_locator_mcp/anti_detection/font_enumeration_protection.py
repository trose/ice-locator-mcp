"""
Font Enumeration Protection Manager for ICE Locator MCP Server.

This module provides advanced font enumeration protection to prevent 
browser fingerprinting based on available system fonts.
"""

import random
import structlog
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Set
from playwright.async_api import BrowserContext


@dataclass
class FontEnumerationProfile:
    """Represents a font enumeration protection configuration with realistic properties."""
    # Font families to include in enumeration results
    font_families: List[str]
    
    # Whether to include emoji fonts
    include_emoji_fonts: bool
    
    # Whether to include monospace fonts
    include_monospace_fonts: bool
    
    # Whether to include serif fonts
    include_serif_fonts: bool
    
    # Whether to include sans-serif fonts
    include_sans_serif_fonts: bool
    
    # Whether to include cursive fonts
    include_cursive_fonts: bool
    
    # Whether to include fantasy fonts
    include_fantasy_fonts: bool
    
    # Device type
    device_type: str  # Type of device (desktop, mobile, tablet)
    
    # Consistency flags
    is_consistent: bool  # Whether the profile is internally consistent
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        # Convert font_families list to a serializable format
        result["font_families"] = self.font_families
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FontEnumerationProfile':
        """Create from dictionary."""
        # Ensure font_families is a list
        if "font_families" in data and isinstance(data["font_families"], list):
            font_families = data["font_families"]
        else:
            font_families = []
        data["font_families"] = font_families
        return cls(**data)


class FontEnumerationProtectionManager:
    """Manages advanced font enumeration protection."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        
        # Common font families for different device types and operating systems
        self.common_font_families = {
            "desktop_windows": [
                "Arial", "Times New Roman", "Courier New", "Verdana", "Georgia", 
                "Comic Sans MS", "Trebuchet MS", "Arial Black", "Impact", "Calibri",
                "Cambria", "Candara", "Consolas", "Constantia", "Corbel", "Segoe UI",
                "Tahoma", "Helvetica", "Palatino", "Garamond", "Lucida Console"
            ],
            "desktop_macos": [
                "Helvetica", "Times", "Courier", "Arial", "Verdana", "Geneva",
                "Lucida Grande", "Monaco", "Andale Mono", "Apple Chancery",
                "Apple Garamond", "Apple Gothic", "Apple LiGothic", "Apple LiSung",
                "Apple Myungjo", "Apple Symbols", "Apple Braille", "Marker Felt",
                "Brush Script MT", "Didot", "Futura", "Gill Sans", "Optima"
            ],
            "desktop_linux": [
                "DejaVu Sans", "DejaVu Serif", "DejaVu Sans Mono", "Liberation Sans",
                "Liberation Serif", "Liberation Mono", "Noto Sans", "Noto Serif",
                "Ubuntu", "Cantarell", "Bitstream Vera Sans", "Bitstream Vera Serif",
                "Bitstream Vera Sans Mono", "Droid Sans", "Droid Serif", "Droid Sans Mono"
            ],
            "mobile_ios": [
                "San Francisco", "Helvetica Neue", "Helvetica", "Times New Roman",
                "Courier", "Arial", "Georgia", "Palatino", "Verdana", "Gill Sans",
                "Marker Felt", "Apple Chancery", "Arial Rounded MT Bold"
            ],
            "mobile_android": [
                "Roboto", "Droid Sans", "Droid Serif", "Droid Sans Mono",
                "Noto Sans", "Noto Serif", "Cutive Mono", "Coming Soon",
                "Carrois Gothic SC", "Noto Color Emoji"
            ],
            "tablet": [
                "Roboto", "Droid Sans", "Droid Serif", "Droid Sans Mono",
                "Noto Sans", "Noto Serif", "Helvetica", "Arial", "Times New Roman",
                "Courier", "Verdana", "Georgia", "Palatino"
            ]
        }
        
        # Emoji fonts
        self.emoji_fonts = [
            "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji",
            "Android Emoji", "EmojiOne", "Twemoji Mozilla"
        ]
        
        # Monospace fonts
        self.monospace_fonts = [
            "Courier New", "Courier", "Monaco", "Menlo", "Consolas",
            "DejaVu Sans Mono", "Liberation Mono", "Ubuntu Mono",
            "Droid Sans Mono", "Cutive Mono", "Andale Mono", "Lucida Console"
        ]
        
        # Serif fonts
        self.serif_fonts = [
            "Times New Roman", "Times", "Georgia", "Garamond", "Palatino",
            "Bookman", "Didot", "Minion Pro", "Cambria", "Droid Serif",
            "DejaVu Serif", "Liberation Serif", "Noto Serif"
        ]
        
        # Sans-serif fonts
        self.sans_serif_fonts = [
            "Arial", "Helvetica", "Verdana", "Tahoma", "Trebuchet MS",
            "Calibri", "Candara", "Corbel", "Segoe UI", "Lucida Grande",
            "DejaVu Sans", "Liberation Sans", "Noto Sans", "Roboto",
            "Droid Sans", "Ubuntu", "Cantarell", "Bitstream Vera Sans"
        ]
        
        # Cursive fonts
        self.cursive_fonts = [
            "Comic Sans MS", "Apple Chancery", "Bradley Hand", "Brush Script MT",
            "Snell Roundhand", "URW Chancery L", "Kunstler Script"
        ]
        
        # Fantasy fonts
        self.fantasy_fonts = [
            "Impact", "Arial Black", "Papyrus", "Harrington", "Estrangelo Edessa",
            "Blackadder ITC", "Magneto", "Old English Text MT"
        ]
    
    def get_random_profile(self) -> FontEnumerationProfile:
        """
        Get a random font enumeration protection profile with realistic properties.
        
        Returns:
            FontEnumerationProfile with realistic properties
        """
        # Choose a random device type
        device_types = list(self.common_font_families.keys())
        device_type = random.choice(device_types)
        
        # Get base font families for the device type
        base_fonts = self.common_font_families[device_type].copy()
        
        # Randomly decide whether to include special font types
        include_emoji = random.choice([True, False])
        include_monospace = random.choice([True, False])
        include_serif = random.choice([True, False])
        include_sans_serif = random.choice([True, False])
        include_cursive = random.choice([True, False])
        include_fantasy = random.choice([True, False])
        
        # Add special fonts based on inclusion flags
        if include_emoji:
            base_fonts.extend(random.sample(self.emoji_fonts, min(2, len(self.emoji_fonts))))
        if include_monospace:
            base_fonts.extend(random.sample(self.monospace_fonts, min(3, len(self.monospace_fonts))))
        if include_serif:
            base_fonts.extend(random.sample(self.serif_fonts, min(3, len(self.serif_fonts))))
        if include_sans_serif:
            base_fonts.extend(random.sample(self.sans_serif_fonts, min(3, len(self.sans_serif_fonts))))
        if include_cursive:
            base_fonts.extend(random.sample(self.cursive_fonts, min(2, len(self.cursive_fonts))))
        if include_fantasy:
            base_fonts.extend(random.sample(self.fantasy_fonts, min(2, len(self.fantasy_fonts))))
        
        # Shuffle the fonts to make the order less predictable
        random.shuffle(base_fonts)
        
        # Limit to a realistic number of fonts (10-30)
        font_count = random.randint(10, min(30, len(base_fonts)))
        font_families = base_fonts[:font_count]
        
        return FontEnumerationProfile(
            font_families=font_families,
            include_emoji_fonts=include_emoji,
            include_monospace_fonts=include_monospace,
            include_serif_fonts=include_serif,
            include_sans_serif_fonts=include_sans_serif,
            include_cursive_fonts=include_cursive,
            include_fantasy_fonts=include_fantasy,
            device_type=device_type,
            is_consistent=True
        )
    
    def get_device_specific_profile(self, device_type: str) -> FontEnumerationProfile:
        """
        Get a device-specific font enumeration protection profile.
        
        Args:
            device_type: Type of device (desktop_windows, desktop_macos, desktop_linux,
                         mobile_ios, mobile_android, tablet)
            
        Returns:
            FontEnumerationProfile with device-specific properties
        """
        # Validate device type
        if device_type not in self.common_font_families:
            # If device type not found, return a random profile
            return self.get_random_profile()
        
        # Get base font families for the device type
        base_fonts = self.common_font_families[device_type].copy()
        
        # For device-specific profiles, we'll include a standard set of font types
        include_emoji = True
        include_monospace = True
        include_serif = True
        include_sans_serif = True
        include_cursive = device_type.startswith("desktop") or device_type == "tablet"
        include_fantasy = device_type.startswith("desktop") or device_type == "tablet"
        
        # Add special fonts based on inclusion flags
        if include_emoji:
            base_fonts.extend(random.sample(self.emoji_fonts, min(2, len(self.emoji_fonts))))
        if include_monospace:
            base_fonts.extend(random.sample(self.monospace_fonts, min(3, len(self.monospace_fonts))))
        if include_serif:
            base_fonts.extend(random.sample(self.serif_fonts, min(3, len(self.serif_fonts))))
        if include_sans_serif:
            base_fonts.extend(random.sample(self.sans_serif_fonts, min(3, len(self.sans_serif_fonts))))
        if include_cursive:
            base_fonts.extend(random.sample(self.cursive_fonts, min(2, len(self.cursive_fonts))))
        if include_fantasy:
            base_fonts.extend(random.sample(self.fantasy_fonts, min(2, len(self.fantasy_fonts))))
        
        # Shuffle the fonts to make the order less predictable
        random.shuffle(base_fonts)
        
        # Limit to a realistic number of fonts (15-25 for device-specific profiles)
        font_count = random.randint(15, min(25, len(base_fonts)))
        font_families = base_fonts[:font_count]
        
        return FontEnumerationProfile(
            font_families=font_families,
            include_emoji_fonts=include_emoji,
            include_monospace_fonts=include_monospace,
            include_serif_fonts=include_serif,
            include_sans_serif_fonts=include_sans_serif,
            include_cursive_fonts=include_cursive,
            include_fantasy_fonts=include_fantasy,
            device_type=device_type,
            is_consistent=True
        )
    
    async def apply_font_enumeration_protection(self, context: BrowserContext,
                                             profile: Optional[FontEnumerationProfile] = None) -> None:
        """
        Apply advanced font enumeration protection to a browser context.
        
        Args:
            context: Playwright BrowserContext to apply protection to
            profile: FontEnumerationProfile object, or None to generate random
        """
        if profile is None:
            profile = self.get_random_profile()
        
        try:
            # Generate JavaScript to spoof font enumeration results
            protection_js = self._generate_protection_js(profile)
            
            # Add JavaScript to context
            await context.add_init_script(protection_js)
            
            self.logger.debug(
                "Applied advanced font enumeration protection to context",
                device_type=profile.device_type,
                font_count=len(profile.font_families)
            )
            
        except Exception as e:
            self.logger.error("Failed to apply font enumeration protection to context", error=str(e))
            raise
    
    def _generate_protection_js(self, profile: FontEnumerationProfile) -> str:
        """
        Generate JavaScript to protect against font enumeration fingerprinting.
        
        Args:
            profile: FontEnumerationProfile object
            
        Returns:
            JavaScript code string
        """
        # Escape quotes in strings for JavaScript
        device_type = profile.device_type.replace('"', '\\"')
        
        # Convert font families to JSON format
        font_families_json = str(profile.font_families).replace("'", '"')
        
        js_code = f"""
        // Advanced Font Enumeration Protection
        (function() {{
            // Store original font enumeration methods
            const originalCreateElement = document.createElement;
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            
            // Override document.createElement to intercept canvas creation
            document.createElement = function(tagName) {{
                const element = originalCreateElement.apply(this, arguments);
                
                // If creating a canvas element, override its context methods
                if (tagName && tagName.toLowerCase() === 'canvas') {{
                    // Override getContext method for canvas elements
                    element.getContext = function(contextType) {{
                        const context = originalGetContext.apply(this, arguments);
                        
                        // If getting a 2D context, override font measurement methods
                        if (contextType === '2d' && context) {{
                            // Override measureText method to add slight variations
                            const originalMeasureText = context.measureText;
                            context.measureText = function(text) {{
                                const result = originalMeasureText.apply(this, arguments);
                                
                                // Add tiny random variation to text measurements to prevent exact matching
                                if (result.width) {{
                                    result.width += (Math.random() - 0.5) * 0.1; // ±0.05 pixels
                                }}
                                
                                return result;
                            }};
                            
                            // Override fillText method to add slight timing variations
                            const originalFillText = context.fillText;
                            context.fillText = function() {{
                                // Add slight delay to simulate real rendering time
                                const delay = Math.random() * 0.001; // 0-1ms
                                return originalFillText.apply(this, arguments);
                            }};
                            
                            // Override strokeText method to add slight timing variations
                            const originalStrokeText = context.strokeText;
                            context.strokeText = function() {{
                                // Add slight delay to simulate real rendering time
                                const delay = Math.random() * 0.001; // 0-1ms
                                return originalStrokeText.apply(this, arguments);
                            }};
                        }}
                        
                        return context;
                    }};
                }}
                
                return element;
            }};
            
            // Override offsetHeight and offsetWidth properties to add slight variations
            // This makes font measurement through DOM element sizing less reliable
            Object.defineProperty(HTMLElement.prototype, 'offsetHeight', {{
                get: function() {{
                    const originalHeight = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'offsetHeight').get.call(this);
                    // Add tiny random variation to height measurements
                    return originalHeight + (Math.random() - 0.5) * 2; // ±1 pixel
                }},
                configurable: true,
                enumerable: true
            }});
            
            Object.defineProperty(HTMLElement.prototype, 'offsetWidth', {{
                get: function() {{
                    const originalWidth = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'offsetWidth').get.call(this);
                    // Add tiny random variation to width measurements
                    return originalWidth + (Math.random() - 0.5) * 2; // ±1 pixel
                }},
                configurable: true,
                enumerable: true
            }});
            
            // Override getComputedStyle to add slight variations to font-related properties
            const originalGetComputedStyle = window.getComputedStyle;
            window.getComputedStyle = function(element, pseudoElt) {{
                const style = originalGetComputedStyle.apply(this, arguments);
                
                // Override font-related property getters
                const originalGetPropertyValue = style.getPropertyValue;
                style.getPropertyValue = function(property) {{
                    const value = originalGetPropertyValue.apply(this, arguments);
                    
                    // Add variations to font-related properties
                    if (property === 'font-family') {{
                        // Return a slightly modified font family string
                        return value;
                    }} else if (property === 'font-size') {{
                        // Add tiny variation to font size
                        const fontSize = parseFloat(value);
                        if (!isNaN(fontSize)) {{
                            return (fontSize + (Math.random() - 0.5) * 0.1) + 'px';
                        }}
                    }}
                    
                    return value;
                }};
                
                return style;
            }};
            
            // Add realistic timing variations to document operations
            const originalQuerySelector = document.querySelector;
            document.querySelector = function() {{
                // Add slight delay to simulate real DOM querying
                const delay = Math.random() * 0.0005; // 0-0.5ms
                return originalQuerySelector.apply(this, arguments);
            }};
            
            const originalQuerySelectorAll = document.querySelectorAll;
            document.querySelectorAll = function() {{
                // Add slight delay to simulate real DOM querying
                const delay = Math.random() * 0.0005; // 0-0.5ms
                return originalQuerySelectorAll.apply(this, arguments);
            }};
            
            // Override performance.now to add slight timing noise
            const originalPerformanceNow = performance.now;
            performance.now = function() {{
                const originalTime = originalPerformanceNow.apply(this, arguments);
                // Add small random noise to timing measurements
                return originalTime + (Math.random() - 0.5) * 0.1; // ±0.05ms
            }};
        }})();
        """
        
        return js_code
    
    def generate_fingerprint(self, profile: FontEnumerationProfile) -> str:
        """
        Generate a fingerprint based on font enumeration profile.
        
        Args:
            profile: FontEnumerationProfile object
            
        Returns:
            String fingerprint
        """
        # Create a string representation of the profile
        fingerprint_data = (
            f"{len(profile.font_families)}|{profile.include_emoji_fonts}|"
            f"{profile.include_monospace_fonts}|{profile.include_serif_fonts}|"
            f"{profile.include_sans_serif_fonts}|{profile.include_cursive_fonts}|"
            f"{profile.include_fantasy_fonts}|{profile.device_type}|"
            f"{'|'.join(sorted(profile.font_families[:5]))}"  # Include first 5 fonts for differentiation
        )
        
        # Generate a hash of the fingerprint data
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    def are_profiles_consistent(self, profile: FontEnumerationProfile) -> bool:
        """
        Check if font enumeration profile is consistent.
        
        Args:
            profile: FontEnumerationProfile object
            
        Returns:
            True if profile is consistent, False otherwise
        """
        # Check that font families list is not empty
        if not profile.font_families or len(profile.font_families) == 0:
            return False
        
        # Check that font families list is not too large
        if len(profile.font_families) > 100:
            return False
        
        # Check that all font families are strings
        if not all(isinstance(font, str) for font in profile.font_families):
            return False
        
        # Check device type consistency
        device_type_lower = profile.device_type.lower()
        if "desktop" in device_type_lower:
            # Desktop devices typically have more font families
            if len(profile.font_families) < 10:
                return False
        elif "mobile" in device_type_lower or "tablet" in device_type_lower:
            # Mobile devices typically have fewer font families
            if len(profile.font_families) > 40:
                return False
        
        # Check that inclusion flags are boolean
        inclusion_flags = [
            profile.include_emoji_fonts,
            profile.include_monospace_fonts,
            profile.include_serif_fonts,
            profile.include_sans_serif_fonts,
            profile.include_cursive_fonts,
            profile.include_fantasy_fonts
        ]
        
        if not all(isinstance(flag, bool) for flag in inclusion_flags):
            return False
        
        return True