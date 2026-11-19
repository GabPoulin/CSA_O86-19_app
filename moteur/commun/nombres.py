"""
Formatage des nombres dans les calculs affichés (trace, note de calcul PDF).

Même nombre de chiffres significatifs partout dans les calculs (demande de l'utilisateur, revue de la
PR #55). Le point est le séparateur décimal (CLAUDE.md). Les constantes de la norme (0.9, 6.3, 0.006…)
restent écrites telles quelles dans les formules ; cs() sert aux valeurs (données et résultats).
"""

import math

CHIFFRES_SIGNIFICATIFS = 3  # décision de l'utilisateur (revue de la PR #55)


def cs(valeur: float, chiffres: int = CHIFFRES_SIGNIFICATIFS) -> str:
    """
    Valeur arrondie à un nombre fixe de chiffres significatifs, sans notation scientifique.

    Exemples (3 chiffres) : 11.8 -> « 11.8 » ; 0.79451 -> « 0.795 » ; 4 085 877 -> « 4090000 » ;
    1 -> « 1.00 » ; 0 -> « 0 ».

    Args:
        valeur (float): Valeur à formater.
        chiffres (int, optional): Chiffres significatifs. Default to CHIFFRES_SIGNIFICATIFS.

    Returns:
        str: Valeur formatée.
    """
    if valeur == 0 or not math.isfinite(valeur):
        return "0" if valeur == 0 else str(valeur)
    decimales = chiffres - 1 - math.floor(math.log10(abs(valeur)))
    arrondie = round(valeur, decimales)
    # L'arrondi peut ajouter un chiffre (ex. 9.9996 -> 10.00) : recalculer les décimales
    if arrondie != 0:
        decimales = chiffres - 1 - math.floor(math.log10(abs(arrondie)))
    if decimales <= 0:
        return f"{round(arrondie, decimales):.0f}"
    return f"{arrondie:.{decimales}f}"
