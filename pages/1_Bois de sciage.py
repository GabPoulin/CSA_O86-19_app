"""_summary_"""

# IMPORTS
from dataclasses import dataclass
from sqlalchemy import orm, create_engine, Column, TEXT, REAL, INTEGER
import streamlit as st
import sawn_lumber
import Accueil


# DB CONNECTIONS
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
        help="""Les méthodes et les données de calcul ne s’appliquent qu’au bois de charpente
        conforme à CSA O141""",
    )

    # --- inputs pour déterminer la catégorie ---
    st.subheader(
        "Matériaux",
        help=""" Les calculs reposent sur l’utilisation de bois d’œuvre classé suivant les Règles
        de classification pour le bois d’œuvre canadien de la NLGA, et identifié au moyen de 
        l’estampille d’une association ou d’un organisme indépendant de classement, conformément 
        à CSA O141""",
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
        help="""Bois de charpente classé mécaniquement par résistance (MSR) et
        bois de charpente évalué par machine (MEL)""",
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
    if CATEGORY == "Valider la disponibilité du bois chez les fournisseurs.":
        st.warning("Valider la disponibilité du bois chez les fournisseurs.", width=380)
        CATEGORY = "Beam"
        MSR, MEL = False, False

    # --- afficher le résultat de la catégorie ---
    with col2.expander("Catégorie", expanded=True):
        st.text(CATEGORY)

    # --- inputs pour déterminer les résistances prévues ---
    SIDE = False
    if CATEGORY == "Beam":
        SIDE = st.toggle(
            "Charges appliquées sur la grande face?",
            help="""
            Les résistances prévues des poutres et des longerons sont fondées sur des charges
            appliquées sur leur face étroite. Si les charges sont appliquées sur leur grande face,
            la résistance prévue en flexion à la fibre extrême et le module d’élasticité prévu 
            doivent être multipliés par des coefficients de correction (CSA O86 - Tableau 6.6)
            """,
        )

    # --- choix de la classe ou essence de bois ---

    if MSR:
        specie = st.pills(
            label="Classe:",
            options=("normal", "courant", "rare"),
            default="courant",
            width="stretch",
            help="Si aucune classe n'est sélectionnée, 'courant' est utilisé par défaut",
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
            help="Si aucune essence n'est sélectionnée, le groupe 'spf' est utilisé par défaut",
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
        help=f"Si aucune classe n'est sélectionnée, '{grade_options[1][0]}' est utilisé par défaut",
    )
    if not grade:
        grade = grade_options[1][0]

    if MSR or MEL:
        st.caption(
            """Le groupe d'essences SPF est utilisé par défaut pour caractériser le bois classé 
            mécaniquement"""
        )

    # --- calculer les résultats de résistances prévues ---
    st.subheader("Résistances prévues et modules d’élasticité")

    compute_resistance = sawn_lumber.specified_strengths(
        category=CATEGORY,
        specie=specie,
        grade=grade,
        side=SIDE,
    )

    # --- afficher les résultats de résistances prévues ---
    with st.expander("Résultats", expanded=True):
        display_resistance = [
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
        for i in range(0, int(len(compute_resistance))):
            col1, col2 = st.columns(
                [3, 1],
                gap=None,
                vertical_alignment="bottom",
                width=620,
            )
            col1.markdown(f"{display_resistance[i][0]} :")
            col2.markdown(f"{display_resistance[i][1]} $= {compute_resistance[i]} MPa$")

    # --- inputs pour déterminer les coefficients ---
    st.subheader("Coefficients de correction")

    duration = st.pills(
        label="Durée d'application de la charge:",
        options=("courte", "normale", "continue"),
        default="normale",
        width="stretch",
        help="Si aucune choix n'est sélectionnée, une durée d'application 'normale' est utilisé par défaut",
    )
    if not duration:
        duration = "normale"

    with st.container(
        horizontal=True,
        horizontal_alignment="distribute",
    ):
        wet = st.toggle("Utilisation en milieu humide")
        treated = st.toggle(
            "Bois traité",
            help="""Dans le cas du bois d’œuvre traité par ignifugation ou avec d’autres produits
            chimiques qui réduisent la résistance, les résistances et la rigidité doivent être
            basées sur des résultats d’essais documentés qui doivent tenir compte de l’effet du
            temps, de la température et de la teneur en humidité""",
        )
        incised = st.toggle("Bois incisé")
        group = st.toggle(
            "3 éléments ou +, avec espacements ≤ 610 mm",
            help="""Cas 1 - Système d'éléments de charpente rapprochés comme les
            fermes à ossature légère, les éléments de charpente composés et les éléments de
            charpente en bois lamellé-collé. Peut aussi s’appliquer à certains systèmes
            traditionnels de solives et de chevrons où les détails de charpente ne satisfont pas
            au cas 2""",
        )
        subfloor = st.toggle(
            "Revêtement ou sous-plancher",
            help="""Cas 2 - Système d'éléments revêtus d’un contreplaqué ou d’un panneau OSB d’au
            moins 9,5 mm d’épaisseur, ou de bois d’au moins 17 mm d’épaisseur combiné à un
            recouvrement de panneaux tel qu’une sous-finition ou un parquet de bois. Le revêtement
            ou le sous-plancher est fixé aux éléments de charpente de manière à procurer une
            rigidité minimale équivalente à celle obtenue à l’aide de clous ordinaires de 2 po
            espacés de 150 mm aux rives des panneaux de revêtement et de 300 mm aux autres
            endroits""",
        )
        built_up = st.toggle(
            "Poutre composée",
            help="""2 éléments ou plus de même hauteur fixés ou collés ensemble de sorte que la
            poutre fléchisse de façon monolithique""",
        )

    with st.expander("Coefficients", expanded=False):
        prop_options = {
            "Flexion": "flex",
            "Cisaillement par fissuration": "cis_f",
            "Cisaillement longitudinal": "cis_v",
            "Compression parallèle au fil": "comp_para",
            "Compression perpendiculaire au fil": "comp_perp",
            "Traction parallèle au fil": "trac",
            "Module d’élasticité": "moe",
        }
        prop_key = st.selectbox(
            "Propriété évaluée:",
            options=(prop_options),
            width=400,
        )
        compute_coefficients = sawn_lumber.modification_factors(
            width=width,
            depth=depth,
            prop=prop_options[prop_key],
            duration=duration,
            category=CATEGORY,
            wet_service=wet,
            treated=treated,
            incised=incised,
            _2ft_spacing=group,
            connected_subfloor=subfloor,
            built_up_beam=built_up,
        )

        display_coefficients = [
            ("Coefficient de durée d’application de la charge", "$K_D$"),
            ("Coefficient de conditions d'utilisation", "$K_S$"),
            ("Coefficient de traitement", "$K_T$"),
            ("Coefficient de système", "$K_H$"),
            ("Coefficient de dimensions", "$K_Z$"),
        ]
        for i in range(0, int(len(compute_coefficients))):
            col1, col2 = st.columns(
                [3, 1],
                gap=None,
                vertical_alignment="bottom",
                width=620,
            )
            col1.markdown(f"{display_coefficients[i][0]} :")
            col2.markdown(f"{display_coefficients[i][1]} $= {compute_coefficients[i]}$")
