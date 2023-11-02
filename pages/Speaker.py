import streamlit as st
from code.util import *
import pandas as pd

# Create speaker role for anyone accessing this page first
user_id = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = 'speaker'
else: 
    user_id = st.session_state['user_id']

with st.container():
    st.header(f"Term suggestions from the audience :point_up:")
    edited_df = st.data_editor(
        suggestion_table(), 
        key = 'selected_suggestions',
        use_container_width = True, 
        num_rows = 'dynamic',
    )
    left_button, right_button, space= st.columns([4,4,6])
    with left_button:
        # NOTE: upon press, script is refreshed anyways, but a "do nothing" is needed right below
        st.button('↻ Get latest data', 'latest_suggestions_requested', type='secondary')
        st.write("")
    with right_button:
        update_term_options = st.button('Update term choices', type='secondary')


st.divider()

with st.container():
    st.header(f"Audience votes for wordcloud :thinking_face:")
    st.data_editor(
        term_table(), 
        key = 'selected_terms',
        use_container_width = True, 
    )
    # NOTE: upon press, script is refreshed anyways, but a "do nothing" is needed right below
    st.button('↻ Get latest data', 'latest_votes_requested', type='secondary')
    st.write("")

# The button to update allowed terms was pressed
if update_term_options:
    update_terms(edited_df)