import discord
import discord.ext.commands as commands
import model as ml

class Handler( commands.Cog ):
    def __init__( self, bot, is_quiet, auto_load ):
        self.bot = bot
        self.is_quiet = is_quiet
        self.model = None
        if ( auto_load ):
            print( "Loading up pickled model" )
            self.model = ml.load_pickle( not self.is_quiet )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        pass

    @commands.command()
    async def hello( self, ctx ):
        """Says hello"""
        return await ctx.channel.send( f"Hello {ctx.author.name}" )

    @commands.command()
    @commands.is_owner()
    async def train( self, ctx ):
        """ Trains the ML model with the training data """
        # If the model was already trained
        if ( self.model):
            await self.send_response( ctx, "Model is already trained and ready to use.", reaction = '❌' )
        else:
            await self.send_response( ctx, "Training the model..." )
            self.model = ml.train_model( not self.is_quiet )
            await self.send_response( ctx, "Model is trained!", reaction = '✅' )
        return

    @commands.command()
    async def predict( self, ctx, *args ):
        """ Predicts with trained ML model """
        # If the model was not trained yet, don't allow predictions
        if ( not self.model ):
            return await self.send_response( ctx, "Cannot predict. The model is not trained yet", reaction = '❌' )
        # Assemble message to send to model
        message = ' '.join( args )
        # Get response message from the prediction
        response = ml.predict_message( self.model, message )
        return await ctx.channel.send( response )

    @commands.command()
    async def reset( self, ctx ):
        """ Resets the model to 'None' """
        self.model = None
        await self.send_response( ctx, "Cleared the model", reaction = '✅' )
        return

    @commands.command()
    @commands.is_owner()
    async def pickle( self, ctx ):
        """ Pickles the current model (serializes the object) """
        await self.send_response( ctx, "Serializing the current trained model" )
        ml.save_pickle( self.model, not self.is_quiet )
        await self.send_response( ctx, "Done!", reaction = '✅' )
        return

    @commands.command()
    async def load( self, ctx ):
        """ Restores the model serialized on the disk """
        await self.send_response( ctx, "Retrieving model from disk" )
        self.model = ml.load_pickle( not self.is_quiet )
        await self.send_response( ctx, "Done!", reaction = '✅' )
        return

    async def send_response( self, ctx, message, reaction = None ):
        """ Responds to a command with a message or reaction """
        # If quiet flag is set to "False" (or was not given as argument), send the message
        if ( not self.is_quiet ):
            return await ctx.channel.send( message )
        # Else, send a reaction to indicate success or failure
        else:
            if ( reaction ): return await ctx.message.add_reaction( reaction )

