import os
import argparse

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Local modules
from src import ml_handler
from src import esv_handler

if __name__ == "__main__":
    # Get command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument( '--verbose', action = 'store_true' )
    parser.add_argument( '--quiet', action = 'store_true' )
    parser.add_argument( '-auto', action = 'store_true' )
    args = parser.parse_args()

    # Get env variables
    load_dotenv()
    TOKEN = os.getenv( 'DISCORD_TOKEN' )
    LOG_CHANNEL_ID = os.getenv( 'LOG_CHANNEL_ID' )
    OWNER_ID = os.getenv( 'OWNER_ID' )
    ESV_API_KEY = os.getenv( 'ESV_API_KEY' )
    ESV_API_URL = os.getenv( 'ESV_API_URL' )

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot( command_prefix='$', intents=intents )

    @bot.event
    async def on_ready():
        """ Event for successful login """
        # Adds commands to bot
        await bot.add_cog( ml_handler.ML_Handler( bot, args.quiet, args.auto ) )
        await bot.add_cog( esv_handler.ESV_Handler( bot, args.quiet, args.auto, ESV_API_KEY, ESV_API_URL ) )
        if ( args.verbose ):
            print( f'Logged in as {bot.user}' )
            await bot.get_channel( int(LOG_CHANNEL_ID) ).send(content="Quaker bot is online")
        return

    bot.run(TOKEN)
