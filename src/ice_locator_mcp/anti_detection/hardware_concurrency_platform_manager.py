"""
Hardware Concurrency and Platform Manager for ICE Locator MCP Server.

This module provides advanced hardware concurrency and platform information masking 
to prevent browser fingerprinting based on hardware characteristics and platform details.
"""

import random
import structlog
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from playwright.async_api import BrowserContext


@dataclass
class HardwareConcurrencyPlatformProfile:
    """Represents a hardware concurrency and platform configuration with realistic properties."""
    # Hardware concurrency
    hardware_concurrency: int  # Number of CPU cores (navigator.hardwareConcurrency)
    
    # Platform information
    platform: str  # Operating system platform (navigator.platform)
    os_family: str  # General OS family (Windows, macOS, Linux, etc.)
    architecture: str  # System architecture (32-bit or 64-bit)
    
    # CPU class information
    cpu_class: str  # CPU class information (navigator.cpuClass)
    device_memory: int  # Device memory in GB (navigator.deviceMemory)
    
    # Device type
    device_type: str  # Type of device (desktop, mobile, tablet)
    
    # Consistency flags
    is_consistent: bool  # Whether the profile is internally consistent
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HardwareConcurrencyPlatformProfile':
        """Create from dictionary."""
        return cls(**data)


