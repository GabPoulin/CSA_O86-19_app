"""
Figures schématiques des vérifications (ARCHITECTURE.md, section 8 ; issue #62).

Chaque figure est un SVG, pas à l'échelle, dessiné à partir de la trace du calcul (Resultat) : la
même figure sert dans l'interface et dans la note de calcul PDF. Les cotes montrent les symboles des
variables utilisées dans le calcul (ex. « L_b »), sans valeurs : les valeurs sont dans le tableau des
données (demande de l'utilisateur, issue #62).

Aucune logique de calcul ici : les valeurs viennent telles quelles de la trace.
"""

from html import escape

from moteur.commun.resultat import Resultat

COULEUR_PRINCIPALE = "#233614"  # élément et appuis (couleurs de la marque, marque/couleurs.md)
COULEUR_ACCENT = "#9E5A00"  # charges et cotes
COULEUR_TEXTE = "#333333"
POLICE = "font-family='Arial, Helvetica, sans-serif'"
TAILLE = 16  # taille du texte des cotes, en unités du SVG (lisible dans la note PDF)


def _symbole(symbole: str) -> str:
    """« L_b » -> L avec b en indice (tspan), pour le texte SVG."""
    base, _, indice = symbole.partition("_")
    texte = escape(base)
    if indice:
        # Indice abaissé avec dy (baseline-shift n'est pas rendu dans la note PDF), puis retour
        texte += (f"<tspan dy='4' font-size='75%'>{escape(indice)}</tspan>"
                  f"<tspan dy='-4'>\u200b</tspan>")
    return texte


def _etiquette(x: float, y: float, symbole: str, ancre: str = "middle") -> str:
    """Étiquette d'une cote ou d'une charge : son symbole seulement (ex. « L_b »)."""
    return (f"<text x='{x}' y='{y}' text-anchor='{ancre}' font-size='{TAILLE}' "
            f"fill='{COULEUR_TEXTE}' {POLICE}>{_symbole(symbole)}</text>")


def _donnee(resultat: Resultat, symbole: str) -> float | None:
    """Valeur d'une donnée de la trace, ou None si elle est absente."""
    for d in resultat.donnees:
        if d.symbole == symbole:
            return d.valeur
    return None


def _bois_de_bout(x: float, y: float, largeur: float, hauteur: float, couleur: str,
                  epaisseur: float = 2) -> str:
    """
    Pièce de bois vue en bout (fil d'extrémité) : rectangle avec un X, convention des dessins de
    charpente en bois (figure 6.1 de la norme ; Manuel de calcul des charpentes en bois, figure 11.3a).
    """
    return (f"<rect x='{x}' y='{y}' width='{largeur}' height='{hauteur}' stroke='{couleur}' "
            f"stroke-width='{epaisseur}'/>"
            f"<path d='M{x} {y} L{x + largeur} {y + hauteur} M{x + largeur} {y} L{x} {y + hauteur}' "
            f"stroke='{couleur}' stroke-width='0.8'/>")


def _hachures(x: float, y: float, largeur: float, hauteur: float, couleur: str) -> str:
    """Appui quelconque, hachuré (rectangle et traits à 45°), comme les icônes de marque/icones/."""
    traits = []
    pas = 7
    for k in range(int((largeur + hauteur) / pas) + 1):
        d = k * pas
        x1, y1 = x + max(0, d - hauteur), y + min(d, hauteur)
        x2, y2 = x + min(d, largeur), y + max(0, d - largeur)
        if d > 0 and (x1, y1) != (x2, y2):
            traits.append(f"M{x1:g} {y1:g} L{x2:g} {y2:g}")
    return (f"<rect x='{x}' y='{y}' width='{largeur}' height='{hauteur}' stroke='{couleur}' "
            f"stroke-width='2'/><path d='{' '.join(traits)}' stroke='{couleur}' stroke-width='0.8'/>")


def _cote_horizontale(x1: float, x2: float, y: float, couleur: str) -> str:
    """Ligne de cote horizontale avec traits d'extrémité."""
    return (f"<path d='M{x1} {y} H{x2} M{x1} {y - 4} V{y + 4} M{x2} {y - 4} V{y + 4}' "
            f"stroke='{couleur}' stroke-width='1.2'/>")


