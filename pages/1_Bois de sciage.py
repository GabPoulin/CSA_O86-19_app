"""_summary_"""

# IMPORTS
from dataclasses import dataclass
from sqlalchemy import orm, create_engine, Column, TEXT, REAL, INTEGER
import streamlit as st
import Accueil
import sawn_lumber
import general_design


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
st.header(
    "Bois de Sciage",
    help="""Les méthodes et les données de calcul ne s’appliquent qu’au bois de charpente
    conforme à CSA O141""",
)


# --- section matériaux ---
st.divider()
st.subheader(
    "Matériaux",
    help=""" Les calculs reposent sur l’utilisation de bois d’œuvre classé suivant les Règles
    de classification pour le bois d’œuvre canadien de la NLGA, et identifié au moyen de 
    l’estampille d’une association ou d’un organisme indépendant de classement, conformément 
    à CSA O141""",
)

with st.container(horizontal_alignment="center"):
    # --- inputs pour déterminer la catégorie ---
    col1, col2 = st.columns(
        2,
        gap="medium",
        width=550,
    )

    with col1:
        width_input = st.number_input(
            "Largeur nominale de l'élément (po)",
            min_value=2,
        )
        depth_input = st.number_input(
            "Hauteur nominale de l'élément (po)",
            min_value=2,
            value=6,
        )
        GREEN = st.toggle(
            "Bois vert",
            help="Bois d’œuvre dont la teneur en humidité dépasse 19 % (H > 19%)",
        )
        BRUT = st.toggle(
            "Dimensions brutes",
            help="Utilise les dimensions nominales en tant que dimensions réelles",
        )
        built_up = st.radio(
            "Élément composé (plis)",
            options=(1, 2, 3, 4, 5),
            horizontal=True,
            help="Élément assemblé composé de plusieurs plis",
        )

    with col2:
        width = sawn_lumber.sizes(width_input, GREEN, BRUT)
        st.metric("Largeur nette de l'élément, b", f"{width} mm")
        depth = sawn_lumber.sizes(depth_input, GREEN, BRUT)
        st.metric("Hauteur nette de l'élément, d", f"{depth} mm")
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
        st.warning(
            "Valider la disponibilité du bois chez les fournisseurs.",
            width=550,
        )
        CATEGORY = "Beam"
        MSR, MEL = False, False

    # --- afficher le résultat de la catégorie ---
    with col2.expander("Catégorie", expanded=True):
        category = {
            "Light": "Charpente légère",
            "Beam": "Poutres et longerons",
            "Post": "Poteaux et bois carrés",
            "Lumber": "Montants, solives et madriers",
            "MEL": "MEL",
            "MSR": "MSR",
        }
        st.text(category[CATEGORY])

    # --- inputs pour déterminer les résistances prévues ---
    SIDE = False
    if CATEGORY == "Beam":
        SIDE = st.toggle(
            "Charges appliquées sur la grande face",
            help="""
            Les résistances prévues des poutres et des longerons sont fondées sur des charges
            appliquées sur leur face étroite. Si les charges sont appliquées sur leur grande face,
            la résistance prévue en flexion à la fibre extrême et le module d’élasticité prévu 
            doivent être multipliés par des coefficients de correction (CSA O86 - Tableau 6.6)
            """,
            width=550,
        )

    # --- choix de la classe ou essence de bois ---
    if MSR or MEL:
        st.caption(
            """Le groupe d'essences S-P-F est utilisé par défaut pour caractériser le bois classé 
            mécaniquement""",
            width=600,
        )
    specie = {
        "Courant": "courant",
        "Normal": "normal",
        "Rare": "rare",
        "D Fir-L (N)": "df",
        "Hem-Fir (N)": "hf",
        "S-P-F": "spf",
        "N. Species": "ns",
    }
    if MSR:
        SPECIE = st.pills(
            label="Groupe:",
            options=("Courant", "Normal", "Rare"),
            default="Courant",
            width=650,
            help="Si aucun Groupe n'est sélectionné, 'Courant' est utilisé par défaut",
        )
        if not SPECIE:
            SPECIE = "Courant"
    elif MEL:
        SPECIE = "Normal"
    else:
        SPECIE = st.pills(
            label="Groupe d'essences:",
            options=("D Fir-L (N)", "Hem-Fir (N)", "S-P-F", "N. Species"),
            default="S-P-F",
            width=650,
            help="Si aucune essence n'est sélectionnée, le groupe 'S-P-F' est utilisé par défaut",
        )
        if not SPECIE:
            SPECIE = "S-P-F"

    # --- choix du grade ---
    grade_options = (
        SawnLumberStrengths.session.query(SawnLumberStrengths)
        .filter(SawnLumberStrengths.category == CATEGORY)
        .filter(SawnLumberStrengths.specie == specie[SPECIE])
        .with_entities(SawnLumberStrengths.grade)
    )
    grade = st.pills(
        label="Classe:",
        options=grade_options,
        default=grade_options[1][0],
        width=650,
        help=f"Si aucune classe n'est sélectionnée, '{grade_options[1][0]}' est utilisé par défaut",
    )
    if not grade:
        grade = grade_options[1][0]


