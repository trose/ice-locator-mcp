# Hardware Concurrency and Platform Manager Documentation

## Overview

The HardwareConcurrencyPlatformManager module provides advanced hardware concurrency and platform information masking to prevent browser fingerprinting based on hardware characteristics and platform details. It implements realistic hardware configurations, platform spoofing, and other techniques to avoid detection while maintaining realistic browser behavior.

## Key Features

- Advanced hardware concurrency spoofing (navigator.hardwareConcurrency)
- Platform information masking (navigator.platform)
- CPU class spoofing (navigator.cpuClass)
- Device memory spoofing (navigator.deviceMemory)
- Device-specific profile generation
- Consistency validation
- Integration with Playwright browser contexts

## Installation

The HardwareConcurrencyPlatformManager is part of the ICE Locator MCP Server and requires no additional installation steps.

## Usage

### Basic Usage

```python
from ice_locator_mcp.anti_detection.hardware_concurrency_platform_manager import HardwareConcurrencyPlatformManager

# Create a HardwareConcurrencyPlatformManager instance
hardware_manager = HardwareConcurrencyPlatformManager()

# Generate a random hardware concurrency and platform profile
profile = hardware_manager.get_random_profile()

# Generate device-specific profiles
win_profile = hardware_manager.get_device_specific_profile("desktop_windows")
mac_profile = hardware_manager.get_device_specific_profile("desktop_macos")
android_profile = hardware_manager.get_device_specific_profile("mobile_android")
```

### Applying Hardware Concurrency and Platform Masking to Browser Context

```python
import asyncio
from playwright.async_api import async_playwright
from ice_locator_mcp.anti_detection.hardware_concurrency_platform_manager import HardwareConcurrencyPlatformManager

async def example():
    hardware_manager = HardwareConcurrencyPlatformManager()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        
        # Apply hardware concurrency and platform masking to the context
        await hardware_manager.apply_hardware_concurrency_platform_masking(context)
        
        # Or apply a specific profile
        profile = hardware_manager.get_device_specific_profile("desktop_windows")
        await hardware_manager.apply_hardware_concurrency_platform_masking(context, profile)
        
        page = await context.new_page()
        await page.goto("https://example.com")
        
        await browser.close()

# Run the example
asyncio.run(example())
```

## API Reference

### HardwareConcurrencyPlatformManager Class

#### `__init__()`
Initializes the HardwareConcurrencyPlatformManager with predefined hardware configurations.

#### `get_random_profile() -> HardwareConcurrencyPlatformProfile`
Get a random hardware concurrency and platform profile with realistic properties.

**Returns:**
- `HardwareConcurrencyPlatformProfile`: Profile with realistic properties

#### `get_device_specific_profile(device_type: str) -> HardwareConcurrencyPlatformProfile`
Get a device-specific hardware concurrency and platform profile.

**Parameters:**
- `device_type` (str): Type of device (desktop_windows, desktop_macos, desktop_linux, mobile_android, mobile_ios, tablet)

**Returns:**
- `HardwareConcurrencyPlatformProfile`: Profile with device-specific properties

#### `apply_hardware_concurrency_platform_masking(context: BrowserContext, profile: Optional[HardwareConcurrencyPlatformProfile] = None) -> None`
Apply advanced hardware concurrency and platform information masking to a browser context.

**Parameters:**
- `context` (BrowserContext): Playwright BrowserContext to apply masking to
- `profile` (Optional[HardwareConcurrencyPlatformProfile]): Profile to apply, or None to generate a random one

#### `generate_fingerprint(profile: HardwareConcurrencyPlatformProfile) -> str`
Generate a fingerprint hash from a hardware concurrency and platform profile.

**Parameters:**
- `profile` (HardwareConcurrencyPlatformProfile): Profile to generate fingerprint from

**Returns:**
- `str`: Fingerprint hash

#### `are_profiles_consistent(profile: HardwareConcurrencyPlatformProfile) -> bool`
Check if a hardware concurrency and platform profile is consistent.

**Parameters:**
- `profile` (HardwareConcurrencyPlatformProfile): Profile to check

**Returns:**
- `bool`: True if profile is consistent, False otherwise

#### `_generate_masking_js(profile: HardwareConcurrencyPlatformProfile) -> str`
Generate JavaScript code for hardware concurrency and platform masking (internal method).

**Parameters:**
- `profile` (HardwareConcurrencyPlatformProfile): Profile to generate JavaScript from

**Returns:**
- `str`: JavaScript code string

### HardwareConcurrencyPlatformProfile Dataclass

Represents a hardware concurrency and platform configuration with realistic properties.

