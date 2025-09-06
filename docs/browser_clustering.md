# Browser Clustering

The browser clustering system distributes requests across multiple browser instances to improve performance, reliability, and reduce detection risk.

## Overview

Browser clustering is an advanced technique that manages multiple browser instances to:
- Distribute workload across multiple processes
- Provide failover mechanisms for failed requests
- Implement load balancing based on instance health
- Enable efficient resource utilization through instance pooling

## Features

### Load Balancing
The cluster manager uses a health-based load balancing algorithm that considers:
- Success rate of each instance
- Consecutive failure count
- Time since last use
- Overall request count

### Failover Mechanisms
When a request fails on one instance, the system automatically:
- Attempts failover to another healthy instance
- Preserves session state when possible
- Maintains request continuity

### Instance Pooling
Browser instances are efficiently managed through:
- Available instance pool for new requests
- Busy instance tracking for active requests
- Automatic instance creation up to configured limits
- Health monitoring and automatic restart of problematic instances

### Health Monitoring
Each instance is continuously monitored for:
- Responsiveness
- Success/failure rates
- Resource utilization
- Automatic restart when unhealthy

## Usage

### Basic Setup

```python
from src.ice_locator_mcp.anti_detection.browser_cluster import BrowserClusterManager
from src.ice_locator_mcp.core.config import SearchConfig

# Create configuration
config = SearchConfig(
    max_retries=3,
    timeout=30,
    delay_range=(1, 3)
)

# Create cluster manager with up to 5 instances
cluster_manager = BrowserClusterManager(config, max_instances=5)

# Initialize the cluster
await cluster_manager.initialize()
```

### Handling Requests

```python
# Handle a request through the cluster
session_id = "user_session_123"
url = "https://example.com"

try:
    content = await cluster_manager.handle_request(session_id, url)
    print("Request successful")
except Exception as e:
    print(f"Request failed: {e}")
```

### Cleanup

```python
# Clean up all resources
await cluster_manager.cleanup()
```

## Configuration

The [BrowserClusterManager](file:///Users/trose/src/locator-mcp/src/ice_locator_mcp/anti_detection/browser_cluster.py#L103-L219) accepts the following parameters:

- `config`: Search configuration object
- `max_instances`: Maximum number of browser instances to maintain (default: 5)

## Health Scoring

Each browser instance receives a health score between 0.0 and 1.0 based on:

1. Success Rate (70% weight): Higher success rates improve the score
2. Consecutive Failures (20% weight): More consecutive failures reduce the score
3. Recency (10% weight): Recently used instances get a slight bonus

Instances with consecutive failures >= 3 are considered unhealthy and automatically restarted.

## Example

See [browser_clustering_example.py](file:///Users/trose/src/locator-mcp/examples/browser_clustering_example.py) for a complete working example.

## Testing

The browser clustering functionality is tested through [test_browser_clustering.py](file:///Users/trose/src/locator-mcp/tests/test_browser_clustering.py) which verifies:
- Cluster initialization
- Instance creation and management
- Load balancing mechanisms
- Failover functionality
- Resource cleanup

Run tests with:
```bash
python -m pytest tests/test_browser_clustering.py -v
```