def _cote_verticale(x: float, y1: float, y2: float, couleur: str) -> str:
    """Ligne de cote verticale avec traits d'extrémité."""
    return (f"<path d='M{x} {y1} V{y2} M{x - 4} {y1} H{x + 4} M{x - 4} {y2} H{x + 4}' "
            f"stroke='{couleur}' stroke-width='1.2'/>")


def _fleches_reparties(x1: float, x2: float, y_haut: float, y_bas: float, accent: str) -> str:
    """Charge répartie : une ligne et des flèches vers le bas, entre x1 et x2."""
    nombre = max(2, round((x2 - x1) / 24))
    pas = (x2 - x1) / nombre
    fleches = " ".join(
        f"M{x1 + i * pas:g} {y_haut} V{y_bas} M{x1 + i * pas - 4:g} {y_bas - 6} "
        f"L{x1 + i * pas:g} {y_bas} L{x1 + i * pas + 4:g} {y_bas - 6}"
        for i in range(nombre + 1)
    )
    return (f"<path d='M{x1} {y_haut} H{x2} {fleches}' stroke='{accent}' stroke-width='1.8' "
            f"stroke-linecap='round' stroke-linejoin='round'/>")


def _section_seule(x_section: float, y: float, plis: int, principale: str, accent: str) -> str:
    """
    Section de l'élément, sans appui, avec les cotes b et d. L'élément est vu en bout : chaque pli
    avec son X (figure 6.1 de la norme). Avec plusieurs plis, la cote b est celle d'un pli (b est la
    largeur d'un pli dans les traces de 6.5.3 et 6.5.4).

    Args:
        x_section, y (float): Coin supérieur gauche de l'élément, en unités du SVG.
        plis (int): Nombre de plis.
        principale, accent (str): Couleurs de l'élément et des cotes.

    Returns:
        str: Éléments SVG de la section.
    """
    pointille = f"stroke='{principale}' stroke-width='0.8' stroke-dasharray='3 3'"
    largeur_pli = 40 if plis == 1 else max(16, 76 / plis)
    largeur_section = largeur_pli * plis
    x_cote_d = x_section + largeur_section + 12
    return (
        "".join(_bois_de_bout(x_section + i * largeur_pli, y, largeur_pli, 46, principale,
                              epaisseur=2.5) for i in range(plis))
        + f"<path d='M{x_section} {y + 48} V{y + 64} M{x_section + largeur_pli} {y + 48} V{y + 64}' "
          f"{pointille}/>"
        + _cote_horizontale(x_section, x_section + largeur_pli, y + 60, accent)
        + _etiquette(x_section + largeur_pli / 2, y + 82, "b")
        + f"<path d='M{x_section + largeur_section + 2} {y} H{x_cote_d + 4} "
          f"M{x_section + largeur_section + 2} {y + 46} H{x_cote_d + 4}' {pointille}/>"
        + _cote_verticale(x_cote_d, y, y + 46, accent)
        + _etiquette(x_cote_d + 8, y + 28, "d", ancre="start")
    )


