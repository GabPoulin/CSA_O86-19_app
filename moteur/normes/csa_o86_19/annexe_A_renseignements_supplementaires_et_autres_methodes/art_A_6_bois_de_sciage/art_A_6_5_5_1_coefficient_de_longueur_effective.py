"""
CSA O86:19 - A.6.5.5.1 Coefficient de longueur effective, K_e (annexe A, informative, p. 303-304).

Tableau A.4 : valeurs de calcul minimales du coefficient de longueur effective, K_e, des éléments en
compression, selon le degré de retenue aux extrémités.

Note du tableau A.4 : L_e = K_e L, où L est l'entraxe des appuis latéraux de l'élément en compression
dans le plan de flambage en question. Aux extrémités de l'élément, cette distance doit être mesurée
depuis la surface extérieure des appuis en haut et en bas. K_e ne doit pas être inférieur à celui
qu'indiquerait une analyse rationnelle. S'il est difficile d'évaluer avec précision les conditions de
retenue aux extrémités, une valeur conservatrice doit être utilisée.
"""

# Tableau A.4 : (degré de retenue aux extrémités, K_e), textes exacts de la norme
TABLEAU_A_4: tuple[tuple[str, float], ...] = (
    ("Translation et rotation fixes aux deux extrémités", 0.65),
    ("Translation fixe aux deux extrémités et rotation fixe à une extrémité", 0.80),
    ("Translation fixe et rotation libre aux deux extrémités", 1.00),
    (
        "Translation et rotation fixes à une extrémité, translation libre et rotation fixe à "
        "l'autre extrémité",
        1.20,
    ),
    (
        "Translation et rotation fixes à une extrémité, translation libre et rotation "
        "partiellement fixe à l'autre extrémité",
        1.50,
    ),
    (
        "Translation fixe et rotation libre à une extrémité, translation libre et rotation fixe à "
        "l'autre extrémité",
        2.00,
    ),
    (
        "Translation et rotation fixes à une extrémité, translation et rotation libres à l'autre "
        "extrémité",
        2.00,
    ),
)


def degres_de_retenue() -> list[str]:
    """Degrés de retenue aux extrémités du tableau A.4, dans l'ordre de la norme."""
    return [degre for degre, _ in TABLEAU_A_4]


def K_e(degre_de_retenue: str) -> float:
    """
    Tableau A.4 Coefficient de longueur effective, K_e, selon le degré de retenue aux extrémités.

    Args:
        degre_de_retenue (str): Degré de retenue, tel qu'écrit au tableau A.4
            (voir degres_de_retenue()).

    Returns:
        float: K_e.

    Raises:
        ValueError: Si le degré de retenue n'est pas au tableau A.4.
    """
    for degre, coefficient in TABLEAU_A_4:
        if degre == degre_de_retenue:
            return coefficient
    raise ValueError(f"Degré de retenue absent du tableau A.4 : {degre_de_retenue!r}.")
