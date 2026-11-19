"""
Point d'entrée de Datum (streamlit run Accueil.py ; fichier principal de Streamlit Cloud).

Pas de page d'accueil pour l'instant (décision de l'utilisateur) : l'application ouvre directement la
page Bois de sciage. Le menu de navigation est caché tant qu'il n'y a qu'une page.
"""

import streamlit as st

PAGES = [st.Page("pages/1_Bois de sciage.py", title="Bois de sciage", icon=":material/park:")]

st.navigation(PAGES, position="hidden").run()