def _section(x_section: float, y: float, b: float | None, b_element: float | None, plis: int,
             principale: str, accent: str) -> str:
    """
    Section de l'élément sur son appui, avec les cotes d et b. L'élément est vu en bout : chaque pli
    avec son X (figure 6.1 de la norme). L'appui (hachuré) est dessiné plus étroit si b < b_élément.

    Args:
        x_section, y (float): Coin supérieur gauche de l'élément, en unités du SVG.
        b, b_element (float | None): Largeur d'appui et largeur de l'élément, mm (dessin de l'appui).
        plis (int): Nombre de plis.
        principale, accent (str): Couleurs de l'élément et des cotes.

    Returns:
        str: Éléments SVG de la section.
    """
    pointille = f"stroke='{principale}' stroke-width='0.8' stroke-dasharray='3 3'"
    largeur_pli = 40 if plis == 1 else max(16, 76 / plis)  # la section s'élargit avec les plis
    largeur_section = largeur_pli * plis
    largeur_appui = (
        round(largeur_section * 0.7) if b is not None and b_element and b < b_element
        else largeur_section
    )
    x_appui = x_section + (largeur_section - largeur_appui) / 2
    x_cote_d = x_section + largeur_section + 12
    return (
        "".join(_bois_de_bout(x_section + i * largeur_pli, y, largeur_pli, 46, principale,
                              epaisseur=2.5) for i in range(plis))
        + _hachures(x_appui, y + 46, largeur_appui, 24, principale)
        + f"<path d='M{x_appui} {y + 72} V{y + 122} M{x_appui + largeur_appui} {y + 72} V{y + 122}' "
          f"{pointille}/>"
        + _cote_horizontale(x_appui, x_appui + largeur_appui, y + 118, accent)
        + _etiquette(x_section + largeur_section / 2, y + 140, "b")
        + f"<path d='M{x_section + largeur_section + 2} {y} H{x_cote_d + 4} "
          f"M{x_section + largeur_section + 2} {y + 46} H{x_cote_d + 4}' {pointille}/>"
        + _cote_verticale(x_cote_d, y, y + 46, accent)
        + _etiquette(x_cote_d + 8, y + 28, "d", ancre="start")
    )


def compression_perpendiculaire(
    resultat: Resultat, principale: str = COULEUR_PRINCIPALE, accent: str = COULEUR_ACCENT
) -> str:
    """
    Figure de 6.5.6.2 (compression perpendiculaire au fil à un appui) : la réaction de l'appui
    seulement, par-dessous (figure 6.2 de la norme : R_f ≤ Q_r).

    À gauche, l'élévation : l'élément sur l'appui (hachuré), la longueur d'appui L_b et la réaction
    R_f. À droite, la section (élément vu en bout, chaque pli avec son X) : la hauteur d de l'élément et
    la largeur d'appui b. Symboles seulement : les valeurs sont dans le tableau des données.

    Args:
        resultat (Resultat): Trace de verifier_compression_perpendiculaire_au_fil().
        principale (str, optional): Couleur de l'élément et de l'appui. Default to celle de la marque.
        accent (str, optional): Couleur de la charge et des cotes. Default to celle de la marque.

    Returns:
        str: SVG de la figure.
    """
    b = _donnee(resultat, "b")
    b_element = _donnee(resultat, "b_{élément}")
    plis = int(_donnee(resultat, "n") or 1)
    pointille = f"stroke='{principale}' stroke-width='0.8' stroke-dasharray='3 3'"

    # Élévation : élément (y 20 à 66) coupé à droite, appui sous l'extrémité gauche (x 14 à 60)
    elevation = (
        f"<path d='M6 20 H150 L145 32 L155 43 L145 55 L150 66 H6 Z' stroke='{principale}' "
        f"stroke-width='2.5' stroke-linejoin='round'/>"
        + _hachures(14, 66, 46, 24, principale)
        # Réaction R_f, par-dessous
        + f"<path d='M37 128 V94 M31 101 L37 94 L43 101 M30 128 H44' stroke='{accent}' "
          f"stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/>"
        + _etiquette(66, 116, "R_f", ancre="start")
        # Longueur d'appui L_b
        + f"<path d='M14 92 V142 M60 92 V142' {pointille}/>"
        + _cote_horizontale(14, 60, 138, accent)
        + _etiquette(37, 158, "L_b")
    )

    section = _section(196, 20, b, b_element, plis, principale, accent)

    return (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 330 168' fill='none'>"
        f"<g transform='translate(16 0)'>{elevation}{section}</g></svg>"
    )


