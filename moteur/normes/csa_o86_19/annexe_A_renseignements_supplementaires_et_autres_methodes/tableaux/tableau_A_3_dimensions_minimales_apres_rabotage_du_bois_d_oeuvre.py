"""
CSA O86:19 - Tableau A.3 Dimensions minimales après rabotage du bois d'œuvre (annexe A, p. 308-309).

Voir 6.5.2 : dimensions nettes du bois sec (6.5.2.1) ou vert (6.5.2.2), arrondies au millimètre près.

Décisions validées avec l'utilisateur (CLAUDE.md) :
    - Dimensions nominales offertes : 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14 et 16 po.
    - 7 et 9 po : seulement pour le gros bois vert (165 et 216 mm).
    - Gros bois (face étroite >= 5 po nominal) vert : dimensions du gros bois du tableau A.3.
    - Mode « dimensions brutes » : convention de l'utilisateur (hors tableau A.3), conservée telle quelle.
"""

from moteur.normes.csa_o86_19.base_de_donnees import lire

_PO_EN_MM = 25.4


def _ligne(nominale: float):
    lignes = lire("SELECT * FROM lumber_sizes WHERE nominal = ?", (nominale,))
    return lignes[0] if lignes else None


def dimensions_nominales() -> list[int]:
    """
    Tableau A.3 Dimensions nominales offertes, po (bois de dimension et gros bois).

    Returns:
        list[int]: Dimensions nominales, po.
    """
    lignes = lire(
        "SELECT nominal FROM lumber_sizes "
        "WHERE dry IS NOT NULL OR green_timber IS NOT NULL ORDER BY nominal"
    )
    return [ligne["nominal"] for ligne in lignes]


def est_gros_bois(b_nominale: float, d_nominale: float) -> bool:
    """
    Tableau A.3 Gros bois : face étroite de 114 mm (5 po nominal) ou plus.

    Args:
        b_nominale (float): Largeur nominale, po.
        d_nominale (float): Hauteur nominale, po.

    Returns:
        bool: True si l'élément est du gros bois.
    """
    return min(b_nominale, d_nominale) >= 5


def dimension_nette(
    nominale: float,
    vert: bool = False,
    brut: bool = False,
    gros_bois: bool = False,
) -> int:
    """
    Tableau A.3 Dimension nette (minimale après rabotage), mm.

    Args:
        nominale (float): Dimension nominale, po (dimension réelle, po, en mode brut).
        vert (bool, optional): Bois vert (teneur en humidité > 19 %). Default to False.
        brut (bool, optional): Dimensions brutes (convention de l'utilisateur). Default to False.
        gros_bois (bool, optional): Gros bois (voir est_gros_bois). En vert, dimensions du gros
            bois du tableau A.3. Default to False.

    Returns:
        int: Dimension nette, mm.

    Raises:
        ValueError: Si la dimension nominale n'est pas au tableau A.3 (hors mode brut).
    """
    ligne = _ligne(nominale)

    if brut:
        if ligne is None:
            return int(round(nominale * _PO_EN_MM))
        return ligne["green_brut"] if vert else ligne["dry_brut"]

    if ligne is None:
        raise ValueError(
            f"La dimension nominale {nominale} po n'est pas offerte (tableau A.3). "
            f"Dimensions disponibles : {dimensions_nominales()} po."
        )
    if vert and gros_bois and ligne["green_timber"] is not None:
        return ligne["green_timber"]
    if ligne["dry"] is None:
        raise ValueError(
            f"La dimension nominale {nominale} po est offerte seulement pour le gros bois vert "
            "(tableau A.3) : face étroite de 5 po ou plus et bois vert."
        )
    return ligne["green"] if vert else ligne["dry"]
