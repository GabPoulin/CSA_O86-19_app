"""Page Streamlit : calcul des éléments en bois de sciage (CSA O86:19, chapitre 6)."""

# IMPORTS
import streamlit as st
import acces
import config
import datetime
from moteur.commun.note_de_calcul import (
    COULEUR_ACCENT,
    COULEUR_PRINCIPALE,
    Apparence,
    EnTete,
    produire_pdf,
)
from moteur.normes.csa_o86_19.ch_6_bois_de_sciage.art_6_3_resistances_prevues_et_modules_d_elasticite import (  # noqa: E501
    tableau_des_resistances,
)
from moteur.normes.csa_o86_19.ch_6_bois_de_sciage.art_6_5_calcul_des_resistances import (
    art_6_5_3_resistance_au_moment_de_flexion as art_6_5_3,
    art_6_5_4_resistance_au_cisaillement as art_6_5_4,
    art_6_5_5_resistance_a_la_compression_parallele_au_fil as art_6_5_5,
    art_6_5_6_resistance_a_la_compression_perpendiculaire_au_fil as art_6_5_6,
)
import sawn_lumber
import general_design
from sawn_lumber import SawnLumberStrengths


# CODE
def show_verification(message: str) -> None:
    """Affiche le résultat de la vérification à l'état limite avec la bonne couleur."""
    if message.startswith("État limite respecté"):
        st.success(message, width=650, icon=":material/check_circle:")
    elif message.startswith("État limite dépassé"):
        st.error(message, width=650, icon=":material/error:")
    else:
        st.info(message, width=650, icon=":material/info:")


# ---- en-tête ----
config.configurer_page("Bois de sciage")
st.title(config.TITLE, anchor=False)
st.caption(config.SOUS_TITRE)
st.page_link(
    "Accueil.py",
    label="Retour à l'accueil",
    icon=":material/home:",
)
st.header(
    "Bois de Sciage",
    anchor=False,
    help="""Les méthodes et les données de calcul ne s'appliquent qu'au bois de charpente
    conforme à CSA O141""",
)


