"""
CSA O86:19 - 5.1 Calculs aux états limites (p. 40).

    5.1.2 États limites ultimes

5.1.2 b) : « l'assurance que pour chaque effet de charge décrit à l'alinéa a), l'effet de charge
pondéré ne dépasse pas la résistance pondérée correspondante ».

Dans le code, on parle de « charge pondérée » (terme utilisé ailleurs dans la norme : P_f, T_f, V_f,
M_f…), comparée à la « résistance pondérée ».
"""

from moteur.commun.resultat import Verification


def verifier_etat_limite_ultime(
    charge: float,
    resistance: float,
    symbole_charge: str = "",
    symbole_resistance: str = "",
    unite: str = "",
    grandeur: str | None = None,
) -> Verification:
    """
    5.1.2 États limites ultimes : la charge pondérée ne doit pas dépasser la résistance pondérée.

    Le ratio est comparé à 1,00 avant d'être arrondi : un ratio exactement égal à 1,00 respecte
    l'état limite (« ne dépasse pas »). Une résistance nulle ou négative ne respecte pas l'état limite.

    Args:
        charge (float): Charge pondérée (>= 0, calculs de base en valeurs positives seulement).
        resistance (float): Résistance pondérée correspondante, dans la même unité.
        symbole_charge (str, optional): Symbole de la charge en LaTeX (ex. "P_f").
        symbole_resistance (str, optional): Symbole de la résistance en LaTeX (ex. "P_r").
        unite (str, optional): Unité métrique commune (ex. "kN").
        grandeur (str | None, optional): Grandeur pour l'affichage en impérial.

    Returns:
        Verification: Ratio et état (respecté ou dépassé).

    Raises:
        ValueError: Si la charge est négative.
    """
    if charge < 0:
        raise ValueError("La charge pondérée doit être positive ou nulle (calculs de base, 5.1.2).")

    if resistance <= 0:
        ratio = float("inf")
        respecte = False
    else:
        ratio = charge / resistance
        respecte = ratio <= 1

    return Verification(
        article="5.1.2",
        symbole_charge=symbole_charge,
        charge=charge,
        symbole_resistance=symbole_resistance,
        resistance=resistance,
        ratio=ratio,
        respecte=respecte,
        unite=unite,
        grandeur=grandeur,
    )
