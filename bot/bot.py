#!/usr/bin/env python3
"""Discord Bot for Fantasy Football Assistant.

This bot forwards chat messages from Discord channels to the LLM Agent,
which then uses the MCP server to get fantasy football data from Sleeper API.
"""

import discord
from discord.ext import commands
import requests
import os
from pathlib import Path

# Load environment variables from .env file if it exists
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    print(f"Loading environment from {env_file}")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value

# Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
LLM_API_URL = os.getenv("LLM_API_URL", "http://localhost:8001")
API_KEY = os.getenv("API_KEY", "your-api-key-here")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")

# Validate required configuration
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is required")

if not API_KEY or API_KEY == "your-api-key-here":
    raise ValueError("API_KEY environment variable must be set to a secure value")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)


@bot.event
async def on_ready():
    """Called when the bot is ready."""
    print(f"✅ {bot.user} is connected to Discord!")
    print(f"📡 LLM Agent URL: {LLM_API_URL}")
    print(f"🔑 API Key: {'*' * len(API_KEY) if API_KEY != 'your-api-key-here' else 'NOT SET'}")
    print(f"⚡ Command prefix: {COMMAND_PREFIX}")
    print(f"🏈 Ready to answer fantasy football questions!")
    print(f"💬 Natural conversation mode enabled - mention me or chat naturally!")


@bot.event
async def on_message(message):
    """Handle all messages for natural conversation."""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Check if the bot was mentioned or if it's a direct message
    bot_mentioned = bot.user.mentioned_in(message)
    is_dm = isinstance(message.channel, discord.DMChannel)
    
    # Process commands first (if they start with the command prefix)
    if message.content.startswith(COMMAND_PREFIX):
        await bot.process_commands(message)
        return
    
    # Handle natural conversation (mentions, DMs, or if no other commands)
    if bot_mentioned or is_dm:
        # Extract the actual question (remove the mention)
        question = message.content
        if bot_mentioned:
            # Remove the bot mention from the question
            question = question.replace(f'<@{bot.user.id}>', '').replace(f'<@!{bot.user.id}>', '').strip()
        
        # If the question is empty after removing mention, ask for clarification
        if not question:
            await message.channel.send("TWADE WIFF MEEE")
            return
        
        # Process the question using the same logic as the ask command
        await process_fantasy_football_question(message, question)
    
    # Also respond to messages that seem like fantasy football questions (optional)
    elif any(keyword in message.content.lower() for keyword in ['fantasy', 'football', 'league', 'team', 'roster', 'player', 'nfl', 'sleeper']):
        # Only respond if the message is a question or seems like it needs a response
        if '?' in message.content or any(word in message.content.lower() for word in ['who', 'what', 'when', 'where', 'why', 'how', 'tell me', 'show me']):
            await process_fantasy_football_question(message, message.content)


