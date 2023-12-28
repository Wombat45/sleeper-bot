import requests
import json
import os
import logging
import discord
from discord.ext import commands
from sleeper_utils import Draft  # Import the Draft class from the drafts module
from sleeper_utils import Member  # Import the Member class from the sleeper_utils module
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)

# Load the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
LEAGUE_ID = os.getenv('LEAGUE_ID')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def sleeper(ctx, username: str):
    print('sleeper command is being executed')
    try:
        response = requests.get(f'https://api.sleeper.app/v1/user/{username}')
        data = json.loads(response.text)
        member = Member(data["user_id"], data["username"])
        await ctx.send(f'User: {member.get_id()}, Username: {member.get_username()}')
    except Exception as e:
        print(e)
        await ctx.send('An error occurred while fetching the data.')

@bot.command()
async def drafts(ctx):
    print('drafts command is being executed')
    try:
        drafts_by_season = Draft.get_drafts(LEAGUE_ID)
        seasons = drafts_by_season.keys()
        message = 'Seasons: ' + ', '.join(seasons)
        await ctx.send(message)
    except Exception as e:
        print(e)
        await ctx.send('An error occurred while fetching the data.')

@bot.command()
async def picks(ctx, season):
    print('picks command is being executed')
    try:
        picks_for_season = Draft.get_picks_for_season(LEAGUE_ID, season)
        if picks_for_season:
            message = f'Picks for season {season}:\n```json'
            for pick in picks_for_season:
                message += f'\n{json.dumps(pick, indent=2)}'
            message += '```'
            await ctx.send(message)
        else:
            await ctx.send(f'No picks found for season {season}.')
    except Exception as e:
        print(e)
        await ctx.send('An error occurred while fetching the data.')

bot.run(TOKEN)