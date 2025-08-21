"""Configuration management for the Sleeper MCP server.

This module handles all configuration settings for the application, including:
- Server settings
- API endpoints
- Rate limiting parameters
- Caching configuration
"""
import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class SleeperAPIConfig(BaseModel):
    """Configuration for the Sleeper API."""

    base_url: HttpUrl = Field(
        default="https://api.sleeper.app/v1",
        description="Base URL for the Sleeper API",
    )
    rate_limit_per_minute: int = Field(
        default=1000,
        description="Maximum number of requests allowed per minute",
    )
    timeout_seconds: float = Field(
        default=30.0,
        description="Timeout for API requests in seconds",
    )

    @classmethod
    def from_env(cls) -> "SleeperAPIConfig":
        """Create configuration from environment variables."""
        return cls(
            base_url=os.getenv("SLEEPER_API_BASE_URL", "https://api.sleeper.app/v1"),
            rate_limit_per_minute=int(os.getenv("SLEEPER_API_RATE_LIMIT_PER_MINUTE", "1000")),
            timeout_seconds=float(os.getenv("SLEEPER_API_TIMEOUT_SECONDS", "30.0")),
        )


class CacheConfig(BaseModel):
    """Configuration for caching."""

    ttl_seconds: int = Field(
        default=300,
        description="Time to live for cached items in seconds",
    )
    max_size: int = Field(
        default=1000,
        description="Maximum number of items in the cache",
    )

    @classmethod
    def from_env(cls) -> "CacheConfig":
        """Create configuration from environment variables."""
        return cls(
            ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "300")),
            max_size=int(os.getenv("CACHE_MAX_SIZE", "1000")),
        )


class ServerConfig(BaseModel):
    """Main server configuration."""

    host: str = Field(
        default="0.0.0.0",
        description="Host to bind the server to",
    )
    port: int = Field(
        default=8000,
        description="Port to run the server on",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )
    environment: str = Field(
        default="development",
        description="Server environment (development/production)",
    )

    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Create configuration from environment variables."""
        return cls(
            host=os.getenv("SERVER_HOST", "0.0.0.0"),
            port=int(os.getenv("SERVER_PORT", "8000")),
            debug=os.getenv("SERVER_DEBUG", "false").lower() == "true",
            environment=os.getenv("SERVER_ENVIRONMENT", "development"),
        )


class Config(BaseModel):
    """Root configuration class combining all settings."""

    server: ServerConfig = Field(default_factory=ServerConfig.from_env)
    sleeper_api: SleeperAPIConfig = Field(default_factory=SleeperAPIConfig.from_env)
    cache: CacheConfig = Field(default_factory=CacheConfig.from_env)


@lru_cache()
def get_config() -> Config:
    """Get the application configuration.
    
    Returns:
        Config: Application configuration object
        
    Note:
        This function is cached to avoid reading/parsing configuration multiple times.
    """
    return Config()