async def process_fantasy_football_question(message, question):
    """Process a fantasy football question and send the response.
    
    Args:
        message: Discord message object
        question: The fantasy football question to ask
    """
    try:
        print(f"🤔 Question from {message.author}: {question}")
        
        # Forward question to LLM Agent
        response = requests.post(
            f"{LLM_API_URL}/query",
            json={"query": question},
            headers={"X-API-Key": API_KEY},
            timeout=30  # 30 second timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("response", "Sorry, I couldn't get a response.")
            
            # Check if the response is too short or empty
            if not answer or len(answer.strip()) < 10:
                await message.channel.send("🤔 Hmm, I got a very short response. Let me try to get more details about that.")
                print(f"⚠️ Short response from LLM: '{answer}'")
                return
            
            # Split long responses to avoid Discord message limits
            if len(answer) > 2000:
                # Split into chunks
                chunks = [answer[i:i+1900] for i in range(0, len(answer), 1900)]
                for i, chunk in enumerate(chunks):
                    await message.channel.send(f"**Response (Part {i+1}/{len(chunks)}):**\n{chunk}")
            else:
                # Send the response directly without any prefix
                await message.channel.send(answer)
                
        elif response.status_code == 401:
            await message.channel.send("❌ Authentication failed. Please check the API key configuration.")
            print(f"🔴 Authentication failed for user {message.author}")
            
        elif response.status_code == 500:
            await message.channel.send("❌ The LLM Agent encountered an error. Please try again later.")
            print(f"🔴 LLM Agent error for user {message.author}: {response.text}")
            
        else:
            await message.channel.send(f"❌ Unexpected error (Status: {response.status_code}). Please try again.")
            print(f"🔴 Unexpected error for user {message.author}: {response.status_code} - {response.text}")
            
    except requests.exceptions.Timeout:
        await message.channel.send("⏰ The request timed out. Please try again.")
        print(f"⏰ Timeout for user {message.author}")
        
    except requests.exceptions.ConnectionError:
        await message.channel.send("🔌 Cannot connect to the LLM Agent. Please check if it's running.")
        print(f"🔌 Connection error for user {message.author}")
        
    except Exception as e:
        await message.channel.send(f"❌ An unexpected error occurred: {str(e)}")
        print(f"🔴 Unexpected error for user {message.author}: {str(e)}")


@bot.command(name='ask')
async def ask_league(ctx, *, question):
    """Ask a fantasy football question.
    
    Args:
        ctx: Discord context
        question: The fantasy football question to ask
    """
    await process_fantasy_football_question(ctx.message, question)


@bot.command(name='bothelp')
async def help_command(ctx):
    """Show help information."""
    help_text = f"""
**🏈 Fantasy Football Assistant Bot**

**Commands:**
`{COMMAND_PREFIX}ask <question>` - Ask a fantasy football question
`{COMMAND_PREFIX}bothelp` - Show this help information
`{COMMAND_PREFIX}status` - Check LLM Agent status

**Natural Conversation:**
• **Mention me** (@BotName) to chat naturally
• **Direct messages** for private conversations
• **Smart detection** of fantasy football questions
• **No commands needed** - just chat!

**Examples:**
`{COMMAND_PREFIX}ask who is john`
`{COMMAND_PREFIX}ask league info`
`{COMMAND_PREFIX}ask what week is it`
`{COMMAND_PREFIX}ask team rosters`

**Natural Examples:**
`@BotName who is john?`
`@BotName tell me about the league`
`@BotName what week is it?`
`@BotName show me team rosters`

**Supported Topics:**
• User information and profiles
• League details and settings
• Team rosters and players
• NFL season state and schedule
• Fantasy football strategies

**Need Help?**
Contact the bot administrator if you encounter any issues.
"""
    await ctx.send(help_text)


@bot.command(name='status')
async def status_command(ctx):
    """Check the status of the LLM Agent."""
    try:
        response = requests.get(f"{LLM_API_URL}/health", timeout=10)
        if response.status_code == 200:
            status = response.json()
            await ctx.send(f"✅ **LLM Agent Status:** {status.get('status', 'Unknown')}")
        else:
            await ctx.send(f"❌ **LLM Agent Status:** Error (Status: {response.status_code})")
    except Exception as e:
        await ctx.send(f"❌ **LLM Agent Status:** Cannot connect - {str(e)}")


@bot.event
async def on_command_error(ctx, error):
    """Handle command errors."""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument. Use `{COMMAND_PREFIX}bothelp` for usage information.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Command not found. Use `{COMMAND_PREFIX}bothelp` for available commands.")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")
        print(f"🔴 Command error for user {ctx.author}: {str(error)}")


if __name__ == "__main__":
    print("🚀 Starting Fantasy Football Discord Bot...")
    print(f"📡 LLM Agent URL: {LLM_API_URL}")
    print(f"🔑 API Key: {'*' * len(API_KEY) if API_KEY != 'your-api-key-here' else 'NOT SET'}")
    print(f"⚡ Command prefix: {COMMAND_PREFIX}")
    
    if not DISCORD_TOKEN:
        print("❌ ERROR: DISCORD_TOKEN not set!")
        print("   Please create a .env file with your Discord bot token.")
        exit(1)
    
    try:
        bot.run(DISCORD_TOKEN)
    except discord.LoginFailure:
        print("❌ ERROR: Invalid Discord bot token!")
        print("   Please check your DISCORD_TOKEN in the .env file.")
    except Exception as e:
        print(f"❌ ERROR: Failed to start bot: {str(e)}")