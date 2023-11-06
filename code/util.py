import os
from time import sleep, time
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sqlitedict import SqliteDict
import pandas as pd


COLORS = [
    '#ec3333',
    '#eb1948',
    '#e7005c',
    '#dd006f',
    '#d00082',
    '#be1293',
    '#a727a2',
    '#8b36ae',
    '#6941b7',
    '#3749bc',
    '#0060d3',
    '#0073df',
    '#0083df',
    '#0091d3',
    '#009cbe',
    '#00a6a1',
    '#00af7f',
    '#00b75c',
    '#3abc37',
]
COLORS.reverse()
DEFAULT_COLOR = '#ffa755'


# Function to keep color consistent among common words 
class SimpleGroupedColorFunc(object):
    def __init__(self, color_to_words, default_color):
        self.word_to_color = {word: color
                              for (color, words) in color_to_words.items()
                              for word in words}
        self.default_color = default_color
    def __call__(self, word, **kwargs):
        return self.word_to_color.get(word, self.default_color)


# From a list of word frequencies, generate a wordcloud
# words : {'science': 55, 'rules': 34}
# loc   : Where to write the wordcloud
# Returns the location of the wordcloud
def make_word_cloud(words, max_words=25, loc='data/word_cloud.png'):
    top_words = [k for k, v in sorted(words.items(), key=lambda x: x[1])]
    top_words = [[i] for i in top_words]
    color_to_words = dict(zip(COLORS, top_words))

    grouped_color_func = SimpleGroupedColorFunc(color_to_words, DEFAULT_COLOR)
    wc = WordCloud(background_color="white", 
                   #max_words = max_words, 
                   prefer_horizontal = 1,
                   width = 1000, 
                   height = 1000, 
                   margin = 5,
                   #scale = 1,
                   min_font_size=6,
                   max_font_size = 80,
                   relative_scaling = .7,
                   font_path='data/Montserrat-Regular.ttf')#,
                   #color_func=grouped_color_func)
    wc.generate_from_frequencies(words)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(loc, dpi=300)
    return(loc)


def modify_suggestion(action, word, user_id, role='audience', loc='data/app.sqlite'):
    app_data = SqliteDict(loc, autocommit=True)
    # Create a new suggestions dictionary, or load the old one
    suggestions = dict()
    if 'suggestions' in app_data.keys():
        suggestions = app_data['suggestions']
    
    # CRUD like actions 
    #print(f"SUGGESTION     {action.upper():<8s} {word:<10s}")
    if action == 'create':
        if word not in suggestions.keys():
            suggestions[word] = {
                'count'    : 1, 
                'users'    : [user_id],
                'selected' : role=='speaker'
            }
        else:
            # It's already present, increase the count and add the user_id
            suggestions[word]['count'] += 1
            suggestions[word]['users'].append(user_id)
    elif action == 'read':
        result = None
        try:
            result = suggestions[word]
            app_data.close()
        except KeyError:
            result = None
        return result
    elif action == 'allow':
        suggestions[word]['selected'] = True
        modify_term('create', word, user_id, role)
    elif action == 'disallow':
        suggestions[word]['selected'] = False
        modify_term('delete', word, user_id, role)
    elif action=='delete':
        try:
            del suggestions[word]
        except KeyError:
            pass
        modify_term('delete', word, user_id, role)
    #print(f"Saving suggestions...")
    app_data['suggestions'] = suggestions
    app_data.close()


# Read suggested terms in the format:
# suggestions = {'word': {'count': 1, 'users': ['531ACD4...','132FF3...'], 'selected': True}}
# loc      : the location of the database to store suggestions
# as_table : whether to return as a pandas dataframe or just the suggestions dictionary
#            Column headers: 'Word' (str), 'Suggestion Count' (int), 'Allow it?' (bool)
#            Sorted descendingly by 'Suggestion Count'
def read_suggestions(loc='data/app.sqlite', as_table=True):
    # Get the suggestions dictionary
    app_data = SqliteDict(loc, autocommit=True)
    if 'suggestions' not in app_data.keys():
        suggestions = {}
    else:
        suggestions = app_data['suggestions']
    app_data.close()

    if as_table:
        # Make the table if requested
        table = pd.DataFrame(columns=['Word', 'Suggestion Count', 'Allow it?'])
        for word, props in suggestions.items():
            table.loc[len(table.index)] = [word, props['count'], props['selected']]
        table = table\
                .sort_values('Word', ascending=True)\
                .reset_index(drop=True)\
                .set_index('Word')
        #table = table.reset_index(drop=True).set_index('Word')
        return table
    else:
        return suggestions


def modify_term(action, word, user_id, role='audience', loc='data/app.sqlite'):
    app_data = SqliteDict(loc, autocommit=True)
    # Create a new terms dictionary, or load the old one
    terms = dict()
    if 'terms' in app_data.keys():
        terms = app_data['terms']
    
    #print(f"TERM           {action.upper():<8s} {word:<10s}")
    if action == 'create':
        if word not in terms.keys():
            terms[word] = {
                'vote'     : 1, 
                'users'    : [user_id],
            }
        else:
            # We could warn, but no action is ok too
            #print("CREATE IGNORED; ALREADY EXISTS")
            pass
    elif action == 'vote':
        if word in terms.keys():
            # Increase the vote and add the user_id
            # (as long as an audience member hasn't already voted)
            if (role == 'audience' and 'user_id' not in terms[word]['users']) or role == 'speaker':
                terms[word]['vote'] += 1
                if user_id not in terms[word]['users']:
                    terms[word]['users'].append(user_id)
    elif action == 'read':
        result = None
        try:
            result = terms[word]
        except KeyError:
            result = None
        return result
    elif action=='delete':
        try:
            del terms[word]
        except KeyError:
            pass
    #print(f"Saving terms...")
    app_data['terms'] = terms
    app_data.close()


