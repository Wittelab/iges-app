import streamlit as st
from PIL import Image

image = Image.open('word_cloud.png')

st.image(image, caption='Sunrise by the mountains')