from time import sleep
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sqlitedict import SqliteDict
import pandas as pd


def forever_word_cloud():
    while True:
        words = read_terms(role='speaker')
        words = {k:v['vote'] for k,v in words.items()}
        make_word_cloud(words)
        sleep(1)


# From a list of word frequencies, generate a wordcloud
# words : {'science': 55, 'rules': 34}
# loc   : Where to write the wordcloud
# Returns the location of the wordcloud
def make_word_cloud(words, loc='data/word_cloud.png'):
    wc = WordCloud(
        background_color='white', 
        max_words = 20, 
        prefer_horizontal = .5,
        font_step = 2,
        relative_scaling = 0.6,
        width = 2000, 
        height = 1000, 
        margin = 0)
    wc.generate_from_frequencies(words)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(loc, dpi=300)
    return(loc)


# An audience member can suggest a new term, `new_suggestion` which 
#   will be displayed to the speaker as a suggestion for the term box
# new_suggestion  : a word/phrase suggested as a term to vote on for the word cloud
# user_id         : the hash key representing a unique user
# role            : 'speaker' or 'audience'; 'speaker' can vote multiple times
# loc             : the location of the database to store suggestions
# Will write a word entry into the database like this:
# suggestions = {'word': {'count': 1, 'users': ['531ACD4...','132FF3...'], 'selected': True}}
def suggest_term(new_suggestion, user_id, role='audience', loc='data/app.sqlite'):
    if not isinstance(new_suggestion, str):
        return False
    
    # Get suggetions
    app_data = SqliteDict(loc, autocommit=True)
    suggestions = dict()
    if 'suggestions' in app_data.keys():
        suggestions = app_data['suggestions']
    #print(f"Loaded suggestions {suggestions}")
    
    # Add suggestions
    if new_suggestion not in suggestions.keys():
        suggestions[new_suggestion] = {
            'count'    : 1, 
            'users'    : [user_id],
            'selected' : False
        }
        # Speaker suggestions are automatically allowed
        # This is especially important for inital list population
        if role=='speaker':
            suggestions[new_suggestion]['selected'] = True
    elif user_id not in suggestions[new_suggestion]['users'] or role=='speaker':
        suggestions[new_suggestion]['count'] +=1
        suggestions[new_suggestion]['users'].append(user_id)

    
    app_data['suggestions'] = suggestions
    app_data.close()


# Read suggested terms in the format:
# suggestions = {'word': {'count': 1, 'users': ['531ACD4...','132FF3...'], 'selected': True}}
# loc : the location of the database to store suggestions
# Returns suggestions
def read_suggestions(loc='data/app.sqlite'):
    app_data = SqliteDict(loc, autocommit=True)
    if 'suggestions' not in app_data.keys():
        suggestions = {}
    else:
        suggestions = app_data['suggestions']
    app_data.close()
    return suggestions


# Read suggested terms as a pandas DataFrame
# Column headers: 'Word' (str), 'Suggestion Count' (int), 'Allow it?' (bool)
# loc : the location of the database to store suggestions
# Returns the DataFrame
def suggestion_table(loc='data/app.sqlite'):
    suggestions = read_suggestions(loc=loc)
    table = pd.DataFrame(columns=['Word', 'Suggestion Count', 'Allow it?'])
    for word, props in suggestions.items():
        table.loc[len(table.index)] = [word, props['count'], props['selected']]
    table = table\
            .sort_values('Suggestion Count', ascending=False)\
            .reset_index(drop=True)\
            .set_index('Word')
    return table


