"""_summary_"""

# IMPORTS
from dataclasses import dataclass
from sqlalchemy import orm, create_engine, Column, TEXT, REAL, INTEGER
import streamlit as st
import sawn_lumber as saw


# DB CONNECTION
@dataclass
class SawnLumberStrengths(orm.declarative_base()):
    """
    Se connecte à la table sawn_lumber_strengths de csa_o86_19.db.

    """

    __tablename__ = "sawn_lumber_strengths"
    index: int = Column("index", INTEGER, primary_key=True)
    category: str = Column("category", TEXT)
    specie: str = Column("specie", TEXT)
    grade: str = Column("grade", TEXT)
    fb: float = Column("fb", REAL)
    fv: float = Column("fv", REAL)
    fc: float = Column("fc", REAL)
    fcp: float = Column("fcp", REAL)
    ft: float = Column("ft", REAL)
    e: int = Column("e", INTEGER)
    e05: int = Column("e05", INTEGER)
    engine = create_engine("sqlite:///csa_o86_19.db")
    Session = orm.sessionmaker(engine)
    session = Session()


# CODE
st.title("Calculatrice | CSA-O86")
st.header("Bois de Sciage")
st.page_link("Accueil.py", label="Retour à l'accueil")

st.divider()

with st.container(horizontal_alignment="center"):

    # inputs pour déterminer la catégorie
    col1, col2 = st.columns(spec=2, gap="large")
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
        width="stretch",
        border=True,
    )

    # st.divider()

    # inputs pour déterminer les résistances spécifiques
    # choix de la classe
    side = False
    if category == "Beam":
        side = st.toggle(
            "Charges appliquées sur la grande face?",
            help="""
            Les résistances prévues des poutres et des longerons sont fondées sur des charges
            appliquées sur leur face étroite. Si les charges sont appliquées sur leur grande face,
            la résistance prévue en flexion à la fibre extrême et le module d’élasticité prévu doivent
            être multipliés par des coefficients de correction (CSA O86 - tableau 6.6)
            """,
        )

    # choix de la classe ou essence de bois
    # note pour indiquer l'essence choisie en cas de MSR ou MEL
    if msr or mel:
        st.info(
            "Le groupe d'essences SPF est utilisé par défaut pour caractériser le bois classé mécaniquement.",
            width=600,
        )

    if msr:
        specie = st.pills(
            label="Classe:",
            options=("normal", "courant", "rare"),
            default="courant",
            width="stretch",
            help="Si aucune classe n'est sélectionnée, 'courant' est utilisé par défaut.",
        )
        if not specie:
            specie = "courant"
    elif mel:
        specie = "normal"
    else:
        specie = st.pills(
            label="Groupe d'essences:",
            options=("df", "hf", "spf", "ns"),
            default="spf",
            width="stretch",
            help="Si aucune essence n'est sélectionnée, le groupe 'spf' est utilisé par défaut.",
        )
        if not specie:
            specie = "spf"

    # choix du grade
    grade_options = (
        SawnLumberStrengths.session.query(SawnLumberStrengths)
        .filter(SawnLumberStrengths.category == category)
        .filter(SawnLumberStrengths.specie == specie)
        .with_entities(SawnLumberStrengths.grade)
    )

    grade = st.pills(
        label="Grade:",
        options=grade_options,
        default=grade_options[1][0],
        width="stretch",
        help=f"Si aucun grade n'est sélectionnée, '{grade_options[1][0]}' est utilisé par défaut.",
    )
    if not grade:
        grade = grade_options[1][0]

    resistance = saw.specified_strengths(
        category=category,
        specie=specie,
        grade=grade,
        side=side,
    )

    st.header("Résistances prévues:")
    value_name = [
        ("Flexion", "$f_b$"),
        ("Cisaillement longitudinal", "$f_v$"),
        ("Compression parallèle au fil", "$f_c$"),
        ("Compression perpendiculaire au fil", "$f_{cp}$"),
        ("Traction parallèle au fil", "$f_t$"),
        ("Module d’élasticité", "$E$"),
        (
            "Module d’élasticité pour les calculs des éléments en compression",
            "$E_{05}$",
        ),
    ]
    col1, col2 = st.columns([3, 1])
    for i in range(0, int(len(resistance))):
        col1.markdown(f"{value_name[i][0]} :")
        col2.markdown(f"{value_name[i][1]} $= {resistance[i]} MPa$")
