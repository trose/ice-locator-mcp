# Usage Examples

This guide provides practical examples for using the ICE Locator MCP Server in various scenarios.

## Basic Search Examples

### Search by Name

```python
# Simple name search
result = await session.call_tool("search_by_name", {
    "first_name": "John",
    "last_name": "Doe"
})

# Enhanced name search with fuzzy matching
result = await session.call_tool("search_by_name", {
    "first_name": "José",
    "last_name": "García",
    "middle_name": "Luis",
    "fuzzy_match": True,
    "confidence_threshold": 0.8
})
```

### Search by A-Number

```python
# A-Number search with validation
result = await session.call_tool("search_by_alien_number", {
    "alien_number": "A123456789",
    "validate_format": True
})

# A-Number search without 'A' prefix
result = await session.call_tool("search_by_alien_number", {
    "alien_number": "123456789"
})
```

### Search by Facility

```python
# Search by facility name
result = await session.call_tool("search_by_facility", {
    "facility_name": "Houston Contract Detention Facility"
})

# Search by location
result = await session.call_tool("search_by_facility", {
    "city": "Houston",
    "state": "TX"
})
```

## Advanced Search Examples

### Natural Language Queries

```python
# Parse natural language query
result = await session.call_tool("parse_natural_query", {
    "query": "Find Maria Rodriguez from Guatemala at Houston facility",
    "auto_execute": True,
    "confidence_threshold": 0.7
})

# Spanish language query
result = await session.call_tool("parse_natural_query", {
    "query": "Buscar a Juan Pérez en el centro de detención",
    "language": "es",
    "auto_execute": False
})
```

### Bulk Search Operations

```python
# Multiple searches at once
result = await session.call_tool("bulk_search", {
    "searches": [
        {
            "type": "name",
            "first_name": "John",
            "last_name": "Doe",
            "fuzzy_match": True
        },
        {
            "type": "alien_number",
            "alien_number": "A987654321"
        },
        {
            "type": "facility",
            "facility_name": "Example Detention Center"
        }
    ],
    "max_concurrent": 3,
    "include_summary": True
})
```

## Client Integration Examples

### Python Client with AsyncIO

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class ICELocatorClient:
    def __init__(self, config_path=None):
        self.server_params = StdioServerParameters(
            command="ice-locator-mcp",
            args=[],
            env={"ICE_LOCATOR_CONFIG": config_path} if config_path else {}
        )
    
    async def search_detainee(self, first_name, last_name, **kwargs):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                result = await session.call_tool("search_by_name", {
                    "first_name": first_name,
                    "last_name": last_name,
                    **kwargs
                })
                
                return result.content[0].text
    
    async def smart_search(self, query):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                result = await session.call_tool("parse_natural_query", {
                    "query": query,
                    "auto_execute": True
                })
                
                return result.content[0].text

# Usage
async def main():
    client = ICELocatorClient("/path/to/config.json")
    
    # Basic search
    result = await client.search_detainee("John", "Doe", fuzzy_match=True)
    print(result)
    
    # Smart search
    result = await client.smart_search("Find Maria in Houston facility")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### JavaScript/Node.js Client

```javascript
import { Client } from '@modelcontextprotocol/client';
import { StdioTransport } from '@modelcontextprotocol/client/stdio';

class ICELocatorClient {
    constructor(configPath = null) {
        this.transport = new StdioTransport({
            command: 'ice-locator-mcp',
            args: [],
            env: configPath ? { ICE_LOCATOR_CONFIG: configPath } : {}
        });
        this.client = new Client(this.transport);
    }

    async initialize() {
        await this.client.initialize();
    }

    async searchByName(firstName, lastName, options = {}) {
        const result = await this.client.callTool('search_by_name', {
            first_name: firstName,
            last_name: lastName,
            ...options
        });
        return result.content[0].text;
    }

    async smartSearch(query) {
        const result = await this.client.callTool('parse_natural_query', {
            query: query,
            auto_execute: true
        });
        return result.content[0].text;
    }

    async close() {
        await this.client.close();
    }
}

// Usage
async function main() {
    const client = new ICELocatorClient('/path/to/config.json');
    
    try {
        await client.initialize();
        
        // Basic search
        const result1 = await client.searchByName('John', 'Doe', {
            fuzzy_match: true,
            confidence_threshold: 0.8
        });
        console.log(result1);
        
        // Smart search
        const result2 = await client.smartSearch('Find Maria Rodriguez in Texas');
        console.log(result2);
        
    } finally {
        await client.close();
    }
}

main().catch(console.error);
```

