# Fantasy Football Assistant System Architecture

This document describes the complete architecture of the Fantasy Football Assistant system, which consists of three main components working together to provide intelligent fantasy football insights through Discord.

## System Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Discord Bot   │───▶│   LLM Agent      │───▶│   MCP Server    │───▶│   Sleeper API   │
│   (bot/)        │    │   (llm-agent/)   │    │   (mcp-server/) │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └─────────────────┘
```

## Component Details

### 1. Discord Bot (`bot/`)

**Purpose**: Interfaces with Discord to receive user questions and forward them to the LLM Agent.

**Key Features**:
- Listens for `!ask` commands in Discord channels
- Forwards questions to the LLM Agent via HTTP API
- Returns responses back to Discord users
- Handles authentication via API key

**Technology Stack**:
- Python with `discord.py` library
- HTTP client for communicating with LLM Agent
- Environment-based configuration

**Configuration**:
- `DISCORD_TOKEN`: Discord bot token
- `LLM_API_URL`: URL of the LLM Agent (e.g., `http://localhost:8001`)
- `API_KEY`: Shared secret for authentication

**Usage Example**:
```
User: !ask who is john
Bot: [Forwards to LLM Agent]
Agent: [Processes query and gets data from MCP Server]
Bot: [Returns response to Discord]
```

### 2. LLM Agent (`llm-agent/`)

**Purpose**: Intelligent middleware that processes natural language queries, determines what data is needed, and communicates with the MCP Server.

**Key Features**:
- Natural language query processing
- Pattern recognition for fantasy football queries
- Automatic function detection and parameter extraction
- MCP Server communication
- Response generation and formatting

**Technology Stack**:
- FastAPI for HTTP API
- Async HTTP client for MCP communication
- Regex-based pattern matching
- Pydantic models for data validation

**Query Processing Flow**:
1. Receives query from Discord Bot
2. Analyzes query using regex patterns
3. Determines which MCP functions to call
4. Executes function calls against MCP Server
5. Formats and returns response

**Supported Query Patterns**:
- User queries: `"who is john"`, `"john profile"`
- League queries: `"league info"`, `"league details"`
- Roster queries: `"rosters"`, `"team rosters"`
- NFL state: `"what week is it"`, `"nfl state"`

**Configuration**:
- `API_KEY`: Authentication secret
- `MCP_SERVER_URL`: MCP Server endpoint
- `DEFAULT_LEAGUE_ID`: Default fantasy league ID
- `LLM_URL`: External LLM service (optional)

### 3. MCP Server (`mcp-server/`)

**Purpose**: Model Context Protocol server that provides structured access to Sleeper API data with enhanced fantasy football context.

**Key Features**:
- MCP protocol implementation
- Sleeper API integration
- Rich fantasy football domain knowledge
- Caching and rate limiting
- Enhanced context and strategy suggestions

**Technology Stack**:
- FastAPI for HTTP API
- MCP protocol implementation
- Sleeper API client
- Caching layer
- Fantasy football context providers

**Available Functions**:
- `get_user(identifier)`: Get user information
- `get_user_leagues(user_id, season)`: Get user's leagues
- `get_league(league_id)`: Get league details
- `get_league_rosters(league_id)`: Get team rosters
- `get_league_users(league_id)`: Get league members
- `get_nfl_state()`: Get NFL season status

**Enhanced Context**:
- Position information (QB, RB, WR, TE, K, DEF)
- Scoring rules and calculations
- League type analysis (PPR, standard, keeper)
- Strategy suggestions based on settings

## Data Flow

### 1. User Interaction Flow

```
1. User types "!ask who is john" in Discord
2. Discord Bot receives command
3. Bot sends HTTP POST to LLM Agent: /query
4. LLM Agent analyzes query using pattern matching
5. Agent detects "get_user" function needed
6. Agent calls MCP Server: /invoke with get_user("john")
7. MCP Server calls Sleeper API for user data
8. MCP Server returns enhanced data with context
9. LLM Agent formats response
10. Bot sends response back to Discord
```

### 2. Data Enhancement Flow

```
1. MCP Server receives function call
2. Server calls Sleeper API
3. Server enhances raw data with:
   - Position information
   - Scoring explanations
   - Strategy suggestions
   - League type analysis
4. Server returns enhanced data
5. LLM Agent processes enhanced data
6. Agent generates intelligent response
```

## Configuration Management

### Environment Variables

Each component has its own configuration:

**Discord Bot**:
```bash
DISCORD_TOKEN=your_discord_token
LLM_API_URL=http://localhost:8001
API_KEY=your_shared_secret
```

**LLM Agent**:
```bash
API_KEY=your_shared_secret          # For secure communication with Discord Bot
MCP_SERVER_URL=http://localhost:8000 # MCP Server endpoint (no auth required)
DEFAULT_LEAGUE_ID=your_league_id    # Default fantasy league ID
LLM_URL=http://localhost:11434/api/generate # External LLM service (optional)
```

