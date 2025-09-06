"""
Example demonstrating advanced WebGL and canvas rendering simulation.
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.webgl_canvas_manager import WebGLCanvasManager, WebGLProfile, CanvasProfile


async def main():
    """Demonstrate WebGLCanvasManager usage."""
    # Create WebGLCanvasManager instance
    webgl_canvas_manager = WebGLCanvasManager()
    
    # Generate a random WebGL profile
    webgl_profile = webgl_canvas_manager.get_random_webgl_profile()
    print("Random WebGL Profile:")
    print(f"  Vendor: {webgl_profile.vendor}")
    print(f"  Renderer: {webgl_profile.renderer}")
    print(f"  Extensions: {len(webgl_profile.extensions)} extensions")
    print(f"  Parameters: {len(webgl_profile.parameters)} parameters")
    print()
    
    # Generate a random canvas profile
    canvas_profile = webgl_canvas_manager.get_random_canvas_profile()
    print("Random Canvas Profile:")
    print(f"  Text rendering variations: {canvas_profile.text_rendering_variations}")
    print(f"  Noise injection level: {canvas_profile.noise_injection_level}")
    print(f"  Rendering timing variation: {canvas_profile.rendering_timing_variation}")
    print()
    
    # Generate a completely realistic WebGL and canvas profile
    realistic_webgl = webgl_canvas_manager.generate_realistic_webgl_profile()
    realistic_canvas = webgl_canvas_manager.generate_realistic_canvas_profile()
    print("Realistic WebGL Profile:")
    print(f"  Vendor: {realistic_webgl.vendor}")
    print(f"  Renderer: {realistic_webgl.renderer}")
    print()
    
    print("Realistic Canvas Profile:")
    print(f"  Text rendering variations: {realistic_canvas.text_rendering_variations}")
    print(f"  Noise injection level: {realistic_canvas.noise_injection_level}")
    print()
    
    # Generate WebGL and canvas fingerprints
    webgl_fingerprint = webgl_canvas_manager.generate_webgl_fingerprint(realistic_webgl)
    canvas_fingerprint = webgl_canvas_manager.generate_canvas_fingerprint(realistic_canvas)
    print("WebGL Fingerprint:")
    print(f"  Hash: {webgl_fingerprint}")
    print()
    
    print("Canvas Fingerprint:")
    print(f"  Hash: {canvas_fingerprint}")
    print()
    
    # Check profile consistency
    is_webgl_consistent = webgl_canvas_manager.is_webgl_profile_consistent(realistic_webgl)
    is_canvas_consistent = webgl_canvas_manager.is_canvas_profile_consistent(realistic_canvas)
    print("Profile Consistency:")
    print(f"  WebGL profile consistent: {is_webgl_consistent}")
    print(f"  Canvas profile consistent: {is_canvas_consistent}")
    print()
    
    # Generate spoofing JavaScript code
    webgl_js = webgl_canvas_manager._generate_webgl_spoofing_js(realistic_webgl)
    canvas_js = webgl_canvas_manager._generate_canvas_spoofing_js(realistic_canvas)
    print("Generated JavaScript Code:")
    print(f"  WebGL JS length: {len(webgl_js)} characters")
    print(f"  Canvas JS length: {len(canvas_js)} characters")
    print()


if __name__ == "__main__":
    asyncio.run(main())