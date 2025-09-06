"""
Example demonstrating request pattern obfuscation features.

This example shows how the request obfuscator randomizes header order,
varies accept-language headers naturally, and avoids predictable patterns.
"""

import asyncio
import random
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ice_locator_mcp.anti_detection.request_obfuscator import RequestObfuscator


async def demonstrate_header_order_randomization():
    """Demonstrate header order randomization."""
    print("=== Header Order Randomization Demo ===")
    
    obfuscator = RequestObfuscator()
    
    # Generate multiple sets of headers
    headers_list = []
    for i in range(5):
        headers = await obfuscator.obfuscate_request(
            session_id=f"demo_session_{i}",
            base_headers={"Custom": f"value_{i}"},
            request_type="general"
        )
        headers_list.append(list(headers.keys()))
        print(f"Request {i+1} header order: {list(headers.keys())}")
    
    print("\n")


async def demonstrate_accept_language_variation():
    """Demonstrate accept-language header variation."""
    print("=== Accept-Language Variation Demo ===")
    
    obfuscator = RequestObfuscator()
    
    # Generate multiple accept-language headers
    for i in range(5):
        # Force profile rotation for more variation
        obfuscator.profile_rotation_time = 0
        
        headers = await obfuscator.obfuscate_request(
            session_id=f"lang_session_{i}",
            base_headers={},
            request_type="general"
        )
        
        if 'Accept-Language' in headers:
            print(f"Request {i+1} Accept-Language: {headers['Accept-Language']}")
    
    print("\n")


async def demonstrate_request_timing_variation():
    """Demonstrate request timing variation."""
    print("=== Request Timing Variation Demo ===")
    
    obfuscator = RequestObfuscator()
    
    # Calculate multiple delays
    delays = []
    for i in range(10):
        delay = await obfuscator.calculate_delay(
            session_id="timing_demo",
            request_type="search",
            context_info={"related_to_previous": False}
        )
        delays.append(delay)
        print(f"Request {i+1} delay: {delay:.2f} seconds")
    
    avg_delay = sum(delays) / len(delays)
    print(f"\nAverage delay: {avg_delay:.2f} seconds")
    print(f"Delay range: {min(delays):.2f} - {max(delays):.2f} seconds")
    print("\n")


async def demonstrate_pattern_detection_avoidance():
    """Demonstrate pattern detection avoidance."""
    print("=== Pattern Detection Avoidance Demo ===")
    
    obfuscator = RequestObfuscator()
    
    # Generate multiple request patterns
    patterns = []
    for i in range(15):
        headers = await obfuscator.obfuscate_request(
            session_id=f"pattern_session_{i}",
            base_headers={"X-Custom": f"data_{i}"},
            request_type=random.choice(["search", "navigation", "form_submit", "ajax"])
        )
        
        delay = await obfuscator.calculate_delay(
            session_id=f"pattern_session_{i}",
            request_type=headers.get("X-Requested-With", "general"),
            context_info={"related_to_previous": random.choice([True, False])}
        )
        
        pattern = {
            'header_count': len(headers),
            'has_dnt': 'DNT' in headers,
            'has_pragma': 'Pragma' in headers,
            'delay': delay
        }
        patterns.append(pattern)
        
        print(f"Pattern {i+1}: {pattern}")
    
    # Show variation statistics
    header_counts = [p['header_count'] for p in patterns]
    dnt_count = sum(1 for p in patterns if p['has_dnt'])
    pragma_count = sum(1 for p in patterns if p['has_pragma'])
    delays = [p['delay'] for p in patterns]
    
    print(f"\nPattern Variation Statistics:")
    print(f"  Header count range: {min(header_counts)} - {max(header_counts)}")
    print(f"  DNT header frequency: {dnt_count}/{len(patterns)} ({dnt_count/len(patterns)*100:.1f}%)")
    print(f"  Pragma header frequency: {pragma_count}/{len(patterns)} ({pragma_count/len(patterns)*100:.1f}%)")
    print(f"  Delay range: {min(delays):.2f} - {max(delays):.2f} seconds")
    print("\n")


async def main():
    """Run all demonstrations."""
    print("Request Pattern Obfuscation Examples")
    print("====================================\n")
    
    await demonstrate_header_order_randomization()
    await demonstrate_accept_language_variation()
    await demonstrate_request_timing_variation()
    await demonstrate_pattern_detection_avoidance()
    
    print("=== Summary ===")
    print("The request obfuscator provides several key anti-detection features:")
    print("1. Header Order Randomization - Headers are shuffled to avoid sequence-based detection")
    print("2. Natural Language Variation - Accept-Language headers vary realistically")
    print("3. Timing Variation - Request delays include human-like randomness")
    print("4. Pattern Avoidance - Random inclusion/exclusion of optional headers")
    print("\nThese features work together to make automated requests appear more human-like")


if __name__ == "__main__":
    asyncio.run(main())