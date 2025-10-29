"""_summary_"""

import streamlit as st
import sawn_lumber as saw

st.title("6 | Bois de Sciage")
st.page_link("Accueil.py", label="Retour à l'accueil")


col1, col2, col3 = st.columns(3)
b = col1.number_input("Largeur de l'élément (mm)", min_value=38, width=160)
d = col2.number_input("Hauteur de l'élément (mm)", min_value=38, width=160, value=140)
msr_mel = col3.pills("Bois classé mécaniquement?", options=("MSR", "MEL"))
msr, mel = False, False
if msr_mel == "MSR":
    msr = True
elif msr_mel == "MEL":
    mel = True

WOOD_CATEGORIE = saw.lumber_category(b, d, msr, mel)

st.divider()
st.metric("Catégorie:", value=WOOD_CATEGORIE)
st.divider()
