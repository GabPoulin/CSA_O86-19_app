"""Paramètres partagés de l'interface : nom du produit et image de marque (voir marque/)."""

import streamlit as st

TITLE = "Datum"
SOUS_TITRE = "par Le Repère Ingénierie"

# Logo horizontal blanc pour la barre latérale vert forêt ; symbole seul quand elle est repliée
LOGO_BARRE_LATERALE = "marque/logos/LeRepere_logo-horizontal_blanc.svg"
SYMBOLE_BARRE_LATERALE = "marque/logos/LeRepere_symbole_blanc.svg"
# Icône de l'onglet du navigateur
ICONE = "marque/logos/LeRepere_symbole_gris.png"


def configurer_page(titre_page: str) -> None:
    """
    Configure la page (titre de l'onglet, icône) et affiche le logo dans la barre latérale.

    Doit être appelée en premier dans chaque page Streamlit.
    """
    st.set_page_config(page_title=f"{titre_page} | {TITLE}", page_icon=ICONE)
    st.logo(LOGO_BARRE_LATERALE, size="large", icon_image=SYMBOLE_BARRE_LATERALE)
