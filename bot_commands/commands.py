import requests
import json
import os
import logging
from discord.ext import commands
from sleeper_utils import Draft  # Import the Draft class from the drafts module
from sleeper_utils import Member  # Import the Member class from the sleeper_utils module
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)

# Load the .env file
load_dotenv()

LEAGUE_ID = os.getenv('LEAGUE_ID')

class SleeperCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print('SleeperCommands is being instantiated')
        
    @commands.command()
    async def sleeper(self, ctx, username: str):  # Remove the "self" parameter
        print('sleeper command is being executed')
        # Make a request to the Sleeper API
        try:
            response = requests.get(f'https://api.sleeper.app/v1/user/{username}')
            data = json.loads(response.text)
            
            # Create a new Member object with the data from the Sleeper API
            member = Member(data["user_id"], data["username"])

            # Send a message to the Discord channel with the data from the Member object
            await ctx.send(f'User: {member.get_id()}, Username: {member.get_username()}')
        except Exception as e:
            print(e)
            await ctx.send('An error occurred while fetching the data.')

    @commands.command()
    async def drafts(self, ctx):
        print('drafts command is being executed')
        try:
            # Get all drafts grouped by season
            drafts_by_season = Draft.get_drafts(LEAGUE_ID)

            # Create a string to store the message
            message = ''

            # Iterate over the seasons
            for season, drafts in drafts_by_season.items():
                # Add the season to the message
                message += f'Season: {season}\n'

                # Iterate over the drafts for this season
                for draft in drafts:
                    # Add the draft to the message
                    message += f'Draft ID: {draft["draft_id"]}, Picks: {len(draft["picks"])}\n'

                # Add a newline to the message to separate the seasons
                message += '\n'

            # Send the message to the Discord channel
            await ctx.send(message)
        except Exception as e:
            print(e)
            await ctx.send('An error occurred while fetching the data.')

    @commands.command()
    async def picks(self, ctx, season: str):
        print('picks command is being executed')
        try:
            # Get the picks for the specified season
            picks = Draft.get_picks_for_season(LEAGUE_ID, season)

            # Check if any picks were found
            if picks is None:
                await ctx.send(f'No picks found for season {season}.')
                return

            # Create a string to store the message
            message = f'Picks for season {season}:\n'

            # Iterate over the picks
            for pick in picks:
                # Add the pick to the message
                message += f'Pick ID: {pick["pick_id"]}, Player ID: {pick["player_id"]}\n'

            # Send the message to the Discord channel
            await ctx.send(message)
        except Exception as e:
            print(e)
            await ctx.send('An error occurred while fetching the data.')