# --- section matériaux ---
st.divider()
st.subheader(
    "Matériaux",
    anchor=False,
    help=""" Les calculs reposent sur l'utilisation de bois d'œuvre classé suivant les Règles
    de classification pour le bois d'œuvre canadien de la NLGA, et identifié au moyen de 
    l'estampille d'une association ou d'un organisme indépendant de classement, conformément 
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
        GREEN = st.toggle(
            "Bois vert",
            help="Bois d'œuvre dont la teneur en humidité dépasse 19 % (H > 19%)",
        )
        BRUT = st.toggle(
            "Dimensions brutes",
            help="Utilise les dimensions nominales en tant que dimensions réelles",
        )
        if BRUT:
            width_input = st.number_input(
                "Largeur réelle de l'élément, $b$ (po)",
                min_value=1.50,
                step=0.25,
                icon=":material/fit_page_width:",
            )
            depth_input = st.number_input(
                "Hauteur réelle de l'élément, $d$ (po)",
                min_value=1.50,
                value=5.50,
                step=0.25,
                icon=":material/fit_page_height:",
            )
        else:
            NOMINAL_SIZES = sawn_lumber.nominal_sizes()
            width_input = st.selectbox(
                "Largeur nominale de l'élément, $b$ (po)",
                options=NOMINAL_SIZES,
                index=NOMINAL_SIZES.index(2),
                help="Dimensions nominales du tableau A.3",
            )
            depth_input = st.selectbox(
                "Hauteur nominale de l'élément, $d$ (po)",
                options=NOMINAL_SIZES,
                index=NOMINAL_SIZES.index(6),
                help="Dimensions nominales du tableau A.3",
            )
        built_up = st.radio(
            "Élément composé (plis)",
            options=(1, 2, 3, 4, 5),
            horizontal=True,
            help="Élément assemblé composé de plusieurs plis",
        )

    with col2:
        TIMBER = not BRUT and sawn_lumber.is_timber(width_input, depth_input)
        try:
            width = sawn_lumber.sizes(width_input, GREEN, BRUT, TIMBER)
            depth = sawn_lumber.sizes(depth_input, GREEN, BRUT, TIMBER)
        except ValueError as error:
            st.error(str(error), icon=":material/error:")
            st.stop()
        if built_up == 1:
            st.metric("Largeur nette de l'élément, $b$", f"{width} mm")
        else:
            st.metric(
                "Largeur nette de l'élément, $b$",
                f"{built_up}*{width} = {built_up*width} mm",
            )

        st.metric("Hauteur nette de l'élément, $d$", f"{depth} mm")
        msr_mel = col2.segmented_control(
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
        LIGHT_FRAMING = False
        if not (MSR or MEL) and sawn_lumber.admits_light_framing(width, depth):
            LIGHT_FRAMING = col2.toggle(
                "Charpente légère (Const., Std.)",
                help="""Tableau 6.3 : une section de 38 à 89 mm x 38 à 89 mm peut prendre les classes
                du tableau 6.4 (structure choisie, n° 1/n° 2, n° 3/montant), utilisées par défaut, ou
                celles du tableau 6.5 (Construction, Standard).""",
            )

    # --- calcul pour déterminer la catégorie ---
    CATEGORY = sawn_lumber.lumber_category(
        width=width,
        depth=depth,
        is_msr=MSR,
        is_mel=MEL,
        light_framing=LIGHT_FRAMING,
    )
    if CATEGORY == "Valider la disponibilité du bois chez les fournisseurs.":
        col1.warning(
            "Valider la disponibilité du bois chez les fournisseurs.",
            width=550,
            icon=":material/person_alert:",
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
            la résistance prévue en flexion à la fibre extrême et le module d'élasticité prévu 
            doivent être multipliés par des coefficients de correction (CSA O86 - Tableau 6.6)
            """,
            width=550,
        )

    # --- choix de la classe ou essence de bois ---
    if MSR or MEL:
        st.caption(
            """Le groupe d'essences S-P-F est utilisé par défaut pour caractériser le bois classé 
            mécaniquement""",
            width=550,
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
        SPECIE = st.segmented_control(
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
        SPECIE = st.segmented_control(
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
        SawnLumberStrengths.session.query(SawnLumberStrengths)  # type: ignore
        .filter(SawnLumberStrengths.category == CATEGORY)  # type: ignore
        .filter(SawnLumberStrengths.specie == specie[SPECIE])  # type: ignore
        .with_entities(SawnLumberStrengths.grade)  # type: ignore
    )
    grade = st.segmented_control(
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
st.subheader("Résistances prévues et modules d'élasticité", anchor=False)

# --- calculer les résultats de résistances prévues ---
compute_resistance = sawn_lumber.specified_strengths(
    category=CATEGORY,
    specie=specie[SPECIE],
    grade=grade,
    side=SIDE,
)

with st.container(horizontal_alignment="center"):
    # --- afficher les résultats de résistances prévues ---
    with st.expander("Voir plus:", width=650):
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
                "Module d'élasticité",
                "$E$",
            ),
            (
                "Module d'élasticité pour les calculs des éléments en compression",
                "$E_{05}$",
            ),
        ]
        for i in range(0, int(len(compute_resistance))):
            col1, col2 = st.columns([3, 1])
            col1.text(f"{display_resistance[i][0]}:")
            col2.markdown(f"{display_resistance[i][1]} $={compute_resistance[i]}MPa$")


# --- section coefficients ---
st.divider()
st.subheader("Coefficients de correction", anchor=False)

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
        help="""Dans le cas du bois d'œuvre traité par ignifugation ou avec d'autres produits
        chimiques qui réduisent la résistance, les résistances et la rigidité doivent être
        basées sur des résultats d'essais documentés qui doivent tenir compte de l'effet du
        temps, de la température et de la teneur en humidité""",
    )
    incised = col2.checkbox(
        "Bois incisé",
    )
    group = col2.checkbox(
        "3 éléments ou + @ ≤ 2 pi c/c",
        help="""Cas 1 - Système d'éléments de charpente rapprochés comme les
        fermes à ossature légère, les éléments de charpente composés et les éléments de
        charpente en bois lamellé-collé. Peut aussi s'appliquer à certains systèmes
        traditionnels de solives et de chevrons où les détails de charpente ne satisfont pas
        au cas 2""",
    )
    subfloor = col2.checkbox(
        "Revêtement ou sous-plancher",
        help="""Cas 2 - Système d'éléments revêtus d'un contreplaqué ou d'un panneau OSB d'au
        moins 9,5 mm d'épaisseur, ou de bois d'au moins 17 mm d'épaisseur combiné à un
        recouvrement de panneaux tel qu'une sous-finition ou un parquet de bois. Le revêtement
        ou le sous-plancher est fixé aux éléments de charpente de manière à procurer une
        rigidité minimale équivalente à celle obtenue à l'aide de clous ordinaires de 2 po
        espacés de 150 mm aux rives des panneaux de revêtement et de 300 mm aux autres
        endroits""",
    )
    PLIS = True
    if built_up == 1:
        PLIS = False

    # --- afficher les résultats des coefficients ---
    with st.expander("Voir plus:", width=650):
        prop_options = {
            "Flexion": "flex",
            "Cisaillement par fissuration": "cis_f",
            "Cisaillement longitudinal": "cis_v",
            "Compression parallèle au fil": "comp_para",
            "Compression perpendiculaire au fil": "comp_perp",
            "Traction parallèle au fil": "trac",
            "Module d'élasticité": "moe",
        }
        PROP_KEY = st.segmented_control(
            """Pour consultation uniquement, les bons coefficients sont utilisés automatiquement
            dans les calculs""",
            options=prop_options,
            width="stretch",
            default="Flexion",
            help="Si aucune propriété n'est sélectionné, 'Flexion' est sélectionné par défaut",
        )
        if not PROP_KEY:
            PROP_KEY = "Flexion"

        # --- calculer les corfficients ---
        compute_coefficients = sawn_lumber.modification_factors(
            width=width,
            depth=depth,
            prop=prop_options[PROP_KEY],
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
            ("Coefficient de durée d'application de la charge", "$K_D$"),
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
st.subheader("Calcul des résistances", anchor=False)
# Vérifications pour la note de calcul PDF (issue #50) : traces du nouveau moteur, mêmes entrées
NOTE = {}
SOURCE = tableau_des_resistances(CATEGORY)  # tableau des résistances prévues (6.3)

# Onglets offerts au compte connecté (acces.py, ACCES_GROUPE_LANTIER.md ; issue #56)
ONGLETS_POSSIBLES = {
    "flexion": "Moment de flexion",
    "cisaillement": "Cisaillement",
    "compression_parallele": "Compression parallèle au fil",
    "compression_perpendiculaire": "Compression perpendiculaire au fil",
    "compression_oblique": "Compression oblique par rapport au fil",
    "traction": "Traction parallèle au fil",
    "flexion_et_charge_axiale": "Flexion et charge axiale combinée",
}
OFFERTS = [cle for cle in ONGLETS_POSSIBLES if acces.permis(cle)]
ONGLETS = dict(zip(OFFERTS, st.tabs([ONGLETS_POSSIBLES[cle] for cle in OFFERTS]))) if OFFERTS else {}
if not OFFERTS:
    st.info(
        "Aucune vérification n'est encore offerte à ce compte.", width=650, icon=":material/info:"
    )

if "flexion" in ONGLETS:
    with ONGLETS["flexion"]:
        acces.avertir_si_en_test("flexion")
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
            built_up_beam=PLIS,
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
                    help="""Support latéral assuré aux points d'appui afin d'empêcher le déplacement
                    latéral et la rotation""",
                    value=True,
                )
                TIE_ROD = st.toggle(
                    "Pannes ou tirants",
                    help="Alignement maintenu à l'aide de pannes ou de tirants",
                )
                COMP_EDGE = st.toggle(
                    "Rive supérieure maintenue",
                    help="""Rive comprimée maintenu par fixation directe du platelage ou par des solives
                    dont l'espacement ne dépasse pas 610 mm""",
                    value=subfloor,
                )
                BLOCK = st.toggle(
                    "Entremises",
                    help=f"""Présence d'entretoises ou d'entremises dont l'espacement ne dépasse pas
                    huit fois la hauteur de la section de l'élément -> $ 8 \\cdot d = {8*depth} $
                    mm c/c""",
                )
                TEN_EDGE = st.toggle(
                    "Rive inférieure maintenue",
                    help="Rive en tension maintenue",
                )
                PLIES_FASTENED = False
                if built_up > 1:
                    PLIES_FASTENED = st.toggle(
                        f"Plis fixés à au plus 4d = {4 * depth} mm c/c",
                        help="""6.5.3.2.4 : poutre composée dont les plis sont solidement attachés les
                        uns aux autres à intervalles ne dépassant pas quatre fois la hauteur. Les
                        supports latéraux ci-dessus (6.5.3.2.3) ne s'appliquent pas aux poutres
                        composées.""",
                    )

            try:
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
                        plies_fastened=PLIES_FASTENED,
                    )
                    / 1000000
                )
            except ValueError as error:
                mr = None
                kl_message = str(error)
            with col2:
                mf = st.number_input(
                    "$Mf: (kN \\cdot m)$",
                    min_value=0.00,
                    value=None,
                    width=550,
                    placeholder="Moment pondéré",
                    step=1.00,
                    icon=":material/input:",
                )
                if mr is None:
                    st.error(kl_message, width=650, icon=":material/error:")
                else:
                    VERIF = general_design.limit_states_design(mf, mr)
                    st.write(f"$Mr = {round(mr,2)} kN \\cdot m$")
                    show_verification(VERIF)
                    NOTE["Flexion (6.5.3)"] = art_6_5_3.verifier_flexion(
                        b=width, d=depth, f_b=compute_resistance[0], plis=built_up,
                        K_D=kd, K_H=kh, K_Sb=ksb, K_T=kt, K_Zb=kzb,
                        support_lateral_aux_appuis=LATERAL, pannes_ou_tirants=TIE_ROD,
                        rive_comprimee_maintenue=COMP_EDGE, entretoises_ou_entremises=BLOCK,
                        rive_tendue_maintenue=TEN_EDGE, plis_fixes_a_au_plus_4d=PLIES_FASTENED,
                        M_f=mf, source_resistances=SOURCE,
                    )