def compression_pres_d_un_appui(
    resultat: Resultat, principale: str = COULEUR_PRINCIPALE, accent: str = COULEUR_ACCENT
) -> str:
    """
    Figure de 6.5.6.3 (compression perpendiculaire au fil près d'un appui) : l'élément sur son appui,
    avec un autre élément appuyé sur le dessus, dont la charge P_f est à une distance du centre de
    l'appui inférieure ou égale à la hauteur d de l'élément (figure 6.2 de la norme : P_f ≤ Q'_r).

    À gauche, l'élévation : l'élément appuyé sur le dessus (hachuré) avec la charge P_f et sa longueur
    d'appui, l'appui (hachuré) avec la sienne, et la distance ≤ d entre les deux. Les longueurs d'appui
    portent les symboles de 6.5.6.3.2 : L_b1 pour la plus petite, L_b2 pour la plus grande.
    À droite, la section (chaque pli avec son X) : la hauteur d et la largeur d'appui b.

    Args:
        resultat (Resultat): Trace de verifier_compression_perpendiculaire_pres_d_un_appui().
        principale (str, optional): Couleur de l'élément et des appuis. Default to celle de la marque.
        accent (str, optional): Couleur de la charge et des cotes. Default to celle de la marque.

    Returns:
        str: SVG de la figure.
    """
    b = _donnee(resultat, "b")
    b_element = _donnee(resultat, "b_{élément}")
    plis = int(_donnee(resultat, "n") or 1)
    pointille = f"stroke='{principale}' stroke-width='0.8' stroke-dasharray='3 3'"
    # 6.5.6.3.2 : L_b1 est la plus petite longueur d'appui, L_b2 la plus grande ; la trace indique
    # laquelle est celle de la charge (sur le dessus)
    description_1 = next((d.description for d in resultat.donnees if d.symbole == "L_{b1}"), "")
    L_b_charge, L_b_appui = ("L_b1", "L_b2") if "(charge)" in description_1 else ("L_b2", "L_b1")

    # Élévation : élément (y 82 à 128) coupé à gauche, appui sous l'extrémité droite (x 214 à 260),
    # élément appuyé sur le dessus (x 170 à 206) près de l'appui
    elevation = (
        f"<path d='M260 82 H50 L45 94 L55 105 L45 117 L50 128 H260 Z' stroke='{principale}' "
        f"stroke-width='2.5' stroke-linejoin='round'/>"
        + _hachures(170, 60, 36, 22, principale)
        + _hachures(214, 128, 46, 24, principale)
        # Charge P_f sur l'élément du dessus
        + f"<path d='M188 4 V56 M182 49 L188 56 L194 49' stroke='{accent}' stroke-width='2.2' "
          f"stroke-linecap='round' stroke-linejoin='round'/>"
        + _etiquette(180, 26, "P_f", ancre="end")
        # Longueur d'appui de la charge (au-dessus de l'élément du dessus)
        + f"<path d='M170 58 V42 M206 58 V42' {pointille}/>"
        + _cote_horizontale(170, 206, 46, accent)
        + _etiquette(164, 52, L_b_charge, ancre="end")
        # Distance entre la charge et le centre de l'appui : au plus d (6.5.6.3.1)
        + f"<path d='M188 130 V176 M237 154 V176' {pointille}/>"
        + _cote_horizontale(188, 237, 172, accent)
        + f"<text x='182' y='177' text-anchor='end' font-size='{TAILLE}' fill='{COULEUR_TEXTE}' "
          f"{POLICE}>≤ {_symbole('d')}</text>"
        # Longueur d'appui à l'appui
        + f"<path d='M214 154 V196 M260 154 V196' {pointille}/>"
        + _cote_horizontale(214, 260, 192, accent)
        + _etiquette(237, 212, L_b_appui)
    )
    section = _section(296, 82, b, b_element, plis, principale, accent)

    return (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='30 0 380 222' fill='none'>"
        f"{elevation}{section}</svg>"
    )


