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
has_voted = False
if 'has_voted' not in st.session_state:
    st.session_state['has_voted'] = False
else: 
    has_voted = st.session_state['has_voted']


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
    st.header(f"What does the future look like? :thinking_face:🗳")
    prompt  = f"Please vote for up to {max_selections} concepts/terms that you think will "\
            f"represent important research topics in the upcoming years"
    selected_terms = st.multiselect(
        prompt,
        read_terms(as_table=False),
        key = 'selected_terms',
        placeholder = 'Select terms...',
        default = None,
        max_selections = max_selections
    )
    left_button, cheat = st.columns([3,5])
    with left_button:
        placeholder = st.empty()
        terms_were_submitted =  placeholder.button('Vote', 'terms_were_submitted', disabled=has_voted, type='secondary')

    if user_id=='speaker':
        with cheat:
            if st.button('Vote as many times as you like!'):
                vote_for_terms(selected_terms, 'speaker', role='speaker')
                st.session_state['has_voted'] = False


with st.container():
    message = st.empty()
    if has_voted:
        message.warning("You've already voted")
    if terms_were_submitted:
        if len(selected_terms)==0:
            message.warning("No terms were selected")
        else:
            vote_for_terms(selected_terms, user_id, role='audience')
            st.session_state['has_voted'] = True
            placeholder.empty()
            with st.spinner('Voting...'):
                sleep(1)
            placeholder.button('Vote', disabled=True, key='disabled_vote', type='secondary')
            message.success("Thanks for your vote!")

st.write("")
#suggested = read_suggestions()
#suggested
#st.session_state