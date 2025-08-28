# MCP Tools Documentation

This document provides detailed specifications for all Model Context Protocol (MCP) tools provided by the ICE Locator MCP Server.

## Tool Discovery

The server supports the standard MCP tool discovery protocol. All available tools can be discovered using:

```json
{
  "method": "tools/list",
  "params": {}
}
```

## Tool Specifications

### search_by_name

**Purpose:** Search for detainees using name-based criteria with advanced fuzzy matching capabilities.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "first_name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 50,
      "description": "First name of the person to search for"
    },
    "last_name": {
      "type": "string", 
      "minLength": 1,
      "maxLength": 50,
      "description": "Last name of the person to search for"
    },
    "middle_name": {
      "type": "string",
      "maxLength": 50,
      "description": "Optional middle name or initial"
    },
    "fuzzy_match": {
      "type": "boolean",
      "default": true,
      "description": "Enable fuzzy matching for names with variations"
    },
    "confidence_threshold": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "default": 0.8,
      "description": "Minimum confidence score for fuzzy matches"
    },
    "phonetic_matching": {
      "type": "boolean",
      "default": true,
      "description": "Enable phonetic matching (Soundex, Metaphone)"
    },
    "cultural_variants": {
      "type": "boolean", 
      "default": true,
      "description": "Include cultural name variations and transliterations"
    }
  },
  "required": ["first_name", "last_name"],
  "additionalProperties": false
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "alien_number": {"type": "string"},
          "facility_name": {"type": "string"},
          "facility_address": {"type": "string"},
          "booking_date": {"type": "string", "format": "date"},
          "status": {"type": "string"},
          "confidence_score": {"type": "number"},
          "match_details": {
            "type": "object",
            "properties": {
              "name_similarity": {"type": "number"},
              "phonetic_match": {"type": "boolean"},
              "fuzzy_components": {
                "type": "object",
                "properties": {
                  "first_name": {"type": "number"},
                  "last_name": {"type": "number"},
                  "middle_name": {"type": "number"}
                }
              }
            }
          }
        }
      }
    },
    "search_metadata": {
      "type": "object",
      "properties": {
        "query_time": {"type": "string", "format": "date-time"},
        "total_results": {"type": "integer"},
        "search_type": {"type": "string"},
        "processing_time_ms": {"type": "integer"}
      }
    }
  }
}
```

**Error Conditions:**
- `INVALID_NAME_FORMAT`: Name contains invalid characters
- `NAME_TOO_SHORT`: Name shorter than minimum length
- `NAME_TOO_LONG`: Name exceeds maximum length
- `CONFIDENCE_OUT_OF_RANGE`: Confidence threshold not between 0.0 and 1.0

### search_by_alien_number

**Purpose:** Search for detainees using their Alien Registration Number (A-Number).

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "alien_number": {
      "type": "string",
      "pattern": "^A?[0-9]{8,9}$",
      "description": "Alien Registration Number with or without 'A' prefix"
    },
    "validate_format": {
      "type": "boolean",
      "default": true,
      "description": "Validate A-Number format before searching"
    },
    "include_history": {
      "type": "boolean",
      "default": false,
      "description": "Include historical facility transfers"
    }
  },
  "required": ["alien_number"],
  "additionalProperties": false
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "alien_number": {"type": "string"},
          "facility_name": {"type": "string"},
          "facility_address": {"type": "string"},
          "booking_date": {"type": "string", "format": "date"},
          "status": {"type": "string"},
          "last_updated": {"type": "string", "format": "date-time"},
          "transfer_history": {
            "type": "array",
            "items": {
              "type": "object", 
              "properties": {
                "facility_name": {"type": "string"},
                "transfer_date": {"type": "string", "format": "date"},
                "reason": {"type": "string"}
              }
            }
          }
        }
      }
    }
  }
}
```

**Error Conditions:**
- `INVALID_ALIEN_NUMBER`: A-Number format is invalid
- `ALIEN_NUMBER_NOT_FOUND`: No records found for A-Number
- `VALIDATION_FAILED`: Format validation failed

### search_by_facility

