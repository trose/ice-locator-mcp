"""
Browser Extension Simulation System for ICE Locator MCP Server.

This module provides browser extension simulation to make the browser appear more realistic
by implementing common extension fingerprints and behaviors.
"""

import asyncio
import json
import time
import random
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import structlog


@dataclass
class ExtensionProfile:
    """Represents a browser extension with its properties."""
    id: str
    name: str
    version: str
    description: str
    permissions: List[str]
    enabled: bool = True
    installed_at: float = time.time()
    last_updated: float = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExtensionProfile':
        """Create from dictionary."""
        return cls(**data)


class ExtensionManager:
    """Manages browser extension simulation to make the browser appear more realistic."""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        
        # Common browser extensions with realistic properties
        self.common_extensions = [
            ExtensionProfile(
                id="nmmhkkegccagdldgiimedpiccmgmieda",
                name="Chrome Web Store Payments",
                version="1.0.0.7",
                description="Provides payment methods in the Chrome Web Store",
                permissions=["webRequest", "webRequestBlocking", "storage"]
            ),
            ExtensionProfile(
                id="pjkljhegncpnkpknbcohdijeoejaedia",
                name="Gmail",
                version="8.1",
                description="Gmail Chrome App",
                permissions=["identity", "identity.email", "storage"]
            ),
            ExtensionProfile(
                id="apdfllckaahabafndbhieahigkjlhalf",
                name="Google Drive",
                version="14.1",
                description="Google Drive Chrome App",
                permissions=["identity", "storage"]
            ),
            ExtensionProfile(
                id="ghbmnnjooekpmoecnnnilnnbdlolhkhi",
                name="Google Docs Offline",
                version="1.7",
                description="Edit, create, and view your documents, spreadsheets, and presentations offline",
                permissions=["unlimitedStorage", "storage"]
            ),
            ExtensionProfile(
                id="aapbdbdomjkkjkaonfhkkikfgjllcleb",
                name="Google Translate",
                version="2.0.7",
                description="View translations easily as you browse the web",
                permissions=["activeTab", "contextMenus", "storage"]
            ),
            ExtensionProfile(
                id="coobgpohoikkiipiblmjeljniedjpjpf",
                name="Grammarly for Chrome",
                version="14.932.1",
                description="Grammarly helps you write mistake-free English anywhere on the web",
                permissions=["activeTab", "contextMenus", "storage", "tabs", "webNavigation", "webRequest", "webRequestBlocking"]
            ),
            ExtensionProfile(
                id="cjpalhdlnbpafiamejdnhcphjbkeiagm",
                name="uBlock Origin",
                version="1.58.0",
                description="Finally, an efficient blocker. Easy on CPU and memory.",
                permissions=["activeTab", "storage", "tabs", "unlimitedStorage", "webNavigation", "webRequest", "webRequestBlocking"]
            ),
            ExtensionProfile(
                id="gighmmpiobklfepjocnamgkkbiglidom",
                name="AdBlock",
                version="4.46.0",
                description="Block ads and pop-ups on YouTube, Facebook, Twitch, and your favorite websites",
                permissions=["activeTab", "storage", "tabs", "unlimitedStorage", "webNavigation", "webRequest", "webRequestBlocking"]
            ),
            ExtensionProfile(
                id="dbepggeogbaibhgnhhndojpepiihcmeb",
                name="Video Downloader professional",
                version="5.2.3",
                description="Download videos from any website in any format and quality",
                permissions=["activeTab", "downloads", "storage", "tabs", "webNavigation", "webRequest", "webRequestBlocking"]
            ),
            ExtensionProfile(
                id="bfbmjmiodbnnpllbbbfblcplfjjepjdn",
                name="YouTube Video Downloader",
                version="4.1.1",
                description="Download any YouTube video with this simple extension",
                permissions=["activeTab", "downloads", "storage", "tabs"]
            )
        ]
        
        # Extension behavior patterns
        self.extension_behaviors = {
            "ad_blocker": {
                "request_blocking": True,
                "content_script_injection": True,
                "dom_modification": True,
                "network_monitoring": True
            },
            "grammar_checker": {
                "content_script_injection": True,
                "text_analysis": True,
                "context_menu": True
            },
            "translator": {
                "content_script_injection": True,
                "context_menu": True,
                "popup_ui": True
            },
            "video_downloader": {
                "content_script_injection": True,
                "download_monitoring": True,
                "context_menu": True
            }
        }
    
    def get_random_extensions(self, count: int = 5) -> List[ExtensionProfile]:
        """Get a random selection of extensions to simulate."""
        # Always include some core extensions
        selected_extensions = [
            self.common_extensions[0],  # Chrome Web Store Payments
            self.common_extensions[3]   # Google Docs Offline
        ]
        
        # Add random extensions
        remaining_extensions = [ext for ext in self.common_extensions if ext not in selected_extensions]
        additional_count = min(count - len(selected_extensions), len(remaining_extensions))
        selected_extensions.extend(random.sample(remaining_extensions, additional_count))
        
        # Randomize enabled status (most extensions are enabled)
        for ext in selected_extensions:
            ext.enabled = random.random() > 0.1  # 90% chance of being enabled
            ext.last_updated = time.time() - random.randint(0, 30 * 24 * 60 * 60)  # Updated within last 30 days
        
        return selected_extensions
    
    def generate_extension_fingerprints(self, extensions: List[ExtensionProfile]) -> Dict[str, Any]:
        """Generate realistic extension fingerprints for browser simulation."""
        # Create chrome.runtime.getManifest() like data
        manifest_data = []
        for ext in extensions:
            if ext.enabled:
                manifest_data.append({
                    "name": ext.name,
                    "version": ext.version,
                    "description": ext.description,
                    "permissions": ext.permissions,
                    "manifest_version": 3 if random.random() > 0.3 else 2,  # Most are MV3 now
                    "key": self._generate_extension_key()
                })
        
        # Create chrome.management.getAll() like data
        management_data = []
        for ext in extensions:
            management_data.append({
                "id": ext.id,
                "name": ext.name,
                "version": ext.version,
                "description": ext.description,
                "enabled": ext.enabled,
                "type": "extension",
                "homepageUrl": f"https://chrome.google.com/webstore/detail/{ext.id}",
                "installType": "normal",
                "mayDisable": True,
                "offlineEnabled": False,
                "optionsUrl": "",
                "permissions": ext.permissions,
                "shortName": ext.name,
                "updateUrl": "https://clients2.google.com/service/update2/crx",
                "versionName": ext.version
            })
        
        return {
            "manifests": manifest_data,
            "management": management_data,
            "count": len([ext for ext in extensions if ext.enabled])
        }
    
    def _generate_extension_key(self) -> str:
        """Generate a realistic extension key."""
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        return ''.join(random.choice(chars) for _ in range(56)) + "="
    
    async def inject_extension_scripts(self, extensions: List[ExtensionProfile]) -> str:
        """Generate JavaScript code to inject extension-like behavior into the browser."""
        js_code = """
        // Extension simulation script
        (function() {
            // Simulate chrome object with extension properties
            if (!window.chrome) {
                window.chrome = {};
            }
            
            // Add extension-specific APIs
            window.chrome.runtime = window.chrome.runtime || {};
            window.chrome.management = window.chrome.management || {};
            window.chrome.extension = window.chrome.extension || {};
            
            // Simulate extension manifest
            window.chrome.runtime.getManifest = function() {
                return {
                    "manifest_version": 3,
                    "name": "Browser Extension Simulator",
                    "version": "1.0.0",
                    "description": "Simulates browser extensions for realistic fingerprinting",
                    "permissions": ["activeTab", "storage", "contextMenus"]
                };
            };
            
            // Simulate extension ID
            window.chrome.runtime.id = "simulated-extension-id";
            
            // Simulate extension connect
            window.chrome.runtime.connect = function() {
                return {
                    onMessage: { addListener: function() {} },
                    onDisconnect: { addListener: function() {} },
                    postMessage: function() {},
                    disconnect: function() {}
                };
            };
            
            // Simulate extension sendMessage
            window.chrome.runtime.sendMessage = function() {
                // Simulate async response
                setTimeout(() => {}, Math.random() * 100);
            };
            
            // Simulate extension management
            window.chrome.management = {
                getAll: function(callback) {
                    if (callback) {
                        callback([
                            {
                                "id": "simulated-extension-id",
                                "name": "Browser Extension Simulator",
                                "version": "1.0.0",
                                "description": "Simulates browser extensions for realistic fingerprinting",
                                "enabled": true,
                                "type": "extension",
                                "homepageUrl": "https://example.com",
                                "installType": "normal",
                                "mayDisable": true,
                                "offlineEnabled": false,
                                "optionsUrl": "",
                                "permissions": ["activeTab", "storage"],
                                "shortName": "Extension Simulator",
                                "updateUrl": "",
                                "versionName": "1.0.0"
                            }
                        ]);
                    }
                    return Promise.resolve([
                        {
                            "id": "simulated-extension-id",
                            "name": "Browser Extension Simulator",
                            "version": "1.0.0",
                            "description": "Simulates browser extensions for realistic fingerprinting",
                            "enabled": true,
                            "type": "extension",
                            "homepageUrl": "https://example.com",
                            "installType": "normal",
                            "mayDisable": true,
                            "offlineEnabled": false,
                            "optionsUrl": "",
                            "permissions": ["activeTab", "storage"],
                            "shortName": "Extension Simulator",
                            "updateUrl": "",
                            "versionName": "1.0.0"
                        }
                    ]);
                }
            };
            
            // Simulate extension storage
            window.chrome.storage = {
                local: {
                    get: function(keys, callback) {
                        if (callback) callback({});
                        return Promise.resolve({});
                    },
                    set: function(items, callback) {
                        if (callback) callback();
                        return Promise.resolve();
                    },
                    remove: function(keys, callback) {
                        if (callback) callback();
                        return Promise.resolve();
                    },
                    clear: function(callback) {
                        if (callback) callback();
                        return Promise.resolve();
                    }
                },
                sync: {
                    get: function(keys, callback) {
                        if (callback) callback({});
                        return Promise.resolve({});
                    },
                    set: function(items, callback) {
                        if (callback) callback();
                        return Promise.resolve();
                    },
                    remove: function(keys, callback) {
                        if (callback) callback();
                        return Promise.resolve();
                    },
                    clear: function(callback) {
                        if (callback) callback();
                        return Promise.resolve();
                    }
                }
            };
            
            // Simulate extension context menus
            window.chrome.contextMenus = {
                create: function() {},
                update: function() {},
                remove: function() {},
                removeAll: function() {}
            };
            
            // Simulate extension tabs
            window.chrome.tabs = {
                query: function(queryInfo, callback) {
                    if (callback) callback([]);
                    return Promise.resolve([]);
                },
                get: function(tabId, callback) {
                    if (callback) callback(null);
                    return Promise.resolve(null);
                },
                create: function(createProperties, callback) {
                    if (callback) callback({id: Math.floor(Math.random() * 10000)});
                    return Promise.resolve({id: Math.floor(Math.random() * 10000)});
                },
                update: function(tabId, updateProperties, callback) {
                    if (callback) callback({id: tabId});
                    return Promise.resolve({id: tabId});
                },
                remove: function(tabIds, callback) {
                    if (callback) callback();
                    return Promise.resolve();
                }
            };
            
            // Simulate extension web navigation
            window.chrome.webNavigation = {
                onBeforeNavigate: {
                    addListener: function() {}
                },
                onCompleted: {
                    addListener: function() {}
                }
            };
            
            // Simulate extension web request
            window.chrome.webRequest = {
                onBeforeRequest: {
                    addListener: function() {}
                },
                onBeforeSendHeaders: {
                    addListener: function() {}
                },
                onHeadersReceived: {
                    addListener: function() {}
                }
            };
            
            // Add extension-like DOM elements
            function addExtensionIndicators() {
                // Add extension-like meta tags
                const metaExtension = document.createElement('meta');
                metaExtension.name = "extension-version";
                metaExtension.content = "1.0.0";
                document.head.appendChild(metaExtension);
                
                // Add extension-like classes to body
                document.body.classList.add('extension-simulated');
                
                // Simulate extension content script injection timing
                document.documentElement.setAttribute('data-extension-injected', Date.now().toString());
            }
            
            // Run when DOM is ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', addExtensionIndicators);
            } else {
                addExtensionIndicators();
            }
            
            // Simulate extension background script behavior
            function simulateExtensionActivity() {
                // Simulate periodic extension activity
                setInterval(() => {
                    // Simulate storage operations
                    if (window.chrome.storage) {
                        window.chrome.storage.local.get('lastActivity', () => {});
                    }
                    
                    // Simulate message passing
                    if (window.chrome.runtime && Math.random() > 0.7) {
                        window.chrome.runtime.sendMessage({type: 'heartbeat', timestamp: Date.now()});
                    }
                }, Math.random() * 30000 + 10000); // Every 10-40 seconds
                
                // Simulate initial extension load delay
                setTimeout(() => {
                    document.documentElement.setAttribute('data-extension-loaded', 'true');
                }, Math.random() * 2000 + 500); // 0.5-2.5 seconds after DOM ready
            }
            
            simulateExtensionActivity();
        })();
        """
        
        return js_code
    
    def get_extension_categories(self, extensions: List[ExtensionProfile]) -> Set[str]:
        """Get categories of extensions for behavior simulation."""
        categories = set()
        
        ad_blocker_names = ["ublock", "adblock", "adguard", "adblocker"]
        grammar_names = ["grammarly", "grammar", "languagetool"]
        translator_names = ["translate", "translation", "linguee", "deepl"]
        downloader_names = ["download", "video", "audio", "media"]
        
        for ext in extensions:
            name_lower = ext.name.lower()
            if any(name in name_lower for name in ad_blocker_names):
                categories.add("ad_blocker")
            elif any(name in name_lower for name in grammar_names):
                categories.add("grammar_checker")
            elif any(name in name_lower for name in translator_names):
                categories.add("translator")
            elif any(name in name_lower for name in downloader_names):
                categories.add("video_downloader")
        
        return categories
    
    async def simulate_extension_behavior(self, extensions: List[ExtensionProfile]) -> str:
        """Generate JavaScript code to simulate realistic extension behavior patterns."""
        categories = self.get_extension_categories(extensions)
        
        js_code = """
        // Extension behavior simulation
        (function() {
            // Simulate realistic timing delays for extension-like behavior
            function randomDelay(min, max) {
                return Math.random() * (max - min) + min;
            }
            
            // Simulate content script injection delays
            setTimeout(() => {
                // Add extension-like attributes to DOM
                document.documentElement.setAttribute('data-extension-behavior', 'simulated');
                
                // Simulate extension API usage patterns
                function simulateAPIUsage() {
        """
        
        # Add behavior based on extension categories
        if "ad_blocker" in categories:
            js_code += """
                    // Simulate ad blocker behavior
                    if (Math.random() > 0.8) {
                        // Simulate DOM modification for ad blocking
                        const observer = new MutationObserver(() => {
                            // Would normally look for and hide ad elements
                        });
                        observer.observe(document.body, { childList: true, subtree: true });
                    }
            """
        
        if "grammar_checker" in categories:
            js_code += """
                    // Simulate grammar checker behavior
                    if (Math.random() > 0.7) {
                        // Simulate text analysis on input fields
                        document.addEventListener('input', (e) => {
                            if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT') {
                                // Would normally analyze text for grammar
                                setTimeout(() => {}, randomDelay(100, 500));
                            }
                        });
                    }
            """
        
        if "translator" in categories:
            js_code += """
                    // Simulate translator behavior
                    if (Math.random() > 0.6) {
                        // Simulate context menu additions
                        document.addEventListener('contextmenu', () => {
                            // Would normally add translation options
                            setTimeout(() => {}, randomDelay(50, 200));
                        });
                    }
            """
        
        js_code += """
                }
                
                // Simulate periodic extension activity
                setInterval(simulateAPIUsage, randomDelay(10000, 30000));
                simulateAPIUsage();
            }, randomDelay(1000, 3000)); // Initial delay
        })();
        """
        
        return js_code