## Command Line Examples

### Direct CLI Usage

```bash
# Basic name search
ice-locator-mcp search --first-name "John" --last-name "Doe"

# A-Number search
ice-locator-mcp search --alien-number "A123456789"

# Facility search
ice-locator-mcp search --facility "Houston Contract Detention"

# Natural language search
ice-locator-mcp smart-search "Find José García in California"

# Bulk search from file
ice-locator-mcp bulk-search --input searches.json --output results.json
```

### Batch Processing

```bash
# Create batch search file
cat > batch_searches.json << EOF
{
  "searches": [
    {
      "type": "name",
      "first_name": "John",
      "last_name": "Doe"
    },
    {
      "type": "alien_number", 
      "alien_number": "A123456789"
    }
  ]
}
EOF

# Run batch search
ice-locator-mcp batch --file batch_searches.json --output results.json
```

## Integration with AI Assistants

### Claude Desktop Integration

```json
{
  "mcpServers": {
    "ice-locator": {
      "command": "ice-locator-mcp",
      "args": ["--config", "/path/to/config.json"],
      "env": {
        "ICE_LOCATOR_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

Example Claude conversation:
```
User: "Can you help me find information about someone in ICE custody named Maria Rodriguez?"

Claude: I can help you search for detainee information. Let me search for Maria Rodriguez in the ICE database.

[Uses search_by_name tool]

Based on the search, I found [results]. Here's what I found...
```

### Custom AI Assistant Integration

```python
class ImmigrationAssistant:
    def __init__(self):
        self.ice_client = ICELocatorClient()
    
    async def help_find_detainee(self, user_query):
        # Parse user intent
        if "A-number" in user_query or "alien number" in user_query:
            # Extract A-number and search
            a_number = self.extract_a_number(user_query)
            result = await self.ice_client.search_by_a_number(a_number)
        else:
            # Use natural language search
            result = await self.ice_client.smart_search(user_query)
        
        # Provide guidance
        guidance = self.generate_guidance(result)
        
        return {
            "search_results": result,
            "guidance": guidance,
            "resources": self.get_resources()
        }
```

## Error Handling Examples

### Robust Error Handling

```python
import asyncio
from mcp.client.exceptions import McpError

async def robust_search(first_name, last_name):
    client = ICELocatorClient()
    
    try:
        result = await client.search_detainee(first_name, last_name)
        return {"status": "success", "data": result}
        
    except McpError as e:
        if "rate limit" in str(e).lower():
            # Wait and retry
            await asyncio.sleep(60)
            return await robust_search(first_name, last_name)
        else:
            return {"status": "error", "message": str(e)}
            
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {e}"}
```

### Retry Logic

```python
async def search_with_retry(search_func, max_retries=3, delay=1):
    for attempt in range(max_retries):
        try:
            return await search_func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            # Exponential backoff
            wait_time = delay * (2 ** attempt)
            await asyncio.sleep(wait_time)
```

## Performance Optimization Examples

### Connection Pooling

```python
class PooledICEClient:
    def __init__(self, pool_size=5):
        self.pool_size = pool_size
        self.connections = asyncio.Queue(maxsize=pool_size)
        self._initialized = False
    
    async def initialize(self):
        if self._initialized:
            return
            
        for _ in range(self.pool_size):
            client = ICELocatorClient()
            await self.connections.put(client)
        
        self._initialized = True
    
    async def search(self, *args, **kwargs):
        client = await self.connections.get()
        try:
            return await client.search_detainee(*args, **kwargs)
        finally:
            await self.connections.put(client)
