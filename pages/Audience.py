import streamlit as st
from time import sleep
import hashlib
from code.util import *

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


# Define parameters
max_selections = 5
term_options   = ['Green', 'Yellow', 'Red', 'Blue']


# The main page
with st.container():
    st.header(f"What does the future look like? :thinking_face:")
    prompt  = f"Please choose up to {max_selections} concepts/terms that you think will "\
              f"represent important research topics in the upcoming years"
    selected_terms = st.multiselect(
        prompt,
        read_terms(),
        key = 'selected_terms',
        default = None,
        max_selections = max_selections
    )
    terms_were_submitted = st.button("Select", "terms_were_submitted", type="primary")
    
    st.divider()
    st.header(f"I'd like to suggest my own term! :point_up:")
    suggested_term = st.text_input(
        "Suggest a term to the speaker", 
        "Artificial Intelligence",
        key = 'suggested_term',
    )
    term_was_suggested = st.button("Suggest", "term_was_suggested", type="primary")

suggested = read_suggestions()
suggested

if terms_were_submitted:
    vote_for_terms(selected_terms, user_id)

if term_was_suggested:
    write_suggestions(suggested_term, user_id)
