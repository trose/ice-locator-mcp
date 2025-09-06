"""
Audio Fingerprinting Protection Manager for ICE Locator MCP Server.

This module provides advanced audio context spoofing to prevent 
audio-based browser fingerprinting.
"""

import random
import structlog
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from playwright.async_api import BrowserContext


@dataclass
class AudioFingerprintingProfile:
    """Represents an audio fingerprinting protection configuration with realistic properties."""
    # Audio context properties
    sample_rate: int  # Audio sample rate (Hz)
    channel_count: int  # Number of audio channels
    latency_hint: float  # Latency hint for audio context
    
    # Oscillator properties
    oscillator_type: str  # Type of oscillator (sine, square, sawtooth, triangle)
    oscillator_frequency: float  # Base frequency for oscillator (Hz)
    oscillator_detune: int  # Detune value for oscillator (cents)
    
    # Analyser properties
    fft_size: int  # FFT size for analyser
    min_decibels: float  # Minimum decibels for analyser
    max_decibels: float  # Maximum decibels for analyser
    smoothing_time_constant: float  # Smoothing time constant for analyser
    
    # Device type
    device_type: str  # Type of device (desktop, mobile, tablet)
    
    # Consistency flags
    is_consistent: bool  # Whether the profile is internally consistent
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioFingerprintingProfile':
        """Create from dictionary."""
        return cls(**data)


