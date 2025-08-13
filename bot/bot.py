# bot/bot.py
import discord
from discord.ext import commands
import requests
import os

bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
LLM_API_URL = os.getenv("LLM_API_URL")
API_KEY = os.getenv("API_KEY")

@bot.command(name='ask')
async def ask_league(ctx, *, question):
    try:
        response = requests.post(
            LLM_API_URL,
            json={"query": question},
            headers={"X-API-Key": API_KEY}
        )
        llm_reply = response.json()["response"]
        await ctx.send(llm_reply)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

bot.run(os.getenv("DISCORD_TOKEN"))