def flexion(
    resultat: Resultat, principale: str = COULEUR_PRINCIPALE, accent: str = COULEUR_ACCENT
) -> str:
    """
    Figure de 6.5.3 (résistance au moment de flexion) : poutre sur deux appuis (hachurés) sous une
    charge répartie, moment pondéré M_f (M_f ≤ M_r). À droite, la section : chaque pli avec son X, b
    (largeur d'un pli) et d.

    Args:
        resultat (Resultat): Trace de verifier_flexion().
        principale, accent (str, optional): Couleurs de l'élément et des charges. Default to celles
            de la marque.

    Returns:
        str: SVG de la figure.
    """
    plis = int(_donnee(resultat, "n") or 1)
    elevation = (
        _fleches_reparties(14, 206, 8, 30, accent)
        + f"<rect x='14' y='32' width='192' height='36' stroke='{principale}' stroke-width='2.5'/>"
        + _hachures(14, 68, 26, 16, principale)
        + _hachures(180, 68, 26, 16, principale)
        + f"<path d='M40 76 Q110 104 180 76' stroke='{principale}' stroke-width='1.2' "
          f"stroke-dasharray='4 4'/>"
        + _etiquette(110, 114, "M_f")
    )
    return (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 360 124' fill='none'>"
        f"{elevation}{_section_seule(240, 26, plis, principale, accent)}</svg>"
    )


def cisaillement(
    resultat: Resultat, principale: str = COULEUR_PRINCIPALE, accent: str = COULEUR_ACCENT
) -> str:
    """
    Figure de 6.5.4.3 (résistance au cisaillement) : poutre sur son appui (hachuré) sous une charge
    répartie, effort tranchant pondéré V_f près de l'appui (V_f ≤ V_r). À droite, la section : chaque
    pli avec son X, b (largeur d'un pli) et d.

    Args:
        resultat (Resultat): Trace de verifier_cisaillement().
        principale, accent (str, optional): Couleurs de l'élément et des charges. Default to celles
            de la marque.

    Returns:
        str: SVG de la figure.
    """
    plis = int(_donnee(resultat, "n") or 1)
    elevation = (
        _fleches_reparties(14, 196, 8, 30, accent)
        + f"<path d='M14 32 H206 L201 41 L211 50 L201 59 L206 68 H14 Z' stroke='{principale}' "
          f"stroke-width='2.5' stroke-linejoin='round'/>"
        + _hachures(14, 68, 26, 16, principale)
        # Coupe près de l'appui et efforts tranchants de part et d'autre
        + f"<path d='M78 24 V76' stroke='{principale}' stroke-width='1' stroke-dasharray='4 3'/>"
        + f"<path d='M70 106 V84 M66 90 L70 84 L74 90 M86 84 V106 M82 100 L86 106 L90 100' "
          f"stroke='{accent}' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/>"
        + _etiquette(96, 102, "V_f", ancre="start")
    )
    return (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 360 124' fill='none'>"
        f"{elevation}{_section_seule(240, 26, plis, principale, accent)}</svg>"
    )


def cisaillement_a_l_entaille(
    resultat: Resultat, principale: str = COULEUR_PRINCIPALE, accent: str = COULEUR_ACCENT
) -> str:
    """
    Figure de 6.5.4.4 (cisaillement par fissuration à l'entaille), d'après la figure 6.1 de la norme :
    entaille à la rive en traction au-dessus de l'appui (hachuré), profondeur d_n, longueur e du centre
    de l'appui au coin rentrant, fissure (pointillé) au coin rentrant, effort tranchant pondéré V_f à
    l'appui (V_f ≤ F_r, 6.5.4.4.3). À droite, la section : chaque pli avec son X, b et d.

    Args:
        resultat (Resultat): Trace de verifier_cisaillement_par_fissuration().
        principale, accent (str, optional): Couleurs de l'élément et des charges. Default to celles
            de la marque.

    Returns:
        str: SVG de la figure.
    """
    plis = int(_donnee(resultat, "n") or 1)
    pointille = f"stroke='{principale}' stroke-width='0.8' stroke-dasharray='3 3'"
    elevation = (
        _fleches_reparties(14, 196, 8, 30, accent)
        # Élément entaillé (y 32 à 72) : rive inférieure remontée de d_n (y 52) entre l'extrémité et le
        # coin rentrant (x 90)
        + f"<path d='M14 32 H206 L201 42 L211 52 L201 62 L206 72 H90 V52 H14 Z' stroke='{principale}' "
          f"stroke-width='2.5' stroke-linejoin='round'/>"
        + _hachures(22, 52, 32, 16, principale)
        # Fissure au coin rentrant, dans le prolongement de l'entaille
        + f"<path d='M92 52 H132' stroke='{accent}' stroke-width='1.8' stroke-dasharray='4 3'/>"
        # Profondeur de l'entaille d_n, dans le vide de l'entaille
        + f"<path d='M74 72 H88' {pointille}/>"
        + _cote_verticale(80, 52, 72, accent)
        + _etiquette(73, 67, "d_n", ancre="end")
        # Longueur de l'entaille e : du centre de l'appui au coin rentrant
        + f"<path d='M38 70 V122 M90 74 V122' {pointille}/>"
        + _cote_horizontale(38, 90, 118, accent)
        + _etiquette(64, 138, "e")
        # Effort tranchant à l'appui (sous l'appui, à gauche de la cote e)
        + f"<path d='M28 104 V72 M24 78 L28 72 L32 78' stroke='{accent}' stroke-width='2' "
          f"stroke-linecap='round' stroke-linejoin='round'/>"
        + _etiquette(20, 98, "V_f", ancre="end")
    )
    return (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='-24 0 384 146' fill='none'>"
        f"{elevation}{_section_seule(240, 26, plis, principale, accent)}</svg>"
    )