**MCP Server**:
```bash
SERVER_HOST=0.0.0.0                # Server binding
SERVER_PORT=8000                    # Server port
SLEEPER_API_BASE_URL=https://api.sleeper.app/v1  # Public API (no auth)
CACHE_TTL_SECONDS=300              # Cache time-to-live
```

**Note**: The Sleeper API is a read-only public API that doesn't require authentication. The API key is only used for secure communication between the Discord Bot and LLM Agent.

## Deployment Architecture

### Development Setup

```bash
# Terminal 1: Start MCP Server
cd mcp-server
uv sync
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Start LLM Agent
cd llm-agent
pip install -r requirements.txt
python start_agent.py

# Terminal 3: Start Discord Bot
cd bot
pip install -r requirements.txt
python bot.py
```

### Production Deployment

**Option 1: Docker Compose**
```yaml
version: '3.8'
services:
  mcp-server:
    build: ./mcp-server
    ports:
      - "8000:8000"
    environment:
      - SERVER_ENVIRONMENT=production
  
  llm-agent:
    build: ./llm-agent
    ports:
      - "8001:8000"
    environment:
      - MCP_SERVER_URL=http://mcp-server:8000
    depends_on:
      - mcp-server
  
  discord-bot:
    build: ./bot
    environment:
      - LLM_API_URL=http://llm-agent:8000
    depends_on:
      - llm-agent
```

**Option 2: Kubernetes**
- Deploy each component as separate pods
- Use services for inter-component communication
- Configure environment variables via ConfigMaps/Secrets

## Security Considerations

### Authentication
- **Inter-component authentication**: API key-based authentication between Discord Bot and LLM Agent
- **Discord bot token security**: Secure storage of Discord bot credentials
- **No Sleeper API auth**: The Sleeper API is a read-only public API that doesn't require authentication
- **Environment variable protection**: Secure storage of configuration values

### Rate Limiting
- MCP Server enforces Sleeper API rate limits (1000 requests/minute)
- LLM Agent can implement additional rate limiting for query processing
- Discord Bot can implement user-based rate limiting for Discord commands

### Data Privacy
- No sensitive data stored permanently
- Caching with appropriate TTL
- Secure communication between components
- **Public data only**: All fantasy football data from Sleeper is publicly accessible

## Monitoring and Observability

### Health Checks
- Each component provides `/health` endpoints
- Docker health checks for container monitoring
- Integration tests for component communication

### Logging
- Structured logging with context
- Error tracking and reporting
- Performance metrics collection

### Metrics
- API response times
- Function call success rates
- Cache hit ratios
- Error rates and types

## Scaling Considerations

### Horizontal Scaling
- MCP Server: Multiple instances behind load balancer
- LLM Agent: Multiple instances for query processing
- Discord Bot: Single instance (Discord limitation)

### Caching Strategy
- MCP Server: Redis for API response caching
- LLM Agent: In-memory caching for frequent queries
- Response caching for similar questions

### Database Considerations
- Currently stateless (no persistent storage)
- Can add database for:
  - Query history
  - User preferences
  - Cached responses
  - Analytics data

## Testing Strategy

### Unit Tests
- Each component has comprehensive unit tests
- Mock external dependencies
- Test edge cases and error conditions

### Integration Tests
- Test component communication
- End-to-end query flows
- API contract validation

### Load Testing
- Simulate multiple Discord users
- Test MCP Server performance
- Validate rate limiting

## Future Enhancements

### LLM Integration
- Integrate with actual LLM for response generation
- Implement conversation memory
- Add natural language understanding improvements

### Advanced Features
- Player comparison tools
- Trade analysis
- Waiver wire recommendations
- Draft assistance

### Platform Expansion
- Slack integration
- Web interface
- Mobile app
- API for third-party integrations

## Troubleshooting Guide

### Common Issues

1. **MCP Server Connection Failed**
   - Check if MCP Server is running on port 8000
   - Verify network connectivity
   - Check environment variables

2. **Discord Bot Not Responding**
   - Verify bot token is valid
   - Check if bot has proper permissions
   - Ensure LLM Agent is accessible

3. **Query Pattern Not Matching**
   - Review regex patterns in LLM Agent
   - Add new patterns for missing query types
   - Test pattern matching logic

4. **API Rate Limiting**
   - Check Sleeper API rate limits
   - Implement caching for frequently requested data
   - Add delay between requests if needed

### Debug Commands

```bash
# Check MCP Server
curl http://localhost:8000/health
curl http://localhost:8000/capabilities

# Check LLM Agent
curl http://localhost:8001/health
curl http://localhost:8001/capabilities

# Test query flow
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"query": "who is john"}'
```

## Conclusion

This architecture provides a robust, scalable foundation for a fantasy football assistant system. The separation of concerns allows each component to be developed, tested, and deployed independently while maintaining clear interfaces for communication.

The system is designed to be:
- **Maintainable**: Clear component boundaries and responsibilities
- **Scalable**: Can handle increased load through horizontal scaling
- **Secure**: Proper authentication and rate limiting
- **Observable**: Health checks, logging, and monitoring
- **Testable**: Comprehensive testing at all levels

By following this architecture, you can build a production-ready fantasy football assistant that provides valuable insights to your Discord community.
