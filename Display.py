import streamlit as st
from PIL import Image
from code.util import *
from time import sleep, time
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(layout="wide")

# Create speaker role for anyone accessing this page first
user_id = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = 'speaker'
    # This should be the first page load lets populate initial terms and make a word cloud
    populate_initial_terms()
else: 
    user_id = st.session_state['user_id']

if 'last_words' not in st.session_state:
    st.session_state['last_words'] = None


# Barcode
with st.container():
    barcode = Image.open('data/qr_code.png')
    left_co, cent_co,last_co = st.columns([4,1,4])
    with cent_co:
        st.image(barcode, use_column_width='always')

st.divider()

# Wordcloud
with st.container():
    wordcloud = Image.open('data/word_cloud.png')
    left_co, cent_co, last_co = st.columns([1,2,1])
    with cent_co:
        wordcloud_holder = st.empty()
    wordcloud_holder = st.image(wordcloud, use_column_width='auto')


# Get the words
words = read_terms(role='speaker', as_table=False)
words = {k:v['vote']+1 for k,v in words.items()}


# If the words/votes have changed, make a new wordcloud
if words != st.session_state['last_words']:
    make_word_cloud(words)
    st.session_state['last_words'] = words
# Wait a few seconds and repeat
sleep(5)
st.rerun()

## SAFER, BUT RESULTS IN UGLY PAGE LOADS
#while True:
#    if words != st.session_state['last_words']:
#       make_word_cloud(words)
#       st.session_state['last_words'] = words
#    sleep(5)
#    wordcloud = Image.open('data/word_cloud.png')
#    wordcloud_holder.empty()
#    wordcloud_holder.image(wordcloud, use_column_width='auto')
