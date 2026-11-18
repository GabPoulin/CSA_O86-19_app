"""Page d'accueil de Datum, par Le Repère Ingénierie."""

import streamlit as st
import config

config.configurer_page("Accueil")

st.title(body=config.TITLE, anchor=False)
st.caption(config.SOUS_TITRE)
st.header("Accueil", anchor=False)
st.page_link(
    "pages/1_Bois de sciage.py",
    icon=":material/park:",
)
