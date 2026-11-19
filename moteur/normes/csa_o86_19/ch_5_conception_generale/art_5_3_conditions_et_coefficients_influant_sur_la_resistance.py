"""
CSA O86:19 - 5.3 Conditions et coefficients influant sur la résistance (p. 41-43).

    5.3.2 Coefficient de durée d'application de la charge, K_D
        5.3.2.1 Généralités : K_D selon le tableau 5.1, sans dépasser 1,15
        5.3.2.2 Coefficient de durée d'application continue de la charge :
            K_D = 1,0 - 0,50 log(P_L / P_s) >= 0,65, si P_L > P_s

Points d'interprétation en attente (issue #58) : comportement de l'ancien code conservé.
"""

import math

# Tableau 5.1 (p. 42) : durée d'application de la charge -> K_D
TABLEAU_5_1: dict[str, float] = {
    "courte": 1.15,
    "normale": 1.00,
    "continue": 0.65,
}
K_D_MAXIMAL = 1.15  # 5.3.2.1 : K_D ne doit pas dépasser 1,15
K_D_MINIMAL_CONTINUE = 0.65  # 5.3.2.2 : K_D >= 0,65


def K_D(duree: str) -> float:
    """
    5.3.2.1 Coefficient de durée d'application de la charge, K_D (tableau 5.1).

    Args:
        duree (str): Durée d'application de la charge : « courte », « normale » ou « continue ».

    Returns:
        float: K_D.

    Raises:
        ValueError: Si la durée est inconnue.
    """
    try:
        return min(TABLEAU_5_1[duree], K_D_MAXIMAL)
    except KeyError:
        raise ValueError(f"Durée d'application de la charge invalide : {duree!r} (tableau 5.1).") from None


def K_D_charge_continue(P_L: float, P_s: float) -> float:
    """
    5.3.2.2 Coefficient de durée d'application continue de la charge.

    K_D = 1,0 - 0,50 log(P_L / P_s) >= 0,65, applicable si P_L > P_s.

    Args:
        P_L (float): Charge spécifiée de durée d'application continue (même unité que P_s).
        P_s (float): Charge spécifiée de durée d'application normale (S, L, S + 0,5 L ou 0,5 S + L,
            coefficients de risque égaux à 1,0).

    Returns:
        float: K_D.

    Raises:
        ValueError: Si P_s n'est pas positive, ou si P_L <= P_s (5.3.2.2 ne s'applique pas).
    """
    if P_s <= 0:
        raise ValueError("P_s doit être positive (5.3.2.2).")
    if P_L <= P_s:
        raise ValueError("5.3.2.2 s'applique seulement si P_L > P_s.")
    return min(max(1.0 - 0.50 * math.log10(P_L / P_s), K_D_MINIMAL_CONTINUE), K_D_MAXIMAL)
