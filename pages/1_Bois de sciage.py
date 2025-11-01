"""_summary_"""

# IMPORTS
from dataclasses import dataclass
from sqlalchemy import orm, create_engine, Column, TEXT, REAL, INTEGER
import streamlit as st
import sawn_lumber
import Accueil


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

# ---- en-tête ----
st.title(Accueil.TITLE)
st.page_link("Accueil.py", label="Retour à l'accueil")
st.divider()

# --- container principal ---
with st.container(horizontal_alignment="center"):
    st.header(
        "Bois de Sciage",
        help="""Les méthodes et les données de calcul de ne s’appliquent qu’au bois de charpente 
        conforme à CSA O141.""",
    )

    # --- inputs pour déterminer la catégorie ---
    st.subheader(
        "Matériaux",
        help=""" Les calculs reposent sur l’utilisation de bois d’œuvre classé suivant les Règles 
        de classification pour le bois d’œuvre canadien de la NLGA, et identifié au moyen de 
        l’estampille d’une association ou d’un organisme indépendant de classement, conformément 
        à CSA O141.""",
    )
    col1, col2 = st.columns(2, gap="medium")
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
    MSR, MEL = False, False
    if msr_mel == "MSR":
        MSR = True
    elif msr_mel == "MEL":
        MEL = True

    # --- calcul pour déterminer la catégorie ---
    CATEGORY = sawn_lumber.lumber_category(
        width=width,
        depth=depth,
        is_msr=MSR,
        is_mel=MEL,
    )

    # --- afficher le résultat de la catégorie ---
    with col2.expander("Catégorie", expanded=True):
        st.text(CATEGORY)

    # --- inputs pour déterminer les résistances prévues ---
    st.subheader(
        "Résistances prévues et modules d’élasticité",
        help="""Pour plus d'informations, consultez les tableaux 6.4 à 6.9 de la norme CSA O86.""",
    )
    SIDE = False
    if CATEGORY == "Beam":
        SIDE = st.toggle(
            "Charges appliquées sur la grande face?",
            help="""
            Les résistances prévues des poutres et des longerons sont fondées sur des charges
            appliquées sur leur face étroite. Si les charges sont appliquées sur leur grande face,
            la résistance prévue en flexion à la fibre extrême et le module d’élasticité prévu 
            doivent être multipliés par des coefficients de correction (CSA O86 - tableau 6.6)
            """,
        )

    # --- choix de la classe ou essence de bois ---
    if MSR or MEL:
        st.info(
            """Le groupe d'essences SPF est utilisé par défaut pour caractériser le bois classé 
            mécaniquement"""
        )

    if MSR:
        specie = st.pills(
            label="Classe:",
            options=("normal", "courant", "rare"),
            default="courant",
            width="stretch",
            help="Si aucune classe n'est sélectionnée, 'courant' est utilisé par défaut.",
        )
        if not specie:
            specie = "courant"
    elif MEL:
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

    # --- choix du grade ---
    grade_options = (
        SawnLumberStrengths.session.query(SawnLumberStrengths)
        .filter(SawnLumberStrengths.category == CATEGORY)
        .filter(SawnLumberStrengths.specie == specie)
        .with_entities(SawnLumberStrengths.grade)
    )

    grade = st.pills(
        label="Classe:",
        options=grade_options,
        default=grade_options[1][0],
        width="stretch",
        help=f"Si aucune classe n'est sélectionnée, '{grade_options[1][0]}' est utilisé par défaut.",
    )
    if not grade:
        grade = grade_options[1][0]

    # --- calculer les résultats de résistances prévues ---
    resistance = sawn_lumber.specified_strengths(
        category=CATEGORY,
        specie=specie,
        grade=grade,
        side=SIDE,
    )

    # --- afficher les résultats de résistances prévues ---
    with st.expander("Résistances prévues", expanded=True):
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
        for i in range(0, int(len(resistance))):
            col1, col2 = st.columns(
                [3, 1],
                gap=None,
                vertical_alignment="bottom",
                width=620,
            )
            col1.markdown(f"{value_name[i][0]} :")
            col2.markdown(f"{value_name[i][1]} $= {resistance[i]} MPa$")

    #