```

### Caching Results

```python
import time
from functools import wraps

def cache_results(ttl=3600):
    cache = {}
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{hash((args, tuple(kwargs.items())))}"
            
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < ttl:
                    return result
            
            result = await func(*args, **kwargs)
            cache[key] = (result, time.time())
            return result
        
        return wrapper
    return decorator

@cache_results(ttl=1800)  # 30 minute cache
async def cached_search(first_name, last_name):
    client = ICELocatorClient()
    return await client.search_detainee(first_name, last_name)
```

## Testing Examples

### Unit Testing

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_search_by_name():
    with patch('ice_locator_mcp.server.search_by_name') as mock_search:
        mock_search.return_value = {
            "status": "found",
            "results": [{"name": "John Doe", "alien_number": "A123456789"}]
        }
        
        client = ICELocatorClient()
        result = await client.search_detainee("John", "Doe")
        
        assert "John Doe" in result
        mock_search.assert_called_once()
```

### Integration Testing

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_end_to_end_search():
    client = ICELocatorClient()
    
    # Test with known good data
    result = await client.search_detainee("Test", "User")
    
    # Verify result format
    assert isinstance(result, str)
    assert len(result) > 0
```

## Monitoring and Logging Examples

### Custom Logging

```python
import logging
import structlog

# Configure structured logging
logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("ice_locator_client")

async def logged_search(first_name, last_name):
    logger.info("Starting search", first_name=first_name, last_name=last_name)
    
    try:
        client = ICELocatorClient()
        result = await client.search_detainee(first_name, last_name)
        
        logger.info("Search completed", 
                   result_length=len(result),
                   status="success")
        
        return result
        
    except Exception as e:
        logger.error("Search failed", error=str(e), status="error")
        raise
```

### Metrics Collection

```python
import time
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class SearchMetrics:
    total_searches: int = 0
    successful_searches: int = 0
    failed_searches: int = 0
    average_response_time: float = 0.0
    response_times: List[float] = None
    
    def __post_init__(self):
        if self.response_times is None:
            self.response_times = []

class MetricsCollector:
    def __init__(self):
        self.metrics = SearchMetrics()
    
    async def timed_search(self, search_func, *args, **kwargs):
        start_time = time.time()
        
        try:
            result = await search_func(*args, **kwargs)
            self.metrics.successful_searches += 1
            return result
            
        except Exception as e:
            self.metrics.failed_searches += 1
            raise
            
        finally:
            response_time = time.time() - start_time
            self.metrics.response_times.append(response_time)
            self.metrics.total_searches += 1
            
            # Update average
            self.metrics.average_response_time = (
                sum(self.metrics.response_times) / len(self.metrics.response_times)
            )
    
    def get_stats(self) -> Dict:
        return {
            "total_searches": self.metrics.total_searches,
            "success_rate": (
                self.metrics.successful_searches / self.metrics.total_searches
                if self.metrics.total_searches > 0 else 0
            ),
            "average_response_time": self.metrics.average_response_time,
            "min_response_time": min(self.metrics.response_times) if self.metrics.response_times else 0,
            "max_response_time": max(self.metrics.response_times) if self.metrics.response_times else 0
        }
```

## Security Examples

### Secure Configuration

```python
import os
from cryptography.fernet import Fernet

class SecureConfig:
    def __init__(self, key_file="config.key"):
        self.key_file = key_file
        self.cipher = self._load_or_create_key()
    
    def _load_or_create_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            os.chmod(self.key_file, 0o600)  # Owner read/write only
        
        return Fernet(key)
    
    def encrypt_config(self, config_data):
        encrypted = self.cipher.encrypt(config_data.encode())
        return encrypted
    
    def decrypt_config(self, encrypted_data):
        decrypted = self.cipher.decrypt(encrypted_data)
        return decrypted.decode()
```

These examples demonstrate various ways to integrate and use the ICE Locator MCP Server effectively while maintaining security, performance, and reliability.