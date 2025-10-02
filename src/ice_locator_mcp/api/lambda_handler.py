"""
AWS Lambda handler for the ICE Locator heatmap API.
Adapts the FastAPI app to work with API Gateway.
"""

import os
import sys
from mangum import Mangum

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

# Import SST SDK for linked resources
try:
    from sst import Resource

    # Construct database URL from linked Postgres
    database_url = f"postgresql://{Resource.Database.username}:{Resource.Database.password}@{Resource.Database.host}:{Resource.Database.port}/{Resource.Database.database}"
except ImportError:
    # Fallback for local development
    database_url = os.environ.get("DATABASE_URL", "postgresql://localhost/ice_locator")

# Import and create the FastAPI app with database URL
from ice_locator_mcp.api.heatmap_api import create_app

app = create_app(database_url=database_url)

# Create Mangum handler
handler = Mangum(app, lifespan="off")
