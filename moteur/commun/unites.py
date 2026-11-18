"""
Unités : conversions entre le métrique et l'impérial.

Tous les calculs se font en métrique, comme dans les normes. Ces conversions servent UNIQUEMENT à
l'affichage des entrées et des résultats pour l'utilisateur (ARCHITECTURE.md, section 8).

Facteurs exacts (définitions internationales) :
    1 po = 25,4 mm ; 1 pi = 304,8 mm ; 1 lb (force) = 4,448 221 615 260 5 N.
"""

from dataclasses import dataclass

_LB_EN_N = 4.4482216152605
_PO_EN_MM = 25.4
_PI_EN_MM = 304.8


@dataclass(frozen=True)
class Grandeur:
    """
    Une grandeur physique avec son unité métrique et son unité impériale d'affichage.

    Args:
        unite_metrique (str): Unité métrique d'affichage (ex. "kN").
        unite_imperiale (str): Unité impériale d'affichage (ex. "lb").
        facteur (float): Nombre d'unités métriques dans 1 unité impériale.
        decimales_metrique (int): Décimales à l'affichage en métrique.
        decimales_imperiale (int): Décimales à l'affichage en impérial.
    """

    unite_metrique: str
    unite_imperiale: str
    facteur: float
    decimales_metrique: int
    decimales_imperiale: int


GRANDEURS: dict[str, Grandeur] = {
    # Dimensions d'une section (b, d, longueur d'appui...) : mm et po
    "dimension": Grandeur("mm", "po", _PO_EN_MM, 0, 2),
    # Longueurs d'un élément (L, L_e...) : mm et pi
    "longueur": Grandeur("mm", "pi", _PI_EN_MM, 0, 2),
    # Aires : mm² et po²
    "aire": Grandeur("mm²", "po²", _PO_EN_MM**2, 0, 2),
    # Forces : kN et lb
    "force": Grandeur("kN", "lb", _LB_EN_N / 1000, 2, 0),
    # Moments : kN·m et lb·po (préférence de l'utilisateur)
    "moment": Grandeur("kN·m", "lb·po", _LB_EN_N * _PO_EN_MM / 1e6, 2, 0),
    # Contraintes et résistances prévues : MPa et psi
    "contrainte": Grandeur("MPa", "psi", _LB_EN_N / _PO_EN_MM**2, 2, 0),
}


def grandeur(nom: str) -> Grandeur:
    """
    Retourne la grandeur demandée.

    Raises:
        KeyError: Si la grandeur n'existe pas.
    """
    if nom not in GRANDEURS:
        raise KeyError(f"Grandeur inconnue : {nom!r}. Choix : {sorted(GRANDEURS)}.")
    return GRANDEURS[nom]


def vers_imperial(valeur: float, nom_grandeur: str) -> float:
    """Convertit une valeur métrique (unité d'affichage) en impérial."""
    return valeur / grandeur(nom_grandeur).facteur


def vers_metrique(valeur: float, nom_grandeur: str) -> float:
    """Convertit une valeur impériale en métrique (unité d'affichage)."""
    return valeur * grandeur(nom_grandeur).facteur


def deux_unites(valeur: float, nom_grandeur: str) -> str:
    """
    Formate une valeur métrique avec son équivalent impérial, pour la note de calcul.

    Exemple : deux_unites(38, "dimension") -> "38 mm (1.50 po)".
    Le point est utilisé comme séparateur décimal.
    """
    g = grandeur(nom_grandeur)
    imperial = vers_imperial(valeur, nom_grandeur)
    return (
        f"{valeur:.{g.decimales_metrique}f} {g.unite_metrique} "
        f"({imperial:.{g.decimales_imperiale}f} {g.unite_imperiale})"
    )