# --- section résistances prévues ---
st.divider()
st.subheader("Résistances prévues et modules d’élasticité")

# --- calculer les résultats de résistances prévues ---
compute_resistance = sawn_lumber.specified_strengths(
    category=CATEGORY,
    specie=specie[SPECIE],
    grade=grade,
    side=SIDE,
)

with st.container(horizontal_alignment="center"):
    # --- afficher les résultats de résistances prévues ---
    with st.expander("Résistances", width=650):
        display_resistance = [
            (
                "Flexion",
                "$f_b$",
            ),
            (
                "Cisaillement longitudinal",
                "$f_v$",
            ),
            (
                "Compression parallèle au fil",
                "$f_c$",
            ),
            (
                "Compression perpendiculaire au fil",
                "$f_{cp}$",
            ),
            (
                "Traction parallèle au fil",
                "$f_t$",
            ),
            (
                "Module d’élasticité",
                "$E$",
            ),
            (
                "Module d’élasticité pour les calculs des éléments en compression",
                "$E_{05}$",
            ),
        ]
        for i in range(0, int(len(compute_resistance))):
            col1, col2 = st.columns([3, 1])
            col1.text(f"{display_resistance[i][0]}:")
            col2.markdown(f"{display_resistance[i][1]} $={compute_resistance[i]}MPa$")


# --- section coefficients ---
st.divider()
st.subheader("Coefficients de correction")

with st.container(horizontal_alignment="center"):
    # --- inputs pour déterminer les coefficients ---
    col1, col2 = st.columns(2, vertical_alignment="bottom", width=550)
    duration = {
        "Courte (≤ 7 jours)": "courte",
        "Normale": "normale",
        "Continue (permanente)": "continue",
    }
    DURATION = col1.radio(
        label="Durée d'application de la charge:",
        options=("Courte (≤ 7 jours)", "Normale", "Continue (permanente)"),
        index=1,
        horizontal=False,
    )
    wet = col1.checkbox(
        "Utilisation en milieu humide",
    )
    treated = col2.checkbox(
        "Bois traité",
        help="""Dans le cas du bois d’œuvre traité par ignifugation ou avec d’autres produits
        chimiques qui réduisent la résistance, les résistances et la rigidité doivent être
        basées sur des résultats d’essais documentés qui doivent tenir compte de l’effet du
        temps, de la température et de la teneur en humidité""",
    )
    incised = col2.checkbox(
        "Bois incisé",
    )
    group = col2.checkbox(
        "3 éléments ou + @ ≤ 2 pi c/c",
        help="""Cas 1 - Système d'éléments de charpente rapprochés comme les
        fermes à ossature légère, les éléments de charpente composés et les éléments de
        charpente en bois lamellé-collé. Peut aussi s’appliquer à certains systèmes
        traditionnels de solives et de chevrons où les détails de charpente ne satisfont pas
        au cas 2""",
    )
    subfloor = col2.checkbox(
        "Revêtement ou sous-plancher",
        help="""Cas 2 - Système d'éléments revêtus d’un contreplaqué ou d’un panneau OSB d’au
        moins 9,5 mm d’épaisseur, ou de bois d’au moins 17 mm d’épaisseur combiné à un
        recouvrement de panneaux tel qu’une sous-finition ou un parquet de bois. Le revêtement
        ou le sous-plancher est fixé aux éléments de charpente de manière à procurer une
        rigidité minimale équivalente à celle obtenue à l’aide de clous ordinaires de 2 po
        espacés de 150 mm aux rives des panneaux de revêtement et de 300 mm aux autres
        endroits""",
    )
    PLIS = True
    if built_up == 1:
        PLIS = False

    # --- afficher les résultats des corfficients ---
    with st.expander("Coefficients", width=650):
        prop_options = {
            "Flexion": "flex",
            "Cisaillement par fissuration": "cis_f",
            "Cisaillement longitudinal": "cis_v",
            "Compression parallèle au fil": "comp_para",
            "Compression perpendiculaire au fil": "comp_perp",
            "Traction parallèle au fil": "trac",
            "Module d’élasticité": "moe",
        }
        prop_key = st.segmented_control(
            "Propriété affichée:",
            options=prop_options,
            width="stretch",
            default="Flexion",
            help="Si aucune propriété n'est sélectionné, 'Flexion' est sélectionné par défaut",
        )
        if not prop_key:
            prop_key = "Flexion"

        # --- calculer les corfficients ---
        compute_coefficients = sawn_lumber.modification_factors(
            width=width,
            depth=depth,
            prop=prop_options[prop_key],
            duration=duration[DURATION],
            category=CATEGORY,
            wet_service=wet,
            treated=treated,
            incised=incised,
            _2ft_spacing=group,
            connected_subfloor=subfloor,
            built_up_beam=PLIS,
        )

        display_coefficients = [
            ("Coefficient de durée d’application de la charge", "$K_D$"),
            ("Coefficient de conditions d'utilisation", "$K_S$"),
            ("Coefficient de traitement", "$K_T$"),
            ("Coefficient de système", "$K_H$"),
            ("Coefficient de dimensions", "$K_Z$"),
        ]
        for i in range(0, int(len(compute_coefficients))):
            col1, col2 = st.columns([3, 1])
            col1.markdown(f"{display_coefficients[i][0]}:")
            col2.markdown(f"{display_coefficients[i][1]} $={compute_coefficients[i]}$")


