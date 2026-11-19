"""
CSA O86:19 - 6.4 Coefficients de correction (p. 59-63).

    6.4.1 Coefficient de durée d'application de la charge, K_D : voir 5.3.2 (chapitre 5).
    6.4.2 Coefficient de conditions d'utilisation, K_S (tableau 6.10)
    6.4.3 Coefficient de traitement, K_T (tableau 6.11)
    6.4.4 Coefficient de système, K_H (tableau 6.12)
    6.4.5 Coefficient de dimensions, K_Z (tableau 6.13)

Propriétés (lignes des tableaux 6.10 à 6.13) : voir PROPRIETES.

Interprétations validées avec l'utilisateur (CLAUDE.md, issue #7) :
    - K_H : un élément composé de 2 plis ou plus prend toujours la colonne « Poutres composées ».
      La colonne MSR (1,20) est une sous-colonne du cas 2 ; au cas 1, le MSR prend 1,10.
      Traction au cas 2 (« — » au tableau 6.12) : K_H = 1,00.
    - K_Z (issue #45) : la dimension réelle (sèche, verte ou brute) choisit la ligne du tableau 6.13 ;
      une grande face absente du tableau prend la ligne de la dimension supérieure (conservateur, ex.
      143 mm -> ligne « 184 à 191 ») ; une face étroite entre deux colonnes (65 à 88 mm, 103 à 113 mm)
      prend la plus petite valeur des deux colonnes voisines (conservateur).
    - K_T (issue #45) : bois traité et incisé de plus de 89 mm d'épaisseur, absent du tableau 6.11 :
      K_T = 1,00.
"""

import math

FLEXION = "flexion"
CISAILLEMENT_PAR_FISSURATION = "cisaillement_par_fissuration"
CISAILLEMENT_LONGITUDINAL = "cisaillement_longitudinal"
COMPRESSION_PARALLELE = "compression_parallele_au_fil"
COMPRESSION_PERPENDICULAIRE = "compression_perpendiculaire_au_fil"
TRACTION_PARALLELE = "traction_parallele_au_fil"
MODULE_D_ELASTICITE = "module_d_elasticite"

PROPRIETES = (
    FLEXION,
    CISAILLEMENT_PAR_FISSURATION,
    CISAILLEMENT_LONGITUDINAL,
    COMPRESSION_PARALLELE,
    COMPRESSION_PERPENDICULAIRE,
    TRACTION_PARALLELE,
    MODULE_D_ELASTICITE,
)


def _verifier_propriete(propriete: str) -> None:
    if propriete not in PROPRIETES:
        raise ValueError(f"Propriété inconnue : {propriete!r}. Choix : {PROPRIETES}.")


# 6.4.2 Tableau 6.10 Coefficients de conditions d'utilisation, K_S (p. 61)
# propriété : (symbole, milieu sec, milieu humide face étroite <= 89 mm, milieu humide > 89 mm)
TABLEAU_6_10: dict[str, tuple[str, float, float, float]] = {
    FLEXION: ("K_Sb", 1.00, 0.84, 1.00),
    CISAILLEMENT_PAR_FISSURATION: ("K_Sf", 1.00, 0.70, 0.70),
    CISAILLEMENT_LONGITUDINAL: ("K_Sv", 1.00, 0.96, 1.00),
    COMPRESSION_PARALLELE: ("K_Sc", 1.00, 0.69, 0.91),
    COMPRESSION_PERPENDICULAIRE: ("K_Scp", 1.00, 0.67, 0.67),
    TRACTION_PARALLELE: ("K_St", 1.00, 0.84, 1.00),
    MODULE_D_ELASTICITE: ("K_SE", 1.00, 0.94, 1.00),
}

# 6.4.3 Tableau 6.11 Coefficient de traitement, K_T (p. 62), bois traité d'au plus 89 mm, incisé
# (milieu sec, milieu humide)
TABLEAU_6_11_MODULE_D_ELASTICITE = (0.90, 0.95)
TABLEAU_6_11_AUTRES_PROPRIETES = (0.75, 0.85)
EPAISSEUR_MAXIMALE_INCISEE = 89  # mm, tableau 6.11 : « bois traité d'au plus 89 mm, incisé »

# 6.4.4 Tableau 6.12 Coefficients de système, K_H (p. 62)
CAS_1 = "cas_1"
CAS_2 = "cas_2"
POUTRES_COMPOSEES = "poutres_composees"
# propriété : (cas 1, cas 2 classé visuellement, cas 2 MSR, poutres composées)
# Traction au cas 2 : « — » au tableau, 1,00 (issue #7). Autres propriétés : 1,00.
TABLEAU_6_12: dict[str, tuple[float, float, float, float]] = {
    FLEXION: (1.10, 1.40, 1.20, 1.10),
    CISAILLEMENT_LONGITUDINAL: (1.10, 1.40, 1.20, 1.10),
    COMPRESSION_PARALLELE: (1.10, 1.10, 1.10, 1.00),
    TRACTION_PARALLELE: (1.10, 1.00, 1.00, 1.00),
}
AUTRE_PROPRIETE_K_H = (1.00, 1.00, 1.00, 1.00)

