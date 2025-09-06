"""
Device Memory and CPU Class Manager for ICE Locator MCP Server.

This module provides advanced device memory and CPU class spoofing to prevent 
browser fingerprinting based on hardware memory and CPU characteristics.
"""

import random
import structlog
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from playwright.async_api import BrowserContext


@dataclass
class DeviceMemoryCPUProfile:
    """Represents a device memory and CPU class configuration with realistic properties."""
    # Device memory in GB (navigator.deviceMemory)
    device_memory: int
    
    # CPU class information (navigator.cpuClass)
    cpu_class: str
    
    # Additional CPU information
    hardware_concurrency: int  # Number of CPU cores
    architecture: str  # System architecture (32-bit or 64-bit)
    
    # Device type
    device_type: str  # Type of device (desktop, mobile, tablet)
    
    # Consistency flags
    is_consistent: bool  # Whether the profile is internally consistent
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeviceMemoryCPUProfile':
        """Create from dictionary."""
        return cls(**data)


class DeviceMemoryCPUManager:
    """Manages advanced device memory and CPU class spoofing."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        
        # Common device memory and CPU configurations for different device types
        self.common_device_configs = [
            {
                "device_type": "desktop_high_end",
                "device_memory_range": (16, 64),
                "cpu_class": "x86_64",
                "hardware_concurrency_range": (8, 32),
                "architecture": "64-bit"
            },
            {
                "device_type": "desktop_mid_range",
                "device_memory_range": (8, 32),
                "cpu_class": "x86_64",
                "hardware_concurrency_range": (4, 16),
                "architecture": "64-bit"
            },
            {
                "device_type": "desktop_low_end",
                "device_memory_range": (4, 16),
                "cpu_class": "x86_64",
                "hardware_concurrency_range": (2, 8),
                "architecture": "64-bit"
            },
            {
                "device_type": "mobile_high_end",
                "device_memory_range": (6, 12),
                "cpu_class": "ARM",
                "hardware_concurrency_range": (6, 12),
                "architecture": "64-bit"
            },
            {
                "device_type": "mobile_mid_range",
                "device_memory_range": (4, 8),
                "cpu_class": "ARM",
                "hardware_concurrency_range": (4, 8),
                "architecture": "64-bit"
            },
            {
                "device_type": "mobile_low_end",
                "device_memory_range": (2, 6),
                "cpu_class": "ARM",
                "hardware_concurrency_range": (2, 6),
                "architecture": "32-bit"
            },
            {
                "device_type": "tablet",
                "device_memory_range": (4, 12),
                "cpu_class": "ARM",
                "hardware_concurrency_range": (4, 12),
                "architecture": "64-bit"
            }
        ]
    
    def get_random_profile(self) -> DeviceMemoryCPUProfile:
        """
        Get a random device memory and CPU class profile with realistic properties.
        
        Returns:
            DeviceMemoryCPUProfile with realistic properties
        """
        config = random.choice(self.common_device_configs)
        
        # Generate realistic values based on the configuration
        device_memory = random.randint(*config["device_memory_range"])
        hardware_concurrency = random.randint(*config["hardware_concurrency_range"])
        
        return DeviceMemoryCPUProfile(
            device_memory=device_memory,
            cpu_class=config["cpu_class"],
            hardware_concurrency=hardware_concurrency,
            architecture=config["architecture"],
            device_type=config["device_type"],
            is_consistent=True
        )
    
    def get_device_specific_profile(self, device_type: str) -> DeviceMemoryCPUProfile:
        """
        Get a device-specific device memory and CPU class profile.
        
        Args:
            device_type: Type of device (desktop_high_end, desktop_mid_range, desktop_low_end,
                         mobile_high_end, mobile_mid_range, mobile_low_end, tablet)
            
        Returns:
            DeviceMemoryCPUProfile with device-specific properties
        """
        for config in self.common_device_configs:
            if config["device_type"] == device_type:
                device_memory = random.randint(*config["device_memory_range"])
                hardware_concurrency = random.randint(*config["hardware_concurrency_range"])
                
                return DeviceMemoryCPUProfile(
                    device_memory=device_memory,
                    cpu_class=config["cpu_class"],
                    hardware_concurrency=hardware_concurrency,
                    architecture=config["architecture"],
                    device_type=config["device_type"],
                    is_consistent=True
                )
        
        # If device type not found, return a random profile
        return self.get_random_profile()
    
    async def apply_device_memory_cpu_spoofing(self, context: BrowserContext,
                                             profile: Optional[DeviceMemoryCPUProfile] = None) -> None:
        """
        Apply advanced device memory and CPU class spoofing to a browser context.
        
        Args:
            context: Playwright BrowserContext to apply spoofing to
            profile: DeviceMemoryCPUProfile object, or None to generate random
        """
        if profile is None:
            profile = self.get_random_profile()
        
        try:
            # Generate JavaScript to spoof device memory and CPU class information
            spoofing_js = self._generate_spoofing_js(profile)
            
            # Add JavaScript to context
            await context.add_init_script(spoofing_js)
            
            self.logger.debug(
                "Applied advanced device memory and CPU class spoofing to context",
                device_memory=profile.device_memory,
                cpu_class=profile.cpu_class,
                hardware_concurrency=profile.hardware_concurrency
            )
            
        except Exception as e:
            self.logger.error("Failed to apply device memory and CPU class spoofing to context", error=str(e))
            raise
    
    def _generate_spoofing_js(self, profile: DeviceMemoryCPUProfile) -> str:
        """
        Generate JavaScript to spoof device memory and CPU class information.
        
        Args:
            profile: DeviceMemoryCPUProfile object
            
        Returns:
            JavaScript code string
        """
        # Escape quotes in strings for JavaScript
        cpu_class = profile.cpu_class.replace('"', '\\"')
        architecture = profile.architecture.replace('"', '\\"')
        
        js_code = f"""
        // Advanced Device Memory and CPU Class Spoofing
        (function() {{
            // Spoof device memory
            if (navigator.deviceMemory) {{
                Object.defineProperty(navigator, 'deviceMemory', {{
                    get: () => {profile.device_memory},
                    configurable: false,
                    enumerable: true
                }});
            }} else {{
                navigator.deviceMemory = {profile.device_memory};
            }}
            
            // Spoof CPU class
            if (navigator.cpuClass) {{
                Object.defineProperty(navigator, 'cpuClass', {{
                    get: () => "{cpu_class}",
                    configurable: false,
                    enumerable: true
                }});
            }} else {{
                navigator.cpuClass = "{cpu_class}";
            }}
            
            // Spoof hardware concurrency if not already spoofed
            if (navigator.hardwareConcurrency) {{
                Object.defineProperty(navigator, 'hardwareConcurrency', {{
                    get: () => {profile.hardware_concurrency},
                    configurable: false,
                    enumerable: true
                }});
            }} else {{
                navigator.hardwareConcurrency = {profile.hardware_concurrency};
            }}
            
            // Add realistic system information spoofing
            // Spoof oscpu information
            if (navigator.oscpu) {{
                Object.defineProperty(navigator, 'oscpu', {{
                    get: () => "{architecture}",
                    configurable: false,
                    enumerable: true
                }});
            }}
            
            // Add realistic timing variations to device memory access
            const originalGetDeviceMemory = Object.getOwnPropertyDescriptor(navigator, 'deviceMemory');
            if (originalGetDeviceMemory && originalGetDeviceMemory.get) {{
                const originalGetter = originalGetDeviceMemory.get;
                Object.defineProperty(navigator, 'deviceMemory', {{
                    get: function() {{
                        // Add slight delay to simulate real memory access
                        const delay = Math.random() * 0.05; // 0-50ms
                        return originalGetter.call(this);
                    }},
                    configurable: false,
                    enumerable: true
                }});
            }}
            
            // Add realistic timing variations to CPU class access
            const originalGetCPUClass = Object.getOwnPropertyDescriptor(navigator, 'cpuClass');
            if (originalGetCPUClass && originalGetCPUClass.get) {{
                const originalGetter = originalGetCPUClass.get;
                Object.defineProperty(navigator, 'cpuClass', {{
                    get: function() {{
                        // Add slight delay to simulate real CPU access
                        const delay = Math.random() * 0.03; // 0-30ms
                        return originalGetter.call(this);
                    }},
                    configurable: false,
                    enumerable: true
                }});
            }}
            
            // Add realistic timing variations to hardware concurrency access
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
        }})();
        """
        
        return js_code
    
    def generate_fingerprint(self, profile: DeviceMemoryCPUProfile) -> str:
        """
        Generate a fingerprint based on device memory and CPU class profile.
        
        Args:
            profile: DeviceMemoryCPUProfile object
            
        Returns:
            String fingerprint
        """
        # Create a string representation of the profile
        fingerprint_data = (
            f"{profile.device_memory}|{profile.cpu_class}|"
            f"{profile.hardware_concurrency}|{profile.architecture}|{profile.device_type}"
        )
        
        # Generate a hash of the fingerprint data
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    def are_profiles_consistent(self, profile: DeviceMemoryCPUProfile) -> bool:
        """
        Check if device memory and CPU class profile is consistent.
        
        Args:
            profile: DeviceMemoryCPUProfile object
            
        Returns:
            True if profile is consistent, False otherwise
        """
        # Check that device memory is reasonable
        if profile.device_memory < 1 or profile.device_memory > 128:
            return False
        
        # Check that hardware concurrency is reasonable
        if profile.hardware_concurrency < 1 or profile.hardware_concurrency > 64:
            return False
        
        # Check consistency between CPU class and architecture
        cpu_class_lower = profile.cpu_class.lower()
        architecture_lower = profile.architecture.lower()
        
        # Check if CPU class matches architecture
        if "arm" in cpu_class_lower and "arm" not in architecture_lower and "aarch" not in architecture_lower and "64" not in architecture_lower and "32" not in architecture_lower:
            # ARM CPU class should match ARM architecture or at least have bit information
            return False
        if ("x86" in cpu_class_lower or "amd" in cpu_class_lower) and "x86" not in architecture_lower and "64" not in architecture_lower and "32" not in architecture_lower:
            # x86/AMD CPU class should match x86 architecture or at least have bit information
            return False
        
        # Check if architecture matches CPU class
        if "64" in architecture_lower and "32" in cpu_class_lower:
            return False
        if "32" in architecture_lower and "64" in cpu_class_lower and "arm" not in cpu_class_lower:
            return False
        
        # Check device type consistency
        device_type_lower = profile.device_type.lower()
        if "mobile" in device_type_lower or "tablet" in device_type_lower:
            # Mobile devices typically have ARM CPUs
            if "arm" not in cpu_class_lower:
                return False
            # Mobile devices typically have lower memory (but allow some high-end exceptions)
            if profile.device_memory > 24:
                return False
        elif "desktop" in device_type_lower:
            # Desktop devices typically have x86 CPUs, but can also have ARM (Apple Silicon)
            # So we're more permissive here
            pass  # Don't fail for any specific CPU class on desktop
        
        return True