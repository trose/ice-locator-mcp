# Request Pattern Obfuscation

Request Pattern Obfuscation is a key component of the fortified browser approach that helps avoid detection based on request timing and sequences. This system randomizes various aspects of HTTP requests to make them appear more human-like and less predictable.

## Features

### 1. Header Order Randomization

The system randomizes the order of HTTP headers to avoid detection based on header sequence patterns. Many automated systems send headers in a consistent order, which can be a red flag for anti-bot systems.

```python
# Headers are shuffled to avoid sequence-based detection
headers1 = ['User-Agent', 'Accept', 'Accept-Language', 'Connection']
headers2 = ['Connection', 'Accept-Language', 'User-Agent', 'Accept']
```

### 2. Natural Accept-Language Variation

The system generates realistic Accept-Language headers with natural variation in language selection and quality values:

- Randomly selects 1-3 languages from the browser's supported languages
- Generates realistic quality values (q=0.1-1.0) with variation
- Varies the order of languages in the header

### 3. Request Timing Variation

The system introduces human-like delays between requests to avoid burst pattern detection:

- Uses multiple timing profiles (human_fast, human_normal, human_slow)
- Adds random variance to base delays
- Adjusts timing based on request type and context
- Slows down after consecutive requests or errors

### 4. Pattern Detection Avoidance

The system avoids predictable patterns by:

- Randomly including/excluding optional headers (DNT, Pragma, Cache-Control)
- Varying header values within normal ranges
- Using different browser profiles with distinct characteristics
- Rotating browser profiles periodically

## Implementation Details

### Header Randomization

The `RequestObfuscator` class provides the core functionality:

```python
from src.ice_locator_mcp.anti_detection.request_obfuscator import RequestObfuscator

obfuscator = RequestObfuscator()
headers = await obfuscator.obfuscate_request(
    session_id="session_123",
    base_headers={"Custom": "value"},
    request_type="search"
)
```

### Timing Control

The system calculates human-like delays:

```python
delay = await obfuscator.calculate_delay(
    session_id="session_123",
    request_type="search",
    context_info={"related_to_previous": False}
)
await asyncio.sleep(delay)
```

## Configuration

The request obfuscator uses several timing profiles:

- **human_fast**: Base delay 1.0s, variance 0.5s
- **human_normal**: Base delay 2.0s, variance 1.0s  
- **human_slow**: Base delay 4.0s, variance 2.0s

The system automatically adjusts timing based on:
- Request type (search, form_submit, navigation, etc.)
- Consecutive request count
- Error history
- Context information

## Benefits

1. **Avoids Sequence Detection**: Randomized header order prevents detection based on consistent sequences
2. **Natural Language Patterns**: Realistic Accept-Language headers match human browser behavior
3. **Human-like Timing**: Variable delays mimic human browsing patterns
4. **Pattern Avoidance**: Random inclusion of optional headers prevents predictable patterns
5. **Profile Rotation**: Periodic browser profile changes simulate different users

## Integration

The request pattern obfuscation system integrates with other anti-detection components:

- Works with browser fingerprinting evasion
- Complements proxy rotation strategies
- Enhances behavioral simulation
- Supports TLS fingerprint randomization

See the [examples/request_pattern_obfuscation_example.py](../examples/request_pattern_obfuscation_example.py) for a complete demonstration of these features.