**Purpose:** Search for detainees at specific facilities or locations.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "facility_name": {
      "type": "string",
      "maxLength": 100,
      "description": "Name of the detention facility"
    },
    "city": {
      "type": "string",
      "maxLength": 50,
      "description": "City where facility is located"
    },
    "state": {
      "type": "string",
      "pattern": "^[A-Z]{2}$",
      "description": "Two-letter state abbreviation"
    },
    "zip_code": {
      "type": "string",
      "pattern": "^[0-9]{5}(-[0-9]{4})?$",
      "description": "ZIP code of facility"
    },
    "facility_type": {
      "type": "string",
      "enum": ["detention_center", "processing_center", "family_facility", "contract_facility"],
      "description": "Type of facility"
    },
    "include_capacity": {
      "type": "boolean",
      "default": false,
      "description": "Include facility capacity information"
    },
    "active_only": {
      "type": "boolean",
      "default": true,
      "description": "Only include currently active detainees"
    }
  },
  "anyOf": [
    {"required": ["facility_name"]},
    {"required": ["city", "state"]},
    {"required": ["zip_code"]}
  ],
  "additionalProperties": false
}
```

**Error Conditions:**
- `FACILITY_NOT_FOUND`: Specified facility doesn't exist
- `INVALID_STATE_CODE`: State abbreviation is invalid
- `INVALID_ZIP_CODE`: ZIP code format is invalid
- `LOCATION_AMBIGUOUS`: Multiple facilities match criteria

### bulk_search

**Purpose:** Execute multiple search operations in parallel with intelligent batching.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "searches": {
      "type": "array",
      "minItems": 1,
      "maxItems": 10,
      "items": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string",
            "description": "Optional identifier for this search"
          },
          "type": {
            "type": "string",
            "enum": ["name", "alien_number", "facility"],
            "description": "Type of search to perform"
          }
        },
        "required": ["type"],
        "allOf": [
          {
            "if": {"properties": {"type": {"const": "name"}}},
            "then": {
              "properties": {
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "middle_name": {"type": "string"},
                "fuzzy_match": {"type": "boolean"}
              },
              "required": ["first_name", "last_name"]
            }
          },
          {
            "if": {"properties": {"type": {"const": "alien_number"}}},
            "then": {
              "properties": {
                "alien_number": {"type": "string"}
              },
              "required": ["alien_number"]
            }
          },
          {
            "if": {"properties": {"type": {"const": "facility"}}},
            "then": {
              "properties": {
                "facility_name": {"type": "string"},
                "city": {"type": "string"},
                "state": {"type": "string"}
              },
              "anyOf": [
                {"required": ["facility_name"]},
                {"required": ["city", "state"]}
              ]
            }
          }
        ]
      }
    },
    "max_concurrent": {
      "type": "integer",
      "minimum": 1,
      "maximum": 5,
      "default": 3,
      "description": "Maximum number of concurrent searches"
    },
    "include_summary": {
      "type": "boolean",
      "default": true,
      "description": "Include summary statistics in response"
    },
    "stop_on_error": {
      "type": "boolean",
      "default": false,
      "description": "Stop all searches if one fails"
    }
  },
  "required": ["searches"],
  "additionalProperties": false
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "status": {"type": "string", "enum": ["success", "error", "timeout"]},
          "data": {"type": "object"},
          "error": {"type": "string"},
          "processing_time_ms": {"type": "integer"}
        }
      }
    },
    "summary": {
      "type": "object",
      "properties": {
        "total_searches": {"type": "integer"},
        "successful_searches": {"type": "integer"}, 
        "failed_searches": {"type": "integer"},
        "total_results": {"type": "integer"},
        "total_time_ms": {"type": "integer"},
        "average_time_ms": {"type": "number"}
      }
    }
  }
}
```

**Error Conditions:**
- `TOO_MANY_SEARCHES`: Exceeds maximum batch size
- `INVALID_SEARCH_TYPE`: Unknown search type specified
- `BATCH_TIMEOUT`: Entire batch operation timed out
- `CONCURRENT_LIMIT_EXCEEDED`: Too many concurrent operations

### get_facility_info

