"""Page d'accueil de la calculatrice CSA O86:19."""

import streamlit as st
from config import TITLE

st.title(body=TITLE, anchor=False)
st.header("Accueil", anchor=False)
st.page_link(
    "pages/1_Bois de sciage.py",
    icon=":material/park:",
)
