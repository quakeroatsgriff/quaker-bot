import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Local modules
import handler

# Get env variables
load_dotenv()
TOKEN = os.getenv( 'DISCORD_TOKEN' )
LOG_CHANNEL_ID = os.getenv( 'LOG_CHANNEL_ID' )
OWNER_ID = os.getenv( 'OWNER_ID' )

intents = discord.Intents.default()
intents.message_content = True
# bot_client = discord.Client( intents=intents )
bot = commands.Bot( command_prefix='$', intents=intents )

# Event that prints sucessful login
@bot.event
async def on_ready():
    """ Adds commands to bot """
    await bot.add_cog( handler.Handler( bot ) )
    print( f'Logged in as {bot.user}' )
    await bot.get_channel( int(LOG_CHANNEL_ID) ).send(content="Quaker bot is online")
    return

@bot.command(name="sync")
@commands.has_permissions(administrator=True)
async def sync_commands_with_bot( ctx ):
    """ Synchronizes commands with the bot """
    await bot.add_cog( handler.Handler( bot ) )
    await ctx.channel.send( "Done!" )
    return

bot.run(TOKEN)
