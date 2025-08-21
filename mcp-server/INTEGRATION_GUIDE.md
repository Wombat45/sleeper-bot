# Integration Guide for Your Own LLM

This guide explains how to integrate the Sleeper MCP server with your own LLM client or application.

## What is MCP?

The Model Context Protocol (MCP) is a standard protocol that allows LLMs to access external data sources and tools. This server implements the MCP specification to provide fantasy football data from Sleeper.

## Quick Start

1. **Start the MCP server:**
```bash
cd mcp-server
uv sync
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

2. **Test the server:**
```bash
curl http://localhost:8000/health
curl http://localhost:8000/capabilities
```

## MCP Protocol Endpoints

The server exposes these MCP-compatible endpoints:

- `GET /capabilities` - Get available functions and their descriptions
- `POST /invoke` - Execute a function with parameters
- `GET /health` - Health check

## Available Functions

### `get_user(identifier: str)`
Get information about a Sleeper user by username or user ID.

**Example:**
```bash
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "function_name": "get_user",
    "parameters": {"identifier": "your_username"}
  }'
```

### `get_user_leagues(user_id: str, season: str, sport: str = "nfl")`
Get all leagues for a specific user in a given season.

**Example:**
```bash
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "function_name": "get_user_leagues",
    "parameters": {"user_id": "123", "season": "2024"}
  }'
```

### `get_league(league_id: str)`
Get detailed information about a specific league.

**Example:**
```bash
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "function_name": "get_league",
    "parameters": {"league_id": "456"}
  }'
```

### `get_league_rosters(league_id: str)`
Get all rosters in a specific league.

### `get_league_users(league_id: str)`
Get all users in a specific league.

### `get_nfl_state()`
Get current NFL season state information.

## Integration Patterns

### 1. Direct HTTP Integration

Your LLM can make direct HTTP calls to the MCP server:

```python
import httpx

async def get_fantasy_data(function_name: str, parameters: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/invoke",
            json={
                "function_name": function_name,
                "parameters": parameters
            }
        )
        return response.json()
```

### 2. MCP Client Library

Use an MCP client library to handle the protocol:

```python
from mcp import ClientSession, StdioServerParameters

async def connect_to_mcp():
    async with ClientSession(
        StdioServerParameters(
            command="uvicorn",
            args=["src.main:app"]
        )
    ) as session:
        # Use session to call functions
        result = await session.call_tool("get_user", {"identifier": "username"})
        return result
```

### 3. Function Calling

Your LLM can use function calling to access fantasy football data:

```python
# Define available functions for your LLM
available_functions = [
    {
        "name": "get_user",
        "description": "Get information about a Sleeper user",
        "parameters": {
            "type": "object",
            "properties": {
                "identifier": {
                    "type": "string",
                    "description": "Username or user ID"
                }
            },
            "required": ["identifier"]
        }
    }
    # ... other functions
]

# When your LLM needs fantasy football data, it can call these functions
```

## Fantasy Football Context

The server provides rich context about fantasy football:

- **Position Information**: Detailed descriptions of QB, RB, WR, TE, K, DEF
- **Scoring Rules**: How different stats translate to fantasy points
- **League Types**: PPR vs standard, keeper leagues, etc.
- **Strategy Suggestions**: Based on league settings

## Error Handling

The server returns structured error responses:

```json
{
  "status": "error",
  "error": "Rate limit exceeded. Please try again later."
}
```

Common error scenarios:
- Rate limiting (429)
- Invalid function names (400)
- API errors (500)

## Security Considerations

As per MCP specification:
- No authentication required (read-only API)
- Rate limiting enforced (1000 requests/minute)
- No sensitive data exposure
- Clear error reporting

**Note**: The Sleeper API is a read-only public API that doesn't require authentication. All fantasy football data is publicly accessible.

## Configuration

Copy `env.example` to `.env` and modify as needed:

```bash
cp env.example .env
# Edit .env with your preferred settings
```

## Development

- **Add new functions**: Extend `src/mcp/functions.py`
- **Modify context**: Update `src/mcp/context.py`
- **Add caching**: Extend `src/services/cache.py`

## Testing

Run the test suite:

```bash
uv run pytest
```

## Production Deployment

For production use:

1. Set `SERVER_ENVIRONMENT=production`
2. Use a proper WSGI server (Gunicorn, uWSGI)
3. Set up reverse proxy (Nginx, Apache)
4. Configure logging and monitoring
5. Set appropriate rate limits

## Troubleshooting

- **Server won't start**: Check if port 8000 is available
- **API errors**: Verify Sleeper API is accessible
- **Rate limiting**: Reduce request frequency or increase limits
- **Cache issues**: Check disk space and permissions

## Next Steps

1. Start the server and test basic functionality
2. Integrate with your LLM using one of the patterns above
3. Customize functions and context for your specific needs
4. Add authentication if required
5. Scale for production use
