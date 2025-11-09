"""_summary_"""

import streamlit as st

TITLE = "Calculatrice | Bois"
st.title(body=TITLE, anchor=False)
st.header("Accueil", anchor=False)
st.page_link(
    "pages/1_Bois de sciage.py",
    icon=":material/park:",
)
