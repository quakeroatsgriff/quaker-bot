import discord
import discord.ext.commands as commands
import model

class Handler( commands.Cog ):
    def __init__( self, bot ):
        self.bot = bot
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
            await ctx.channel.send( "Training the model..." )
            self.model = model.train_model( False )
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
        response = model.predict_message( self.model, message )
        return await ctx.channel.send( response )

    @commands.command()
    async def reset( self, ctx ):
        """ Resets the model to 'None' """
        self.model = None
        return await ctx.channel.send( "Cleared the model" )

