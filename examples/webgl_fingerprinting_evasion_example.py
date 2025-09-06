"""
Example demonstrating advanced WebGL fingerprinting evasion.
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.webgl_fingerprinting_evasion import WebGLFingerprintingEvasionManager, AdvancedWebGLProfile


async def main():
    """Demonstrate WebGLFingerprintingEvasionManager usage."""
    # Create WebGLFingerprintingEvasionManager instance
    webgl_evasion_manager = WebGLFingerprintingEvasionManager()
    
    # Generate a random WebGL profile
    webgl_profile = webgl_evasion_manager.get_random_webgl_profile()
    print("Random WebGL Profile:")
    print(f"  Vendor: {webgl_profile.vendor}")
    print(f"  Renderer: {webgl_profile.renderer}")
    print(f"  Unmasked Vendor: {webgl_profile.unmasked_vendor}")
    print(f"  Unmasked Renderer: {webgl_profile.unmasked_renderer}")
    print(f"  Version: {webgl_profile.version}")
    print(f"  Extensions: {len(webgl_profile.extensions)} extensions")
    print(f"  Max Texture Size: {webgl_profile.max_texture_size}")
    print(f"  WebGL Version: {webgl_profile.preferred_webgl_version}")
    print()
    
    # Generate a WebGL 1 profile
    webgl1_profile = webgl_evasion_manager.get_random_webgl_profile(1)
    print("WebGL 1 Profile:")
    print(f"  Vendor: {webgl1_profile.vendor}")
    print(f"  Renderer: {webgl1_profile.renderer}")
    print(f"  Version: {webgl1_profile.version}")
    print(f"  Extensions: {len(webgl1_profile.extensions)} extensions")
    print()
    
    # Generate a WebGL 2 profile
    webgl2_profile = webgl_evasion_manager.get_random_webgl_profile(2)
    print("WebGL 2 Profile:")
    print(f"  Vendor: {webgl2_profile.vendor}")
    print(f"  Renderer: {webgl2_profile.renderer}")
    print(f"  Version: {webgl2_profile.version}")
    print(f"  Extensions: {len(webgl2_profile.extensions)} extensions")
    print()
    
    # Generate WebGL fingerprints
    fingerprint1 = webgl_evasion_manager.generate_webgl_fingerprint(webgl_profile)
    fingerprint2 = webgl_evasion_manager.generate_webgl_fingerprint(webgl1_profile)
    fingerprint3 = webgl_evasion_manager.generate_webgl_fingerprint(webgl2_profile)
    print("WebGL Fingerprints:")
    print(f"  Random Profile: {fingerprint1}")
    print(f"  WebGL 1 Profile: {fingerprint2}")
    print(f"  WebGL 2 Profile: {fingerprint3}")
    print()
    
    # Check profile consistency
    is_consistent1 = webgl_evasion_manager.is_webgl_profile_consistent(webgl_profile)
    is_consistent2 = webgl_evasion_manager.is_webgl_profile_consistent(webgl1_profile)
    is_consistent3 = webgl_evasion_manager.is_webgl_profile_consistent(webgl2_profile)
    print("Profile Consistency:")
    print(f"  Random Profile: {is_consistent1}")
    print(f"  WebGL 1 Profile: {is_consistent2}")
    print(f"  WebGL 2 Profile: {is_consistent3}")
    print()
    
    # Generate evasion JavaScript code
    js_code = webgl_evasion_manager._generate_webgl_evasion_js(webgl_profile)
    print("Generated JavaScript Code:")
    print(f"  JavaScript length: {len(js_code)} characters")
    print(f"  Contains WebGLRenderingContext: {'WebGLRenderingContext' in js_code}")
    print(f"  Contains WebGL2RenderingContext: {'WebGL2RenderingContext' in js_code}")
    print(f"  Contains UNMASKED_VENDOR_WEBGL: {'UNMASKED_VENDOR_WEBGL' in js_code}")
    print()


if __name__ == "__main__":
    asyncio.run(main())