# --- section calcul des résistances ---
st.divider()
st.subheader("Calcul des résistances")
flex, shear, comp_para, comp_perp, comp_angle, trac, combi = st.tabs(
    [
        "Moment de flexion",
        "Cisaillement",
        "Compression parallèle au fil",
        "Compression perpendiculaire au fil",
        "Compression oblique par rapport au fil",
        "Traction parallèle au fil",
        "Flexion et charge axiale combinée",
    ]
)

with flex:
    kd, ksb, kt, kh, kzb = sawn_lumber.modification_factors(
        width=width,
        depth=depth,
        prop="flex",
        duration=duration[DURATION],
        category=CATEGORY,
        wet_service=wet,
        treated=treated,
        incised=incised,
        _2ft_spacing=group,
        connected_subfloor=subfloor,
        built_up_beam=built_up,
    )
    beam_flex = sawn_lumber.Resistances(
        b=width,
        d=depth,
        kd=kd,
        kh=kh,
        kt=kt,
        ply=built_up,
    )

    with st.container(horizontal_alignment="center"):
        col1, col2 = st.columns(2, width=550)
        with col1:
            LATERAL = st.toggle(
                "Support latéral aux appuis",
                help="""Support latéral assuré aux points d’appui afin d’empêcher le déplacement
                latéral et la rotation""",
            )
            COMP_EDGE = st.toggle(
                "Rive supérieure maintenue",
                help="""Rive comprimée maintenu par fixation directe du platelage ou par des solives
                dont l’espacement ne dépasse pas 610 mm""",
                value=subfloor,
            )
            TEN_EDGE = st.toggle(
                "Rive inférieure maintenue",
                help="Rive en tension maintenue",
            )
        with col2:
            TIE_ROD = st.toggle(
                "Pannes ou tirants",
                help="Alignement maintenu à l’aide de pannes ou de tirants",
            )
            BLOCK = st.toggle(
                "Entremises",
                help=f"""Présence d'entretoises ou d'entremises dont l’espacement ne
                dépasse pas huit fois la hauteur de la section de l’élément -> $ 8 \cdot d = {8*depth} $
                mm c/c""",
            )

        mr = (
            beam_flex.bending_moment(
                fb=compute_resistance[0],
                ksb=ksb,
                kzb=kzb,
                lateral_support=LATERAL,
                compressive_edge_support=COMP_EDGE,
                tensile_edge_support=TEN_EDGE,
                blocking_support=BLOCK,
                tie_rods_support=TIE_ROD,
            )
            / 1000000
        )
        col2.write(f"$Mr = {round(mr,2)} kN \cdot m$")
        mf = st.number_input("$Mf: (kN \cdot m)$", 0.00, width=550)
        verif = general_design.limit_states_design(mf, mr)
        st.text(verif)