**Attributes:**
- `hardware_concurrency` (int): Number of CPU cores (navigator.hardwareConcurrency)
- `platform` (str): Operating system platform (navigator.platform)
- `os_family` (str): General OS family (Windows, macOS, Linux, etc.)
- `architecture` (str): System architecture (32-bit or 64-bit)
- `cpu_class` (str): CPU class information (navigator.cpuClass)
- `device_memory` (int): Device memory in GB (navigator.deviceMemory)
- `device_type` (str): Type of device (desktop, mobile, tablet)
- `is_consistent` (bool): Whether the profile is internally consistent

## Hardware Concurrency Masking

### Navigator Properties Masked
- `navigator.hardwareConcurrency`: Number of CPU cores
- `navigator.platform`: Operating system platform
- `navigator.cpuClass`: CPU class information
- `navigator.deviceMemory`: Device memory in GB
- `navigator.oscpu`: OS and CPU information
- `navigator.buildID`: Browser build identifier
- `navigator.product`: Browser product name
- `navigator.productSub`: Browser product sub-version
- `navigator.appVersion`: Browser application version

### Device-Specific Configurations

The HardwareConcurrencyPlatformManager includes predefined configurations for different device types:

#### Desktop Windows
- Platform: Win32
- OS Family: Windows
- Architecture: 64-bit
- CPU Class: x86_64
- Hardware Concurrency: 2-16 cores
- Device Memory: 4-32 GB

#### Desktop macOS
- Platform: MacIntel
- OS Family: macOS
- Architecture: 64-bit
- CPU Class: x86_64
- Hardware Concurrency: 2-16 cores
- Device Memory: 4-32 GB

#### Desktop Linux
- Platform: Linux x86_64
- OS Family: Linux
- Architecture: 64-bit
- CPU Class: x86_64
- Hardware Concurrency: 2-16 cores
- Device Memory: 4-32 GB

#### Mobile Android
- Platform: Linux armv8l
- OS Family: Android
- Architecture: 32-bit
- CPU Class: ARM
- Hardware Concurrency: 2-8 cores
- Device Memory: 2-8 GB

#### Mobile iOS
- Platform: iPhone
- OS Family: iOS
- Architecture: 64-bit
- CPU Class: ARM
- Hardware Concurrency: 2-6 cores
- Device Memory: 2-6 GB

#### Tablet
- Platform: iPad
- OS Family: iOS
- Architecture: 64-bit
- CPU Class: ARM
- Hardware Concurrency: 2-8 cores
- Device Memory: 2-8 GB

## Technical Implementation

### JavaScript Injection
The manager injects JavaScript code that overrides browser properties to mask hardware and platform information. The injected code:

1. Defines property getters for hardware-related navigator properties
2. Ensures consistent values across different access methods
3. Adds realistic timing delays to simulate real hardware access
4. Maintains compatibility with legitimate website functionality

### Consistency Validation
Profiles are validated for internal consistency to ensure realistic combinations of properties:

- Hardware concurrency values are within reasonable ranges
- Platform information matches OS family
- Architecture is consistent with platform
- Device memory values are realistic

### Profile Management
- Random profile generation with realistic value distributions
- Device-specific profile selection
- Profile serialization and deserialization
- Fingerprint generation for tracking

## Integration with Browser Simulator

The HardwareConcurrencyPlatformManager integrates seamlessly with the BrowserSimulator to provide realistic hardware and platform masking:

```python
from ice_locator_mcp.anti_detection.browser_simulator import BrowserSimulator
from ice_locator_mcp.anti_detection.hardware_concurrency_platform_manager import HardwareConcurrencyPlatformManager
from ice_locator_mcp.core.config import SearchConfig

# Create browser simulator
config = SearchConfig()
browser_sim = BrowserSimulator(config)
hardware_manager = HardwareConcurrencyPlatformManager()

# The HardwareConcurrencyPlatformManager can be used alongside other protection managers
# to create comprehensive anti-fingerprinting protection
```

## Best Practices

1. **Use device-specific profiles**: Choose profiles that match the target device type
2. **Vary profiles**: Use different profiles to avoid detection patterns
3. **Apply early**: Apply masking to contexts before creating pages
4. **Check consistency**: Verify that profiles are consistent and realistic
5. **Update regularly**: Change profiles periodically to avoid fingerprinting

## Testing

The HardwareConcurrencyPlatformManager includes comprehensive tests to ensure functionality:

```bash
python -m pytest tests/test_hardware_concurrency_platform_manager.py -v
```

## Contributing

Contributions to improve hardware concurrency and platform masking techniques or add new device configurations are welcome. Please ensure all tests pass before submitting pull requests.

## License

This module is part of the ICE Locator MCP Server and is licensed under the project's license.