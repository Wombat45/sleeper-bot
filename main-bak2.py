# Import the necessary modules
import discord
import logging
import os
from discord.ext import commands
from dotenv import load_dotenv
from bot_commands import SleeperCommands

logging.basicConfig(level=logging.DEBUG)

# Load the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Create a new bot instance
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Instantiate the cog and add it to the bot
sleeper_commands = SleeperCommands(bot)
bot.add_cog(sleeper_commands)

@bot.event
async def on_ready():
    # Log the list of all commands
    all_commands = bot.commands
    print(f'All commands: {", ".join([cmd.name for cmd in all_commands])}')

    # Check if the 'sleeper' command is registered
    command = bot.get_command('sleeper')
    if command:
        print(f'The command "{command.name}" is registered with the bot.')
    else:
        print('The command is not registered with the bot.')

    # Check if the cog is correctly instantiated
    if isinstance(sleeper_commands, commands.Cog):
        print('The cog is correctly instantiated.')
    else:
        print('The cog is not correctly instantiated.')
    
# Log in the bot
bot.run(TOKEN)