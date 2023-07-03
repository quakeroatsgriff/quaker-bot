import discord.ext.commands as commands
import discord
import requests
import re
import random as rand

class ESV_Handler( commands.Cog ):
    def __init__( self, bot, is_quiet, auto_load, ESV_API_KEY, ESV_API_URL ):
        self.bot = bot
        self.is_quiet = is_quiet
        self.key = ESV_API_KEY
        self.url = ESV_API_URL

    # Silly listener that listens to $retrieve messages from within matt's minecraft server
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if ( message.content.startswith( '$retrieve' ) ):
            matches = re.findall( r"\w+|(?<=\d:)\d+|(?<=\d)-\d+", message.content )
            matches.pop( 0 )
            input_message = ' '.join( matches )
            print( input_message )
            passage = await self.get_esv_text( input_message )
            # Print out passage if passage found
            if ( passage ):
                passage = re.sub( r'\n ', '\n>', passage )
                # Passage title in bold font
                response_message = f"**{ input_message }**\n> { passage }"
                try:
                    await message.channel.send( response_message )
                # Passage may be too long to send over discord message. Truncate the message to the first 2000 characters
                except discord.errors.HTTPException:
                    await self.send_response( message, "Passage may be too long. Truncating it.", "❌" )
                    await message.channel.send( response_message[:2000] )
                    return
            # Passage not found
            else:
                return await self.send_response( message, "Passage not found. Usage: `$retrieve <Book> <Chapter>:<Verse(s)>`", "❌" )

    @commands.command()
    async def retrieve( self, ctx, *args ):
        #TODO
        return
        """ Retrieves desginated passage from the ESV Bible and print it in chat """
        input_message = ' '.join( args )
        print( input_message )
        passage = await self.get_esv_text( input_message )
        # Print out passage if passage found
        if ( passage ):
            passage = re.sub( r'\n ', '\n>', passage )
            # Passage title in bold font
            response_message = f"**{ input_message }**\n> { passage }"
            try:
                await ctx.channel.send( response_message )
            # Passage may be too long to send over discord message. Truncate the message to the first 2000 characters
            except discord.errors.HTTPException:
                await self.send_response( ctx, "Passage may be too long. Truncating it.", "❌" )
                await ctx.channel.send( response_message[:2000] )
                return
        # Passage not found
        else:
            return await self.send_response( ctx, "Passage not found. Usage: `$retrieve <Book> <Chapter>:<Verse(s)>`", "❌" )

    @commands.command()
    async def proverbs( self, ctx, *args ):
        """ Retrieves a random proverbs verse from the ESV Bible and print it in chat """
        CHAPTER_LENGTHS = [
            33, 22, 35, 27, 23, 35, 27, 36, 18, 32,
            31, 28, 25, 35, 33, 33, 28, 24, 29, 30,
            31, 29, 35, 34, 28, 28, 27, 28, 27, 33,
            31
        ]
        # Get random chapter and verse numbers
        chapter = rand.randrange(1, len(CHAPTER_LENGTHS) )
        verse = rand.randint(1, CHAPTER_LENGTHS[chapter] )
        input_message = f'Proverbs {chapter}:{verse}'
        # GET request
        passage = await self.get_esv_text( input_message )
        passage = re.sub( r'\n ', '\n>', passage )
        response_message = f"Random Proverbs verse of the day:\n**{ input_message }**\n> { passage }"
        return await ctx.channel.send( response_message )

    async def send_response( self, ctx, message, reaction = None ):
        """ Responds to a command with a message or reaction """
        # If quiet flag is set to "False" (or was not given as argument), send the message
        if ( not self.is_quiet ):
            return await ctx.channel.send( message )
        # Else, send a reaction to indicate success or failure
        else:
            if ( reaction ): return await ctx.message.add_reaction( reaction )

    async def get_esv_text( self, passage ) -> bool:
        """ Sends and API GET request to https://api.esv.org and gets the given passage """
        params = {
            'q': passage,
            'include-headings': False,
            'include-footnotes': False,
            'include-verse-numbers': True,
            'include-short-copyright': True,
            'include-passage-references': False
        }
        headers = {
            'Authorization': f'Token {self.key}'
        }
        # Get request
        response = requests.get( self.url, params = params, headers = headers )
        print( response )
        print(response.json() )
        passages = response.json()['passages']
        # return the passage text OR False if passage was not found
        return passages[0].strip() if passages else False