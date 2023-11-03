import streamlit as st
from PIL import Image
from code.util import *
from time import sleep, time
#from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide")

# Create speaker role for anyone accessing this page first
user_id = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = 'speaker'
    # This should be the first page load, lets lazily populate the votes table
    populate_initial_terms()
else: 
    user_id = st.session_state['user_id']
if 'last_words' not in st.session_state:
    st.session_state['last_words'] = None
#if 'start_time' not in st.session_state:
#    st.session_state['start_time'] = time()
if 'last_update_time' not in st.session_state:
    st.session_state['last_update_time'] = time()


with st.container():
    wordcloud = Image.open('data/word_cloud.png')
    left_co, cent_co, last_co = st.columns([1,6,1])
    with cent_co:
        st.image(wordcloud, use_column_width='always')
    
    st.divider()
    
    barcode = Image.open('data/qr_code.png')
    left_co, cent_co,last_co = st.columns([4,1,4])
    with cent_co:
        st.image(barcode, use_column_width='always')


words = read_terms(role='speaker')
words = {k:v['vote']+1 for k,v in words.items()}
#words

time_since_update = time() - st.session_state['last_update_time']
if words != st.session_state['last_words'] or time_since_update>60:
    make_word_cloud(words)
    st.session_state['last_words'] = words
    st.session_state['last_update_time'] = time()
    print(f"\nChecking in 1 minute ", end="", flush=True)
    st.rerun()
else:
    #elapsed = int(time() - st.session_state['start_time'])
    #updated = int(time() - st.session_state['last_update_time'])
    #print(f"Total time alive: {elapsed}s. Time since last update: {updated}s")
    print(f"."*5, end="", flush=True)
    sleep(5)
    st.rerun()
#count = st_autorefresh(interval=2)