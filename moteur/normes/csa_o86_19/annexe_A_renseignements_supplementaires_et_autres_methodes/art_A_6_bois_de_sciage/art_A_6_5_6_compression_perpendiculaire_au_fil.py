"""
CSA O86:19 - A.6.5.6 Compression perpendiculaire au fil (annexe A, informative, p. 315).

Rapport entre la résistance moyenne en compression perpendiculaire au fil et la densité moyenne du
bois anhydre. Option seulement (décision de l'utilisateur) : par défaut, f_cp vient des tableaux
6.4 à 6.9. La formule peut donner plus que les tableaux (ex. pruche-sapin : 6,28 contre 4,6 MPa) :
l'interface doit alors afficher un avertissement.
"""


def f_cp(G: float, limite_de_tolerance: bool = True) -> float:
    """
    A.6.5.6 Résistance prévue en compression perpendiculaire au fil à partir de la densité.

    f_cp = 0,9 L (2243,8 G - 473,8) / M, avec L = 1,8125 et M = 145,038.
    Pour le bois dont la densité est qualifiée et marquée selon les règles du NLGA, l'équation peut
    être utilisée sans la limite de tolérance de 0,9.

    Args:
        G (float): Densité moyenne du bois anhydre (tableau A.11 ou densité marquée).
        limite_de_tolerance (bool, optional): Appliquer la limite de tolérance de 0,9.
            Default to True.

    Returns:
        float: f_cp, MPa.

    Raises:
        ValueError: Si la densité ne donne pas une résistance positive.
    """
    coefficient = 0.9 if limite_de_tolerance else 1
    resistance = coefficient * 1.8125 * (2243.8 * G - 473.8) / 145.038
    if resistance <= 0:
        raise ValueError(f"La densité G = {G} ne donne pas une résistance positive (A.6.5.6).")

    return resistance
