"""
Media Device Spoofing Manager for ICE Locator MCP Server.

This module provides advanced media device spoofing to prevent enumeration-based fingerprinting.
"""

import random
import structlog
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from playwright.async_api import BrowserContext


@dataclass
class MediaDevice:
    """Represents a media device with realistic properties."""
    device_id: str
    kind: str  # 'audioinput', 'audiooutput', 'videoinput'
    label: str
    group_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MediaDevice':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class MediaDeviceProfile:
    """Represents a media device configuration with realistic properties."""
    # Media devices
    audio_input_devices: List[MediaDevice]
    audio_output_devices: List[MediaDevice]
    video_input_devices: List[MediaDevice]
    
    # Device type
    device_type: str  # Type of device (desktop, mobile, tablet)
    
    # Consistency flags
    is_consistent: bool  # Whether the profile is internally consistent
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "audio_input_devices": [device.to_dict() for device in self.audio_input_devices],
            "audio_output_devices": [device.to_dict() for device in self.audio_output_devices],
            "video_input_devices": [device.to_dict() for device in self.video_input_devices],
            "device_type": self.device_type,
            "is_consistent": self.is_consistent
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MediaDeviceProfile':
        """Create from dictionary."""
        audio_inputs = [MediaDevice.from_dict(device) for device in data["audio_input_devices"]]
        audio_outputs = [MediaDevice.from_dict(device) for device in data["audio_output_devices"]]
        video_inputs = [MediaDevice.from_dict(device) for device in data["video_input_devices"]]
        return cls(
            audio_input_devices=audio_inputs,
            audio_output_devices=audio_outputs,
            video_input_devices=video_inputs,
            device_type=data["device_type"],
            is_consistent=data["is_consistent"]
        )


