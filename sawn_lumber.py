"""
CSA O86:19: Règles de calcul des charpentes en bois.
 6 Bois de sciage.
----------------------------------------------------

6.2 Matériaux.

6.3 Résistances prévues et modules d'élasticité.

6.4 Coefficients de correction.
    6.4.1 Coefficient de durée d'application de la charge, Kd.
     6.4.2 Coefficient de conditions d'utilisation, Ks.
      6.4.3 Coefficient de traitement, Kt.
       6.4.4 Coefficient de système, Kh.
        6.4.5 Coefficient de dimensions, Kz.
        
6.5 Calcul des résistances.
    6.5.2 Dimensions.
     6.5.3 Résistance au moment de flexion.
      6.5.4 Résistance au cisaillement.
       6.5.5 Résistance à la compression parallèle au fil.
        6.5.6 Résistance à la compression perpendiculaire au fil.
         6.5.7 Résistance à la compression oblique par rapport au fil.
          6.5.8 Résistance à la traction parallèle au fil.
           6.5.9 Résistance à la flexion et à la charge axiale combinées.
            6.5.10 Platelage.
             6.5.11 Fondations permanentes en bois.
              6.5.12 Applications propres aux fermes.
              
6.6 États limites de tenue en service.

____________________________________________________________________________________________________
    
    auteur: GabPoulin
    email: poulin33@me.com

"""

# IMPORTS


# DB CONNECTION


# CODE
def categories(width: int, depth: int) -> str:
    """
    6.2 Matériaux.

    Args:
        width (int): Largeur de l'élément, mm.
        depth (int): Hauteur de l'élément, mm.

    Returns:
        str: Catégorie de bois d'oeuvre.

    Raises:
        ValueError: Si les dimensions sont trop petites.

    """
    small = min(width, depth)
    large = max(width, depth)

    if small < 38:
        raise ValueError("Les dimensions ne peuvent pas être plus petites que 38 mm.")

    if large > 394:
        print("Valider la disponibilité du bois chez les fournisseurs.")

    if small < 89 and large < 89:
        category = "light"
    elif small >= 114:
        if large - small >= 51:
            category = "beam"
        else:
            category = "post"
    else:
        category = "lumber"

    return category


# TESTS
def _tests():
    """
    Tests pour les calculs de bois de sciage.

    """
    # Test categories
    test_categories = categories(width=38, depth=140)
    expected_result = "lumber"
    assert (
        test_categories == expected_result
    ), f"categories -> FAILED\n {expected_result = }\n {test_categories = }"


# RUN FILE
if __name__ == "__main__":
    _tests()


# END