# Read terms in the format:
# terms = {'word': {'vote': 1, 'users': ['531ACD4...','132FF3...']}}
# loc      : the location of the database to store suggestions
# role     : the type of user requesting the terms ('audience' or 'speaker')
# as_table : whether to return as a pandas dataframe or just the suggestions dictionary
#            Column headers: 'Word' (str), 'Votes' (int)
#            Sorted descendingly by 'Votes'
def read_terms(loc='data/app.sqlite', role='audience', as_table=True):
    app_data = SqliteDict(loc, autocommit=True)
    if 'terms' not in app_data.keys():
        terms = {}
    else:
        terms = app_data['terms']
    app_data.close()

    if as_table:
        # Make the table if requested
        table = pd.DataFrame(columns=['Word', 'Votes'])
        for word, props in terms.items():
            table.loc[len(table.index)] = [word, props['vote']]
        table = table\
                .sort_values(['Votes', 'Word'], ascending=[False, True])\
                .reset_index(drop=True)\
                .set_index('Word')
        if role == 'audience':
            # The audience can only see the terms, not the votes, etc.
            table.drop(columns='Votes')
        else:
            return table
    else:
        # The audience can only see the terms, not the votes, etc.
        if role == 'audience':
            choices = terms.keys()
            choices = sorted(choices)
            return choices
        else:
            return terms


# When an audience member votes on terms, this function updates the database
# voted_terms : a term or list of terms
# user_id    : the hash key representing a unique user
# role       : 'speaker' or 'audience'; 'speaker' can vote multiple times
# loc        : the location of the database to store terms
# Updates the database to tally votes (increments 'vote'):
# terms = {word : {'vote':0, 'users': ['531ACD4...','132FF3...']}}
def vote_for_terms(voted_terms, user_id, role='audience', loc='data/app.sqlite'):
    if isinstance(voted_terms, str):
        voted_terms = [voted_terms]
    if not isinstance(voted_terms, list):
        return
    print(f"---{int(time())} VOTING BY {user_id}---")
    # Vote for the term (only once if not the speaker)
    for term in voted_terms:
        modify_term('vote', term, user_id, role)


def update_terms(edited_df, user_id='speaker', role='speaker'):
    current_suggestions = read_suggestions(as_table=False)
    # Set the default 'Allow it?' state to true 
    edited_df = edited_df.fillna(True)
    print(f"---{int(time())} SUGGESTION UPDATE---")
    # Check if anything was added or allowed/disallowed
    #print(edited_df)
    edited_df = edited_df.reset_index()
    for i,r in edited_df.iterrows():
        word = r['Word']
        allowed = r['Allow it?']
        if r['Word'] not in current_suggestions.keys():
            modify_suggestion('create', word, user_id, role)
            current_suggestions = read_suggestions(as_table=False)
            allowed = True
        if allowed:
            modify_suggestion('allow', word, user_id, role)
        elif not allowed:
            modify_suggestion('disallow', word, user_id, role)

    # Check to see if anything was deleted
    for word in list(current_suggestions.keys()):
        if word not in list(edited_df['Word']):
            modify_suggestion('delete', word, user_id, role)


# Populate the initial term table and update the database
# word_loc : the location of the starting word file (just a single word/term per line)
# db_loc   : the location of the database to store terms
# This will update the term table for display to the speaker upon first page load
def populate_initial_terms(word_loc='data/starting_words.tsv', db_loc='data/app.sqlite'):
    # Load if needed
    app_data = SqliteDict(db_loc, autocommit=True)
    if 'status' not in app_data.keys():
        app_data['status'] = 'Loading'

    # Don't do anything if population has already happened
    # NOTE: A hard reset can be done instead
    if app_data['status'] == 'Loaded':
        return
    
    # Otherwise, load the inital words, populate as suggestions and terms
    # TODO: We can set the initial vote count too here, but its ignored for now
    print("Loading initial terms...")
    words = pd.read_csv(word_loc, sep="\t", names=['Word', 'Votes'])
    words['Allow it?'] = True
    for i,r in words.iterrows():
        word = r['Word']
        vote = int(r['Votes'])
        modify_suggestion('create', word, 'speaker', role='speaker', loc=db_loc)
        modify_term('create', word, 'speaker', role='speaker', loc=db_loc)
        for i in range(vote):
            modify_term('vote', word, 'speaker', role='speaker')

    app_data['status'] = 'Loaded'
    app_data.close()
    words = read_terms(role='speaker', as_table=False)
    words = {k:v['vote']+1 for k,v in words.items()}
    make_word_cloud(words)


def do_hard_reset():
    print(f"Performing hard reset...")
    try:
        os.remove('data/app.sqlite')
        os.remove('data/wordcloud.png')
    except:
        pass
    populate_initial_terms()
