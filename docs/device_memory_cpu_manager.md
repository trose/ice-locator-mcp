# Device Memory and CPU Class Manager Documentation

## Overview

The DeviceMemoryCPUManager module provides advanced device memory and CPU class spoofing to prevent browser fingerprinting based on hardware memory and CPU characteristics. It implements realistic device memory configurations, CPU class spoofing, and other techniques to avoid detection while maintaining realistic browser behavior.

## Key Features

- Advanced device memory spoofing (navigator.deviceMemory)
- CPU class spoofing (navigator.cpuClass)
- Hardware concurrency spoofing (navigator.hardwareConcurrency)
- Device-specific profile generation
- Consistency validation
- Integration with Playwright browser contexts

## Installation

The DeviceMemoryCPUManager is part of the ICE Locator MCP Server and requires no additional installation steps.

## Usage

### Basic Usage

```python
from ice_locator_mcp.anti_detection.device_memory_cpu_manager import DeviceMemoryCPUManager

# Create a DeviceMemoryCPUManager instance
device_manager = DeviceMemoryCPUManager()

# Generate a random device memory and CPU class profile
profile = device_manager.get_random_profile()

# Generate device-specific profiles
high_end_profile = device_manager.get_device_specific_profile("desktop_high_end")
mobile_profile = device_manager.get_device_specific_profile("mobile_low_end")
```

### Applying Device Memory and CPU Class Spoofing to Browser Context

```python
import asyncio
from playwright.async_api import async_playwright
from ice_locator_mcp.anti_detection.device_memory_cpu_manager import DeviceMemoryCPUManager

async def example():
    device_manager = DeviceMemoryCPUManager()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        
        # Apply device memory and CPU class spoofing to the context
        await device_manager.apply_device_memory_cpu_spoofing(context)
        
        # Or apply a specific profile
        profile = device_manager.get_device_specific_profile("desktop_high_end")
        await device_manager.apply_device_memory_cpu_spoofing(context, profile)
        
        page = await context.new_page()
        await page.goto("https://example.com")
        
        await browser.close()

# Run the example
asyncio.run(example())
```

## API Reference

### DeviceMemoryCPUManager Class

#### `__init__()`
Initializes the DeviceMemoryCPUManager with predefined device configurations.

#### `get_random_profile() -> DeviceMemoryCPUProfile`
Get a random device memory and CPU class profile with realistic properties.

**Returns:**
- `DeviceMemoryCPUProfile`: Profile with realistic properties

#### `get_device_specific_profile(device_type: str) -> DeviceMemoryCPUProfile`
Get a device-specific device memory and CPU class profile.

**Parameters:**
- `device_type` (str): Type of device (desktop_high_end, desktop_mid_range, desktop_low_end, mobile_high_end, mobile_mid_range, mobile_low_end, tablet)

**Returns:**
- `DeviceMemoryCPUProfile`: Profile with device-specific properties

#### `apply_device_memory_cpu_spoofing(context: BrowserContext, profile: Optional[DeviceMemoryCPUProfile] = None) -> None`
Apply advanced device memory and CPU class spoofing to a browser context.

**Parameters:**
- `context` (BrowserContext): Playwright BrowserContext to apply spoofing to
- `profile` (Optional[DeviceMemoryCPUProfile]): Profile to apply, or None to generate a random one

#### `generate_fingerprint(profile: DeviceMemoryCPUProfile) -> str`
Generate a fingerprint hash from a device memory and CPU class profile.

**Parameters:**
- `profile` (DeviceMemoryCPUProfile): Profile to generate fingerprint from

**Returns:**
- `str`: Fingerprint hash

#### `are_profiles_consistent(profile: DeviceMemoryCPUProfile) -> bool`
Check if a device memory and CPU class profile is consistent.

**Parameters:**
- `profile` (DeviceMemoryCPUProfile): Profile to check

**Returns:**
- `bool`: True if profile is consistent, False otherwise

#### `_generate_spoofing_js(profile: DeviceMemoryCPUProfile) -> str`
Generate JavaScript code for device memory and CPU class spoofing (internal method).

**Parameters:**
- `profile` (DeviceMemoryCPUProfile): Profile to generate JavaScript from

**Returns:**
- `str`: JavaScript code string