if "cisaillement" in ONGLETS:
    with ONGLETS["cisaillement"]:
        acces.avertir_si_en_test("cisaillement")
        kd, ksv, kt, kh, kzv = sawn_lumber.modification_factors(
            width=width,
            depth=depth,
            prop="cis_v",
            duration=duration[DURATION],
            category=CATEGORY,
            wet_service=wet,
            treated=treated,
            incised=incised,
            _2ft_spacing=group,
            connected_subfloor=subfloor,
            built_up_beam=PLIS,
        )
        beam_shear = sawn_lumber.Resistances(
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
                notch_depth = st.number_input(
                    "Profondeur de l'entaille, $d_n$ (mm)",
                    min_value=0,
                    max_value=int(0.25 * depth),
                    value=None,
                    placeholder="Optionnel",
                    help=f"Ne doit pas dépasser $ 0,25 \\cdot d = {0.25*depth} $ mm",
                    icon=":material/height:",
                )
                notch_length = st.number_input(
                    "Longueur de l'entaille, $e$ (mm)",
                    min_value=0,
                    value=None,
                    placeholder="Optionnel",
                    icon=":material/arrow_range:",
                )
                st.image("images/notch_2_NoBckgrd.png")

            with col2:
                vf = st.number_input(
                    "$Vf: (kN)$",
                    0.00,
                    value=None,
                    width=550,
                    placeholder="Cisaillement pondéré",
                    step=1.00,
                    icon=":material/input:",
                )

                ksf = 1
                if notch_depth and notch_length:
                    kd, ksf, kt, kh, kzf = sawn_lumber.modification_factors(
                        width=width,
                        depth=depth,
                        prop="cis_f",
                        duration=duration[DURATION],
                        category=CATEGORY,
                        wet_service=wet,
                        treated=treated,
                        incised=incised,
                        _2ft_spacing=group,
                        connected_subfloor=subfloor,
                        built_up_beam=PLIS,
                    )

                vr, fr = beam_shear.shear(
                    fv=compute_resistance[1],
                    ksv=ksv,
                    ksf=ksf,
                    kzv=kzv,
                    dn=notch_depth,
                    e=notch_length,
                )
                vr = vr / 1000
                fr = fr / 1000
                if 0 < fr < vr:
                    vr = fr
                    st.write(f"$Fr = {round(vr,2)} kN$")
                else:
                    st.write(f"$Vr = {round(vr,2)} kN$")
                VERIF = general_design.limit_states_design(vf, vr)
                show_verification(VERIF)

                entaille = bool(notch_depth and notch_length)
                NOTE["Cisaillement (6.5.4.3)"] = art_6_5_4.verifier_cisaillement(
                    b=width, d=depth, f_v=compute_resistance[1], plis=built_up,
                    d_n=notch_depth if entaille else 0,
                    K_D=beam_shear.kd, K_H=beam_shear.kh, K_Sv=ksv, K_T=beam_shear.kt, K_Zv=kzv,
                    V_f=vf, source_resistances=SOURCE,
                )
                if entaille:
                    NOTE["Cisaillement par fissuration à l'entaille (6.5.4.4)"] = (
                        art_6_5_4.verifier_cisaillement_par_fissuration(
                            b=width, d=depth, d_n=notch_depth, e=notch_length, plis=built_up,
                            K_D=kd, K_H=kh, K_Sf=ksf, K_T=kt, V_f=vf,
                        )
                    )

if "compression_parallele" in ONGLETS:
    with ONGLETS["compression_parallele"]:
        acces.avertir_si_en_test("compression_parallele")
        with st.container(horizontal_alignment="center"):
            if built_up > 1:
                st.warning(
                    """Éléments composés de plusieurs plis en compression (6.5.5.3) :
                    fonctionnalité à venir.""",
                    width=550,
                )
            else:
                kd, ksc, kt, kh, _ = sawn_lumber.modification_factors(
                    width=width,
                    depth=depth,
                    prop="comp_para",
                    duration=duration[DURATION],
                    category=CATEGORY,
                    wet_service=wet,
                    treated=treated,
                    incised=incised,
                    _2ft_spacing=group,
                    connected_subfloor=subfloor,
                    built_up_beam=PLIS,
                )
                _, kse, _, _, _ = sawn_lumber.modification_factors(
                    width=width,
                    depth=depth,
                    prop="moe",
                    duration=duration[DURATION],
                    category=CATEGORY,
                    wet_service=wet,
                    treated=treated,
                    incised=incised,
                    _2ft_spacing=group,
                    connected_subfloor=subfloor,
                    built_up_beam=PLIS,
                )
                fc_modified = sawn_lumber.compression_strength(
                    fc=compute_resistance[2], kd=kd, kh=kh, ksc=ksc, kt=kt
                )
                e05 = compute_resistance[6]
                axes = None

                col1, col2 = st.columns(2, width=550)
                with col1:
                    length = st.number_input(
                        "Longueur de l'élément, $L$ (mm)",
                        min_value=1,
                        value=None,
                        step=100,
                        placeholder="Requis",
                        help="Longueur réelle de l'élément, utilisée pour $K_{Zc}$ (6.5.5.2.4)",
                        icon=":material/straighten:",
                    )
                    le_b = st.number_input(
                        "Longueur effective selon $b$, $L_{e,b}$ (mm)",
                        min_value=1,
                        value=None,
                        step=100,
                        placeholder="Requis",
                        help="""Longueur effective associée à la largeur $b$,
                        $L_e = K_e \\cdot L$ entre les appuis latéraux (6.5.5.2.2)""",
                        icon=":material/fit_page_width:",
                    )
                    le_d = st.number_input(
                        "Longueur effective selon $d$, $L_{e,d}$ (mm)",
                        min_value=1,
                        value=None,
                        step=100,
                        placeholder="Requis",
                        help="""Longueur effective associée à la hauteur $d$,
                        $L_e = K_e \\cdot L$ entre les appuis latéraux (6.5.5.2.2)""",
                        icon=":material/fit_page_height:",
                    )

                with col2:
                    pf = st.number_input(
                        "$Pf: (kN)$",
                        min_value=0.00,
                        value=None,
                        width=550,
                        placeholder="Charge axiale pondérée",
                        step=1.00,
                        icon=":material/input:",
                    )
                    if length is None or le_b is None or le_d is None:
                        st.info(
                            "Spécifiez $L$, $L_{e,b}$ et $L_{e,d}$ pour calculer $Pr$",
                            width=650,
                            icon=":material/info:",
                        )
                    else:
                        try:
                            axis_b = sawn_lumber.compression_parallel_axis(
                                dimension=width,
                                length=length,
                                effective_length=le_b,
                                fc_modified=fc_modified,
                                area=width * depth,
                                e05=e05,
                                kse=kse,
                                kt=kt,
                            )
                            axis_d = sawn_lumber.compression_parallel_axis(
                                dimension=depth,
                                length=length,
                                effective_length=le_d,
                                fc_modified=fc_modified,
                                area=width * depth,
                                e05=e05,
                                kse=kse,
                                kt=kt,
                            )
                        except ValueError as error:
                            st.error(str(error), width=650, icon=":material/error:")
                        else:
                            axes = (axis_b, axis_d)
                            pr = min(axis_b[3], axis_d[3]) / 1000
                            st.write(f"$Pr = {pr:.2f} kN$")
                            VERIF = general_design.limit_states_design(pf, pr)
                            show_verification(VERIF)
                            NOTE["Compression parallèle au fil (6.5.5)"] = (
                                art_6_5_5.verifier_compression_parallele_au_fil(
                                    b=width, d=depth, L=length, L_b=le_b, L_d=le_d,
                                    f_c=compute_resistance[2], E_05=e05,
                                    K_D=kd, K_H=kh, K_Sc=ksc, K_T=kt, K_SE=kse, P_f=pf,
                                    source_resistances=SOURCE,
                                )
                            )

                if axes:
                    with st.expander("Voir plus:", width=650):
                        st.markdown(
                            f"$F_c = f_c (K_D K_H K_{{Sc}} K_T) = {compute_resistance[2]} \\cdot "
                            f"({kd} \\cdot {kh} \\cdot {ksc} \\cdot {kt}) = {fc_modified:.3f}$ MPa"
                        )
                        st.markdown(f"$E_{{05}} = {e05}$ MPa, $K_{{SE}} = {kse}$")
                        for label, axis in zip(
                            ("Selon $b$", "Selon $d$"), axes
                        ):
                            cc, kzc, kc, pr_axis = axis
                            st.markdown(
                                f"**{label}** : $C_c = {cc:.2f}$, $K_{{Zc}} = {kzc:.4f}$, "
                                f"$K_C = {kc:.4f}$, $Pr = {pr_axis / 1000:.2f} kN$"
                            )

if "compression_perpendiculaire" in ONGLETS:
    with ONGLETS["compression_perpendiculaire"]:
        acces.avertir_si_en_test("compression_perpendiculaire")
        with st.container(horizontal_alignment="center"):
            kd, kscp, kt, _, _ = sawn_lumber.modification_factors(
                width=width,
                depth=depth,
                prop="comp_perp",
                duration=duration[DURATION],
                category=CATEGORY,
                wet_service=wet,
                treated=treated,
                incised=incised,
                _2ft_spacing=group,
                connected_subfloor=subfloor,
                built_up_beam=PLIS,
            )
            member_width = built_up * width
            kzcp = sawn_lumber.bearing_size_factor(member_width, depth)

            # --- résistance prévue fcp : tableaux 6.4 à 6.9, ou densité G en option (A.6.5.6) ---
            fcp = compute_resistance[3]
            col1, col2 = st.columns(2, width=550)
            with col1:
                use_density = st.checkbox(
                    "$f_{cp}$ à partir de la densité $G$",
                    key="cp_use_density",
                    help="""Option (annexe A.6.5.6, informative). Par défaut, $f_{cp}$ vient des
                    tableaux 6.4 à 6.9""",
                )
            if use_density:
                with col1:
                    density = st.number_input(
                        "Densité moyenne du bois anhydre, $G$",
                        min_value=0.30,
                        max_value=0.80,
                        value=sawn_lumber.density_table_a11(
                            specie[SPECIE], compute_resistance[5]
                        ),
                        step=0.01,
                        key="cp_density",
                        help="Valeur proposée selon le tableau A.11",
                    )
                with col2:
                    nlga = st.checkbox(
                        "Densité marquée NLGA (sans la limite de tolérance de 0,9)",
                        key="cp_nlga",
                    )
                fcp_table = fcp
                fcp = sawn_lumber.bearing_strength_from_density(
                    density, tolerance_limit=not nlga
                )
                if fcp > fcp_table:
                    st.warning(
                        f"""$f_{{cp}}$ calculé à partir de $G$ ({fcp:.2f} MPa) est plus élevé que la
                        valeur des tableaux 6.4 à 6.9 ({fcp_table} MPa) : non conservateur.""",
                        width=550,
                        icon=":material/warning:",
                    )
            fcp_modified = sawn_lumber.bearing_strength(fcp, kd=kd, kscp=kscp, kt=kt)
            SOURCE_FCP = "A.6.5.6 (densité G)" if use_density else SOURCE

            col1, col2 = st.columns(2, width=550)
            with col1:
                bearing_width_input = st.number_input(
                    "Largeur d'appui, $b$ (mm)",
                    min_value=1.0,
                    value=None,
                    step=1.0,
                    placeholder=f"Largeur de l'élément = {member_width} mm",
                    key="cp_bearing_width",
                    help="Optionnel : si vide, la largeur de l'élément est utilisée",
                    icon=":material/fit_page_width:",
                )
                bearing_width = member_width
                if bearing_width_input is not None:
                    bearing_width = min(bearing_width_input, member_width)
                    if bearing_width_input > member_width:
                        st.warning(
                            f"La largeur d'appui est limitée à la largeur de l'élément ({member_width} mm).",
                            icon=":material/warning:",
                        )
                support_length = st.number_input(
                    "Longueur d'appui, $L_b$ (mm)",
                    min_value=1.0,
                    value=None,
                    step=1.0,
                    placeholder="Requis",
                    key="cp_support_length",
                    help="Longueur d'appui parallèle au fil (6.5.6.2)",
                    icon=":material/arrow_range:",
                )
                support_far = st.checkbox(
                    "Appui à au moins 75 mm de l'extrémité",
                    key="cp_support_far",
                    help="Condition a) de 6.5.6.5 pour $K_B$",
                )
                support_low_bending = st.checkbox(
                    "Appui hors des fortes contraintes de flexion",
                    key="cp_support_low_bending",
                    help="Condition b) de 6.5.6.5 pour $K_B$",
                )
                near_load = st.checkbox(
                    "Charge à moins de $d$ du centre de l'appui",
                    key="cp_near_load",
                    help=f"""Charge appliquée à une distance du centre de l'appui inférieure ou égale
                    à la hauteur de l'élément, $d = {depth}$ mm (6.5.6.3)""",
                )
                if near_load:
                    load_length = st.number_input(
                        "Longueur d'appui de la charge (mm)",
                        min_value=1.0,
                        value=None,
                        step=1.0,
                        placeholder="Requis",
                        key="cp_load_length",
                        help="Longueur d'appui de la charge, parallèle au fil (6.5.6.3.2)",
                        icon=":material/arrow_range:",
                    )
                    load_far = st.checkbox(
                        "Charge à au moins 75 mm de l'extrémité",
                        key="cp_load_far",
                        help="Condition a) de 6.5.6.5 pour $K_B$",
                    )
                    load_low_bending = st.checkbox(
                        "Charge hors des fortes contraintes de flexion",
                        key="cp_load_low_bending",
                        help="Condition b) de 6.5.6.5 pour $K_B$",
                    )

            details = []
            with col2:
                rf = st.number_input(
                    "$Rf: (kN)$",
                    min_value=0.00,
                    value=None,
                    width=550,
                    placeholder="Réaction pondérée à l'appui",
                    step=1.00,
                    key="cp_rf",
                    icon=":material/input:",
                )
                if support_length is None:
                    st.info(
                        "Spécifiez la longueur d'appui pour calculer $Qr$",
                        width=650,
                        icon=":material/info:",
                    )
                else:
                    kb_support = sawn_lumber.bearing_length_factor(
                        support_length, support_far, support_low_bending
                    )
                    area = bearing_width * support_length
                    qr = (
                        sawn_lumber.bearing_resistance(fcp_modified, area, kb_support, kzcp)
                        / 1000
                    )
                    st.write(f"$Qr = {qr:.2f} kN$")
                    show_verification(general_design.limit_states_design(rf, qr))
                    NOTE["Compression perpendiculaire au fil (6.5.6.2)"] = (
                        art_6_5_6.verifier_compression_perpendiculaire_au_fil(
                            b=bearing_width, d=depth, L_b=support_length, f_cp=fcp,
                            K_D=kd, K_Scp=kscp, K_T=kt,
                            loin_de_l_extremite=support_far,
                            hors_fortes_contraintes_de_flexion=support_low_bending,
                            R_f=rf, largeur_element=member_width,
                            source_resistances=SOURCE_FCP,
                        )
                    )
                    details.append(
                        f"Appui : $A_b = {bearing_width:g} \\cdot {support_length:g} = {area:.0f}$ mm², "
                        f"$K_B = {kb_support:.4f}$, "
                        f"$Qr = {qr:.2f} kN$"
                    )

                if near_load:
                    pf_near = st.number_input(
                        "$Pf: (kN)$ près de l'appui",
                        min_value=0.00,
                        value=None,
                        width=550,
                        placeholder="Charge pondérée près de l'appui",
                        step=1.00,
                        key="cp_pf",
                        icon=":material/input:",
                    )
                    if support_length is None or load_length is None:
                        st.info(
                            "Spécifiez les deux longueurs d'appui pour calculer $Q'r$",
                            width=650,
                            icon=":material/info:",
                        )
                    else:
                        kb_load = sawn_lumber.bearing_length_factor(
                            load_length, load_far, load_low_bending
                        )
                        kb_near = min(kb_support, kb_load)
                        average_area = sawn_lumber.average_bearing_area(
                            bearing_width, load_length, support_length
                        )
                        qr_near = (
                            sawn_lumber.bearing_resistance_near_support(
                                fcp_modified, average_area, kb_near, kzcp
                            )
                            / 1000
                        )
                        st.write(f"$Q'r = {qr_near:.2f} kN$")
                        show_verification(general_design.limit_states_design(pf_near, qr_near))
                        NOTE["Compression perpendiculaire près d'un appui (6.5.6.3)"] = (
                            art_6_5_6.verifier_compression_perpendiculaire_pres_d_un_appui(
                                b=bearing_width, d=depth, L_b_appui=support_length,
                                L_b_charge=load_length, f_cp=fcp, K_D=kd, K_Scp=kscp, K_T=kt,
                                appui_loin_de_l_extremite=support_far,
                                appui_hors_fortes_contraintes_de_flexion=support_low_bending,
                                charge_loin_de_l_extremite=load_far,
                                charge_hors_fortes_contraintes_de_flexion=load_low_bending,
                                P_f=pf_near, largeur_element=member_width,
                                source_resistances=SOURCE_FCP,
                            )
                        )
                        details.append(
                            f"Charge près de l'appui : $A'_b = {average_area:.0f}$ mm², "
                            f"$K_B = \\min({kb_support:.4f}, {kb_load:.4f}) = {kb_near:.4f}$, "
                            f"$Q'r = {qr_near:.2f} kN$"
                        )

            if details:
                with st.expander("Voir plus:", width=650):
                    st.markdown(
                        f"$F_{{cp}} = f_{{cp}} (K_D K_{{Scp}} K_T) = {fcp:.2f} \\cdot "
                        f"({kd} \\cdot {kscp} \\cdot {kt}) = {fcp_modified:.3f}$ MPa"
                    )
                    st.markdown(
                        f"$K_{{Zcp}} = {kzcp:.4f}$ (largeur/hauteur = "
                        f"{member_width}/{depth} = {member_width / depth:.2f})"
                    )
                    for line in details:
                        st.markdown(line)

if "compression_oblique" in ONGLETS:
    with ONGLETS["compression_oblique"]:
        with st.container(horizontal_alignment="center"):
            st.warning("Fonctionnalité à venir.", width=200)

if "traction" in ONGLETS:
    with ONGLETS["traction"]:
        with st.container(horizontal_alignment="center"):
            st.warning("Fonctionnalité à venir.", width=200)

if "flexion_et_charge_axiale" in ONGLETS:
    with ONGLETS["flexion_et_charge_axiale"]:
        with st.container(horizontal_alignment="center"):
            st.warning("Fonctionnalité à venir.", width=200)


# --- note de calcul PDF (issue #50) ---
FONCTION_DE_LA_VERIFICATION = {
    "Flexion (6.5.3)": "flexion",
    "Cisaillement (6.5.4.3)": "cisaillement",
    "Cisaillement par fissuration à l'entaille (6.5.4.4)": "cisaillement",
    "Compression parallèle au fil (6.5.5)": "compression_parallele",
    "Compression perpendiculaire au fil (6.5.6.2)": "compression_perpendiculaire",
    "Compression perpendiculaire près d'un appui (6.5.6.3)": "compression_perpendiculaire",
}
if acces.permis("note_pdf"):
    st.divider()
    st.subheader("Note de calcul (PDF)", anchor=False)
    with st.container(horizontal_alignment="center"):
        if not NOTE:
            st.info(
                "Faites au moins une vérification pour produire la note de calcul.",
                width=650,
                icon=":material/info:",
            )
        else:
            with st.expander("En-tête de la note", width=650):
                col1, col2 = st.columns(2)
                client = col1.text_input("Client")
                projet = col2.text_input("Projet")
                adresse = col1.text_input("Adresse du projet")
                dossier = col2.text_input("Numéro de dossier")
                ingenieur = col1.text_input("Ingénieur")
                oiq = col2.text_input("Numéro OIQ")
                date = col1.date_input("Date", value=datetime.date.today(), format="YYYY-MM-DD")
                element = col2.text_input("Nom de l'élément", value="Élément 1")
            with st.expander("Apparence de la note (logo et couleurs)", width=650):
                st.caption(
                    """Par défaut : logo et couleurs de Le Repère. Ces réglages restent actifs pendant la
                    séance ; l'enregistrement permanent viendra avec les comptes utilisateurs."""
                )
                logo = st.file_uploader("Logo (PNG, JPG ou SVG)", type=["png", "jpg", "jpeg", "svg"])
                col1, col2 = st.columns(2)
                principale = col1.color_picker("Couleur principale", value=COULEUR_PRINCIPALE)
                accent = col2.color_picker("Couleur d'accent", value=COULEUR_ACCENT)
            with st.container(width=650):
                acces.avertir_si_en_test("note_pdf")
                st.markdown("Vérifications à inclure :")
                choix = [nom for nom in NOTE if st.checkbox(nom, value=True, key=f"note_{nom}")]
                if choix:
                    pdf = produire_pdf(
                        [
                        (element, NOTE[nom], acces.en_test(FONCTION_DE_LA_VERIFICATION[nom]))
                        for nom in choix
                    ],
                        EnTete(client, projet, adresse, dossier, str(date), ingenieur, oiq),
                        Apparence(logo.getvalue() if logo else None, principale, accent),
                    )
                    st.download_button(
                        "Télécharger la note de calcul (PDF)",
                        data=pdf,
                        file_name=f"note_de_calcul_{dossier or 'datum'}_{date}.pdf",
                        mime="application/pdf",
                        icon=":material/download:",
                        type="primary",
                    )
