from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sqlitedict import SqliteDict
import pandas as pd


def make_word_cloud(words, loc="data/word_cloud.png"):
    wc = WordCloud(
        background_color="black", 
        max_words = 20, 
        prefer_horizontal = 1,
        width = 1000, 
        height = 1000, 
        margin = 5)
    wc.generate_from_frequencies(words)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(loc, dpi=300)
    return(loc)


def write_suggestions(new_suggestion, user_id, god=True):
    if not isinstance(new_suggestion, str):
        return False
    
    # Get suggetions
    app_data = SqliteDict('data/app.sqlite', autocommit=True)
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
    elif user_id not in suggestions[new_suggestion]['users'] or god:
        suggestions[new_suggestion]['count'] +=1
        suggestions[new_suggestion]['users'].append(user_id)
    
    app_data['suggestions'] = suggestions
    app_data.close()


def read_suggestions():
    app_data = SqliteDict('data/app.sqlite', autocommit=True)
    if 'suggestions' not in app_data.keys():
        suggestions = {}
    else:
        suggestions = app_data['suggestions']
    app_data.close()
    return suggestions


def suggestion_table():
    suggestions = read_suggestions()
    table = pd.DataFrame(columns=['Word', 'Votes', 'Allow it?'])
    for word, props in suggestions.items():
        table.loc[len(table.index)] = [word, props['count'], props['selected']]
    table = table\
            .sort_values('Votes', ascending=False)\
            .reset_index(drop=True)\
            .set_index('Word')
    return table


def update_terms(suggestion_table):
    suggestion_table = pd.DataFrame(suggestion_table).reset_index()
    #print(updated_terms)
    allowed_terms = list(suggestion_table[suggestion_table['Allow it?']]['Word'])
    unallowed_terms = list(suggestion_table[~suggestion_table['Allow it?']]['Word'])
    print(f"Allowed  : {allowed_terms}")
    print(f"Unallowed: {unallowed_terms}")
    # Get terms
    app_data = SqliteDict('data/app.sqlite', autocommit=True)
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
        app_data['suggestions'][allowed_term]['selected'] = True
    for unallowed_term in unallowed_terms:
        app_data['suggestions'][unallowed_term]['selected'] = False
    #print(f"Saved suggestions")
    app_data.close()


def read_terms(role='audience'):
    app_data = SqliteDict('data/app.sqlite', autocommit=True)
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


def vote_for_terms(voted_terms, user_id, god=True):
    if isinstance(voted_terms, str):
        voted_terms = [voted_terms]
    if not isinstance(voted_terms, list):
        return
    
    # Get terms
    app_data = SqliteDict('data/app.sqlite', autocommit=True)
    terms = dict()
    if 'terms' in app_data.keys():
        terms = app_data['terms']
    
    # Vote for the term (once)
    print(f"TERMS: {terms}")
    print(f"Voted: {voted_terms}")
    for voted_term in voted_terms:
        if user_id not in terms[voted_term]['users'] or god:
            terms[voted_term]['vote'] +=1
            terms[voted_term]['users'].append(user_id)
    # Save
    app_data['terms'] = terms
    app_data.close()


def term_table():
    terms = read_terms(role='speaker')
    print(f">>{terms}<<")
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

