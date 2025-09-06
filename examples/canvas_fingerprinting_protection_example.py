"""
Example demonstrating advanced canvas fingerprinting protection.
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.canvas_fingerprinting_protection import CanvasFingerprintingProtectionManager, AdvancedCanvasProfile


async def main():
    """Demonstrate CanvasFingerprintingProtectionManager usage."""
    # Create CanvasFingerprintingProtectionManager instance
    canvas_protection_manager = CanvasFingerprintingProtectionManager()
    
    # Generate a random advanced canvas profile
    canvas_profile = canvas_protection_manager.get_random_canvas_profile()
    print("Random Advanced Canvas Profile:")
    print(f"  Text rendering noise: {canvas_profile.text_rendering_noise}")
    print(f"  Pixel data noise level: {canvas_profile.pixel_data_noise_level}")
    print(f"  Rendering delay range: {canvas_profile.rendering_delay_min}-{canvas_profile.rendering_delay_max}ms")
    print(f"  Image data transformation: {canvas_profile.image_data_transformation}")
    print(f"  Image data block size: {canvas_profile.image_data_block_size}")
    print(f"  Path rendering noise: {canvas_profile.path_rendering_noise}")
    print()
    
    # Generate device-specific profiles
    desktop_profile = canvas_protection_manager.get_device_specific_profile("desktop")
    mobile_profile = canvas_protection_manager.get_device_specific_profile("mobile")
    tablet_profile = canvas_protection_manager.get_device_specific_profile("tablet")
    
    print("Device-Specific Canvas Profiles:")
    print(f"  Desktop - Text noise: {desktop_profile.text_rendering_noise}, Path noise: {desktop_profile.path_rendering_noise}")
    print(f"  Mobile - Text noise: {mobile_profile.text_rendering_noise}, Path noise: {mobile_profile.path_rendering_noise}")
    print(f"  Tablet - Text noise: {tablet_profile.text_rendering_noise}, Path noise: {tablet_profile.path_rendering_noise}")
    print()
    
    # Generate a canvas fingerprint
    fingerprint = canvas_protection_manager.generate_canvas_fingerprint(canvas_profile)
    print("Canvas Fingerprint:")
    print(f"  Hash: {fingerprint}")
    print()
    
    # Check profile consistency
    is_consistent = canvas_protection_manager.are_profiles_consistent(canvas_profile)
    print("Profile Consistency:")
    print(f"  Canvas profile consistent: {is_consistent}")
    print()
    
    # Generate protection JavaScript code
    js_code = canvas_protection_manager._generate_canvas_protection_js(canvas_profile)
    print("Generated JavaScript Code:")
    print(f"  JS length: {len(js_code)} characters")
    print()
    
    # Example of creating a custom profile
    custom_profile = AdvancedCanvasProfile(
        text_rendering_noise=0.03,
        text_baseline_variation=0.015,
        font_smoothing_variation=True,
        pixel_data_noise_level=0.01,
        pixel_data_rounding=2,
        color_depth_variation=True,
        rendering_delay_min=2.0,
        rendering_delay_max=10.0,
        timing_jitter=1.0,
        image_data_transformation="noise",
        image_data_block_size=8,
        path_rendering_noise=0.02,
        line_cap_variation=True,
        line_join_variation=True,
        composite_operation_variations=True,
        global_alpha_variation=0.05,
        gradient_noise_level=0.02,
        pattern_distortion_level=0.02,
        webgl_context_protection=True,
        webgl_parameter_noise=0.01
    )
    
    print("Custom Canvas Profile:")
    print(f"  Custom text noise: {custom_profile.text_rendering_noise}")
    print(f"  Custom pixel noise: {custom_profile.pixel_data_noise_level}")
    print(f"  Custom transformation: {custom_profile.image_data_transformation}")
    print()
    
    # Generate fingerprint for custom profile
    custom_fingerprint = canvas_protection_manager.generate_canvas_fingerprint(custom_profile)
    print("Custom Profile Fingerprint:")
    print(f"  Hash: {custom_fingerprint}")
    print()


if __name__ == "__main__":
    asyncio.run(main())