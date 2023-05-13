import pandas as pd
import numpy as np
import re
import sys
import argparse
import pickle

from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import GridSearchCV
from sklearn.compose import TransformedTargetRegressor
from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.naive_bayes import MultinomialNB

#Class that cleans up and prepares the tweet text in the pipeline for the count vectorizer
class Preprocessor( BaseEstimator, TransformerMixin ):
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
    def __init__(self, columns):
        self.columns = columns

    def fit(self, xs, xy, **params):
        return self

    # actually perform the selection
    def transform(self, xs):
        return xs[self.columns]

def train_model(debug_flag):
    # data = pd.read_csv( "./csv/train.csv" )
    data = pd.read_csv( "./csv/train.csv" ).sample(frac=0.1)
    # data = pd.read_csv( "./csv/train_small.csv" )
    # data = pd.read_csv( "./csv/train_five.csv" )
    ys = data["toxic"]
    xs = data.drop( columns = ['toxic', 'id'] )

    # use this instead of 'english' when testing if certain SWs improve performance
    ourStopWords = ['the', 'a', 'an', 'that']

    grid_params = {
        # 'vectorize__strip_accents' : ["unicode"],
        # 'vectorize__stop_words' : ["english"],
        'vectorize__ngram_range' : [(1,1)],
        'vectorize__max_features': [20000],
        # 'vectorize__max_df': [0.5,0.6,0.7,.8, 1],
    }

    regressor = TransformedTargetRegressor(
            LinearRegression( n_jobs = -1 ),
            func = np.sqrt,
            inverse_func = np.square
    )

    steps=[
        ( 'column_select', SelectColumns( 'comment_text' ) ),
        (' preprocess', Preprocessor() ),
        ( 'vectorize', CountVectorizer() ),
        # ( 'regressor', regressor ),
        ( 'nb', MultinomialNB() ),

    ]

    print("Fitting Data...",file=sys.stderr)
    pipe=Pipeline( steps )
    if ( debug_flag ):
        # transform text in pipeline preprocessor and print out processed text
        with pd.option_context('display.max_rows', None,
            'display.max_columns', None,
            'display.width', None):
            print( pipe.transform( xs ).to_csv() )
    search = GridSearchCV( pipe, grid_params, scoring = 'accuracy', n_jobs = 10 )
    # search = GridSearchCV(pipe, grid_params, scoring = 'r2', n_jobs = -1, cv = 5)
    fitted_model = search.fit( xs,ys )
    print( search.best_score_ )
    print( search.best_params_ )
    # print(search.best_estimator_)

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
    # Predict
    result = model.predict( input_dataframe ).tolist()[0]
    if (  result == 1 ):
        return "I think that was toxic."
    else:
        return "I don't think that was toxic."

def save_pickle( model, debug_flag ):
    """ Saves a model to disk by serializing """
    if ( debug_flag ): print( "Saving model to file:", model )
    pickle.dump( model, open( './models/model.pkl', 'wb') )

def load_pickle( debug_flag ):
    """ Loads a serialized model from disk """
    return pickle.load(open('./models/model.pkl','rb'))

if __name__ == "__main__":
    # Get command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument( '--debug', action = 'store_true' )
    args = parser.parse_args()

    train_model( debug_flag = args.debug )