class HardwareConcurrencyPlatformManager:
    """Manages advanced hardware concurrency and platform information masking."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        
        # Common hardware configurations for different device types
        self.common_device_configs = [
            {
                "device_type": "desktop_windows",
                "hardware_concurrency_range": (2, 16),
                "platform": "Win32",
                "os_family": "Windows",
                "architecture": "64-bit",
                "cpu_class": "x86_64",
                "device_memory_range": (4, 32)
            },
            {
                "device_type": "desktop_macos",
                "hardware_concurrency_range": (2, 16),
                "platform": "MacIntel",
                "os_family": "macOS",
                "architecture": "64-bit",
                "cpu_class": "x86_64",
                "device_memory_range": (4, 32)
            },
            {
                "device_type": "desktop_linux",
                "hardware_concurrency_range": (2, 16),
                "platform": "Linux x86_64",
                "os_family": "Linux",
                "architecture": "64-bit",
                "cpu_class": "x86_64",
                "device_memory_range": (4, 32)
            },
            {
                "device_type": "mobile_android",
                "hardware_concurrency_range": (2, 8),
                "platform": "Linux armv8l",
                "os_family": "Android",
                "architecture": "32-bit",
                "cpu_class": "ARM",
                "device_memory_range": (2, 8)
            },
            {
                "device_type": "mobile_ios",
                "hardware_concurrency_range": (2, 6),
                "platform": "iPhone",
                "os_family": "iOS",
                "architecture": "64-bit",
                "cpu_class": "ARM",
                "device_memory_range": (2, 6)
            },
            {
                "device_type": "tablet",
                "hardware_concurrency_range": (2, 8),
                "platform": "iPad",
                "os_family": "iOS",
                "architecture": "64-bit",
                "cpu_class": "ARM",
                "device_memory_range": (2, 8)
            }
        ]
    
    def get_random_profile(self) -> HardwareConcurrencyPlatformProfile:
        """
        Get a random hardware concurrency and platform profile with realistic properties.
        
        Returns:
            HardwareConcurrencyPlatformProfile with realistic properties
        """
        config = random.choice(self.common_device_configs)
        
        # Generate realistic values based on the configuration
        hardware_concurrency = random.randint(*config["hardware_concurrency_range"])
        device_memory = random.randint(*config["device_memory_range"])
        
        return HardwareConcurrencyPlatformProfile(
            hardware_concurrency=hardware_concurrency,
            platform=config["platform"],
            os_family=config["os_family"],
            architecture=config["architecture"],
            cpu_class=config["cpu_class"],
            device_memory=device_memory,
            device_type=config["device_type"],
            is_consistent=True
        )
    
    def get_device_specific_profile(self, device_type: str) -> HardwareConcurrencyPlatformProfile:
        """
        Get a device-specific hardware concurrency and platform profile.
        
        Args:
            device_type: Type of device (desktop_windows, desktop_macos, desktop_linux, 
                         mobile_android, mobile_ios, tablet)
            
        Returns:
            HardwareConcurrencyPlatformProfile with device-specific properties
        """
        for config in self.common_device_configs:
            if config["device_type"] == device_type:
                hardware_concurrency = random.randint(*config["hardware_concurrency_range"])
                device_memory = random.randint(*config["device_memory_range"])
                
                return HardwareConcurrencyPlatformProfile(
                    hardware_concurrency=hardware_concurrency,
                    platform=config["platform"],
                    os_family=config["os_family"],
                    architecture=config["architecture"],
                    cpu_class=config["cpu_class"],
                    device_memory=device_memory,
                    device_type=config["device_type"],
                    is_consistent=True
                )
        
        # If device type not found, return a random profile
        return self.get_random_profile()
    
    async def apply_hardware_concurrency_platform_masking(self, context: BrowserContext,
                                                        profile: Optional[HardwareConcurrencyPlatformProfile] = None) -> None:
        """
        Apply advanced hardware concurrency and platform information masking to a browser context.
        
        Args:
            context: Playwright BrowserContext to apply masking to
            profile: HardwareConcurrencyPlatformProfile object, or None to generate random
        """
        if profile is None:
            profile = self.get_random_profile()
        
        try:
            # Generate JavaScript to mask hardware concurrency and platform information
            masking_js = self._generate_masking_js(profile)
            
            # Add JavaScript to context
            await context.add_init_script(masking_js)
            
            self.logger.debug(
                "Applied advanced hardware concurrency and platform masking to context",
                hardware_concurrency=profile.hardware_concurrency,
                platform=profile.platform,
                device_memory=profile.device_memory
            )
            
        except Exception as e:
            self.logger.error("Failed to apply hardware concurrency and platform masking to context", error=str(e))
            raise
    
    def _generate_masking_js(self, profile: HardwareConcurrencyPlatformProfile) -> str:
        """
        Generate JavaScript to mask hardware concurrency and platform information.
        
        Args:
            profile: HardwareConcurrencyPlatformProfile object
            
        Returns:
            JavaScript code string
        """
        # Escape quotes in strings for JavaScript
        platform = profile.platform.replace('"', '\\"')
        cpu_class = profile.cpu_class.replace('"', '\\"')
        os_family = profile.os_family.replace('"', '\\"')
        architecture = profile.architecture.replace('"', '\\"')
        
        js_code = f"""
        // Advanced Hardware Concurrency and Platform Information Masking
        (function() {{
            // Mask hardware concurrency
            if (navigator.hardwareConcurrency) {{
                Object.defineProperty(navigator, 'hardwareConcurrency', {{
                    get: () => {profile.hardware_concurrency},
                    configurable: false,
                    enumerable: true
                }});
            }} else {{
                navigator.hardwareConcurrency = {profile.hardware_concurrency};
            }}
            
            // Mask platform information
            Object.defineProperty(navigator, 'platform', {{
                get: () => "{platform}",
                configurable: false,
                enumerable: true
            }});
            
            // Mask CPU class
            if (navigator.cpuClass) {{
                Object.defineProperty(navigator, 'cpuClass', {{
                    get: () => "{cpu_class}",
                    configurable: false,
                    enumerable: true
                }});
            }} else {{
                navigator.cpuClass = "{cpu_class}";
            }}
            
            // Mask device memory
            if (navigator.deviceMemory) {{
                Object.defineProperty(navigator, 'deviceMemory', {{
                    get: () => {profile.device_memory},
                    configurable: false,
                    enumerable: true
                }});
            }} else {{
                navigator.deviceMemory = {profile.device_memory};
            }}
            
            // Add realistic system information spoofing
            // Mask os family information in various places
            if (navigator.oscpu) {{
                Object.defineProperty(navigator, 'oscpu', {{
                    get: () => "{os_family} {architecture}",
                    configurable: false,
                    enumerable: true
                }});
            }}
            
            // Mask build identifier
            if (navigator.buildID) {{
                Object.defineProperty(navigator, 'buildID', {{
                    get: () => "20181001000000",
                    configurable: false,
                    enumerable: true
                }});
            }}
            
            // Add realistic timing variations to hardware information access
            const originalGetHardwareConcurrency = Object.getOwnPropertyDescriptor(navigator, 'hardwareConcurrency');
            if (originalGetHardwareConcurrency && originalGetHardwareConcurrency.get) {{
                const originalGetter = originalGetHardwareConcurrency.get;
                Object.defineProperty(navigator, 'hardwareConcurrency', {{
                    get: function() {{
                        // Add slight delay to simulate real hardware access
                        const delay = Math.random() * 0.1; // 0-100ms
                        return originalGetter.call(this);
                    }},
                    configurable: false,
                    enumerable: true
                }});
            }}
            
            // Add realistic timing variations to platform information access
            const originalGetPlatform = Object.getOwnPropertyDescriptor(navigator, 'platform');
            if (originalGetPlatform && originalGetPlatform.get) {{
                const originalGetter = originalGetPlatform.get;
                Object.defineProperty(navigator, 'platform', {{
                    get: function() {{
                        // Add slight delay to simulate real platform access
                        const delay = Math.random() * 0.05; // 0-50ms
                        return originalGetter.call(this);
                    }},
                    configurable: false,
                    enumerable: true
                }});
            }}
            
            // Mask product information
            Object.defineProperty(navigator, 'product', {{
                get: () => "Gecko",
                configurable: false,
                enumerable: true
            }});
            
            Object.defineProperty(navigator, 'productSub', {{
                get: () => "20030107",
                configurable: false,
                enumerable: true
            }});
            
            // Mask app version information
            Object.defineProperty(navigator, 'appVersion', {{
                get: function() {{
                    const original = navigator.userAgent;
                    // Extract version from user agent in a realistic way
                    const match = original.match(/(?:Chrome|Safari|Firefox)\\/([\\d.]+)/);
                    if (match) {{
                        return match[1];
                    }}
                    return "5.0";
                }},
                configurable: false,
                enumerable: true
            }});
        }})();
        """
        
        return js_code
    
    def generate_fingerprint(self, profile: HardwareConcurrencyPlatformProfile) -> str:
        """
        Generate a fingerprint based on hardware concurrency and platform profile.
        
        Args:
            profile: HardwareConcurrencyPlatformProfile object
            
        Returns:
            String fingerprint
        """
        # Create a string representation of the profile
        fingerprint_data = (
            f"{profile.hardware_concurrency}|{profile.platform}|"
            f"{profile.cpu_class}|{profile.device_memory}|{profile.os_family}|"
            f"{profile.architecture}|{profile.device_type}"
        )
        
        # Generate a hash of the fingerprint data
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    def are_profiles_consistent(self, profile: HardwareConcurrencyPlatformProfile) -> bool:
        """
        Check if hardware concurrency and platform profile is consistent.
        
        Args:
            profile: HardwareConcurrencyPlatformProfile object
            
        Returns:
            True if profile is consistent, False otherwise
        """
        # Check that hardware concurrency is reasonable
        if profile.hardware_concurrency < 1 or profile.hardware_concurrency > 64:
            return False
        
        # Check that device memory is reasonable
        if profile.device_memory < 1 or profile.device_memory > 128:
            return False
        
        # Check consistency between platform and other properties
        platform_lower = profile.platform.lower()
        os_family_lower = profile.os_family.lower()
        
        # Check if platform matches OS family
        if "win" in platform_lower and "windows" not in os_family_lower:
            return False
        if ("mac" in platform_lower or "intel" in platform_lower) and "macos" not in os_family_lower:
            return False
        if "linux" in platform_lower and "linux" not in os_family_lower and "android" not in os_family_lower:
            return False
        if "iphone" in platform_lower and "ios" not in os_family_lower:
            return False
        if "ipad" in platform_lower and "ios" not in os_family_lower:
            return False
        if "android" in platform_lower and "android" not in os_family_lower:
            return False
        
        # Check if architecture matches platform
        if "64" in profile.architecture and "32" in platform_lower and "arm" not in platform_lower:
            return False
        if "32" in profile.architecture and "64" in platform_lower and "64" in profile.platform and "arm" not in platform_lower:
            return False
        
        return True
