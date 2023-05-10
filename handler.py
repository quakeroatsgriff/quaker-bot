import discord
import discord.ext.commands as commands

class Handler( commands.Cog ):
    def __init__( self, bot ):
        self.bot = bot
        self.model_loaded = False

    @commands.Cog.listener()
    async def on_member_join(self, member):
        pass

    @commands.command()
    async def hello( self, ctx ):
        """Says hello"""
        await ctx.message( "Hello" )
        return

    @commands.command()
    async def load_model( self, ctx ):
        """ Trains the ML model with the training data"""
        # If the model was already trained
        if ( self.model_loaded ):
            await ctx.message( "Model is already trained and ready to use." )
        else:
            await ctx.message( "Training the model..." )
            self.model_loaded = True
        return

