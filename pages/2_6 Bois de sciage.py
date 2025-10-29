"""_summary_"""

import streamlit as st
import sawn_lumber as saw

st.title("6 | Bois de Sciage")
st.page_link("Accueil.py", label="Retour à l'accueil")

st.divider()

with st.container(horizontal_alignment="center"):

    # inputs pour déterminer la classe
    col1, col2 = st.columns(spec=2, gap="large", width=410)
    width = col1.number_input(
        label="Largeur de l'élément (mm)",
        min_value=38,
    )
    depth = col1.number_input(
        label="Hauteur de l'élément (mm)",
        min_value=38,
        value=140,
    )
    msr_mel = col2.pills(
        label="Bois classé mécaniquement?",
        options=("MSR", "MEL"),
        width="stretch",
    )
    msr, mel = False, False
    if msr_mel == "MSR":
        msr = True
    elif msr_mel == "MEL":
        mel = True

    category = saw.lumber_category(
        width=width,
        depth=depth,
        is_msr=msr,
        is_mel=mel,
    )
    col2.metric(
        label="Catégorie:",
        value=category,
        width="content",
    )

    st.divider()

    # inputs pour déterminer les résistances spécifiques
    side = st.toggle("Charges appliquées sur la grande face?")
    if msr:
        specie = st.pills(
            label="Classe de bois MSR:",
            options=("normal", "courant", "rare"),
            default="normal",
            width="stretch",
            help="Si aucune classe n'est sélectionnée, 'courant' est utilisé par défaut.",
        )
        if not specie:
            specie = "courant"
    elif mel:
        specie = "normal"
    else:
        specie = st.pills(
            label="Essence de bois:",
            options=("df", "hf", "spf", "ns"),
            default="spf",
            width=400,
            help="Si aucune essence n'est sélectionnée, le groupe 'spf' est utilisée par défaut.",
        )
        if not specie:
            specie = "spf"

    if category == "Lumber":
        grade = st.pills(
            label="Grade:",
            options=("ss", "n1-n2", "n3-stud"),
            default="n1-n2",
            width=400,
            help="Si aucun grade n'est sélectionnée, 'n1-n2' est utilisé par défaut.",
        )
        if not grade:
            grade = "n1-n2"
    elif category == "Light":
        grade = st.pills(
            label="Grade:",
            options=("cst", "std"),
            default="std",
            width=400,
            help="Si aucun grade n'est sélectionnée, 'std' est utilisé par défaut.",
        )
        if not grade:
            grade = "std"
    else:
        grade = "ss"

    saw.specified_strengths(
        category=category,
        specie=specie,
        grade=grade,
        side=side,
    )
