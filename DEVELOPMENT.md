# Development Guide

## Running Without Proxies

For development and testing purposes, you can disable proxy usage by setting an environment variable:

```bash
export ICE_LOCATOR_PROXY_ENABLED=false
```

Or run the application with the environment variable set:

```bash
ICE_LOCATOR_PROXY_ENABLED=false python -m src.ice_locator_mcp
```

**Warning**: Running without proxies will likely result in 403 Forbidden errors when accessing the ICE website, as the site implements anti-bot measures that require proxy usage for bypassing. The system will log warnings when proxies are disabled.

To test if your connection is working without proxies, you can run:

```bash
python scripts/test_proxies.py
```

## Self-Hosted Reverse Proxy Considerations

A self-hosted reverse proxy would not be beneficial for accessing the ICE website because:

1. **Single IP Address**: A reverse proxy running on your server would still use a single IP address, which the ICE website could easily block.

2. **No IP Rotation**: Unlike our external proxy system that rotates through multiple IPs, a self-hosted reverse proxy provides no rotation benefits.

3. **No Residential IPs**: A self-hosted proxy would use your server's datacenter IP, not residential IPs that are less likely to be detected.

4. **Detection**: The ICE website's anti-bot measures are designed to detect and block proxy traffic, including self-hosted proxies.

Our current approach using external proxy providers (especially premium residential proxies) is the appropriate solution for accessing the ICE website without being blocked.

## Configuring Premium Proxies

To use premium proxy services, set the appropriate environment variables:

### ScraperAPI
```bash
export SCRAPERAPI_KEY="your_scraperapi_key"
```

### BrightData
```bash
export BRIGHTDATA_USERNAME="your_username"
export BRIGHTDATA_PASSWORD="your_password"
```

### SmartProxy
```bash
export SMARTPROXY_USERNAME="your_username"
export SMARTPROXY_PASSWORD="your_password"
```

### NetNut
```bash
export NETNUT_USERNAME="your_username"
export NETNUT_PASSWORD="your_password"
```

### Oxylabs
```bash
export OXYLABS_USERNAME="your_username"
export OXYLABS_PASSWORD="your_password"
```

### GeoSurf
```bash
export GEOSURF_TOKEN="your_token"
```

### Infatica
```bash
export INFATICA_KEY="your_key"
```

### Storm Proxies
```bash
export STORM_USERNAME="your_username"
export STORM_PASSWORD="your_password"
```

## Testing Proxy Functionality

To test if proxies are working correctly:

```bash
python scripts/test_proxies.py
python -m pytest tests/test_proxy_reputation.py -v
python -m pytest tests/test_premium_proxy_integration.py -v
```

## Free Proxy Limitations

While the system can fetch free proxies from various sources, these are generally unreliable and often don't work due to:
- Being blocked by target websites (including ICE)
- Slow response times
- Frequent downtime
- Poor quality and stability
- Lack of residential IP addresses (datacenter IPs are more easily detected)

For production use, premium residential proxies are strongly recommended. Free proxies should only be used for testing purposes.

## Recommended Development Workflow

1. For local development, use premium proxies or a local proxy service
2. Disable proxies only for testing direct connectivity issues
3. Always test with proxies enabled before deploying to production
4. Monitor proxy performance and rotate providers as needed