# 6.4.5 Tableau 6.13 Coefficient de dimensions, K_Z, bois classé visuellement (p. 63)
# (borne supérieure incluse de la grande face en mm, ligne du tableau,
#  K_Zb et K_Zv selon la face étroite (38 à 64, 89 à 102, 114 ou plus), K_Zt)
# None = « — » au tableau : combinaison impossible (la face étroite ne dépasse pas la grande face).
# Issue #45 : une grande face absente du tableau prend la ligne supérieure (ex. 143 mm -> « 184 à 191 »).
TABLEAU_6_13: tuple[tuple[float, str, tuple[float | None, float | None, float | None], float], ...] = (
    (38, "38", (1.7, None, None), 1.5),
    (64, "64", (1.7, None, None), 1.5),
    (89, "89", (1.7, 1.7, None), 1.5),
    (114, "114", (1.5, 1.6, 1.3), 1.4),
    (140, "140", (1.4, 1.5, 1.3), 1.3),
    (191, "184 à 191", (1.2, 1.3, 1.3), 1.2),
    (241, "235 à 241", (1.1, 1.2, 1.2), 1.1),
    (292, "286 à 292", (1.0, 1.1, 1.1), 1.0),
    (343, "337 à 343", (0.9, 1.0, 1.0), 0.9),
    (math.inf, "387 ou plus", (0.8, 0.9, 0.9), 0.8),
)
# Colonnes de la face étroite du tableau 6.13, mm (bornes incluses)
COLONNES_6_13: tuple[tuple[float, float], ...] = ((38, 64), (89, 102), (114, math.inf))


def K_S(propriete: str, milieu_humide: bool = False, face_etroite: float = 38) -> float:
    """
    6.4.2 Coefficient de conditions d'utilisation, K_S (tableau 6.10).

    Args:
        propriete (str): Propriété (voir PROPRIETES).
        milieu_humide (bool, optional): Utilisation en milieu humide. Default to False.
        face_etroite (float, optional): Face étroite du bois de sciage, mm. Default to 38 mm.

    Returns:
        float: K_S (K_Sb, K_Sf, K_Sv, K_Sc, K_Scp, K_St ou K_SE).
    """
    _verifier_propriete(propriete)
    _, sec, humide_89_ou_moins, humide_plus_de_89 = TABLEAU_6_10[propriete]
    if not milieu_humide:
        return sec
    return humide_89_ou_moins if face_etroite <= 89 else humide_plus_de_89


def K_T(
    propriete: str,
    traite: bool = False,
    incise: bool = False,
    epaisseur: float = 38,
    milieu_humide: bool = False,
) -> float:
    """
    6.4.3.1 Coefficient de traitement, K_T (tableau 6.11).

    Bois non traité, ou traité et non incisé : 1,00. Bois traité d'au plus 89 mm (épaisseur, « of
    thickness 89 mm or less »), incisé : module d'élasticité 0,90 (sec) ou 0,95 (humide) ; autres
    propriétés 0,75 (sec) ou 0,85 (humide). Bois ignifugé : voir 6.4.3.2 (non couvert).

    Args:
        propriete (str): Propriété (voir PROPRIETES).
        traite (bool, optional): Bois traité. Default to False.
        incise (bool, optional): Bois incisé. Default to False.
        epaisseur (float, optional): Épaisseur (face étroite), mm. Default to 38 mm.
        milieu_humide (bool, optional): Utilisation en milieu humide. Default to False.

    Returns:
        float: K_T.
    """
    _verifier_propriete(propriete)
    if not (traite and incise and epaisseur <= EPAISSEUR_MAXIMALE_INCISEE):
        return 1.00
    valeurs = (
        TABLEAU_6_11_MODULE_D_ELASTICITE
        if propriete == MODULE_D_ELASTICITE
        else TABLEAU_6_11_AUTRES_PROPRIETES
    )
    return valeurs[1] if milieu_humide else valeurs[0]


def cas_de_systeme(
    espacement_610_mm_ou_moins: bool = False,
    revetement_conforme_6_4_4_2: bool = False,
    poutre_composee: bool = False,
) -> str | None:
    """
    6.4.4 Cas du coefficient de système (tableau 6.12).

    6.4.4.3 et issue #7 : une poutre composée prend toujours la colonne « Poutres composées ».
    6.4.4.2 : cas 2 si le cas 1 est respecté et que le revêtement satisfait a) et b).
    6.4.4.1 : cas 1 si au moins trois éléments parallèles espacés d'au plus 610 mm.

    Args:
        espacement_610_mm_ou_moins (bool, optional): Conditions de 6.4.4.1 (au moins trois éléments
            essentiellement parallèles, espacement <= 610 mm). Default to False.
        revetement_conforme_6_4_4_2 (bool, optional): Revêtement et fixation selon 6.4.4.2 a) et b).
            Default to False.
        poutre_composee (bool, optional): Poutre composée de deux éléments ou plus (6.4.4.3).
            Default to False.

    Returns:
        str | None: CAS_1, CAS_2, POUTRES_COMPOSEES, ou None (aucun : K_H = 1,00).
    """
    if poutre_composee:
        return POUTRES_COMPOSEES
    if espacement_610_mm_ou_moins and revetement_conforme_6_4_4_2:
        return CAS_2
    if espacement_610_mm_ou_moins:
        return CAS_1
    return None


