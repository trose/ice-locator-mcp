# CAPTCHA Handling

The CAPTCHA handling system provides comprehensive detection, analysis, and solving capabilities for various types of CAPTCHA challenges.

## Overview

The CAPTCHA handler is designed to automatically detect and handle different types of CAPTCHA challenges including:
- reCAPTCHA v2 and v3
- hCaptcha
- Image-based CAPTCHAs
- Text-based CAPTCHAs
- Cloudflare challenges
- FunCaptcha

## Features

### CAPTCHA Detection
The system uses pattern matching to detect various CAPTCHA types:
- HTML element selectors
- Script patterns
- Text keywords
- URL patterns

### CAPTCHA Solving
The system implements multiple solving strategies:
- Internal logic for simple challenges (math problems, etc.)
- Integration with external CAPTCHA solving services
- Bypass strategies for certain challenge types

### External Service Integration
Support for popular CAPTCHA solving services:
- 2Captcha
- Anti-Captcha
- CapSolver

## Usage

### Basic Setup

```python
from src.ice_locator_mcp.anti_detection.captcha_handler import CaptchaHandler

# Create CAPTCHA handler
captcha_handler = CaptchaHandler()
```

### Handling Web Responses

```python
# Handle a web response that might contain a CAPTCHA
html_content = get_web_page_content()
page_url = "https://example.com"
session_id = "user_session_123"

solved, challenge = await captcha_handler.handle_response(
    html_content, 
    page_url, 
    session_id
)

if challenge:
    print(f"Detected CAPTCHA: {challenge.captcha_type.value}")
    print(f"Status: {challenge.status.value}")
else:
    print("No CAPTCHA detected")
```

### Getting Statistics

```python
# Get CAPTCHA handling statistics
stats = captcha_handler.get_challenge_stats()
print(f"Total challenges: {stats['total_challenges']}")
print(f"Success rate: {stats['success_rate']:.2f}")
```

## Configuration

The CAPTCHA handler can be configured through environment variables for external services:

- `TWOCAPTCHA_API_KEY`: API key for 2Captcha service
- `ANTICAPTCHA_API_KEY`: API key for Anti-Captcha service
- `CAPSOLVER_API_KEY`: API key for CapSolver service

## CAPTCHA Types

### reCAPTCHA v2
Detected by:
- `.g-recaptcha` class
- `[data-sitekey]` attribute
- Google reCAPTCHA script URLs

### hCaptcha
Detected by:
- `.h-captcha` class
- `[data-sitekey]` attribute
- hCaptcha script URLs

### Text CAPTCHA
Detected by:
- Specific CSS classes (`.math-captcha`, `.text-challenge`)
- Keywords in text (what is, solve, math problem)

### Cloudflare
Detected by:
- "Just a moment..." title
- "checking your browser" text
- Cloudflare-specific elements

## Example

See [captcha_handler_example.py](file:///Users/trose/src/locator-mcp/examples/captcha_handler_example.py) for a complete working example.

## Testing

The CAPTCHA handling functionality is tested through [test_captcha_handler.py](file:///Users/trose/src/locator-mcp/tests/test_captcha_handler.py) which verifies:
- CAPTCHA detection for various types
- CAPTCHA solving capabilities
- Statistics tracking

Run tests with:
```bash
python -m pytest tests/test_captcha_handler.py -v
```