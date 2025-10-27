"""_summary_"""

import streamlit as st
import sawn_lumber as saw

st.title("6 | Bois de Sciage")
st.page_link("Accueil.py", label="Retour à l'accueil")

b = st.number_input("Largeur de l'élément (mm)", min_value=38)
d = st.number_input("Hauteur de l'élément (mm)", min_value=38)
msr = st.checkbox("Bois de charpente classé mécaniquement par résistance (MSR)")
mel = st.checkbox("Bois de charpente évalué par machine (MEL)")
categorie = saw.lumber_category(b, d, msr, mel)

st.write(categorie)
