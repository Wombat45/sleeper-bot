#!/usr/bin/env python3
"""Startup script for the Sleeper MCP server.

This script loads environment variables and starts the FastAPI server
with proper configuration.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Load environment variables from .env file if it exists
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    print(f"Loading environment from {env_file}")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                os.environ[key] = value

if __name__ == "__main__":
    import uvicorn
    from config.settings import get_config
    
    config = get_config()
    
    print(f"Starting Sleeper MCP Server on {config.server.host}:{config.server.port}")
    print(f"Environment: {config.server.environment}")
    print(f"Debug mode: {config.server.debug}")
    print(f"Sleeper API: {config.sleeper_api.base_url}")
    print(f"Rate limit: {config.sleeper_api.rate_limit_per_minute} requests/minute")
    
    uvicorn.run(
        "main:app",
        host=config.server.host,
        port=config.server.port,
        reload=config.server.debug,
        log_level="debug" if config.server.debug else "info"
    )
