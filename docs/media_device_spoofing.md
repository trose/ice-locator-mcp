# Media Device Spoofing Manager

## Overview

The MediaDeviceSpoofingManager provides advanced media device spoofing to prevent enumeration-based fingerprinting. It implements realistic spoofing of audio and video device information, preventing websites from accessing real media devices while maintaining realistic API behavior.

## Features

- Realistic media device enumeration spoofing
- Device-specific media device configurations
- Consistency validation for media device profiles
- Unique fingerprint generation
- JavaScript code generation for browser context spoofing
- Protection against actual device access

## Installation

The MediaDeviceSpoofingManager is part of the ICE Locator MCP Server and requires no additional installation.

## Usage

### Basic Usage

```python
from ice_locator_mcp.anti_detection.media_device_spoofing import MediaDeviceSpoofingManager

# Create manager instance
media_manager = MediaDeviceSpoofingManager()

# Generate a random media device profile
profile = media_manager.get_random_profile()

# Apply spoofing to a browser context
await media_manager.apply_media_device_spoofing(context, profile)
```

### Device-Specific Profiles

```python
# Generate device-specific profiles
desktop_profile = media_manager.get_device_specific_profile("desktop")
mobile_profile = media_manager.get_device_specific_profile("mobile")
tablet_profile = media_manager.get_device_specific_profile("tablet")
```

### Custom Profiles

```python
from ice_locator_mcp.anti_detection.media_device_spoofing import MediaDeviceProfile, MediaDevice

# Create custom audio input devices
audio_inputs = [
    MediaDevice(
        device_id="custom-audio-input-id",
        kind="audioinput",
        label="Custom Microphone",
        group_id="custom-group-id"
    )
]

# Create custom audio output devices
audio_outputs = [
    MediaDevice(
        device_id="custom-audio-output-id",
        kind="audiooutput",
        label="Custom Speakers",
        group_id="custom-group-id"
    )
]

# Create custom video input devices
video_inputs = [
    MediaDevice(
        device_id="custom-video-input-id",
        kind="videoinput",
        label="Custom Camera",
        group_id="custom-group-id"
    )
]

# Create a custom profile
custom_profile = MediaDeviceProfile(
    audio_input_devices=audio_inputs,
    audio_output_devices=audio_outputs,
    video_input_devices=video_inputs,
    device_type="desktop",
    is_consistent=True
)
```

## API Reference

### MediaDeviceSpoofingManager Class

#### `get_random_profile() -> MediaDeviceProfile`
Generate a random media device profile with realistic properties.

**Returns:**
- `MediaDeviceProfile`: MediaDeviceProfile with realistic properties

#### `get_device_specific_profile(device_type: str) -> MediaDeviceProfile`
Get a device-specific media device profile.

**Parameters:**
- `device_type` (str): Type of device (desktop, mobile, tablet)

**Returns:**
- `MediaDeviceProfile`: MediaDeviceProfile with device-specific properties

#### `apply_media_device_spoofing(context: BrowserContext, profile: Optional[MediaDeviceProfile] = None) -> None`
Apply advanced media device spoofing to a browser context.

**Parameters:**
- `context` (BrowserContext): Playwright BrowserContext to apply spoofing to
- `profile` (Optional[MediaDeviceProfile]): MediaDeviceProfile object, or None to generate random

#### `generate_fingerprint(profile: MediaDeviceProfile) -> str`
Generate a fingerprint based on media device profile.

**Parameters:**
- `profile` (MediaDeviceProfile): MediaDeviceProfile object

**Returns:**
- `str`: Media device fingerprint hash

#### `are_profiles_consistent(profile: MediaDeviceProfile) -> bool`
Check if media device profile is consistent.

**Parameters:**
- `profile` (MediaDeviceProfile): MediaDeviceProfile object

**Returns:**
- `bool`: True if profile is consistent, False otherwise

#### `_generate_spoofing_js(profile: MediaDeviceProfile) -> str`
Generate JavaScript to spoof media device information.

**Parameters:**
- `profile` (MediaDeviceProfile): MediaDeviceProfile object

**Returns:**
- `str`: JavaScript code string

### Data Classes

#### MediaDevice
Represents a media device with realistic properties.

**Attributes:**
- `device_id` (str): Device ID
- `kind` (str): Device kind (audioinput, audiooutput, videoinput)
- `label` (str): Device label
- `group_id` (str): Group ID

#### MediaDeviceProfile
Represents a media device configuration with realistic properties.

**Attributes:**
- `audio_input_devices` (List[MediaDevice]): List of audio input devices
- `audio_output_devices` (List[MediaDevice]): List of audio output devices
- `video_input_devices` (List[MediaDevice]): List of video input devices
- `device_type` (str): Type of device (desktop, mobile, tablet)
- `is_consistent` (bool): Whether the profile is internally consistent

## Device Configurations

The MediaDeviceSpoofingManager includes predefined configurations for:

### Desktop Devices
- 2-5 audio input devices with realistic properties
- 2-6 audio output devices with realistic properties
- 1-3 video input devices with realistic properties

### Mobile Devices
- 1-2 audio input devices (typically built-in or Bluetooth)
- 1-3 audio output devices (typically built-in or Bluetooth)
- 1-2 video input devices (typically built-in)

### Tablet Devices
- 1-3 audio input devices (typically built-in, Bluetooth, or headset)
- 1-4 audio output devices (typically built-in, Bluetooth, or headphones)
- 1-2 video input devices (typically built-in)

## Integration with Browser Simulator

The MediaDeviceSpoofingManager integrates seamlessly with the BrowserSimulator to provide realistic media device spoofing:

```python
from ice_locator_mcp.anti_detection.browser_simulator import BrowserSimulator
from ice_locator_mcp.anti_detection.media_device_spoofing import MediaDeviceSpoofingManager
from ice_locator_mcp.core.config import SearchConfig

# Create browser simulator
config = SearchConfig()
browser_sim = BrowserSimulator(config)
media_manager = MediaDeviceSpoofingManager()

# The MediaDeviceSpoofingManager can be used to create realistic 
# media device configurations for each session
```

## Best Practices

1. **Use realistic profiles**: Choose media device profiles that match real devices
2. **Vary profiles**: Use different profiles to avoid detection patterns
3. **Apply early**: Apply media device spoofing to contexts before creating pages
4. **Check consistency**: Verify that profiles are consistent and realistic
5. **Update regularly**: Change media device profiles periodically to avoid fingerprinting

## Testing

The MediaDeviceSpoofingManager includes comprehensive tests to ensure functionality:

```bash
python -m pytest tests/test_media_device_spoofing.py -v
```

## Contributing

Contributions to improve media device spoofing or add new simulation techniques are welcome. Please ensure all tests pass before submitting pull requests.

## License

This module is part of the ICE Locator MCP Server and is licensed under the project's license.