def compression_parallele(
    resultat: Resultat, principale: str = COULEUR_PRINCIPALE, accent: str = COULEUR_ACCENT
) -> str:
    """
    Figure de 6.5.5 (compression parallèle au fil) : poteau de longueur L sous la charge pondérée P_f
    (P_f ≤ P_r), avec sa déformée de flambage (pointillé). À droite, la section : b et d (flambage
    vérifié selon les deux axes, 6.5.5.2.1).

    Args:
        resultat (Resultat): Trace de verifier_compression_parallele_au_fil().
        principale, accent (str, optional): Couleurs de l'élément et des charges. Default to celles
            de la marque.

    Returns:
        str: SVG de la figure.
    """
    plis = int(_donnee(resultat, "n") or 1)
    pointille = f"stroke='{principale}' stroke-width='0.8' stroke-dasharray='3 3'"
    elevation = (
        f"<path d='M60 4 V28 M54 21 L60 28 L66 21' stroke='{accent}' stroke-width='2.2' "
          f"stroke-linecap='round' stroke-linejoin='round'/>"
        + _etiquette(70, 20, "P_f", ancre="start")
        + f"<rect x='48' y='30' width='24' height='150' stroke='{principale}' stroke-width='2.5'/>"
        + _hachures(36, 180, 48, 14, principale)
        + f"<path d='M42 32 Q24 105 42 178' stroke='{principale}' stroke-width='1.2' "
          f"stroke-dasharray='4 4'/>"
        # Longueur L
        + f"<path d='M74 30 H104 M74 180 H104' {pointille}/>"
        + _cote_verticale(98, 30, 180, accent)
        + _etiquette(106, 110, "L", ancre="start")
    )
    return (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='-40 0 360 200' fill='none'>"
        f"{elevation}{_section_seule(170, 70, plis, principale, accent)}</svg>"
    )


# Figure de chaque vérification, selon l'article de la trace
_FIGURES = {
    "6.5.3": flexion,
    "6.5.4.3": cisaillement,
    "6.5.4.4": cisaillement_a_l_entaille,
    "6.5.5": compression_parallele,
    "6.5.6.2": compression_perpendiculaire,
    "6.5.6.3": compression_pres_d_un_appui,
}


def figure(
    resultat: Resultat, principale: str = COULEUR_PRINCIPALE, accent: str = COULEUR_ACCENT
) -> str | None:
    """
    Figure schématique d'une vérification (même figure dans l'interface et dans la note PDF).

    Args:
        resultat (Resultat): Trace du calcul.
        principale (str, optional): Couleur de l'élément et des appuis. Default to celle de la marque.
        accent (str, optional): Couleur des charges et des cotes. Default to celle de la marque.

    Returns:
        str | None: SVG de la figure, ou None si la vérification n'a pas encore de figure.
    """
    dessiner = _FIGURES.get(resultat.article)
    return dessiner(resultat, principale, accent) if dessiner else None
