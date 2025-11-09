"""_summary_"""

import streamlit as st

TITLE = "Calculatrice | Bois"
st.title(body=TITLE, anchor=False)
st.header("Accueil", anchor=False)
st.page_link(
    "pages/1_Bois de sciage.py",
    use_container_width=True,
    icon=":material/park:",
)
