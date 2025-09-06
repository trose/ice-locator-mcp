"""
Plugin and Extension Fingerprinting Protection Manager for ICE Locator MCP Server.

This module provides advanced plugin and extension fingerprinting protection to prevent 
browser fingerprinting based on installed plugins and extensions.
"""

import random
import structlog
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from playwright.async_api import BrowserContext


@dataclass
class PluginProfile:
    """Represents a browser plugin with realistic properties."""
    name: str
    filename: str
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginProfile':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class ExtensionProfile:
    """Represents a browser extension with realistic properties."""
    id: str
    name: str
    version: str
    description: str
    permissions: List[str]
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExtensionProfile':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class PluginFingerprintingProfile:
    """Represents a plugin and extension fingerprinting configuration with realistic properties."""
    # Plugin information
    plugins: List[PluginProfile]
    
    # Extension information
    extensions: List[ExtensionProfile]
    
    # Device type
    device_type: str  # Type of device (desktop, mobile, tablet)
    
    # Consistency flags
    is_consistent: bool  # Whether the profile is internally consistent
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "plugins": [plugin.to_dict() for plugin in self.plugins],
            "extensions": [ext.to_dict() for ext in self.extensions],
            "device_type": self.device_type,
            "is_consistent": self.is_consistent
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginFingerprintingProfile':
        """Create from dictionary."""
        plugins = [PluginProfile.from_dict(plugin) for plugin in data["plugins"]]
        extensions = [ExtensionProfile.from_dict(ext) for ext in data["extensions"]]
        return cls(
            plugins=plugins,
            extensions=extensions,
            device_type=data["device_type"],
            is_consistent=data["is_consistent"]
        )


