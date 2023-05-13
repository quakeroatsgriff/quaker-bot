import discord
import discord.ext.commands as commands
import model as ml

class Handler( commands.Cog ):
    def __init__( self, bot, is_quiet ):
        self.bot = bot
        self.is_quiet = is_quiet
        self.model = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        pass

    @commands.command()
    async def hello( self, ctx ):
        """Says hello"""
        return await ctx.channel.send( f"Hello {ctx.author.name}" )

    @commands.command()
    async def train( self, ctx ):
        """ Trains the ML model with the training data """
        # If the model was already trained
        if ( self.model):
            await ctx.channel.send( "Model is already trained and ready to use." )
        else:
            if ( not self.is_quiet ):   await ctx.channel.send( "Training the model..." )
            self.model = ml.train_model( not self.is_quiet )
            await ctx.channel.send( "Model is trained!" )
        return

    @commands.command()
    async def predict( self, ctx, *args ):
        """ Predicts with trained ML model """
        # If the model was not trained yet, don't allow predictions
        if ( not self.model ):
            return await ctx.channel.send( "Cannot predict. The model is not trained yet" )
        # Assemble message to send to model
        message = ' '.join( args )
        # Get response message from the prediction
        response = ml.predict_message( self.model, message )
        return await ctx.channel.send( response )

    @commands.command()
    async def reset( self, ctx ):
        """ Resets the model to 'None' """
        self.model = None
        return await ctx.channel.send( "Cleared the model" )

    @commands.command()
    async def pickle( self, ctx ):
        """ Pickles the current model (serializes the object) """
        if ( not self.is_quiet ): await ctx.channel.send( "Serializing the current trained model" )
        ml.save_pickle( self.model, not self.is_quiet )
        return await ctx.channel.send( "Done!" )

    @commands.command()
    async def load( self, ctx ):
        """ Restores the model serialized on the disk """
        if ( not self.is_quiet ): await ctx.channel.send( "Retrieving model from disk" )
        self.model = ml.load_pickle( not self.is_quiet )
        return await ctx.channel.send( "Done!" )
