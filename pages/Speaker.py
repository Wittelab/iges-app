import streamlit as st
from code.util import *
import pandas as pd
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(layout="wide")

# Create speaker role for anyone accessing this page first
user_id = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = 'speaker'
else: 
    user_id = st.session_state['user_id']






lm, left, center, right, rm = st.columns([3,15,3,15,3])
with left:
    st.header(f"Term suggestions from audience :point_down:")
    edited_df = st.data_editor(
        read_suggestions().drop(columns='Suggestion Count'),
        key = 'selected_suggestions',
        use_container_width = True,
        height=1000,
        num_rows = 'dynamic',
    )
    # NOTE: In streamlit order matters! Since this button affects the table below
    #       the function that updates that table should be run before it. The flow
    #       is: button pressed, page refreshes, this if becomes true, the function 
    #       is called, and then the rest of the page renders
    if st.button('Update term candidates', type='secondary'):
        update_terms(edited_df)
        streamlit_js_eval(js_expressions="parent.window.location.reload()")

#with center:
#    st.write("⇨")

with right:
    st.header(f"Audience votes for wordcloud 🗳")
    st.data_editor(
        read_terms(role='speaker'),
        key = 'selected_terms',
        use_container_width = True,
        height=1000,
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