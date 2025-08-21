# Fantasy Football Discord Bot

A Discord bot that forwards fantasy football questions to the LLM Agent, which then uses the MCP server to get data from Sleeper API.

## Overview

This bot is part of a three-component fantasy football assistant system:

```
Discord Users → Discord Bot → LLM Agent → MCP Server → Sleeper API
```

The bot listens for `!ask` commands in Discord channels and forwards them to the LLM Agent for processing.

## Features

- **Simple Commands**: Easy-to-use `!ask` command for fantasy football questions
- **Smart Error Handling**: Graceful handling of timeouts, connection errors, and API failures
- **Long Response Support**: Automatically splits long responses to avoid Discord message limits
- **Status Monitoring**: Built-in commands to check system health
- **Help System**: Comprehensive help command with examples
- **Environment Configuration**: Easy setup with `.env` file

## Quick Start

### 1. Install Dependencies

```bash
cd bot
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
- `DISCORD_TOKEN`: Your Discord bot token
- `API_KEY`: Shared secret for communication with LLM Agent
- `LLM_API_URL`: URL of your LLM Agent (default: http://localhost:8001)
- `COMMAND_PREFIX`: Bot command prefix (default: !)

### 3. Start the Bot

```bash
# Option 1: Using startup script (recommended)
make start

# Option 2: Direct start
make run

# Option 3: Manual start
python start_bot.py
```

## Commands

### `!ask <question>`
Ask a fantasy football question.

**Examples:**
```
!ask who is john
!ask league info
!ask what week is it
!ask team rosters
!ask who is on john's team
```

**Supported Topics:**
- User information and profiles
- League details and settings
- Team rosters and players
- NFL season state and schedule
- Fantasy football strategies

### `!bothelp`
Show help information and available commands.

### `!status`
Check the status of the LLM Agent.

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DISCORD_TOKEN` | Discord bot token | - | ✅ Yes |
| `API_KEY` | Shared secret for LLM Agent | - | ✅ Yes |
| `LLM_API_URL` | URL of LLM Agent | `http://localhost:8001` | ❌ No |
| `COMMAND_PREFIX` | Bot command prefix | `!` | ❌ No |

### Discord Bot Setup

1. **Create a Discord Application**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application"
   - Give it a name (e.g., "Fantasy Football Assistant")

2. **Create a Bot**:
   - Go to "Bot" section
   - Click "Add Bot"
   - Copy the bot token

3. **Set Bot Permissions**:
   - Go to "OAuth2" → "URL Generator"
   - Select scopes: `bot`, `applications.commands`
   - Select permissions: `Send Messages`, `Read Message History`, `Use Slash Commands`
   - Copy the generated URL and invite the bot to your server

4. **Enable Message Content Intent**:
   - Go to "Bot" section
   - Enable "Message Content Intent" under "Privileged Gateway Intents"

## Development

### Running Tests

```bash
make test
```

### Code Quality

```bash
make clean  # Clean up generated files
```

### Docker

```bash
make docker-build  # Build Docker image
make docker-run    # Run Docker container
```

### Configuration Validation

```bash
make validate-env  # Validate environment configuration
make bot-info      # Show bot configuration information
make check-status  # Check if LLM Agent is accessible
```

## Troubleshooting

### Common Issues

1. **Bot Not Responding**
   - Check if bot is online in Discord
   - Verify bot has proper permissions
   - Check console for error messages

2. **"Authentication Failed" Error**
   - Verify `API_KEY` matches between Bot and LLM Agent
   - Check that LLM Agent is running
   - Ensure no extra spaces in environment variables

3. **"Cannot Connect to LLM Agent" Error**
   - Verify LLM Agent is running on the configured URL
   - Check network connectivity
   - Use `make check-status` to verify connection

4. **Discord Login Failures**
   - Verify `DISCORD_TOKEN` is correct
   - Check if bot token is valid
   - Ensure bot is properly invited to the server

### Debug Commands

```bash
# Check bot configuration
make bot-info

# Validate environment
make validate-env

# Check LLM Agent status
make check-status

# Test LLM Agent connection
curl http://localhost:8001/health
```

## Integration with Other Components

### LLM Agent
The bot communicates with the LLM Agent via HTTP API:
- **Endpoint**: `/query`
- **Method**: POST
- **Authentication**: API key in `X-API-Key` header
- **Request**: `{"query": "user question"}`
- **Response**: `{"response": "answer", "context_used": {...}}`

### MCP Server
The bot doesn't directly communicate with the MCP Server - it goes through the LLM Agent:
```
Discord Bot → LLM Agent → MCP Server → Sleeper API
```

## Production Deployment

### Environment Management
- Use secure environment variable management
- Never commit `.env` files to version control
- Use different configurations for dev/staging/prod

### Monitoring
- Monitor bot uptime and response times
- Log all user interactions
- Set up alerts for bot failures

### Scaling
- Discord bots are limited to one instance per token
- Consider using Discord's slash commands for better performance
- Implement rate limiting for bot commands

## Security Considerations

### API Key Security
- Use strong, randomly generated API keys
- Rotate keys periodically
- Store keys securely (not in version control)

### Discord Bot Security
- Keep bot token secure
- Use minimal required permissions
- Monitor bot activity for unusual behavior

### Network Security
- Use HTTPS for LLM Agent communication in production
- Implement IP whitelisting if needed
- Monitor for unauthorized access attempts

## Example Usage

### Basic Questions
```
User: !ask who is john
Bot: Answer: Here's what I found for your query 'who is john':...

User: !ask league info
Bot: Answer: Here's what I found for your query 'league info':...

User: !ask what week is it
Bot: Answer: Here's what I found for your query 'what week is it':...
```

### Error Handling
```
User: !ask invalid question
Bot: Answer: I can help you with fantasy football questions! Try asking about users, leagues, rosters, or NFL state.

User: !ask who is john
Bot: ❌ Cannot connect to the LLM Agent. Please check if it's running.
```

## Next Steps

1. **Customize Commands**: Add more bot commands for specific functions
2. **Slash Commands**: Implement Discord slash commands for better UX
3. **Response Formatting**: Enhance response formatting with embeds and buttons
4. **User Preferences**: Store user preferences and league IDs
5. **Analytics**: Track usage patterns and popular questions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

[Add your chosen license]

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the system architecture documentation
3. Check if all components are running properly
4. Contact the development team
