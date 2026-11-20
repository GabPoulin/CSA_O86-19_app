"""
Figures schématiques des vérifications (ARCHITECTURE.md, section 8 ; issue #62).

Chaque figure est un SVG, pas à l'échelle, dessiné à partir de la trace du calcul (Resultat) : la
même figure sert dans l'interface et dans la note de calcul PDF. Les cotes montrent les variables
utilisées dans le calcul, avec leurs valeurs dans les deux unités (ex. « L_b = 89 mm » et « (3.50 po) »).
Une donnée absente est affichée par son symbole seulement.

Aucune logique de calcul ici : les valeurs viennent telles quelles de la trace.
"""

from html import escape

from moteur.commun.nombres import cs
from moteur.commun.resultat import Resultat
from moteur.commun.unites import deux_unites, grandeur, vers_imperial

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


def _valeurs(valeur: float | None, nom_grandeur: str, resultat: bool = False) -> tuple[str, str]:
    """
    Valeur métrique et valeur impériale entre parenthèses, écrites comme dans la note de calcul : une
    donnée comme dans le tableau des données (unites.deux_unites), un résultat (charge de la
    vérification) avec les chiffres significatifs des calculs (nombres.cs). ("", "") si la valeur est
    absente.
    """
    if valeur is None:
        return "", ""
    if resultat:
        g = grandeur(nom_grandeur)
        return (f"{cs(valeur)} {g.unite_metrique}",
                f"({cs(vers_imperial(valeur, nom_grandeur))} {g.unite_imperiale})")
    metrique, imperial = deux_unites(valeur, nom_grandeur).split(" (")
    return metrique, f"({imperial}"


def _etiquette(x: float, y: float, symbole: str, valeur: float | None, nom_grandeur: str,
               ancre: str = "middle", resultat: bool = False) -> str:
    """Étiquette d'une cote : « symbole = valeur métrique » puis « (valeur impériale) » en dessous."""
    metrique, imperial = _valeurs(valeur, nom_grandeur, resultat)
    ligne_1 = _symbole(symbole) + (f" = {escape(metrique)}" if metrique else "")
    svg = (f"<text x='{x}' y='{y}' text-anchor='{ancre}' font-size='{TAILLE}' "
           f"fill='{COULEUR_TEXTE}' {POLICE}>{ligne_1}</text>")
    if imperial:
        svg += (f"<text x='{x}' y='{y + TAILLE + 3}' text-anchor='{ancre}' "
                f"font-size='{TAILLE - 2}' fill='{COULEUR_TEXTE}' {POLICE}>{escape(imperial)}</text>")
    return svg


def _donnee(resultat: Resultat, symbole: str) -> float | None:
    """Valeur d'une donnée de la trace, ou None si elle est absente."""
    for d in resultat.donnees:
        if d.symbole == symbole:
            return d.valeur
    return None


def _hachures(x: float, y: float, largeur: float, hauteur: float, couleur: str) -> str:
    """Appui hachuré (rectangle et traits à 45°), comme les icônes de marque/icones/."""
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


def compression_perpendiculaire(
    resultat: Resultat, principale: str = COULEUR_PRINCIPALE, accent: str = COULEUR_ACCENT
) -> str:
    """
    Figure de 6.5.6.2 (compression perpendiculaire au fil à un appui) : la réaction de l'appui
    seulement, par-dessous (figure 6.2 de la norme : R_f ≤ Q_r).

    À gauche, l'élévation : l'élément sur l'appui, la longueur d'appui L_b et la réaction R_f. À droite,
    la section : la hauteur d de l'élément et la largeur d'appui b.

    Args:
        resultat (Resultat): Trace de verifier_compression_perpendiculaire_au_fil().
        principale (str, optional): Couleur de l'élément et de l'appui. Default to celle de la marque.
        accent (str, optional): Couleur de la charge et des cotes. Default to celle de la marque.

    Returns:
        str: SVG de la figure.
    """
    b, d, L_b = (_donnee(resultat, s) for s in ("b", "d", "L_b"))
    b_element = _donnee(resultat, "b_{élément}")
    R_f = resultat.verification.charge if resultat.verification else None
    pointille = f"stroke='{principale}' stroke-width='0.8' stroke-dasharray='3 3'"

    # Élévation : élément (y 20 à 66) coupé à droite, appui sous l'extrémité gauche (x 14 à 60)
    elevation = (
        f"<path d='M6 20 H150 L145 32 L155 43 L145 55 L150 66 H6 Z' stroke='{principale}' "
        f"stroke-width='2.5' stroke-linejoin='round'/>"
        + _hachures(14, 66, 46, 24, principale)
        # Réaction R_f, par-dessous
        + f"<path d='M37 128 V94 M31 101 L37 94 L43 101 M30 128 H44' stroke='{accent}' "
          f"stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/>"
        + _etiquette(66, 108, "R_f", R_f, "force", ancre="start", resultat=True)
        # Longueur d'appui L_b
        + f"<path d='M14 92 V142 M60 92 V142' {pointille}/>"
        + _cote_horizontale(14, 60, 138, accent)
        + _etiquette(37, 160, "L_b", L_b, "dimension")
    )

    # Section : élément (largeur b_élément) sur l'appui (largeur b, au plus celle de l'élément)
    x_section, largeur_section = 196, 40
    largeur_appui = 28 if b is not None and b_element and b < b_element else largeur_section
    x_appui = x_section + (largeur_section - largeur_appui) / 2
    x_cote_d = x_section + largeur_section + 12
    section = (
        f"<rect x='{x_section}' y='20' width='{largeur_section}' height='46' stroke='{principale}' "
        f"stroke-width='2.5'/>"
        + _hachures(x_appui, 66, largeur_appui, 24, principale)
        + f"<path d='M{x_appui} 92 V142 M{x_appui + largeur_appui} 92 V142' {pointille}/>"
        + _cote_horizontale(x_appui, x_appui + largeur_appui, 138, accent)
        + _etiquette(x_section + largeur_section / 2, 160, "b", b, "dimension")
        + f"<path d='M{x_section + largeur_section + 2} 20 H{x_cote_d + 4} "
          f"M{x_section + largeur_section + 2} 66 H{x_cote_d + 4}' {pointille}/>"
        + _cote_verticale(x_cote_d, 20, 66, accent)
        + _etiquette(x_cote_d + 8, 40, "d", d, "dimension", ancre="start")
    )

    return (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 390 182' fill='none'>"
        f"<g transform='translate(16 0)'>{elevation}{section}</g></svg>"
    )


# Figure de chaque vérification, selon l'article de la trace
_FIGURES = {
    "6.5.6.2": compression_perpendiculaire,
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