class MediaDeviceSpoofingManager:
    """Manages advanced media device spoofing to prevent enumeration-based fingerprinting."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        
        # Common audio input devices with realistic properties
        self.common_audio_inputs = [
            {"label": "Default - Microphone", "kind": "audioinput"},
            {"label": "Built-in Microphone", "kind": "audioinput"},
            {"label": "USB Microphone", "kind": "audioinput"},
            {"label": "Bluetooth Microphone", "kind": "audioinput"},
            {"label": "Headset Microphone", "kind": "audioinput"},
            {"label": "Webcam Microphone", "kind": "audioinput"},
            {"label": "Conference Microphone", "kind": "audioinput"}
        ]
        
        # Common audio output devices with realistic properties
        self.common_audio_outputs = [
            {"label": "Default - Speakers", "kind": "audiooutput"},
            {"label": "Built-in Speakers", "kind": "audiooutput"},
            {"label": "Headphones", "kind": "audiooutput"},
            {"label": "USB Speakers", "kind": "audiooutput"},
            {"label": "Bluetooth Speakers", "kind": "audiooutput"},
            {"label": "HDMI Output", "kind": "audiooutput"},
            {"label": "Display Audio", "kind": "audiooutput"}
        ]
        
        # Common video input devices with realistic properties
        self.common_video_inputs = [
            {"label": "FaceTime HD Camera", "kind": "videoinput"},
            {"label": "Built-in iSight", "kind": "videoinput"},
            {"label": "USB Camera", "kind": "videoinput"},
            {"label": "Webcam", "kind": "videoinput"},
            {"label": "Logitech Camera", "kind": "videoinput"},
            {"label": "Integrated Camera", "kind": "videoinput"},
            {"label": "HD Webcam", "kind": "videoinput"},
            {"label": "External Webcam", "kind": "videoinput"}
        ]
        
        # Device-specific media device configurations
        self.device_configs = {
            "desktop": {
                "audio_input_count_range": (2, 5),
                "audio_output_count_range": (2, 6),
                "video_input_count_range": (1, 3),
                "common_audio_inputs": self.common_audio_inputs,
                "common_audio_outputs": self.common_audio_outputs,
                "common_video_inputs": self.common_video_inputs
            },
            "mobile": {
                "audio_input_count_range": (1, 2),
                "audio_output_count_range": (1, 3),
                "video_input_count_range": (1, 2),
                "common_audio_inputs": [device for device in self.common_audio_inputs if "Built-in" in device["label"] or "Bluetooth" in device["label"]],
                "common_audio_outputs": [device for device in self.common_audio_outputs if "Built-in" in device["label"] or "Bluetooth" in device["label"]],
                "common_video_inputs": [device for device in self.common_video_inputs if "Built-in" in device["label"] or "Integrated" in device["label"]]
            },
            "tablet": {
                "audio_input_count_range": (1, 3),
                "audio_output_count_range": (1, 4),
                "video_input_count_range": (1, 2),
                "common_audio_inputs": [device for device in self.common_audio_inputs if "Built-in" in device["label"] or "Bluetooth" in device["label"] or "Headset" in device["label"]],
                "common_audio_outputs": [device for device in self.common_audio_outputs if "Built-in" in device["label"] or "Bluetooth" in device["label"] or "Headphones" in device["label"]],
                "common_video_inputs": [device for device in self.common_video_inputs if "Built-in" in device["label"] or "Integrated" in device["label"]]
            }
        }
    
    def _generate_device_id(self) -> str:
        """Generate a realistic device ID."""
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(random.choice(chars) for _ in range(32))
    
    def _generate_group_id(self) -> str:
        """Generate a realistic group ID."""
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(random.choice(chars) for _ in range(16))
    
    def get_random_profile(self) -> MediaDeviceProfile:
        """
        Get a random media device profile with realistic properties.
        
        Returns:
            MediaDeviceProfile with realistic properties
        """
        device_type = random.choice(list(self.device_configs.keys()))
        config = self.device_configs[device_type]
        
        # Generate audio input devices
        audio_input_count = random.randint(*config["audio_input_count_range"])
        audio_inputs = []
        for i in range(audio_input_count):
            device_info = random.choice(config["common_audio_inputs"])
            audio_inputs.append(MediaDevice(
                device_id=self._generate_device_id(),
                kind=device_info["kind"],
                label=device_info["label"],
                group_id=self._generate_group_id()
            ))
        
        # Generate audio output devices
        audio_output_count = random.randint(*config["audio_output_count_range"])
        audio_outputs = []
        for i in range(audio_output_count):
            device_info = random.choice(config["common_audio_outputs"])
            audio_outputs.append(MediaDevice(
                device_id=self._generate_device_id(),
                kind=device_info["kind"],
                label=device_info["label"],
                group_id=self._generate_group_id()
            ))
        
        # Generate video input devices
        video_input_count = random.randint(*config["video_input_count_range"])
        video_inputs = []
        for i in range(video_input_count):
            device_info = random.choice(config["common_video_inputs"])
            video_inputs.append(MediaDevice(
                device_id=self._generate_device_id(),
                kind=device_info["kind"],
                label=device_info["label"],
                group_id=self._generate_group_id()
            ))
        
        return MediaDeviceProfile(
            audio_input_devices=audio_inputs,
            audio_output_devices=audio_outputs,
            video_input_devices=video_inputs,
            device_type=device_type,
            is_consistent=True
        )
    
    def get_device_specific_profile(self, device_type: str) -> MediaDeviceProfile:
        """
        Get a device-specific media device profile.
        
        Args:
            device_type: Type of device (desktop, mobile, tablet)
            
        Returns:
            MediaDeviceProfile with device-specific properties
        """
        if device_type not in self.device_configs:
            return self.get_random_profile()
        
        config = self.device_configs[device_type]
        
        # Generate audio input devices
        audio_input_count = random.randint(*config["audio_input_count_range"])
        audio_inputs = []
        for i in range(audio_input_count):
            device_info = random.choice(config["common_audio_inputs"])
            audio_inputs.append(MediaDevice(
                device_id=self._generate_device_id(),
                kind=device_info["kind"],
                label=device_info["label"],
                group_id=self._generate_group_id()
            ))
        
        # Generate audio output devices
        audio_output_count = random.randint(*config["audio_output_count_range"])
        audio_outputs = []
        for i in range(audio_output_count):
            device_info = random.choice(config["common_audio_outputs"])
            audio_outputs.append(MediaDevice(
                device_id=self._generate_device_id(),
                kind=device_info["kind"],
                label=device_info["label"],
                group_id=self._generate_group_id()
            ))
        
        # Generate video input devices
        video_input_count = random.randint(*config["video_input_count_range"])
        video_inputs = []
        for i in range(video_input_count):
            device_info = random.choice(config["common_video_inputs"])
            video_inputs.append(MediaDevice(
                device_id=self._generate_device_id(),
                kind=device_info["kind"],
                label=device_info["label"],
                group_id=self._generate_group_id()
            ))
        
        return MediaDeviceProfile(
            audio_input_devices=audio_inputs,
            audio_output_devices=audio_outputs,
            video_input_devices=video_inputs,
            device_type=device_type,
            is_consistent=True
        )
    
    async def apply_media_device_spoofing(self, context: BrowserContext,
                                        profile: Optional[MediaDeviceProfile] = None) -> None:
        """
        Apply advanced media device spoofing to a browser context.
        
        Args:
            context: Playwright BrowserContext to apply spoofing to
            profile: MediaDeviceProfile object, or None to generate random
        """
        if profile is None:
            profile = self.get_random_profile()
        
        try:
            # Generate JavaScript to spoof media device information
            spoofing_js = self._generate_spoofing_js(profile)
            
            # Add JavaScript to context
            await context.add_init_script(spoofing_js)
            
            self.logger.debug(
                "Applied advanced media device spoofing to context",
                audio_input_count=len(profile.audio_input_devices),
                audio_output_count=len(profile.audio_output_devices),
                video_input_count=len(profile.video_input_devices),
                device_type=profile.device_type
            )
            
        except Exception as e:
            self.logger.error("Failed to apply media device spoofing to context", error=str(e))
            raise
    
    def _generate_spoofing_js(self, profile: MediaDeviceProfile) -> str:
        """
        Generate JavaScript to spoof media device information.
        
        Args:
            profile: MediaDeviceProfile object
            
        Returns:
            JavaScript code string
        """
        # Create devices JSON
        all_devices = []
        all_devices.extend([{
            "deviceId": device.device_id,
            "kind": device.kind,
            "label": device.label,
            "groupId": device.group_id
        } for device in profile.audio_input_devices])
        
        all_devices.extend([{
            "deviceId": device.device_id,
            "kind": device.kind,
            "label": device.label,
            "groupId": device.group_id
        } for device in profile.audio_output_devices])
        
        all_devices.extend([{
            "deviceId": device.device_id,
            "kind": device.kind,
            "label": device.label,
            "groupId": device.group_id
        } for device in profile.video_input_devices])
        
        devices_json = str(all_devices).replace("'", "\\'")
        
        js_code = f"""
        // Advanced Media Device Spoofing
        (function() {{
            // Override media devices enumeration
            if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {{
                const originalEnumerateDevices = navigator.mediaDevices.enumerateDevices;
                navigator.mediaDevices.enumerateDevices = function() {{
                    return Promise.resolve({devices_json});
                }};
            }}
            
            // Override getUserMedia to prevent actual device access
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {{
                const originalGetUserMedia = navigator.mediaDevices.getUserMedia;
                navigator.mediaDevices.getUserMedia = function(constraints) {{
                    // Return a rejected promise to prevent actual device access
                    // This prevents websites from actually accessing real devices
                    // while still providing realistic API behavior
                    return Promise.reject(new DOMException("Permission denied by user", "NotAllowedError"));
                }};
            }}
            
            // Override media device permissions
            if (navigator.permissions && navigator.permissions.query) {{
                const originalPermissionsQuery = navigator.permissions.query;
                navigator.permissions.query = function(descriptor) {{
                    if (descriptor && descriptor.name === 'camera') {{
                        return Promise.resolve({{state: 'denied'}});
                    }} else if (descriptor && descriptor.name === 'microphone') {{
                        return Promise.resolve({{state: 'denied'}});
                    }}
                    return originalPermissionsQuery.apply(this, arguments);
                }};
            }}
            
            // Add realistic timing variations to media device access
            const originalEnumerateDevices = Object.getOwnPropertyDescriptor(navigator.mediaDevices, 'enumerateDevices');
            if (originalEnumerateDevices && originalEnumerateDevices.value) {{
                const originalFunction = originalEnumerateDevices.value;
                navigator.mediaDevices.enumerateDevices = function() {{
                    // Add slight delay to simulate real device enumeration
                    const delay = Math.random() * 0.1; // 0-100ms
                    return originalFunction.apply(this, arguments);
                }};
            }}
            
            // Override MediaStreamTrack.getSources (deprecated but still used)
            if (MediaStreamTrack && MediaStreamTrack.getSources) {{
                MediaStreamTrack.getSources = function(callback) {{
                    if (callback) {{
                        setTimeout(() => callback({devices_json}), 10);
                    }}
                }};
            }}
            
            // Override MediaStreamTrack.getConstraints to prevent fingerprinting
            if (MediaStreamTrack && MediaStreamTrack.prototype.getConstraints) {{
                const originalGetConstraints = MediaStreamTrack.prototype.getConstraints;
                MediaStreamTrack.prototype.getConstraints = function() {{
                    // Return empty constraints to prevent fingerprinting
                    return {{}};
                }};
            }}
            
            // Override MediaStreamTrack.getSettings to prevent fingerprinting
            if (MediaStreamTrack && MediaStreamTrack.prototype.getSettings) {{
                const originalGetSettings = MediaStreamTrack.prototype.getSettings;
                MediaStreamTrack.prototype.getSettings = function() {{
                    // Return empty settings to prevent fingerprinting
                    return {{}};
                }};
            }}
        }})();
        """
        
        return js_code
    
    def generate_fingerprint(self, profile: MediaDeviceProfile) -> str:
        """
        Generate a fingerprint based on media device profile.
        
        Args:
            profile: MediaDeviceProfile object
            
        Returns:
            String fingerprint
        """
        # Create a string representation of the profile
        audio_input_data = "|".join([f"{d.device_id}:{d.label}" for d in profile.audio_input_devices])
        audio_output_data = "|".join([f"{d.device_id}:{d.label}" for d in profile.audio_output_devices])
        video_input_data = "|".join([f"{d.device_id}:{d.label}" for d in profile.video_input_devices])
        
        fingerprint_data = (
            f"{audio_input_data}|{audio_output_data}|{video_input_data}|{profile.device_type}"
        )
        
        # Generate a hash of the fingerprint data
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    def are_profiles_consistent(self, profile: MediaDeviceProfile) -> bool:
        """
        Check if media device profile is consistent.
        
        Args:
            profile: MediaDeviceProfile object
            
        Returns:
            True if profile is consistent, False otherwise
        """
        # Check that devices have realistic properties
        for device in profile.audio_input_devices:
            if not device.device_id or not device.label or device.kind != "audioinput":
                return False
        
        for device in profile.audio_output_devices:
            if not device.device_id or not device.label or device.kind != "audiooutput":
                return False
        
        for device in profile.video_input_devices:
            if not device.device_id or not device.label or device.kind != "videoinput":
                return False
        
        # Check device type consistency
        if profile.device_type not in self.device_configs:
            return False
        
        # Check device count consistency for device type
        config = self.device_configs[profile.device_type]
        audio_input_range = config["audio_input_count_range"]
        audio_output_range = config["audio_output_count_range"]
        video_input_range = config["video_input_count_range"]
        
        if not (audio_input_range[0] <= len(profile.audio_input_devices) <= audio_input_range[1]):
            return False
        
        if not (audio_output_range[0] <= len(profile.audio_output_devices) <= audio_output_range[1]):
            return False
        
        if not (video_input_range[0] <= len(profile.video_input_devices) <= video_input_range[1]):
            return False
        
        return True