def K_H(propriete: str, cas: str | None = None, msr: bool = False) -> float:
    """
    6.4.4 Coefficient de système, K_H (tableau 6.12).

    Args:
        propriete (str): Propriété (voir PROPRIETES).
        cas (str | None, optional): CAS_1, CAS_2, POUTRES_COMPOSEES ou None (voir cas_de_systeme).
            Default to None (K_H = 1,00).
        msr (bool, optional): Bois MSR (sous-colonne MSR du cas 2). Default to False.

    Returns:
        float: K_H.
    """
    _verifier_propriete(propriete)
    if cas is None:
        return 1.00
    colonnes = TABLEAU_6_12.get(propriete, AUTRE_PROPRIETE_K_H)
    if cas == CAS_1:
        return colonnes[0]
    if cas == CAS_2:
        return colonnes[2] if msr else colonnes[1]
    if cas == POUTRES_COMPOSEES:
        return colonnes[3]
    raise ValueError(f"Cas de système inconnu : {cas!r} (tableau 6.12).")


def _ligne(grande_face: float) -> tuple[float, str, tuple[float | None, ...], float]:
    for ligne in TABLEAU_6_13:
        if grande_face <= ligne[0]:
            return ligne
    raise AssertionError("TABLEAU_6_13 se termine par une borne infinie.")


def ligne_du_tableau_6_13(grande_face: float) -> str:
    """
    Tableau 6.13 : ligne utilisée pour une grande face réelle, mm.

    Grande face absente du tableau : ligne de la dimension supérieure (issue #45).
    """
    return _ligne(grande_face)[1]


def colonnes_du_tableau_6_13(face_etroite: float) -> tuple[int, ...]:
    """
    Tableau 6.13 : colonne(s) de la face étroite réelle, mm (0 : 38 à 64 ; 1 : 89 à 102 ; 2 : 114 ou plus).

    Face étroite entre deux colonnes (65 à 88 mm, 103 à 113 mm) : les deux colonnes voisines ; K_Z prend
    la plus petite des deux valeurs (issue #45).
    """
    for i, (minimum, maximum) in enumerate(COLONNES_6_13):
        if minimum <= face_etroite <= maximum:
            return (i,)
        if face_etroite < minimum:
            return (i - 1, i) if i > 0 else (i,)
    raise AssertionError("COLONNES_6_13 se termine par une borne infinie.")


def K_Z(propriete: str, b: float, d: float, categorie: str) -> float:
    """
    6.4.5 Coefficient de dimensions, K_Z (tableau 6.13).

    6.4.5.1 Bois classé visuellement : K_Zb, K_Zv et K_Zt du tableau 6.13 ; autres propriétés 1,0.
    6.4.5.2 Charpente légère : K_Z = 1,00.
    6.4.5.3 MSR et MEL : K_Z = 1,00, sauf K_Zv selon le tableau 6.13.
    Dimensions réelles absentes du tableau : ligne supérieure, et plus petite des deux colonnes voisines
    (issue #45).
    K_Zc (6.5.5.2.4) et K_Zcp (6.5.6.4) sont calculés à leurs articles.

    Args:
        propriete (str): Propriété (voir PROPRIETES), sauf la compression.
        b (float): Largeur de l'élément, mm.
        d (float): Hauteur de l'élément, mm.
        categorie (str): Code de la catégorie (voir art_6_2_materiaux).

    Returns:
        float: K_Z (K_Zb, K_Zv, K_Zt, ou 1,0 pour les autres propriétés).

    Raises:
        ValueError: Pour la compression (voir K_Zc en 6.5.5.2.4 et K_Zcp en 6.5.6.4).
    """
    _verifier_propriete(propriete)
    if propriete in (COMPRESSION_PARALLELE, COMPRESSION_PERPENDICULAIRE):
        raise ValueError(
            "K_Z en compression : voir K_Zc (6.5.5.2.4) et K_Zcp (6.5.6.4), tableau 6.13."
        )
    if propriete not in (FLEXION, CISAILLEMENT_LONGITUDINAL, TRACTION_PARALLELE):
        return 1.0  # Tableau 6.13 : « Autre propriété »
    if categorie == "Light":
        return 1.0  # 6.4.5.2
    if categorie in ("MSR", "MEL") and propriete != CISAILLEMENT_LONGITUDINAL:
        return 1.0  # 6.4.5.3

    face_etroite, grande_face = min(b, d), max(b, d)
    _, _, flexion_cisaillement, traction = _ligne(grande_face)
    if propriete == TRACTION_PARALLELE:
        return traction
    valeurs = [flexion_cisaillement[c] for c in colonnes_du_tableau_6_13(face_etroite)]
    valeurs = [v for v in valeurs if v is not None]  # « — » : combinaison impossible
    if not valeurs:
        raise AssertionError("Combinaison absente du tableau 6.13 (« — »).")
    return min(valeurs)