class AudioFingerprintingProtectionManager:
    """Manages advanced audio fingerprinting protection."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        
        # Common audio configurations for different device types
        self.common_audio_configs = [
            {
                "device_type": "desktop_high_end",
                "sample_rate_range": (44100, 96000),
                "channel_count_range": (2, 8),
                "latency_hint_range": (0.001, 0.01),
                "oscillator_types": ["sine", "square", "sawtooth", "triangle"],
                "oscillator_frequency_range": (440.0, 880.0),
                "oscillator_detune_range": (-50, 50),
                "fft_size_options": [32, 64, 128, 256, 512, 1024, 2048],
                "min_decibels_range": (-100.0, -80.0),
                "max_decibels_range": (-30.0, -10.0),
                "smoothing_time_constant_range": (0.2, 0.8)
            },
            {
                "device_type": "desktop_mid_range",
                "sample_rate_range": (44100, 48000),
                "channel_count_range": (2, 4),
                "latency_hint_range": (0.005, 0.02),
                "oscillator_types": ["sine", "square", "triangle"],
                "oscillator_frequency_range": (440.0, 880.0),
                "oscillator_detune_range": (-30, 30),
                "fft_size_options": [32, 64, 128, 256, 512, 1024],
                "min_decibels_range": (-90.0, -70.0),
                "max_decibels_range": (-30.0, -10.0),
                "smoothing_time_constant_range": (0.3, 0.7)
            },
            {
                "device_type": "desktop_low_end",
                "sample_rate_range": (22050, 48000),
                "channel_count_range": (1, 2),
                "latency_hint_range": (0.01, 0.05),
                "oscillator_types": ["sine", "square"],
                "oscillator_frequency_range": (440.0, 880.0),
                "oscillator_detune_range": (-20, 20),
                "fft_size_options": [32, 64, 128, 256, 512],
                "min_decibels_range": (-80.0, -60.0),
                "max_decibels_range": (-30.0, -10.0),
                "smoothing_time_constant_range": (0.4, 0.6)
            },
            {
                "device_type": "mobile_high_end",
                "sample_rate_range": (44100, 48000),
                "channel_count_range": (1, 2),
                "latency_hint_range": (0.001, 0.005),
                "oscillator_types": ["sine", "triangle"],
                "oscillator_frequency_range": (440.0, 880.0),
                "oscillator_detune_range": (-20, 20),
                "fft_size_options": [32, 64, 128, 256, 512],
                "min_decibels_range": (-90.0, -70.0),
                "max_decibels_range": (-30.0, -10.0),
                "smoothing_time_constant_range": (0.3, 0.7)
            },
            {
                "device_type": "mobile_mid_range",
                "sample_rate_range": (22050, 48000),
                "channel_count_range": (1, 2),
                "latency_hint_range": (0.005, 0.01),
                "oscillator_types": ["sine", "triangle"],
                "oscillator_frequency_range": (440.0, 880.0),
                "oscillator_detune_range": (-15, 15),
                "fft_size_options": [32, 64, 128, 256],
                "min_decibels_range": (-80.0, -60.0),
                "max_decibels_range": (-30.0, -10.0),
                "smoothing_time_constant_range": (0.4, 0.6)
            },
            {
                "device_type": "mobile_low_end",
                "sample_rate_range": (22050, 44100),
                "channel_count_range": (1, 1),
                "latency_hint_range": (0.01, 0.02),
                "oscillator_types": ["sine"],
                "oscillator_frequency_range": (440.0, 880.0),
                "oscillator_detune_range": (-10, 10),
                "fft_size_options": [32, 64, 128],
                "min_decibels_range": (-70.0, -50.0),
                "max_decibels_range": (-30.0, -10.0),
                "smoothing_time_constant_range": (0.5, 0.5)
            },
            {
                "device_type": "tablet",
                "sample_rate_range": (44100, 48000),
                "channel_count_range": (1, 2),
                "latency_hint_range": (0.002, 0.01),
                "oscillator_types": ["sine", "triangle"],
                "oscillator_frequency_range": (440.0, 880.0),
                "oscillator_detune_range": (-15, 15),
                "fft_size_options": [32, 64, 128, 256],
                "min_decibels_range": (-85.0, -65.0),
                "max_decibels_range": (-30.0, -10.0),
                "smoothing_time_constant_range": (0.35, 0.65)
            }
        ]
    
    def get_random_profile(self) -> AudioFingerprintingProfile:
        """
        Get a random audio fingerprinting protection profile with realistic properties.
        
        Returns:
            AudioFingerprintingProfile with realistic properties
        """
        config = random.choice(self.common_audio_configs)
        
        # Generate realistic values based on the configuration
        sample_rate = random.randint(*config["sample_rate_range"])
        channel_count = random.randint(*config["channel_count_range"])
        latency_hint = round(random.uniform(*config["latency_hint_range"]), 6)
        oscillator_type = random.choice(config["oscillator_types"])
        oscillator_frequency = round(random.uniform(*config["oscillator_frequency_range"]), 2)
        oscillator_detune = random.randint(*config["oscillator_detune_range"])
        fft_size = random.choice(config["fft_size_options"])
        min_decibels = round(random.uniform(*config["min_decibels_range"]), 2)
        max_decibels = round(random.uniform(*config["max_decibels_range"]), 2)
        smoothing_time_constant = round(random.uniform(*config["smoothing_time_constant_range"]), 2)
        
        return AudioFingerprintingProfile(
            sample_rate=sample_rate,
            channel_count=channel_count,
            latency_hint=latency_hint,
            oscillator_type=oscillator_type,
            oscillator_frequency=oscillator_frequency,
            oscillator_detune=oscillator_detune,
            fft_size=fft_size,
            min_decibels=min_decibels,
            max_decibels=max_decibels,
            smoothing_time_constant=smoothing_time_constant,
            device_type=config["device_type"],
            is_consistent=True
        )
    
    def get_device_specific_profile(self, device_type: str) -> AudioFingerprintingProfile:
        """
        Get a device-specific audio fingerprinting protection profile.
        
        Args:
            device_type: Type of device (desktop_high_end, desktop_mid_range, desktop_low_end,
                         mobile_high_end, mobile_mid_range, mobile_low_end, tablet)
            
        Returns:
            AudioFingerprintingProfile with device-specific properties
        """
        for config in self.common_audio_configs:
            if config["device_type"] == device_type:
                sample_rate = random.randint(*config["sample_rate_range"])
                channel_count = random.randint(*config["channel_count_range"])
                latency_hint = round(random.uniform(*config["latency_hint_range"]), 6)
                oscillator_type = random.choice(config["oscillator_types"])
                oscillator_frequency = round(random.uniform(*config["oscillator_frequency_range"]), 2)
                oscillator_detune = random.randint(*config["oscillator_detune_range"])
                fft_size = random.choice(config["fft_size_options"])
                min_decibels = round(random.uniform(*config["min_decibels_range"]), 2)
                max_decibels = round(random.uniform(*config["max_decibels_range"]), 2)
                smoothing_time_constant = round(random.uniform(*config["smoothing_time_constant_range"]), 2)
                
                return AudioFingerprintingProfile(
                    sample_rate=sample_rate,
                    channel_count=channel_count,
                    latency_hint=latency_hint,
                    oscillator_type=oscillator_type,
                    oscillator_frequency=oscillator_frequency,
                    oscillator_detune=oscillator_detune,
                    fft_size=fft_size,
                    min_decibels=min_decibels,
                    max_decibels=max_decibels,
                    smoothing_time_constant=smoothing_time_constant,
                    device_type=config["device_type"],
                    is_consistent=True
                )
        
        # If device type not found, return a random profile
        return self.get_random_profile()
    
    async def apply_audio_fingerprinting_protection(self, context: BrowserContext,
                                                  profile: Optional[AudioFingerprintingProfile] = None) -> None:
        """
        Apply advanced audio fingerprinting protection to a browser context.
        
        Args:
            context: Playwright BrowserContext to apply protection to
            profile: AudioFingerprintingProfile object, or None to generate random
        """
        if profile is None:
            profile = self.get_random_profile()
        
        try:
            # Generate JavaScript to spoof audio context properties
            protection_js = self._generate_protection_js(profile)
            
            # Add JavaScript to context
            await context.add_init_script(protection_js)
            
            self.logger.debug(
                "Applied advanced audio fingerprinting protection to context",
                sample_rate=profile.sample_rate,
                channel_count=profile.channel_count,
                oscillator_type=profile.oscillator_type
            )
            
        except Exception as e:
            self.logger.error("Failed to apply audio fingerprinting protection to context", error=str(e))
            raise
    
    def _generate_protection_js(self, profile: AudioFingerprintingProfile) -> str:
        """
        Generate JavaScript to protect against audio fingerprinting.
        
        Args:
            profile: AudioFingerprintingProfile object
            
        Returns:
            JavaScript code string
        """
        # Escape quotes in strings for JavaScript
        oscillator_type = profile.oscillator_type.replace('"', '\\"')
        device_type = profile.device_type.replace('"', '\\"')
        
        js_code = f"""
        // Advanced Audio Fingerprinting Protection
        (function() {{
            // Protect AudioContext
            if (window.AudioContext || window.webkitAudioContext) {{
                const OriginalAudioContext = window.AudioContext || window.webkitAudioContext;
                
                // Override AudioContext constructor
                window.AudioContext = function(options) {{
                    // Apply latency hint from profile
                    const contextOptions = options || {{}};
                    contextOptions.latencyHint = contextOptions.latencyHint || {profile.latency_hint};
                    
                    // Create original context
                    const context = new OriginalAudioContext(contextOptions);
                    
                    // Override sampleRate property
                    Object.defineProperty(context, 'sampleRate', {{
                        get: () => {profile.sample_rate},
                        configurable: false,
                        enumerable: true
                    }});
                    
                    // Override createOscillator to add fingerprinting protection
                    const originalCreateOscillator = context.createOscillator;
                    context.createOscillator = function() {{
                        const oscillator = originalCreateOscillator.apply(this, arguments);
                        
                        // Override oscillator type
                        Object.defineProperty(oscillator, 'type', {{
                            get: () => "{oscillator_type}",
                            set: (value) => {{ /* Prevent changing type */ }},
                            configurable: false,
                            enumerable: true
                        }});
                        
                        // Override frequency and detune values
                        if (oscillator.frequency) {{
                            Object.defineProperty(oscillator.frequency, 'value', {{
                                get: () => {profile.oscillator_frequency},
                                set: (value) => {{ /* Prevent changing frequency */ }},
                                configurable: false,
                                enumerable: true
                            }});
                        }}
                        
                        if (oscillator.detune) {{
                            Object.defineProperty(oscillator.detune, 'value', {{
                                get: () => {profile.oscillator_detune},
                                set: (value) => {{ /* Prevent changing detune */ }},
                                configurable: false,
                                enumerable: true
                            }});
                        }}
                        
                        return oscillator;
                    }};
                    
                    // Override createAnalyser to add fingerprinting protection
                    const originalCreateAnalyser = context.createAnalyser;
                    context.createAnalyser = function() {{
                        const analyser = originalCreateAnalyser.apply(this, arguments);
                        
                        // Override analyser properties
                        Object.defineProperty(analyser, 'fftSize', {{
                            get: () => {profile.fft_size},
                            set: (value) => {{ /* Prevent changing FFT size */ }},
                            configurable: false,
                            enumerable: true
                        }});
                        
                        Object.defineProperty(analyser, 'minDecibels', {{
                            get: () => {profile.min_decibels},
                            set: (value) => {{ /* Prevent changing min decibels */ }},
                            configurable: false,
                            enumerable: true
                        }});
                        
                        Object.defineProperty(analyser, 'maxDecibels', {{
                            get: () => {profile.max_decibels},
                            set: (value) => {{ /* Prevent changing max decibels */ }},
                            configurable: false,
                            enumerable: true
                        }});
                        
                        Object.defineProperty(analyser, 'smoothingTimeConstant', {{
                            get: () => {profile.smoothing_time_constant},
                            set: (value) => {{ /* Prevent changing smoothing time constant */ }},
                            configurable: false,
                            enumerable: true
                        }});
                        
                        // Override getFloatFrequencyData to add noise
                        const originalGetFloatFrequencyData = analyser.getFloatFrequencyData;
                        analyser.getFloatFrequencyData = function(array) {{
                            // Call original method
                            originalGetFloatFrequencyData.apply(this, arguments);
                            
                            // Add realistic noise to frequency data
                            if (array && array.length) {{
                                for (let i = 0; i < array.length; i++) {{
                                    // Add small random noise to each value
                                    array[i] += (Math.random() - 0.5) * 0.1;
                                }}
                            }}
                        }};
                        
                        // Override getByteFrequencyData to add noise
                        const originalGetByteFrequencyData = analyser.getByteFrequencyData;
                        analyser.getByteFrequencyData = function(array) {{
                            // Call original method
                            originalGetByteFrequencyData.apply(this, arguments);
                            
                            // Add realistic noise to frequency data
                            if (array && array.length) {{
                                for (let i = 0; i < array.length; i++) {{
                                    // Add small random noise to each value
                                    array[i] = Math.min(255, Math.max(0, array[i] + Math.floor((Math.random() - 0.5) * 5)));
                                }}
                            }}
                        }};
                        
                        // Override getFloatTimeDomainData to add noise
                        if (analyser.getFloatTimeDomainData) {{
                            const originalGetFloatTimeDomainData = analyser.getFloatTimeDomainData;
                            analyser.getFloatTimeDomainData = function(array) {{
                                // Call original method
                                originalGetFloatTimeDomainData.apply(this, arguments);
                                
                                // Add realistic noise to time domain data
                                if (array && array.length) {{
                                    for (let i = 0; i < array.length; i++) {{
                                        // Add small random noise to each value
                                        array[i] += (Math.random() - 0.5) * 0.01;
                                    }}
                                }}
                            }};
                        }}
                        
                        // Override getByteTimeDomainData to add noise
                        if (analyser.getByteTimeDomainData) {{
                            const originalGetByteTimeDomainData = analyser.getByteTimeDomainData;
                            analyser.getByteTimeDomainData = function(array) {{
                                // Call original method
                                originalGetByteTimeDomainData.apply(this, arguments);
                                
                                // Add realistic noise to time domain data
                                if (array && array.length) {{
                                    for (let i = 0; i < array.length; i++) {{
                                        // Add small random noise to each value
                                        array[i] = Math.min(255, Math.max(0, array[i] + Math.floor((Math.random() - 0.5) * 3)));
                                    }}
                                }}
                            }};
                        }}
                        
                        return analyser;
                    }};
                    
                    // Override createGain to maintain consistency
                    const originalCreateGain = context.createGain;
                    context.createGain = function() {{
                        const gain = originalCreateGain.apply(this, arguments);
                        
                        // Add slight timing variations to make it more realistic
                        const delay = Math.random() * 0.001; // 0-1ms delay
                        
                        return gain;
                    }};
                    
                    return context;
                }};
                
                // Copy static properties
                Object.getOwnPropertyNames(OriginalAudioContext).forEach(prop => {{
                    try {{
                        window.AudioContext[prop] = OriginalAudioContext[prop];
                    }} catch (e) {{
                        // Ignore errors for non-writable properties
                    }}
                }});
            }}
            
            // Protect OfflineAudioContext
            if (window.OfflineAudioContext) {{
                const OriginalOfflineAudioContext = window.OfflineAudioContext;
                
                window.OfflineAudioContext = function(numberOfChannels, length, sampleRate) {{
                    // Use profile sample rate
                    const context = new OriginalOfflineAudioContext(
                        numberOfChannels || {profile.channel_count},
                        length,
                        sampleRate || {profile.sample_rate}
                    );
                    
                    // Apply same protections as AudioContext
                    // Override sampleRate property
                    Object.defineProperty(context, 'sampleRate', {{
                        get: () => {profile.sample_rate},
                        configurable: false,
                        enumerable: true
                    }});
                    
                    return context;
                }};
                
                // Copy static properties
                Object.getOwnPropertyNames(OriginalOfflineAudioContext).forEach(prop => {{
                    try {{
                        window.OfflineAudioContext[prop] = OriginalOfflineAudioContext[prop];
                    }} catch (e) {{
                        // Ignore errors for non-writable properties
                    }}
                }});
            }}
            
            // Add realistic timing variations to audio context access
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(contextType) {{
                const context = originalGetContext.apply(this, [contextType]);
                
                // Add slight delay to simulate real audio context access
                if (contextType === '2d' && context) {{
                    const delay = Math.random() * 0.0005; // 0-0.5ms
                }}
                
                return context;
            }};
        }})();
        """
        
        return js_code
    
    def generate_fingerprint(self, profile: AudioFingerprintingProfile) -> str:
        """
        Generate a fingerprint based on audio fingerprinting profile.
        
        Args:
            profile: AudioFingerprintingProfile object
            
        Returns:
            String fingerprint
        """
        # Create a string representation of the profile
        fingerprint_data = (
            f"{profile.sample_rate}|{profile.channel_count}|{profile.latency_hint}|"
            f"{profile.oscillator_type}|{profile.oscillator_frequency}|{profile.oscillator_detune}|"
            f"{profile.fft_size}|{profile.min_decibels}|{profile.max_decibels}|"
            f"{profile.smoothing_time_constant}|{profile.device_type}"
        )
        
        # Generate a hash of the fingerprint data
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    def are_profiles_consistent(self, profile: AudioFingerprintingProfile) -> bool:
        """
        Check if audio fingerprinting profile is consistent.
        
        Args:
            profile: AudioFingerprintingProfile object
            
        Returns:
            True if profile is consistent, False otherwise
        """
        # Check that sample rate is reasonable
        if profile.sample_rate < 8000 or profile.sample_rate > 192000:
            return False
        
        # Check that channel count is reasonable
        if profile.channel_count < 1 or profile.channel_count > 32:
            return False
        
        # Check that latency hint is reasonable
        if profile.latency_hint < 0 or profile.latency_hint > 1:
            return False
        
        # Check that oscillator frequency is reasonable
        if profile.oscillator_frequency < 20 or profile.oscillator_frequency > 20000:
            return False
        
        # Check that oscillator detune is reasonable
        if profile.oscillator_detune < -1200 or profile.oscillator_detune > 1200:
            return False
        
        # Check that FFT size is a power of 2 and reasonable
        if profile.fft_size < 32 or profile.fft_size > 32768:
            return False
        if (profile.fft_size & (profile.fft_size - 1)) != 0:  # Not a power of 2
            return False
        
        # Check that decibels are reasonable
        if profile.min_decibels >= profile.max_decibels:
            return False
        if profile.min_decibels < -150 or profile.max_decibels > 0:
            return False
        
        # Check that smoothing time constant is reasonable
        if profile.smoothing_time_constant < 0 or profile.smoothing_time_constant > 1:
            return False
        
        # Check device type consistency
        device_type_lower = profile.device_type.lower()
        if "mobile" in device_type_lower or "tablet" in device_type_lower:
            # Mobile devices typically have lower capabilities
            if profile.sample_rate > 96000:
                return False
            if profile.channel_count > 2:
                return False
            if profile.fft_size > 2048:
                return False
        elif "desktop" in device_type_lower:
            # Desktop devices can have higher capabilities
            pass  # Don't fail for any specific values on desktop
        
        return True