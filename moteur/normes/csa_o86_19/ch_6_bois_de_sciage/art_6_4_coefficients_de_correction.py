"""
CSA O86:19 - 6.4 Coefficients de correction (p. 65-69).

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
    - K_Z pour une dimension absente du tableau 6.13 (ex. 165 ou 216 mm) : ligne de la dimension
      supérieure (conservateur).
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


# 6.4.2 Tableau 6.10 Coefficients de conditions d'utilisation, K_S (p. 67)
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

# 6.4.3 Tableau 6.11 Coefficient de traitement, K_T (p. 68), bois traité d'au plus 89 mm, incisé
# (milieu sec, milieu humide)
TABLEAU_6_11_MODULE_D_ELASTICITE = (0.90, 0.95)
TABLEAU_6_11_AUTRES_PROPRIETES = (0.75, 0.85)
EPAISSEUR_MAXIMALE_INCISEE = 89  # mm, tableau 6.11 : « bois traité d'au plus 89 mm, incisé »

# 6.4.4 Tableau 6.12 Coefficients de système, K_H (p. 68)
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

# 6.4.5 Tableau 6.13 Coefficient de dimensions, K_Z, bois classé visuellement (p. 69)
# (borne supérieure exclue de la grande face en mm, ligne du tableau,
#  K_Zb et K_Zv selon la face étroite (38 à 64, 89 à 102, 114 ou plus), K_Zt)
# Les lignes 38, 64 et 89 ont les mêmes valeurs (1,7 en flexion et cisaillement, 1,5 en traction).
# Bornes du code existant conservées pendant la migration (voir l'issue sur les dimensions vertes
# et brutes absentes du tableau).
TABLEAU_6_13: tuple[tuple[float, str, tuple[float, float, float], float], ...] = (
    (114, "38, 64 et 89", (1.7, 1.7, 1.7), 1.5),
    (140, "114", (1.5, 1.6, 1.3), 1.4),
    (159, "140", (1.4, 1.5, 1.3), 1.3),
    (210, "184 à 191", (1.2, 1.3, 1.3), 1.2),
    (286, "235 à 241", (1.1, 1.2, 1.2), 1.1),
    (337, "286 à 292", (1.0, 1.1, 1.1), 1.0),
    (362, "337 à 343", (0.9, 1.0, 1.0), 0.9),
    (math.inf, "387 ou plus", (0.8, 0.9, 0.9), 0.8),
)


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


def ligne_du_tableau_6_13(grande_face: float) -> str:
    """Tableau 6.13 : ligne (grande face, mm) utilisée pour une grande face donnée, mm."""
    for borne, ligne, _, _ in TABLEAU_6_13:
        if grande_face < borne:
            return ligne
    raise AssertionError("TABLEAU_6_13 se termine par une borne infinie.")


def K_Z(propriete: str, b: float, d: float, categorie: str) -> float:
    """
    6.4.5 Coefficient de dimensions, K_Z (tableau 6.13).

    6.4.5.1 Bois classé visuellement : K_Zb, K_Zv et K_Zt du tableau 6.13 ; autres propriétés 1,0.
    6.4.5.2 Charpente légère : K_Z = 1,00.
    6.4.5.3 MSR et MEL : K_Z = 1,00, sauf K_Zv selon le tableau 6.13.
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
    for borne, _, flexion_cisaillement, traction in TABLEAU_6_13:
        if grande_face < borne:
            if propriete == TRACTION_PARALLELE:
                return traction
            if face_etroite < 89:
                return flexion_cisaillement[0]
            if face_etroite < 114:
                return flexion_cisaillement[1]
            return flexion_cisaillement[2]
    raise AssertionError("TABLEAU_6_13 se termine par une borne infinie.")
