# Plugin and Extension Fingerprinting Protection Manager

## Overview

The PluginFingerprintingProtectionManager provides advanced plugin and extension fingerprinting protection to prevent browser fingerprinting based on installed plugins and extensions. It implements realistic spoofing of plugin lists, extension information, and related browser APIs.

## Features

- Realistic plugin list spoofing
- Extension information spoofing with realistic properties
- Device-specific plugin and extension configurations
- Consistency validation for plugin profiles
- Unique fingerprint generation
- JavaScript code generation for browser context spoofing

## Installation

The PluginFingerprintingProtectionManager is part of the ICE Locator MCP Server and requires no additional installation.

## Usage

### Basic Usage

```python
from ice_locator_mcp.anti_detection.plugin_fingerprinting_protection import PluginFingerprintingProtectionManager

# Create manager instance
plugin_manager = PluginFingerprintingProtectionManager()

# Generate a random plugin and extension profile
profile = plugin_manager.get_random_profile()

# Apply spoofing to a browser context
await plugin_manager.apply_plugin_fingerprinting_protection(context, profile)
```

### Device-Specific Profiles

```python
# Generate device-specific profiles
desktop_profile = plugin_manager.get_device_specific_profile("desktop")
mobile_profile = plugin_manager.get_device_specific_profile("mobile")
tablet_profile = plugin_manager.get_device_specific_profile("tablet")
```

### Custom Profiles

```python
from ice_locator_mcp.anti_detection.plugin_fingerprinting_protection import PluginFingerprintingProfile, PluginProfile, ExtensionProfile

# Create custom plugins
plugins = [
    PluginProfile(
        name="Custom Plugin",
        filename="custom-plugin.dll",
        description="A custom plugin"
    )
]

# Create custom extensions
extensions = [
    ExtensionProfile(
        id="custom-extension-id",
        name="Custom Extension",
        version="1.0.0",
        description="A custom extension",
        permissions=["storage"],
        enabled=True
    )
]

# Create a custom profile
custom_profile = PluginFingerprintingProfile(
    plugins=plugins,
    extensions=extensions,
    device_type="desktop",
    is_consistent=True
)
```

## API Reference

### PluginFingerprintingProtectionManager Class

#### `get_random_profile() -> PluginFingerprintingProfile`
Generate a random plugin and extension fingerprinting profile with realistic properties.

**Returns:**
- `PluginFingerprintingProfile`: PluginFingerprintingProfile with realistic properties

#### `get_device_specific_profile(device_type: str) -> PluginFingerprintingProfile`
Get a device-specific plugin and extension fingerprinting profile.

**Parameters:**
- `device_type` (str): Type of device (desktop, mobile, tablet)

**Returns:**
- `PluginFingerprintingProfile`: PluginFingerprintingProfile with device-specific properties

#### `apply_plugin_fingerprinting_protection(context: BrowserContext, profile: Optional[PluginFingerprintingProfile] = None) -> None`
Apply advanced plugin and extension fingerprinting protection to a browser context.

**Parameters:**
- `context` (BrowserContext): Playwright BrowserContext to apply protection to
- `profile` (Optional[PluginFingerprintingProfile]): PluginFingerprintingProfile object, or None to generate random

#### `generate_fingerprint(profile: PluginFingerprintingProfile) -> str`
Generate a fingerprint based on plugin and extension profile.

**Parameters:**
- `profile` (PluginFingerprintingProfile): PluginFingerprintingProfile object

**Returns:**
- `str`: Plugin fingerprint hash

#### `are_profiles_consistent(profile: PluginFingerprintingProfile) -> bool`
Check if plugin and extension profile is consistent.

**Parameters:**
- `profile` (PluginFingerprintingProfile): PluginFingerprintingProfile object

**Returns:**
- `bool`: True if profile is consistent, False otherwise

#### `_generate_spoofing_js(profile: PluginFingerprintingProfile) -> str`
Generate JavaScript to spoof plugin and extension information.

**Parameters:**
- `profile` (PluginFingerprintingProfile): PluginFingerprintingProfile object

**Returns:**
- `str`: JavaScript code string

### Data Classes

#### PluginProfile
Represents a browser plugin with realistic properties.

**Attributes:**
- `name` (str): Plugin name
- `filename` (str): Plugin filename
- `description` (str): Plugin description

#### ExtensionProfile
Represents a browser extension with realistic properties.

**Attributes:**
- `id` (str): Extension ID
- `name` (str): Extension name
- `version` (str): Extension version
- `description` (str): Extension description
- `permissions` (List[str]): Extension permissions
- `enabled` (bool): Whether the extension is enabled

#### PluginFingerprintingProfile
Represents a plugin and extension fingerprinting configuration with realistic properties.

**Attributes:**
- `plugins` (List[PluginProfile]): List of plugins
- `extensions` (List[ExtensionProfile]): List of extensions
- `device_type` (str): Type of device (desktop, mobile, tablet)
- `is_consistent` (bool): Whether the profile is internally consistent

## Device Configurations

The PluginFingerprintingProtectionManager includes predefined configurations for:

### Desktop Devices
- 3-6 plugins with realistic properties
- 5-10 extensions with realistic properties

### Mobile Devices
- 1-3 plugins (typically PDF-related)
- 2-5 extensions (typically Google services)

### Tablet Devices
- 2-4 plugins with realistic properties
- 3-7 extensions with realistic properties

## Integration with Browser Simulator

The PluginFingerprintingProtectionManager integrates seamlessly with the BrowserSimulator to provide realistic plugin and extension spoofing:

```python
from ice_locator_mcp.anti_detection.browser_simulator import BrowserSimulator
from ice_locator_mcp.anti_detection.plugin_fingerprinting_protection import PluginFingerprintingProtectionManager
from ice_locator_mcp.core.config import SearchConfig

# Create browser simulator
config = SearchConfig()
browser_sim = BrowserSimulator(config)
plugin_manager = PluginFingerprintingProtectionManager()

# The PluginFingerprintingProtectionManager can be used to create realistic 
# plugin and extension configurations for each session
```

## Best Practices

1. **Use realistic profiles**: Choose plugin and extension profiles that match real devices
2. **Vary profiles**: Use different profiles to avoid detection patterns
3. **Apply early**: Apply plugin spoofing to contexts before creating pages
4. **Check consistency**: Verify that profiles are consistent and realistic
5. **Update regularly**: Change plugin and extension profiles periodically to avoid fingerprinting

## Testing

The PluginFingerprintingProtectionManager includes comprehensive tests to ensure functionality:

```bash
python -m pytest tests/test_plugin_fingerprinting_protection.py -v
```

## Contributing

Contributions to improve plugin and extension fingerprinting protection or add new simulation techniques are welcome. Please ensure all tests pass before submitting pull requests.

## License

This module is part of the ICE Locator MCP Server and is licensed under the project's license.