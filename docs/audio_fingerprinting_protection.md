# Audio Fingerprinting Protection Manager

## Overview

The AudioFingerprintingProtectionManager provides advanced protection against audio-based browser fingerprinting techniques. It implements realistic spoofing of AudioContext properties and methods to prevent detection through audio fingerprinting.

## Features

- Realistic AudioContext property spoofing
- Oscillator and analyser fingerprinting protection
- Device-specific audio configurations
- Audio data noise injection
- Consistency validation for audio profiles

## Installation

The AudioFingerprintingProtectionManager is part of the ICE Locator MCP Server and requires no additional installation.

## Usage

### Basic Usage

```python
from ice_locator_mcp.anti_detection.audio_fingerprinting_protection import AudioFingerprintingProtectionManager

# Create manager instance
audio_manager = AudioFingerprintingProtectionManager()

# Generate a random audio profile
profile = audio_manager.get_random_profile()

# Apply protection to a browser context
await audio_manager.apply_audio_fingerprinting_protection(context, profile)
```

### Device-Specific Profiles

```python
# Generate device-specific profiles
desktop_profile = audio_manager.get_device_specific_profile("desktop_high_end")
mobile_profile = audio_manager.get_device_specific_profile("mobile_low_end")
tablet_profile = audio_manager.get_device_specific_profile("tablet")
```

### Custom Profiles

```python
from ice_locator_mcp.anti_detection.audio_fingerprinting_protection import AudioFingerprintingProfile

# Create a custom profile
custom_profile = AudioFingerprintingProfile(
    sample_rate=48000,
    channel_count=2,
    latency_hint=0.005,
    oscillator_type="sine",
    oscillator_frequency=440.0,
    oscillator_detune=10,
    fft_size=1024,
    min_decibels=-90.0,
    max_decibels=-20.0,
    smoothing_time_constant=0.7,
    device_type="desktop_mid_range",
    is_consistent=True
)
```

## API Reference

### AudioFingerprintingProtectionManager Class

#### `get_random_profile() -> AudioFingerprintingProfile`
Generate a random audio fingerprinting protection profile with realistic properties.

**Returns:**
- `AudioFingerprintingProfile`: AudioFingerprintingProfile with realistic properties

#### `get_device_specific_profile(device_type: str) -> AudioFingerprintingProfile`
Get a device-specific audio fingerprinting protection profile.

**Parameters:**
- `device_type` (str): Type of device (desktop_high_end, desktop_mid_range, desktop_low_end, mobile_high_end, mobile_mid_range, mobile_low_end, tablet)

**Returns:**
- `AudioFingerprintingProfile`: AudioFingerprintingProfile with device-specific properties

#### `apply_audio_fingerprinting_protection(context: BrowserContext, profile: Optional[AudioFingerprintingProfile] = None) -> None`
Apply advanced audio fingerprinting protection to a browser context.

**Parameters:**
- `context` (BrowserContext): Playwright BrowserContext to apply protection to
- `profile` (Optional[AudioFingerprintingProfile]): AudioFingerprintingProfile object, or None to generate random

#### `generate_fingerprint(profile: AudioFingerprintingProfile) -> str`
Generate a fingerprint based on audio fingerprinting profile.

**Parameters:**
- `profile` (AudioFingerprintingProfile): AudioFingerprintingProfile object

**Returns:**
- `str`: Audio fingerprint hash

#### `are_profiles_consistent(profile: AudioFingerprintingProfile) -> bool`
Check if audio fingerprinting profile is consistent.

**Parameters:**
- `profile` (AudioFingerprintingProfile): AudioFingerprintingProfile object

**Returns:**
- `bool`: True if profile is consistent, False otherwise

#### `_generate_protection_js(profile: AudioFingerprintingProfile) -> str`
Generate JavaScript to protect against audio fingerprinting.

**Parameters:**
- `profile` (AudioFingerprintingProfile): AudioFingerprintingProfile object

**Returns:**
- `str`: JavaScript code string

### AudioFingerprintingProfile Dataclass

Represents an audio fingerprinting protection configuration with realistic properties.

**Attributes:**
- `sample_rate` (int): Audio sample rate (Hz)
- `channel_count` (int): Number of audio channels
- `latency_hint` (float): Latency hint for audio context
- `oscillator_type` (str): Type of oscillator (sine, square, sawtooth, triangle)
- `oscillator_frequency` (float): Base frequency for oscillator (Hz)
- `oscillator_detune` (int): Detune value for oscillator (cents)
- `fft_size` (int): FFT size for analyser
- `min_decibels` (float): Minimum decibels for analyser
- `max_decibels` (float): Maximum decibels for analyser
- `smoothing_time_constant` (float): Smoothing time constant for analyser
- `device_type` (str): Type of device (desktop, mobile, tablet)
- `is_consistent` (bool): Whether the profile is internally consistent

## Audio Configurations

The AudioFingerprintingProtectionManager includes predefined audio configurations for:

### Desktop Devices
- High-end: 44100-96000 Hz sample rate, 2-8 channels
- Mid-range: 44100-48000 Hz sample rate, 2-4 channels
- Low-end: 22050-48000 Hz sample rate, 1-2 channels

### Mobile Devices
- High-end: 44100-48000 Hz sample rate, 1-2 channels
- Mid-range: 22050-48000 Hz sample rate, 1-2 channels
- Low-end: 22050-44100 Hz sample rate, 1 channel

### Tablet Devices
- 44100-48000 Hz sample rate, 1-2 channels

## Integration with Browser Simulator

The AudioFingerprintingProtectionManager integrates seamlessly with the BrowserSimulator to provide realistic audio fingerprinting protection:

```python
from ice_locator_mcp.anti_detection.browser_simulator import BrowserSimulator
from ice_locator_mcp.anti_detection.audio_fingerprinting_protection import AudioFingerprintingProtectionManager
from ice_locator_mcp.core.config import SearchConfig

# Create browser simulator
config = SearchConfig()
browser_sim = BrowserSimulator(config)
audio_manager = AudioFingerprintingProtectionManager()

# The AudioFingerprintingProtectionManager can be used to create realistic 
# audio configurations for each session
```

## Best Practices

1. **Use realistic profiles**: Choose audio profiles that match real devices
2. **Vary profiles**: Use different profiles to avoid detection patterns
3. **Apply early**: Apply audio fingerprinting protection to contexts before creating pages
4. **Check consistency**: Verify that profiles are consistent and realistic
5. **Update regularly**: Change audio profiles periodically to avoid fingerprinting

## Testing

The AudioFingerprintingProtectionManager includes comprehensive tests to ensure functionality:

```bash
python -m pytest tests/test_audio_fingerprinting_protection.py -v
```

## Contributing

Contributions to improve audio fingerprinting protection or add new simulation techniques are welcome. Please ensure all tests pass before submitting pull requests.

## License

This module is part of the ICE Locator MCP Server and is licensed under the project's license.