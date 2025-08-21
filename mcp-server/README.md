# Sleeper MCP Server

A Machine Context Protocol (MCP) server for integrating Sleeper fantasy sports data with any MCP-compatible LLM client. This server implements the MCP specification to provide structured access to Sleeper's API data.

## Overview

The Sleeper MCP Server acts as a bridge between MCP-compatible LLM clients and the Sleeper Fantasy Sports platform, implementing the Model Context Protocol (MCP) for seamless integration.

Features:
- Structured access to fantasy sports data via MCP
- Rate-limited API access
- Data caching and optimization
- OpenAPI documentation
- MCP-compliant function specifications
- Rich fantasy football domain context and insights

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/sleeper-mcp.git
cd sleeper-mcp

# Install dependencies using uv
uv sync

# Start the server
uv run uvicorn src.main:app
```

## Integration with MCP Clients

The Sleeper MCP server integrates with any MCP-compatible client:

1. Start the server:
```bash
uv run uvicorn src.main:app
```

2. Use with any MCP client:

a. Via session:
```bash
your-mcp-client session --with-extension "uvicorn src.main:app"
```

b. Via single command:
```bash
your-mcp-client run --with-extension "uvicorn src.main:app" -t "your instructions"
```

Available functions:
- `get_user(identifier: str)` - Get user information
- `get_user_leagues(user_id: str, season: str)` - Get leagues for a user
- `get_league(league_id: str)` - Get league details
- `get_league_rosters(league_id: str)` - Get league rosters
- `get_league_users(league_id: str)` - Get league users
- `get_nfl_state()` - Get NFL season state

## MCP Protocol Implementation

This server implements the Model Context Protocol (v2024-11-05) which includes:

1. Initialization Phase:
   - Server capability discovery
   - Protocol version negotiation
   - Feature negotiation

2. Operation Phase:
   - Function discovery and invocation
   - Resource access
   - Error handling

3. Security:
   - Rate limiting
   - Error reporting
   - Access controls

## Development

### Project Structure

```
sleeper-mcp/
├── docs/
│   ├── openapi.yaml        # API specification
│   └── sleeper_api_raw.html # Raw API documentation
├── src/
│   ├── api/               # API endpoints
│   ├── models/            # Data models
│   ├── mcp/              # MCP protocol implementation
│   ├── services/         # Business logic
│   └── config/           # Configuration
├── tests/                # Test suites
├── pyproject.toml        # Project dependencies
├── README.md            # This file
└── TODO.md             # Development tasks
```

### Running Tests

```bash
uv run pytest
```

### Development Server

```bash
uv run uvicorn src.main:app --reload
```

## Security Considerations

As per MCP specification:
- No authentication required (read-only API)
- Rate limiting enforced (1000 requests/minute)
- No sensitive data exposure
- Clear error reporting

**Note**: The Sleeper API is a read-only public API that doesn't require authentication. All fantasy football data is publicly accessible.

## API Documentation

- OpenAPI documentation: `/docs`