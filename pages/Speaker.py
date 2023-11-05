import streamlit as st
from code.util import *
import pandas as pd
from streamlit_js_eval import streamlit_js_eval

# Create speaker role for anyone accessing this page first
user_id = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = 'speaker'
else: 
    user_id = st.session_state['user_id']

with st.container():
    st.header(f"Term suggestions from the audience :point_down:")
    edited_df = st.data_editor(
        suggestion_table().drop(columns='Suggestion Count'), 
        key = 'selected_suggestions',
        use_container_width = True, 
        num_rows = 'dynamic',
    )
    # NOTE: In streamlit order matters! Since this button affects the table below
    #       the function that updates that table should be run before it. The flow
    #       is: button pressed, page refreshes, this if becomes true, the function 
    #       is called, and then the rest of the page renders
    if st.button('Update term candidates', type='secondary'):
        update_terms(edited_df)
    #left_button, right_button, space= st.columns([4,4,6])
    #with left_button:
    #    # NOTE: upon press, script is refreshed anyways, but a "do nothing" is needed right below
    #    st.button('↻ Get latest data', 'latest_suggestions_requested', type='secondary')
    #    st.write("")
    #with right_button:
    #    update_term_options = st.button('Update term choices', type='secondary')

st.divider()

with st.container():
    st.header(f"Audience votes for wordcloud 🗳")
    st.data_editor(
        term_table(), 
        key = 'selected_terms',
        use_container_width = True, 
    )
    # NOTE: upon press, script is refreshed anyways, but a "do nothing" is needed right below
    st.button('↻ Get Latest Vote Tally', 'latest_votes_requested', type='secondary')
    st.write("")

st.divider()

with st.container():
    hard_reset = st.button('Hard Reset', type='primary')

message = st.empty()



if hard_reset:
    do_hard_reset()
    message.warning('Successfully reset, reloading the page in 3 seconds', icon="⚠️")
    sleep(3)
    #message.empty()
    streamlit_js_eval(js_expressions="parent.window.location.reload()")