"""
CSA O86:19 - 6.2 Matériaux (p. 52-55).

    6.2.2.1 Bois de charpente classé visuellement (tableau 6.3 : catégories et dimensions)
    6.2.2.2 Bois de charpente MSR et MEL

Catégories (codes de la base de données) :
    "Light"  : charpente légère (tableau 6.5)
    "Lumber" : solives et madriers, charpente légère de structure, montants (tableau 6.4)
    "Beam"   : poutres et longerons (tableau 6.6)
    "Post"   : poteaux et bois carrés (tableau 6.7)
    "MSR", "MEL" : bois classé mécaniquement (tableaux 6.8 et 6.9)

Frontière poutres / poteaux (tableau 6.3, version anglaise ; notes des tableaux 6.6 et 6.7) : la
grande face dépasse la face étroite de **plus de** 51 mm pour les poutres, de **51 mm ou moins** pour
les poteaux. (La version française du tableau 6.3 écrit « au moins 51 » pour les poutres.)

Comportement conservé tel quel pendant la migration. Voir l'issue #34 pour le choix entre les tableaux
6.4 et 6.5 lorsque les deux s'appliquent (tableau 6.3).
"""

DIMENSION_MAXIMALE = 412  # mm : au-delà, valider la disponibilité chez les fournisseurs


def categorie_de_bois(b: float, d: float, msr: bool = False, mel: bool = False) -> str:
    """
    6.2.2 Catégorie de bois d'œuvre selon les dimensions (tableau 6.3).

    Args:
        b (float): Largeur de l'élément, mm.
        d (float): Hauteur de l'élément, mm.
        msr (bool, optional): Bois classé mécaniquement par résistance (MSR). Default to False.
        mel (bool, optional): Bois évalué par machine (MEL). Default to False.

    Returns:
        str: Code de la catégorie ("Light", "Lumber", "Beam", "Post", "MSR" ou "MEL").

    Raises:
        ValueError: Si une dimension est inférieure à 38 mm, ou si la grande face dépasse 412 mm
            (disponibilité à valider chez les fournisseurs).
    """
    face_etroite = min(b, d)
    grande_face = max(b, d)

    if face_etroite < 38:
        raise ValueError("Les dimensions ne peuvent pas être plus petites que 38 mm.")
    if grande_face > DIMENSION_MAXIMALE:
        raise ValueError("Valider la disponibilité du bois chez les fournisseurs.")

    if face_etroite < 89 and grande_face < 89:
        categorie = "Light"
    elif face_etroite >= 114:
        categorie = "Beam" if grande_face - face_etroite > 51 else "Post"
    else:
        categorie = "Lumber"

    if mel:
        categorie = "MEL"
    if msr:
        categorie = "MSR"

    return categorie
