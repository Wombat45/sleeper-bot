# Fantasy Football LLM Agent

A smart agent that processes fantasy football queries from the Discord bot and uses the MCP server to get data from Sleeper API, then generates intelligent responses.

## Architecture Overview

This agent is part of a three-component fantasy football assistant system:

```
Discord Bot (bot/) → LLM Agent (llm-agent/) → MCP Server (mcp-server/) → Sleeper API
```

1. **Discord Bot**: Forwards chat messages from Discord channels
2. **LLM Agent**: Processes messages and determines what fantasy football data to fetch
3. **MCP Server**: Provides structured access to Sleeper API data

## Features

- **Intelligent Query Processing**: Automatically detects what type of fantasy football data is needed
- **MCP Integration**: Seamlessly communicates with the MCP server
- **Pattern Recognition**: Uses regex patterns to understand user intent
- **Rich Context**: Provides enhanced fantasy football insights and context
- **Error Handling**: Graceful handling of API failures and errors
- **Async Operations**: Non-blocking API calls for better performance

## Quick Start

### 1. Install Dependencies

```bash
cd llm-agent
make install
# or
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
make setup-env
# Edit .env with your actual values
```

Required environment variables:
- `API_KEY`: Secret key for inter-component authentication (between Discord bot and LLM agent)
- `MCP_SERVER_URL`: URL of the MCP server (default: http://localhost:8000)
- `DEFAULT_LEAGUE_ID`: Your default fantasy football league ID
- `LLM_URL`: URL of your LLM service (optional)

**Note**: The Sleeper API is a read-only public API that doesn't require authentication. The API key is only used for secure communication between your Discord bot and the LLM agent.

### 3. Start the Agent

```bash
# Option 1: Using startup script
make start

# Option 2: Direct start
make run

# Option 3: Manual start
uvicorn agent:app --reload --host 0.0.0.0 --port 8001
```

### 4. Test the Agent

```bash
# Check health
make health

# Test a query
make test-query

# Get capabilities
make capabilities
```

## API Endpoints

### POST `/query`
Main endpoint for processing fantasy football queries.

**Request:**
```json
{
  "query": "who is john",
  "user_id": "optional_user_id",
  "league_id": "optional_league_id",
  "season": "optional_season"
}
```

**Response:**
```json
{
  "response": "Here's what I found for your query 'who is john':...",
  "context_used": {
    "function_calls": [...],
    "results": [...]
  },
  "error": null
}
```

**Headers:**
- `X-API-Key`: Your API key for inter-component authentication (between Discord bot and LLM agent)

**Note**: This API key is not for Sleeper API access - it's only used to secure communication between your Discord bot and this LLM agent.

### GET `/health`
Health check endpoint.

### GET `/capabilities`
Get available MCP functions and agent capabilities.

## Supported Query Types

The agent automatically detects and handles these types of queries:

### User Information
- `"who is john"` → `get_user("john")`
- `"john profile"` → `get_user("john")`
- `"john info"` → `get_user("john")`

### League Information
- `"league info"` → `get_league()`
- `"league details"` → `get_league()`
- `"league settings"` → `get_league()`

### User Leagues
- `"leagues for john"` → `get_user_leagues("john", "2024")`
- `"john leagues"` → `get_user_leagues("john", "2024")`

### Team Rosters
- `"rosters"` → `get_league_rosters()`
- `"team rosters"` → `get_league_rosters()`
- `"who is on john's team"` → `get_league_rosters()`

### League Members
- `"league members"` → `get_league_users()`
- `"who is in the league"` → `get_league_users()`

### NFL State
- `"nfl state"` → `get_nfl_state()`
- `"what week is it"` → `get_nfl_state()`
- `"current week"` → `get_nfl_state()`

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | Secret key for API authentication | Required |
| `MCP_SERVER_URL` | URL of the MCP server | `http://localhost:8000` |
| `DEFAULT_LEAGUE_ID` | Default fantasy football league ID | Empty |
| `LLM_URL` | URL of your LLM service | `http://localhost:11434/api/generate` |
| `HOST` | Host to bind the server to | `0.0.0.0` |
| `PORT` | Port to run the server on | `8001` |

### Pattern Customization

You can customize the query patterns by modifying the `_setup_function_patterns()` method in the `FantasyFootballAgent` class:

```python
def _setup_function_patterns(self):
    self.function_patterns = [
        {
            "name": "get_user",
            "patterns": [
                r"user\s+(\w+)",
                r"(\w+)\s+profile",
                # Add your custom patterns here
            ],
            "extract_params": lambda match: {"identifier": match.group(1)}
        },
        # Add more function patterns
    ]
```

## Development

### Running Tests

```bash
make test
```

### Code Quality

```bash
make lint      # Run linting checks
make format    # Format code
make clean     # Clean up generated files
```

### Docker

```bash
make docker-build  # Build Docker image
make docker-run    # Run Docker container
```

## Integration with Discord Bot

The Discord bot should send requests to the agent like this:

```python
import requests

def ask_fantasy_question(question: str) -> str:
    response = requests.post(
        "http://localhost:8001/query",
        json={"query": question},
        headers={"X-API-Key": "your-api-key"}
    )
    return response.json()["response"]

# Usage
answer = ask_fantasy_question("who is john")
```

## Integration with MCP Server

The agent automatically communicates with the MCP server to:

1. **Get Capabilities**: Discover available functions on startup
2. **Invoke Functions**: Call appropriate functions based on user queries
3. **Handle Responses**: Process and format the returned data
4. **Error Handling**: Gracefully handle MCP server errors

## Troubleshooting

### Common Issues

1. **Agent won't start**: Check if port 8001 is available
2. **MCP connection failed**: Verify MCP server is running on the configured URL
3. **API key errors**: Ensure the API key is set correctly in environment
4. **Pattern not matching**: Check the regex patterns in `_setup_function_patterns()`

### Debug Mode

Enable debug logging by setting the log level:

```bash
uvicorn agent:app --reload --log-level debug
```

### Health Checks

Use the health endpoints to diagnose issues:

```bash
curl http://localhost:8001/health
curl http://localhost:8001/capabilities
```

## Next Steps

1. **Customize Patterns**: Add more query patterns for your specific use cases
2. **Enhanced LLM Integration**: Integrate with your actual LLM for better response generation
3. **Caching**: Add caching for frequently requested data
4. **Authentication**: Implement more sophisticated authentication if needed
5. **Monitoring**: Add logging and monitoring for production use

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

[Add your chosen license]