class PluginFingerprintingProtectionManager:
    """Manages advanced plugin and extension fingerprinting protection."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        
        # Common browser plugins with realistic properties
        self.common_plugins = [
            PluginProfile(
                name="Chrome PDF Plugin",
                filename="internal-pdf-viewer",
                description="Portable Document Format"
            ),
            PluginProfile(
                name="Chrome PDF Viewer",
                filename="mhjfbmdgcfjbbpaeojofohoefgiehjai",
                description="Portable Document Format"
            ),
            PluginProfile(
                name="Native Client",
                filename="internal-nacl-plugin",
                description="Native Client"
            ),
            PluginProfile(
                name="Shockwave Flash",
                filename="pepflashplayer.dll",
                description="Shockwave Flash 32.0 r0"
            ),
            PluginProfile(
                name="Widevine Content Decryption Module",
                filename="widevinecdmadapter.dll",
                description="Enables Widevine licenses for encrypted media"
            ),
            PluginProfile(
                name="Chrome Media Router",
                filename="cast_sender.js",
                description="Chrome Media Router"
            )
        ]
        
        # Common browser extensions with realistic properties
        self.common_extensions = [
            ExtensionProfile(
                id="nmmhkkegccagdldgiimedpiccmgmieda",
                name="Chrome Web Store Payments",
                version="1.0.0.6",
                description="Support for payments in the Chrome Web Store",
                permissions=["activeTab", "storage"],
                enabled=True
            ),
            ExtensionProfile(
                id="pjkljhegncpnkpknbcohdijeoejaedia",
                name="Gmail",
                version="8.1",
                description="Gmail Chrome App",
                permissions=["identity", "storage"],
                enabled=True
            ),
            ExtensionProfile(
                id="apdfllckaahabafndbhieahigkjlhalf",
                name="Google Drive",
                version="14.1",
                description="Google Drive Chrome App",
                permissions=["identity", "storage"],
                enabled=True
            ),
            ExtensionProfile(
                id="aohghmighlieiainnegkcijnfilokake",
                name="Google Docs",
                version="0.10",
                description="Create and edit documents",
                permissions=["identity", "storage"],
                enabled=True
            ),
            ExtensionProfile(
                id="blpcfgokakmgnkcojhhkbfbldkacnbeo",
                name="YouTube",
                version="4.2.8",
                description="Enjoy YouTube videos",
                permissions=["activeTab"],
                enabled=True
            ),
            ExtensionProfile(
                id="felcaaldnbdncclmgdcncolpebgiejap",
                name="Google Sheets",
                version="1.1",
                description="Create and edit spreadsheets",
                permissions=["identity", "storage"],
                enabled=True
            ),
            ExtensionProfile(
                id="ghbmnnjooekpmoecnnnilnnbdlolhkhi",
                name="Google Slides",
                version="0.10",
                description="Create and edit presentations",
                permissions=["identity", "storage"],
                enabled=True
            )
        ]
        
        # Device-specific plugin and extension configurations
        self.device_configs = {
            "desktop": {
                "plugin_count_range": (3, 6),
                "extension_count_range": (5, 10),
                "common_plugins": self.common_plugins,
                "common_extensions": self.common_extensions
            },
            "mobile": {
                "plugin_count_range": (1, 3),
                "extension_count_range": (2, 5),
                "common_plugins": [plugin for plugin in self.common_plugins if "PDF" in plugin.name],
                "common_extensions": [ext for ext in self.common_extensions if "Google" in ext.name]
            },
            "tablet": {
                "plugin_count_range": (2, 4),
                "extension_count_range": (3, 7),
                "common_plugins": [plugin for plugin in self.common_plugins if "PDF" in plugin.name or "Flash" not in plugin.name],
                "common_extensions": self.common_extensions
            }
        }
    
    def get_random_profile(self) -> PluginFingerprintingProfile:
        """
        Get a random plugin and extension fingerprinting profile with realistic properties.
        
        Returns:
            PluginFingerprintingProfile with realistic properties
        """
        device_type = random.choice(list(self.device_configs.keys()))
        config = self.device_configs[device_type]
        
        # Select random plugins
        plugin_count = random.randint(*config["plugin_count_range"])
        plugins = random.sample(config["common_plugins"], min(plugin_count, len(config["common_plugins"])))
        
        # Select random extensions
        extension_count = random.randint(*config["extension_count_range"])
        extensions = random.sample(config["common_extensions"], min(extension_count, len(config["common_extensions"])))
        
        # Randomize extension enabled status (most extensions are enabled)
        for ext in extensions:
            ext.enabled = random.random() > 0.1  # 90% chance of being enabled
        
        return PluginFingerprintingProfile(
            plugins=plugins,
            extensions=extensions,
            device_type=device_type,
            is_consistent=True
        )
    
    def get_device_specific_profile(self, device_type: str) -> PluginFingerprintingProfile:
        """
        Get a device-specific plugin and extension fingerprinting profile.
        
        Args:
            device_type: Type of device (desktop, mobile, tablet)
            
        Returns:
            PluginFingerprintingProfile with device-specific properties
        """
        if device_type not in self.device_configs:
            return self.get_random_profile()
        
        config = self.device_configs[device_type]
        
        # Select random plugins
        plugin_count = random.randint(*config["plugin_count_range"])
        plugins = random.sample(config["common_plugins"], min(plugin_count, len(config["common_plugins"])))
        
        # Select random extensions
        extension_count = random.randint(*config["extension_count_range"])
        extensions = random.sample(config["common_extensions"], min(extension_count, len(config["common_extensions"])))
        
        # Randomize extension enabled status (most extensions are enabled)
        for ext in extensions:
            ext.enabled = random.random() > 0.1  # 90% chance of being enabled
        
        return PluginFingerprintingProfile(
            plugins=plugins,
            extensions=extensions,
            device_type=device_type,
            is_consistent=True
        )
    
    async def apply_plugin_fingerprinting_protection(self, context: BrowserContext,
                                                   profile: Optional[PluginFingerprintingProfile] = None) -> None:
        """
        Apply advanced plugin and extension fingerprinting protection to a browser context.
        
        Args:
            context: Playwright BrowserContext to apply protection to
            profile: PluginFingerprintingProfile object, or None to generate random
        """
        if profile is None:
            profile = self.get_random_profile()
        
        try:
            # Generate JavaScript to spoof plugin and extension information
            spoofing_js = self._generate_spoofing_js(profile)
            
            # Add JavaScript to context
            await context.add_init_script(spoofing_js)
            
            self.logger.debug(
                "Applied advanced plugin and extension fingerprinting protection to context",
                plugin_count=len(profile.plugins),
                extension_count=len(profile.extensions),
                device_type=profile.device_type
            )
            
        except Exception as e:
            self.logger.error("Failed to apply plugin and extension fingerprinting protection to context", error=str(e))
            raise
    
    def _generate_spoofing_js(self, profile: PluginFingerprintingProfile) -> str:
        """
        Generate JavaScript to spoof plugin and extension information.
        
        Args:
            profile: PluginFingerprintingProfile object
            
        Returns:
            JavaScript code string
        """
        # Create plugins JSON
        plugins_json = str([{
            "name": plugin.name.replace('"', '\\"'),
            "filename": plugin.filename.replace('"', '\\"'),
            "description": plugin.description.replace('"', '\\"')
        } for plugin in profile.plugins])
        
        # Create extensions JSON (only enabled extensions)
        enabled_extensions = [ext for ext in profile.extensions if ext.enabled]
        extensions_json = str([{
            "id": ext.id.replace('"', '\\"'),
            "name": ext.name.replace('"', '\\"'),
            "version": ext.version.replace('"', '\\"'),
            "description": ext.description.replace('"', '\\"'),
            "permissions": ext.permissions,
            "enabled": ext.enabled
        } for ext in enabled_extensions])
        
        # Create all extensions JSON (for management API)
        all_extensions_json = str([{
            "id": ext.id.replace('"', '\\"'),
            "name": ext.name.replace('"', '\\"'),
            "version": ext.version.replace('"', '\\"'),
            "description": ext.description.replace('"', '\\"'),
            "permissions": ext.permissions,
            "enabled": ext.enabled
        } for ext in profile.extensions])
        
        js_code = f"""
        // Advanced Plugin and Extension Fingerprinting Protection
        (function() {{
            // Spoof navigator.plugins
            const pluginData = {plugins_json};
            
            // Create a fake PluginArray
            function createPluginArray(plugins) {{
                const pluginArray = [];
                
                plugins.forEach(plugin => {{
                    const pluginObj = {{
                        name: plugin.name,
                        filename: plugin.filename,
                        description: plugin.description,
                        length: 0,
                        item: function(index) {{ return null; }},
                        namedItem: function(name) {{ return null; }},
                        toString: function() {{ return "[object Plugin]"; }}
                    }};
                    pluginArray.push(pluginObj);
                }});
                
                // Add array-like properties
                pluginArray.length = plugins.length;
                pluginArray.item = function(index) {{
                    return this[index] || null;
                }};
                pluginArray.namedItem = function(name) {{
                    for (let i = 0; i < this.length; i++) {{
                        if (this[i].name === name) {{
                            return this[i];
                        }}
                    }}
                    return null;
                }};
                pluginArray.toString = function() {{
                    return "[object PluginArray]";
                }};
                pluginArray.refresh = function() {{}};
                
                return pluginArray;
            }}
            
            // Override navigator.plugins
            if (navigator.plugins) {{
                Object.defineProperty(navigator, 'plugins', {{
                    get: () => createPluginArray(pluginData),
                    configurable: false,
                    enumerable: true
                }});
            }} else {{
                navigator.plugins = createPluginArray(pluginData);
            }}
            
            // Spoof navigator.mimeTypes (related to plugins)
            const mimeTypeData = [
                {{ type: "application/pdf", suffixes: "pdf", description: "Portable Document Format" }},
                {{ type: "text/pdf", suffixes: "pdf", description: "Portable Document Format" }}
            ];
            
            // Create a fake MimeTypeArray
            function createMimeTypeArray(mimeTypes) {{
                const mimeTypeArray = [];
                
                mimeTypes.forEach(mimeType => {{
                    const mimeTypeObj = {{
                        type: mimeType.type,
                        suffixes: mimeType.suffixes,
                        description: mimeType.description,
                        enabledPlugin: null
                    }};
                    mimeTypeArray.push(mimeTypeObj);
                }});
                
                // Add array-like properties
                mimeTypeArray.length = mimeTypes.length;
                mimeTypeArray.item = function(index) {{
                    return this[index] || null;
                }};
                mimeTypeArray.namedItem = function(name) {{
                    for (let i = 0; i < this.length; i++) {{
                        if (this[i].type === name) {{
                            return this[i];
                        }}
                    }}
                    return null;
                }};
                mimeTypeArray.toString = function() {{
                    return "[object MimeTypeArray]";
                }};
                
                return mimeTypeArray;
            }}
            
            // Override navigator.mimeTypes
            if (navigator.mimeTypes) {{
                Object.defineProperty(navigator, 'mimeTypes', {{
                    get: () => createMimeTypeArray(mimeTypeData),
                    configurable: false,
                    enumerable: true
                }});
            }} else {{
                navigator.mimeTypes = createMimeTypeArray(mimeTypeData);
            }}
            
            // Spoof chrome.runtime and chrome.management APIs for extension detection
            if (!window.chrome) {{
                window.chrome = {{}};
            }}
            
            // Add extension-specific APIs
            window.chrome.runtime = window.chrome.runtime || {{}};
            window.chrome.management = window.chrome.management || {{}};
            
            // Simulate chrome.runtime.getManifest
            window.chrome.runtime.getManifest = function() {{
                return {{
                    "manifest_version": 3,
                    "name": "Browser Extension Simulator",
                    "version": "1.0.0",
                    "description": "Simulates browser extensions for realistic fingerprinting",
                    "permissions": ["activeTab", "storage"]
                }};
            }};
            
            // Simulate extension ID
            window.chrome.runtime.id = "simulated-extension-id";
            
            // Simulate chrome.management.getAll
            const extensionData = {extensions_json};
            const allExtensionData = {all_extensions_json};
            
            window.chrome.management.getAll = function(callback) {{
                if (callback) {{
                    setTimeout(() => callback(allExtensionData), 10);
                }}
                return Promise.resolve(allExtensionData);
            }};
            
            // Simulate chrome.management.get
            window.chrome.management.get = function(id, callback) {{
                const extension = allExtensionData.find(ext => ext.id === id);
                if (callback) {{
                    setTimeout(() => callback(extension), 10);
                }}
                return Promise.resolve(extension);
            }};
            
            // Add realistic timing variations to plugin and extension access
            const originalGetPlugins = Object.getOwnPropertyDescriptor(navigator, 'plugins');
            if (originalGetPlugins && originalGetPlugins.get) {{
                const originalGetter = originalGetPlugins.get;
                Object.defineProperty(navigator, 'plugins', {{
                    get: function() {{
                        // Add slight delay to simulate real plugin access
                        const delay = Math.random() * 0.05; // 0-50ms
                        return originalGetter.call(this);
                    }},
                    configurable: false,
                    enumerable: true
                }});
            }}
            
            const originalGetMimeTypes = Object.getOwnPropertyDescriptor(navigator, 'mimeTypes');
            if (originalGetMimeTypes && originalGetMimeTypes.get) {{
                const originalGetter = originalGetMimeTypes.get;
                Object.defineProperty(navigator, 'mimeTypes', {{
                    get: function() {{
                        // Add slight delay to simulate real mime type access
                        const delay = Math.random() * 0.03; // 0-30ms
                        return originalGetter.call(this);
                    }},
                    configurable: false,
                    enumerable: true
                }});
            }}
        }})();
        """
        
        return js_code
    
    def generate_fingerprint(self, profile: PluginFingerprintingProfile) -> str:
        """
        Generate a fingerprint based on plugin and extension profile.
        
        Args:
            profile: PluginFingerprintingProfile object
            
        Returns:
            String fingerprint
        """
        # Create a string representation of the profile
        plugin_data = "|".join([f"{p.name}:{p.filename}" for p in profile.plugins])
        extension_data = "|".join([f"{e.name}:{e.id}:{e.enabled}" for e in profile.extensions])
        
        fingerprint_data = (
            f"{plugin_data}|{extension_data}|{profile.device_type}"
        )
        
        # Generate a hash of the fingerprint data
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    def are_profiles_consistent(self, profile: PluginFingerprintingProfile) -> bool:
        """
        Check if plugin and extension profile is consistent.
        
        Args:
            profile: PluginFingerprintingProfile object
            
        Returns:
            True if profile is consistent, False otherwise
        """
        # Check that plugins have realistic properties
        for plugin in profile.plugins:
            if not plugin.name or not plugin.filename:
                return False
        
        # Check that extensions have realistic properties
        for ext in profile.extensions:
            if not ext.id or not ext.name or not ext.version:
                return False
        
        # Check device type consistency
        if profile.device_type not in self.device_configs:
            return False
        
        # Check plugin count consistency for device type
        config = self.device_configs[profile.device_type]
        plugin_count_range = config["plugin_count_range"]
        extension_count_range = config["extension_count_range"]
        
        if not (plugin_count_range[0] <= len(profile.plugins) <= plugin_count_range[1]):
            return False
        
        if not (extension_count_range[0] <= len(profile.extensions) <= extension_count_range[1]):
            return False
        
        return True