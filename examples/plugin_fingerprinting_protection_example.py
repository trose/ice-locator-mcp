"""
Example demonstrating advanced plugin and extension fingerprinting protection.
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.plugin_fingerprinting_protection import PluginFingerprintingProtectionManager, PluginFingerprintingProfile


async def main():
    """Demonstrate PluginFingerprintingProtectionManager usage."""
    # Create PluginFingerprintingProtectionManager instance
    plugin_manager = PluginFingerprintingProtectionManager()
    
    # Generate a random plugin and extension fingerprinting profile
    profile = plugin_manager.get_random_profile()
    print("Random Plugin and Extension Profile:")
    print(f"  Device Type: {profile.device_type}")
    print(f"  Plugin Count: {len(profile.plugins)}")
    print(f"  Extension Count: {len(profile.extensions)}")
    print(f"  Is Consistent: {profile.is_consistent}")
    print()
    
    # Display plugin information
    print("Plugins:")
    for i, plugin in enumerate(profile.plugins):
        print(f"  {i+1}. {plugin.name}")
        print(f"     Filename: {plugin.filename}")
        print(f"     Description: {plugin.description}")
    print()
    
    # Display extension information
    print("Extensions:")
    for i, ext in enumerate(profile.extensions):
        print(f"  {i+1}. {ext.name} (v{ext.version})")
        print(f"     ID: {ext.id}")
        print(f"     Description: {ext.description}")
        print(f"     Permissions: {', '.join(ext.permissions)}")
        print(f"     Enabled: {ext.enabled}")
    print()
    
    # Generate a fingerprint for this profile
    fingerprint = plugin_manager.generate_fingerprint(profile)
    print(f"Profile Fingerprint: {fingerprint}")
    print()
    
    # Generate device-specific profiles
    print("Device-Specific Profiles:")
    
    # Desktop profile
    desktop_profile = plugin_manager.get_device_specific_profile("desktop")
    desktop_fingerprint = plugin_manager.generate_fingerprint(desktop_profile)
    print(f"  Desktop: {len(desktop_profile.plugins)} plugins, {len(desktop_profile.extensions)} extensions")
    print(f"  Desktop Fingerprint: {desktop_fingerprint[:16]}...")
    print()
    
    # Mobile profile
    mobile_profile = plugin_manager.get_device_specific_profile("mobile")
    mobile_fingerprint = plugin_manager.generate_fingerprint(mobile_profile)
    print(f"  Mobile: {len(mobile_profile.plugins)} plugins, {len(mobile_profile.extensions)} extensions")
    print(f"  Mobile Fingerprint: {mobile_fingerprint[:16]}...")
    print()
    
    # Tablet profile
    tablet_profile = plugin_manager.get_device_specific_profile("tablet")
    tablet_fingerprint = plugin_manager.generate_fingerprint(tablet_profile)
    print(f"  Tablet: {len(tablet_profile.plugins)} plugins, {len(tablet_profile.extensions)} extensions")
    print(f"  Tablet Fingerprint: {tablet_fingerprint[:16]}...")
    print()
    
    # Check profile consistency
    print("Profile Consistency Checks:")
    print(f"  Random Profile Consistent: {plugin_manager.are_profiles_consistent(profile)}")
    print(f"  Desktop Profile Consistent: {plugin_manager.are_profiles_consistent(desktop_profile)}")
    print(f"  Mobile Profile Consistent: {plugin_manager.are_profiles_consistent(mobile_profile)}")
    print(f"  Tablet Profile Consistent: {plugin_manager.are_profiles_consistent(tablet_profile)}")
    print()
    
    # Generate JavaScript code for spoofing
    js_code = plugin_manager._generate_spoofing_js(profile)
    print(f"Generated JavaScript Code Length: {len(js_code)} characters")
    print("JavaScript code would be used to spoof plugin and extension information in browser contexts.")


if __name__ == "__main__":
    asyncio.run(main())