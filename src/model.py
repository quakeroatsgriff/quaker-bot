import pandas as pd
import numpy as np
import re
import sys
import argparse
import pickle

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import GridSearchCV
from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.naive_bayes import MultinomialNB

class Preprocessor( BaseEstimator, TransformerMixin ):
    """ Class that cleans up and prepares the tweet text in the pipeline for the count vectorizer """
    def fit( self, xs, ys = None ): return self
    def transform( self, xs ):
        def drop_newline( t ): return re.sub( '\n', ' ', t )
        # Remove Hyperlinks and the single case of "http" but no link
        def drop_hyperlinks( t ): return re.sub(r"\b(?:https?|ftp)://\S+\b", '', t)
        # Removes $, <, >, =, +, etc. and punctuation like hyphens, double quotations,
        # commas, pound signs, periods and turns them into spaces
        def drop_punctuation_and_symbols( t ): return re.sub( r'["#$%&()*+,-./:;<=>@[\]^_`{|}~·]', ' ', t )
        # Removes single quotations. Words like "I'm" will become "im"
        def drop_quotations(t): return re.sub(r"\'","",t)
        #Adds a space before ?
        def spacify_question_mark( t ): return re.sub('\?', ' ?', t )
        #Adds a space before !
        def spacify_exclamation_point( t ): return re.sub('\!', ' !', t )
        def combine_spaces( t ): return re.sub( '\s+', ' ', t )
        #Cut down any repeating characters of 3 or more (like aaaaa) is reduced to length 2 (aa)
        def reduce_extra_characters( t ): return re.sub( r"(.)(\1{1})(\1+)", r"\1\2", t )
        # def reduce_extra_characters(t): return re.sub(r"",'',t)
        transformed = xs.str.lower()              \
            .apply(drop_newline)                  \
            .apply(drop_hyperlinks)               \
            .apply(drop_punctuation_and_symbols)  \
            .apply(reduce_extra_characters)       \
            .apply(drop_quotations)               \
            .apply(spacify_question_mark)         \
            .apply(spacify_exclamation_point)     \
            .apply(combine_spaces)                \
            .str.strip()
        return transformed

class SelectColumns(BaseEstimator, TransformerMixin):
    """ Class used in the pipeline to select certain columns in a dataframe
    and pass them to the next transformation step in the pipeline """
    def __init__(self, columns):
        self.columns = columns

    def fit(self, xs, xy, **params):
        """ Nothing to do here """
        return self

    def transform(self, xs):
        """ Actually perform the selection """
        return xs[self.columns]

def train_model(debug_flag, target = 'toxic' ):
    """ Trains the model with the given features and target """
    data = pd.read_csv( "./csv/train.csv" )
    # data = pd.read_csv( "./csv/train.csv" ).sample( frac = 0.5 )

    train_y = data[ target ]
    train_x = data.drop( columns = [ target , 'id'] )

    grid_params = {
        'vectorize__ngram_range' : [ ( 1,1 ) ],
        'vectorize__max_features': [ 20000 ],
        # 'vectorize__max_df': [0.5,0.6,0.7,.8, 1],
    }

    pipeline_steps = [
        ( 'column_select', SelectColumns( 'comment_text' ) ),
        (' preprocess', Preprocessor() ),
        ( 'vectorize', CountVectorizer() ),
        ( 'nb', MultinomialNB() ),
    ]
    pipe=Pipeline( pipeline_steps )
    search = GridSearchCV( pipe, grid_params, scoring = 'f1', n_jobs = 10 )

    print("Fitting Data...", file = sys.stderr)
    fitted_model = search.fit( train_x, train_y )
    print( search.best_score_ )
    print( search.best_params_ )

    print("Done!",file=sys.stderr)
    return fitted_model

def predict_message( model, message ):
    """ Predicts if a message is toxic using the trained model"""
    # If the model does not exist, we can't predict
    if ( not model ):
        return "No model found!"
    # Turn message into a dataframe
    input_dataframe = pd.DataFrame( columns = ['comment_text'] )
    input_dataframe['comment_text'] = [ message ]
    # Predict and score the percentage of how likely the message is toxic
    score = round( ( model.predict_proba( input_dataframe ).tolist()[0][1] * 100 ), 2 )
    print( message, model.predict( input_dataframe ).tolist()[0] )
    return f"That message was { score }% toxic"

def save_pickle( model, debug_flag ):
    """ Saves a model to disk by serializing """
    if ( debug_flag ): print( "Saving model to file:", model )
    pickle.dump( model, open( './models/model.pkl', 'wb') )

def load_pickle( debug_flag ):
    """ Loads a serialized model from disk """
    return pickle.load( open( './models/model.pkl', 'rb' ) )

if __name__ == "__main__":
    # Get command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument( '--debug', action = 'store_true' )
    args = parser.parse_args()

    model = train_model( debug_flag = args.debug )
