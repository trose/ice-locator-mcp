#!/usr/bin/env python3
"""
Example demonstrating CAPTCHA detection and handling functionality.

This script shows how to use the CAPTCHA handler to detect and solve
various types of CAPTCHA challenges.
"""

import asyncio
import sys
import os

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ice_locator_mcp.anti_detection.captcha_handler import CaptchaHandler, CaptchaType


async def main():
    """Demonstrate CAPTCHA handling functionality."""
    print("CAPTCHA Handler Example")
    print("=" * 30)
    
    # Create CAPTCHA handler
    captcha_handler = CaptchaHandler()
    
    # Example 1: reCAPTCHA v2 detection
    print("\n1. reCAPTCHA v2 Detection:")
    recaptcha_html = """
    <html>
    <body>
        <h1>Login Page</h1>
        <form>
            <input type="text" name="username" placeholder="Username">
            <input type="password" name="password" placeholder="Password">
            <div class="g-recaptcha" data-sitekey="6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"></div>
            <button type="submit">Login</button>
        </form>
        <script src="https://www.google.com/recaptcha/api.js"></script>
    </body>
    </html>
    """
    
    solved, challenge = await captcha_handler.handle_response(
        recaptcha_html, 
        "https://example.com/login", 
        "session_1"
    )
    
    if challenge:
        print(f"  Detected CAPTCHA: {challenge.captcha_type.value}")
        print(f"  Site Key: {challenge.site_key}")
        print(f"  Confidence: {challenge.detection_confidence:.2f}")
        print(f"  Status: {challenge.status.value}")
    else:
        print("  No CAPTCHA detected")
    
    # Example 2: hCaptcha detection
    print("\n2. hCaptcha Detection:")
    hcaptcha_html = """
    <html>
    <body>
        <h1>Contact Form</h1>
        <form>
            <input type="text" name="name" placeholder="Your Name">
            <input type="email" name="email" placeholder="Your Email">
            <div class="h-captcha" data-sitekey="10000000-ffff-ffff-ffff-000000000001"></div>
            <button type="submit">Send Message</button>
        </form>
        <script src="https://hcaptcha.com/1/api.js" async defer></script>
    </body>
    </html>
    """
    
    solved, challenge = await captcha_handler.handle_response(
        hcaptcha_html, 
        "https://example.com/contact", 
        "session_2"
    )
    
    if challenge:
        print(f"  Detected CAPTCHA: {challenge.captcha_type.value}")
        print(f"  Site Key: {challenge.site_key}")
        print(f"  Confidence: {challenge.detection_confidence:.2f}")
        print(f"  Status: {challenge.status.value}")
    else:
        print("  No CAPTCHA detected")
    
    # Example 3: Cloudflare challenge detection
    print("\n3. Cloudflare Challenge Detection:")
    cloudflare_html = """
    <html>
    <head>
        <title>Just a moment...</title>
    </head>
    <body>
        <div id="cf-wrapper">
            <div id="cf-error-details">
                <h1>Checking your browser before accessing example.com</h1>
                <p data-translate="checking_browser">Checking your browser before accessing</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    solved, challenge = await captcha_handler.handle_response(
        cloudflare_html, 
        "https://example.com", 
        "session_3"
    )
    
    if challenge:
        print(f"  Detected CAPTCHA: {challenge.captcha_type.value}")
        print(f"  Confidence: {challenge.detection_confidence:.2f}")
        print(f"  Status: {challenge.status.value}")
    else:
        print("  No CAPTCHA detected")
    
    # Example 4: Text CAPTCHA detection and solving
    print("\n4. Text CAPTCHA Detection and Solving:")
    text_captcha_html = """
    <html>
    <body>
        <h1>Math Challenge</h1>
        <form>
            <p>What is 15 + 27?</p>
            <input type="text" name="captcha_answer">
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    """
    
    # For text CAPTCHAs, we need to modify the HTML to include the detection patterns
    text_captcha_html = """
    <html>
    <body>
        <h1>Math Challenge</h1>
        <form>
            <div class="math-captcha">
                <p>What is 15 + 27?</p>
                <input type="text" name="captcha_answer">
            </div>
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    """
    
    solved, challenge = await captcha_handler.handle_response(
        text_captcha_html, 
        "https://example.com/math-challenge", 
        "session_4"
    )
    
    if challenge:
        print(f"  Detected CAPTCHA: {challenge.captcha_type.value}")
        print(f"  Question: {challenge.question}")
        print(f"  Confidence: {challenge.detection_confidence:.2f}")
        print(f"  Status: {challenge.status.value}")
        if challenge.solution:
            print(f"  Solution: {challenge.solution}")
    else:
        print("  No CAPTCHA detected")
    
    # Example 5: Normal page without CAPTCHA
    print("\n5. Normal Page (No CAPTCHA):")
    normal_html = """
    <html>
    <body>
        <h1>Welcome to Our Website</h1>
        <p>This is a normal page without any CAPTCHA challenges.</p>
        <a href="/about">About Us</a>
    </body>
    </html>
    """
    
    solved, challenge = await captcha_handler.handle_response(
        normal_html, 
        "https://example.com", 
        "session_5"
    )
    
    if challenge:
        print(f"  Detected CAPTCHA: {challenge.captcha_type.value}")
    else:
        print("  No CAPTCHA detected - Page is clean")
    
    # Show statistics
    print("\n6. CAPTCHA Handler Statistics:")
    stats = captcha_handler.get_challenge_stats()
    print(f"  Total Challenges: {stats['total_challenges']}")
    if stats['total_challenges'] > 0:
        print(f"  Solved Challenges: {stats['solved_challenges']}")
        print(f"  Success Rate: {stats['success_rate']:.2f}")
        if 'by_type' in stats:
            print("  By Type:")
            for captcha_type, data in stats['by_type'].items():
                print(f"    {captcha_type}: {data['solved']}/{data['total']} solved")


if __name__ == "__main__":
    asyncio.run(main())