### DeviceMemoryCPUProfile Dataclass

Represents a device memory and CPU class configuration with realistic properties.

**Attributes:**
- `device_memory` (int): Device memory in GB (navigator.deviceMemory)
- `cpu_class` (str): CPU class information (navigator.cpuClass)
- `hardware_concurrency` (int): Number of CPU cores (navigator.hardwareConcurrency)
- `architecture` (str): System architecture (32-bit or 64-bit)
- `device_type` (str): Type of device (desktop, mobile, tablet)
- `is_consistent` (bool): Whether the profile is internally consistent

## Device Memory Spoofing

### Navigator Properties Spoofed
- `navigator.deviceMemory`: Device memory in GB
- `navigator.cpuClass`: CPU class information
- `navigator.hardwareConcurrency`: Number of CPU cores
- `navigator.oscpu`: OS and CPU information

### Device-Specific Configurations

The DeviceMemoryCPUManager includes predefined configurations for different device types:

#### Desktop High-end
- Device Memory: 16-64 GB
- CPU Class: x86_64
- Architecture: 64-bit
- Hardware Concurrency: 8-32 cores

#### Desktop Mid-range
- Device Memory: 8-32 GB
- CPU Class: x86_64
- Architecture: 64-bit
- Hardware Concurrency: 4-16 cores

#### Desktop Low-end
- Device Memory: 4-16 GB
- CPU Class: x86_64
- Architecture: 64-bit
- Hardware Concurrency: 2-8 cores

#### Mobile High-end
- Device Memory: 6-12 GB
- CPU Class: ARM
- Architecture: 64-bit
- Hardware Concurrency: 6-12 cores

#### Mobile Mid-range
- Device Memory: 4-8 GB
- CPU Class: ARM
- Architecture: 64-bit
- Hardware Concurrency: 4-8 cores

#### Mobile Low-end
- Device Memory: 2-6 GB
- CPU Class: ARM
- Architecture: 32-bit
- Hardware Concurrency: 2-6 cores

#### Tablet
- Device Memory: 4-12 GB
- CPU Class: ARM
- Architecture: 64-bit
- Hardware Concurrency: 4-12 cores

## Technical Implementation

### JavaScript Injection
The manager injects JavaScript code that overrides browser properties to spoof device memory and CPU class information. The injected code:

1. Defines property getters for device memory and CPU-related navigator properties
2. Ensures consistent values across different access methods
3. Adds realistic timing delays to simulate real hardware access
4. Maintains compatibility with legitimate website functionality

### Realistic Value Generation
- Device-appropriate memory ranges
- CPU class matching device type
- Consistent hardware concurrency values
- Architecture matching CPU class

### Profile Management
- Random profile generation with realistic value distributions
- Device-specific profile selection
- Profile serialization and deserialization
- Fingerprint generation for tracking

## Integration with Browser Simulator

The DeviceMemoryCPUManager integrates seamlessly with the BrowserSimulator to provide realistic device memory and CPU class spoofing:

```python
from ice_locator_mcp.anti_detection.browser_simulator import BrowserSimulator
from ice_locator_mcp.anti_detection.device_memory_cpu_manager import DeviceMemoryCPUManager
from ice_locator_mcp.core.config import SearchConfig

# Create browser simulator
config = SearchConfig()
browser_sim = BrowserSimulator(config)
device_manager = DeviceMemoryCPUManager()

# The DeviceMemoryCPUManager can be used alongside other protection managers
# to create comprehensive anti-fingerprinting protection
```

## Best Practices

1. **Use device-specific profiles**: Choose profiles that match the target device type
2. **Vary profiles**: Use different profiles to avoid detection patterns
3. **Apply early**: Apply spoofing to contexts before creating pages
4. **Check consistency**: Verify that profiles are consistent and realistic
5. **Update regularly**: Change profiles periodically to avoid fingerprinting

## Testing

The DeviceMemoryCPUManager includes comprehensive tests to ensure functionality:

```bash
python -m pytest tests/test_device_memory_cpu_manager.py -v
```

## Contributing

Contributions to improve device memory and CPU class spoofing techniques or add new device configurations are welcome. Please ensure all tests pass before submitting pull requests.

## License

This module is part of the ICE Locator MCP Server and is licensed under the project's license.