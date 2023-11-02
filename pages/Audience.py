from time import sleep
import streamlit as st
import hashlib
from code.util import *

# Define parameters
max_selections = 5

# Create a hash to identify this particular user session
user_id = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = hashlib.sha256().hexdigest()
else: 
    user_id = st.session_state['user_id']

# Hide the sidebar for audience members
if st.session_state['user_id'] != 'speaker':
    st.set_page_config(initial_sidebar_state="collapsed")
    st.markdown(
        """
        <style>
            [data-testid="collapsedControl"] { display: none }
        </style>
        """, 
        unsafe_allow_html=True,
    )


# The main page
with st.container():
    st.header(f"What does the future look like? :thinking_face:")
    prompt  = f"Please vote for up to {max_selections} concepts/terms that you think will "\
              f"represent important research topics in the upcoming years"
    selected_terms = st.multiselect(
        prompt,
        read_terms(),
        key = 'selected_terms',
        placeholder = 'Select terms...',
        default = None,
        max_selections = max_selections
    )
    left_button, right_button, space= st.columns([3,5,10])
    with left_button:
        placeholder = st.empty()
        terms_were_submitted =  placeholder.button('Vote', 'terms_were_submitted', type='secondary')
    with right_button:
        # NOTE: upon press, script is refreshed anyways, but a "do nothing" is needed right below
        st.button('↻ Get latest options', 'new_terms_requested', type='secondary')
        st.write("")


st.divider()

with st.container():
    st.header(f"I'd like to suggest my own term! :point_up:")
    suggested_term = st.text_input(
        'Suggest a term to the speaker', 
        'Artificial Intelligence',
        key = 'suggested_term',
    )
    term_was_suggested = st.button('Suggest', 'term_was_suggested', type='secondary')


with st.container():
    if terms_were_submitted:
        placeholder.button('Vote', disabled=True, key='disabled_vote', type='secondary')
        with st.spinner('Voting...'):
            vote_for_terms(selected_terms, user_id, role='speaker')
            sleep(1)
        placeholder.button('Vote', disabled=False, key='reenabled_vote', type='secondary')

    if term_was_suggested:
        with st.spinner('Suggesting...'):
            suggest_term( suggested_term, user_id, role='speaker')
            sleep(1)

st.write("")
#suggested = read_suggestions()
#suggested
#st.session_state