# After the speaker has approved a word, it gets moved to the term list
#   which allows the audience members to vote on it for display in the word cloud
# suggestion_table : a pandas dataframe with 'Word' (str), 'Suggestion Count' (int), 'Allow it?' (bool)
# loc              : the location of the database to read/store suggestions/terms
# This will create/remove term entries and update suggestion entries:
# terms = {'term' : {'vote':0, 'users': ['531ACD4...','132FF3...']}}
def update_terms(suggestion_table, loc='data/app.sqlite'):
    suggestion_table = pd.DataFrame(suggestion_table).reset_index()
    allowed_terms = list(suggestion_table[suggestion_table['Allow it?']==True]['Word'])
    unallowed_terms = list(suggestion_table[suggestion_table['Allow it?']==False]['Word'])

    # Get terms
    app_data = SqliteDict(loc, autocommit=True)
    terms = dict()
    if 'terms' in app_data.keys():
        terms = app_data['terms']
    #print(f"Loaded terms")
    
    # Update terms data
    for allowed_term in allowed_terms:
        if allowed_term not in terms.keys():
            terms[allowed_term] = {
                'vote'     : 0,
                'users'    : [],
            }
    # Only allowed terms
    terms = {k:v for (k,v) in terms.items() if k in allowed_terms}
    app_data['terms'] = terms
    #print(f"Saved terms")

    # Get & update suggestions data
    for allowed_term in allowed_terms:
        if allowed_term not in app_data['suggestions']:
            suggest_term(allowed_term, 'speaker', role='speaker')
        app_data['suggestions'][allowed_term]['selected'] = True
    for unallowed_term in unallowed_terms:
        if unallowed_term not in app_data['suggestions']:
            suggest_term(unallowed_term, 'speaker', role='speaker')
        app_data['suggestions'][unallowed_term]['selected'] = False
    #print(f"Saved suggestions")
    app_data.close()


# Read the term list
# role : 'speaker' or 'audience'; 'speaker' can vote multiple times
# loc  : the location of the database to read terms
# Updates terms:
# terms = {'term' : {'vote':0, 'users': ['531ACD4...','132FF3...']}}
def read_terms(role='audience', loc='data/app.sqlite'):
    app_data = SqliteDict(loc, autocommit=True)
    if 'terms' not in app_data.keys():
        terms = {}
    else:
        terms = app_data['terms']
    app_data.close()
    # The audience can only see the terms, not the votes, etc.
    if role == 'audience':
        return terms.keys()
    else:
        return terms


# When an audience member votes on terms, this function updates the database
# voted_terms : a term or list of terms
# user_id    : the hash key representing a unique user
# role       : 'speaker' or 'audience'; 'speaker' can vote multiple times
# loc        : the location of the database to store terms
# Updates the database to tally votes (increments 'vote'):
# terms = {'term' : {'vote':0, 'users': ['531ACD4...','132FF3...']}}
def vote_for_terms(voted_terms, user_id, role='audience', loc='data/app.sqlite'):
    if isinstance(voted_terms, str):
        voted_terms = [voted_terms]
    if not isinstance(voted_terms, list):
        return
    
    # Get terms
    app_data = SqliteDict(loc, autocommit=True)
    terms = dict()
    if 'terms' in app_data.keys():
        terms = app_data['terms']
    
    # Vote for the term (only once if not the speaker)
    for voted_term in voted_terms:
        if user_id not in terms[voted_term]['users'] or role=='speaker':
            terms[voted_term]['vote'] +=1
            terms[voted_term]['users'].append(user_id)
    # Save
    app_data['terms'] = terms
    app_data.close()


# Read voted terms as a pandas DataFrame
# Column headers: 'Word' (str), 'Votes' (int)
# loc : the location of the database to read terms
# Returns the DataFrame
def term_table(loc='data/app.sqlite'):
    terms = read_terms(role='speaker', loc=loc)
    table = pd.DataFrame(columns=['Word', 'Votes'])
    if not terms:
        return table
    for word, props in terms.items():
        table.loc[len(table.index)] = [word, props['vote']]
    table = table\
            .sort_values('Votes', ascending=False)\
            .reset_index(drop=True)\
            .set_index('Word')
    return table


# Populate the initial term table and update the database
# word_loc : the location of the starting word file (just a single word/term per line)
# db_loc   : the location of the database to store terms
# This will update the term table for display to the speaker upon first page load
def populate_initial_terms(word_loc='data/starting_words.tsv', db_loc='data/app.sqlite'):
    words = pd.read_csv(word_loc, sep="\t", names=['Word'])
    words['Votes'] = 0
    words['Allow it?'] = True
    for word in list(words['Word']):
        suggest_term(word, 'speaker', role='speaker', loc=db_loc)
    update_terms(words, loc=db_loc)