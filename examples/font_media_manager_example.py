"""
Example demonstrating advanced font and media simulation.
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ice_locator_mcp.anti_detection.font_media_manager import FontMediaManager, FontProfile, MediaProfile


async def main():
    """Demonstrate font media manager capabilities."""
    print("=== Font and Media Manager Example ===\n")
    
    # Create font media manager
    font_media_manager = FontMediaManager()
    print("✓ FontMediaManager initialized")
    
    # Example 1: Generate a random font list
    print("\n--- Generate Random Font List ---")
    font_list = font_media_manager.get_random_font_list(10)
    print(f"Generated {len(font_list)} fonts:")
    for i, font in enumerate(font_list[:5]):  # Show first 5
        print(f"  {i+1}. {font.name} ({font.generic_family})")
        if font.is_monospace:
            print(f"     - Monospace: {font.is_monospace}")
        if font.is_serif:
            print(f"     - Serif: {font.is_serif}")
    
    # Example 2: Generate a random media profile
    print("\n--- Generate Random Media Profile ---")
    media_profile = font_media_manager.get_random_media_profile()
    print(f"Audio codecs: {len(media_profile.audio_codecs)} supported")
    print(f"Video codecs: {len(media_profile.video_codecs)} supported")
    print(f"Media devices: {len(media_profile.media_devices)} enumerated")
    print(f"WebGL extensions: {len(media_profile.webgl_extensions)} supported")
    print(f"WebGL parameters: {len(media_profile.webgl_parameters)} defined")
    
    # Show some details
    print(f"Sample audio codecs: {media_profile.audio_codecs[:3]}")
    print(f"Sample video codecs: {media_profile.video_codecs[:3]}")
    print(f"Sample WebGL extensions: {media_profile.webgl_extensions[:3]}")
    
    # Show first media device
    if media_profile.media_devices:
        device = media_profile.media_devices[0]
        print(f"Sample media device: {device['kind']} - {device['label']}")
    
    # Example 3: Font analysis
    print("\n--- Font Analysis ---")
    test_fonts = font_media_manager.get_random_font_list(5)
    
    for font in test_fonts:
        print(f"Font: {font.name}")
        print(f"  Generic family: {font.generic_family}")
        print(f"  Monospace: {font_media_manager.is_monospace_font(font)}")
        print(f"  Serif: {font_media_manager.is_serif_font(font)}")
        print(f"  Sans-serif: {font.is_sans_serif}")
        print()
    
    # Example 4: Get font names
    print("\n--- Get Font Names ---")
    font_names = font_media_manager.get_font_names(test_fonts)
    print(f"Font names: {font_names}")
    
    # Example 5: Font and media profile serialization
    print("\n--- Font and Media Profile Serialization ---")
    
    # Serialize font profile
    font_dict = test_fonts[0].to_dict()
    print(f"Serialized font: {font_dict}")
    
    # Deserialize font profile
    deserialized_font = FontProfile.from_dict(font_dict)
    print(f"Deserialized font: {deserialized_font.name}")
    
    # Serialize media profile
    media_dict = media_profile.to_dict()
    print(f"Serialized media profile keys: {list(media_dict.keys())}")
    
    # Deserialize media profile
    deserialized_media = MediaProfile.from_dict(media_dict)
    print(f"Deserialized media profile audio codecs: {len(deserialized_media.audio_codecs)}")
    
    # Example 6: Generate realistic media devices
    print("\n--- Generate Realistic Media Devices ---")
    devices = font_media_manager._generate_realistic_media_devices()
    print(f"Generated {len(devices)} media devices:")
    for i, device in enumerate(devices[:3]):  # Show first 3
        print(f"  {i+1}. {device['kind']} - {device['label']} (ID: {device['deviceId'][:8]}...)")
    
    print("\n=== Font and Media Manager Example Completed ===")


if __name__ == "__main__":
    asyncio.run(main())