**Purpose:** Retrieve comprehensive information about ICE detention facilities.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "facility_name": {
      "type": "string",
      "maxLength": 100,
      "description": "Exact name of the facility"
    },
    "facility_id": {
      "type": "string",
      "pattern": "^[A-Z0-9]{3,10}$",
      "description": "Official facility identifier"
    },
    "include_capacity": {
      "type": "boolean",
      "default": true,
      "description": "Include current capacity and occupancy"
    },
    "include_contact": {
      "type": "boolean",
      "default": true,
      "description": "Include contact information"
    },
    "include_services": {
      "type": "boolean",
      "default": false,
      "description": "Include available services and programs"
    },
    "include_visitation": {
      "type": "boolean",
      "default": false,
      "description": "Include visitation policies and schedules"
    }
  },
  "anyOf": [
    {"required": ["facility_name"]},
    {"required": ["facility_id"]}
  ],
  "additionalProperties": false
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "facility": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "facility_id": {"type": "string"},
        "type": {"type": "string"},
        "operator": {"type": "string"},
        "address": {
          "type": "object",
          "properties": {
            "street": {"type": "string"},
            "city": {"type": "string"},
            "state": {"type": "string"},
            "zip_code": {"type": "string"},
            "country": {"type": "string"}
          }
        },
        "capacity": {
          "type": "object",
          "properties": {
            "total_capacity": {"type": "integer"},
            "current_population": {"type": "integer"},
            "occupancy_rate": {"type": "number"},
            "last_updated": {"type": "string", "format": "date-time"}
          }
        },
        "contact": {
          "type": "object",
          "properties": {
            "phone": {"type": "string"},
            "fax": {"type": "string"},
            "email": {"type": "string"},
            "website": {"type": "string"}
          }
        },
        "services": {
          "type": "array",
          "items": {"type": "string"}
        },
        "visitation": {
          "type": "object",
          "properties": {
            "schedule": {"type": "string"},
            "requirements": {"type": "array", "items": {"type": "string"}},
            "restrictions": {"type": "array", "items": {"type": "string"}}
          }
        }
      }
    }
  }
}
```

### parse_natural_query

**Purpose:** Parse natural language queries into structured search parameters using NLP.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "minLength": 3,
      "maxLength": 500,
      "description": "Natural language search query"
    },
    "auto_execute": {
      "type": "boolean",
      "default": false,
      "description": "Automatically execute the parsed search"
    },
    "confidence_threshold": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "default": 0.7,
      "description": "Minimum parsing confidence to accept"
    },
    "language": {
      "type": "string",
      "pattern": "^[a-z]{2}(-[A-Z]{2})?$",
      "default": "en",
      "description": "Language of the input query"
    },
    "include_alternatives": {
      "type": "boolean",
      "default": true,
      "description": "Include alternative interpretations"
    }
  },
  "required": ["query"],
  "additionalProperties": false
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "parsed_query": {
      "type": "object",
      "properties": {
        "search_type": {"type": "string"},
        "parameters": {"type": "object"},
        "confidence": {"type": "number"},
        "entities_found": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "type": {"type": "string"},
              "value": {"type": "string"},
              "confidence": {"type": "number"},
              "position": {"type": "object"}
            }
          }
        }
      }
    },
    "alternatives": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "search_type": {"type": "string"},
          "parameters": {"type": "object"},
          "confidence": {"type": "number"}
        }
      }
    },
    "suggestions": {
      "type": "array",
      "items": {"type": "string"}
    },
    "execution_result": {
      "type": "object",
      "description": "Only included if auto_execute is true"
    }
  }
}
```

**Supported Query Patterns:**
- "Find [Name] at [Facility/Location]"
- "Search for A-Number [Number]"
- "Who is at [Facility]?"
- "Locate [Name] in [City/State]"
- "Show me detainees in [Location]"

**Error Conditions:**
- `PARSE_FAILED`: Unable to parse natural language query
- `AMBIGUOUS_QUERY`: Multiple valid interpretations found
- `CONFIDENCE_TOO_LOW`: Parsing confidence below threshold
- `UNSUPPORTED_LANGUAGE`: Language not supported

## Tool Response Format

All tools return responses in the standard MCP format:

```json
{
  "content": [
    {
      "type": "text",
      "text": "Human-readable response"
    }
  ],
  "isError": false
}
```

For errors:
```json
{
  "content": [
    {
      "type": "text", 
      "text": "Error: Description of the error"
    }
  ],
  "isError": true
}
```

## Input Validation

All tools implement comprehensive input validation:

### String Validation
- Length limits enforced
- Character set restrictions
- Pattern matching for structured data
- Sanitization of special characters

### Numeric Validation  
- Range checking
- Type enforcement
- Precision limits

### Security Validation
- SQL injection prevention
- XSS prevention
- Path traversal prevention
- Command injection prevention

## Performance Characteristics

### Response Times
- **Name Search:** 500-2000ms (depending on fuzzy matching)
- **A-Number Search:** 200-800ms (exact match)
- **Facility Search:** 300-1200ms
- **Bulk Search:** 1000-5000ms (depends on batch size)
- **Natural Language Parsing:** 100-500ms

### Concurrency Limits
- **Maximum concurrent tools:** 10 per client
- **Bulk search concurrency:** 5 parallel searches
- **Rate limiting:** Adaptive based on success rates

### Caching Strategy
- **Cache TTL:** 1 hour for search results
- **Cache invalidation:** Automatic on data updates
- **Cache hit ratio:** ~85% for repeated searches

## Error Handling

### Retry Logic
- **Automatic retries:** Up to 3 attempts for transient errors
- **Exponential backoff:** Delays increase with each retry
- **Circuit breaker:** Temporary suspension after consecutive failures

### Graceful Degradation
- **Fallback modes:** Reduced functionality when services are impaired
- **Partial results:** Return available data even if some components fail
- **Error context:** Detailed error information for debugging

## Monitoring and Observability

### Metrics Collected
- Request/response times
- Success/error rates
- Cache hit rates
- Resource utilization
- User agent patterns

### Logging
- Request logging (sanitized)
- Error logging with context
- Performance metrics
- Security events

### Health Checks
- Service availability
- Dependency status
- Performance thresholds
- Resource limits