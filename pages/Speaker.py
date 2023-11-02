import streamlit as st
from code.util import *
import pandas as pd

# Create speaker role for anyone accessing this page first
user_id = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = 'speaker'
else: 
    user_id = st.session_state['user_id']

st.header(f"Here are term ideas from the audience :point_up:")
edited_df = st.data_editor(
    suggestion_table(), 
    key = 'selected_suggestions',
    use_container_width = True, 
    num_rows = 'dynamic',
)
ready = st.button('Update')

if ready:
    update_terms(edited_df)

st.divider()
st.header(f"Here's what the audience is thinking :thinking_face:")
st.data_editor(
    term_table(), 
    key = 'selected_terms',
    use_container_width = True, 
)