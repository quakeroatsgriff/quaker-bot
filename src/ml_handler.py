import discord.ext.commands as commands
import src.model as ml
import random as rand
import asyncio

class ML_Handler( commands.Cog ):
    def __init__( self, bot, is_quiet, auto_load ):
        self.bot = bot
        self.is_quiet = is_quiet
        self.model = None
        if ( auto_load ):
            print( "Loading up pickled model" )
            self.model = ml.load_pickle( not self.is_quiet )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        # 1% chance a message is checked to see if it is toxic
        if ( rand.randint(0,99) == 0 ):
            # Only predict if there is a trained model and the message isn't a command
            if ( self.model and not message.content.startswith( '$' ) ):
                return await message.channel.send( ml.predict_message( self.model, message.content ) )
            else:
                return await message.channel.send( '🐴' )

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
        response = ml.predict_message( self.model, message, self.is_quiet )
        response_sent_message = await ctx.channel.send( response )
        # Add reactions to help out user with choosing one
        await response_sent_message.add_reaction( '✅' )
        await response_sent_message.add_reaction( '❌' )
        # Get reaction from user from the bot's reponse message
        def check(reaction, user):
            """ Checks if there was a reaction of either an X or check mark from the command author """
            return \
                ( user == ctx.author ) and \
                ( str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌' ) and \
                ( reaction.message == response_sent_message )

        # Wait for 60 seconds and see if the user will react
        try:
            reaction = await self.bot.wait_for('reaction_add', timeout = 30.0, check = check )
        # Time out
        except asyncio.TimeoutError:
            await self.send_response( response_sent_message, "You didn't react in time." )
        # The user reacted with an appropriate message
        else:
            await self.add_training_instance( message, reaction )
            await self.send_response( ctx, "Updated training file. Please retrain model for the message to be used.", reaction = '✅' )

        # Remove helper reactions from bot from prediction message
        await response_sent_message.remove_reaction( '✅', self.bot.user )
        await response_sent_message.remove_reaction( '❌', self.bot.user )
        return

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

    async def add_training_instance( self, message_text, reaction ):
        """ Adds an instance to the ./csv/train.csv file depending on the reaction """
        # Gets a hash of a message
        def elf_hash(message):
            hashed_message = 0
            high = 0
            for character in message:
                hashed_message = ( hashed_message << 4 ) + ord( character )
                # My text editor highlights 0x F0000000 as black and I can't see it lol
                high = ( hashed_message & 0xF0000000 )
                if ( high ):
                    hashed_message ^= ( high >> 24 )
                hashed_message &= ~high
            return hashed_message
        # Get hash of message text for the instance ID
        message_id = hex( elf_hash( message_text ) )[2:]
        # Verify that there is not an entry for this message already
        if ( not ml.find_instance( message_id, './csv/train.csv' ) ):
            try:
                train_file = open( './csv/train.csv', 'a' )
                # Prediction was verified to be correct
                if ( str( reaction[0] ) == "✅" ):
                    train_file.write( f'"{ message_id }","{ message_text }",1,1,1,1,1,1\n' )
                # Prediction was incorrect
                else:
                    train_file.write( f'"{ message_id }","{ message_text }",0,0,0,0,0,0\n' )
            except FileNotFoundError:
                print("Cannot open training file")
                return False
            return False
        train_file.close()
        return True
