"""
CSA O86:19 - 6.5.5 Résistance à la compression parallèle au fil (p. 68-69).

    6.5.5.1 Longueur effective, L_e
    6.5.5.2.1 Généralités : P_r vérifiée pour les deux axes
    6.5.5.2.2 Élancement, C_C
    6.5.5.2.4 Résistance pondérée à la compression sous charge axiale (P_r, F_c, K_Zc)
    6.5.5.2.5 Coefficient d'élancement, K_C

Interprétations validées avec l'utilisateur (CLAUDE.md) :
    - K_Zc : L = longueur de l'élément (pas L_e ni la longueur entre appuis latéraux).
    - K_T dans K_C : K_T des « autres propriétés » (tableau 6.11), le même que dans F_c.
    - L_e = K_e L (6.5.5.1), avec L = entraxe des appuis latéraux dans le plan de flambage (note du
      tableau A.4). K_e est entré en chiffre ; le tableau A.4 (annexe A, informative) le donne selon
      les conditions d'appui (art_A_6_5_5_1_coefficient_de_longueur_effective.py).
"""

from moteur.commun.nombres import cs
from moteur.commun.registre import enregistrer
from moteur.commun.resultat import Donnee, Etape, Resultat
from moteur.normes.csa_o86_19.ch_5_conception_generale.art_5_1_calculs_aux_etats_limites import (
    verifier_etat_limite_ultime,
)
from moteur.normes.csa_o86_19 import NORME

EDITION = "csa_o86_19"


# FONCTIONS SIMPLES (dans l'ordre de la norme)
def L_e(K_e: float, L: float) -> float:
    """
    6.5.5.1 Longueur effective, L_e.

    L_e = K_e L

    Args:
        K_e (float): Coefficient de longueur effective (valeurs recommandées : tableau A.4).
        L (float): Entraxe des appuis latéraux de l'élément dans le plan de flambage considéré, mm
            (note du tableau A.4).

    Returns:
        float: L_e, mm.

    Raises:
        ValueError: Si une valeur n'est pas positive.
    """
    if K_e <= 0 or L <= 0:
        raise ValueError("K_e et la longueur entre les appuis latéraux doivent être positifs (6.5.5.1).")

    return K_e * L


def C_C(L_e: float, dimension: float) -> float:
    """
    6.5.5.2.2 Élancement, C_C.

    C_C = longueur effective associée à la dimension / dimension, <= 50, selon les deux axes.

    Args:
        L_e (float): Longueur effective associée à la dimension, mm.
        dimension (float): Largeur b ou hauteur d de l'élément (direction du flambage), mm.

    Returns:
        float: C_C.

    Raises:
        ValueError: Si une valeur n'est pas positive ou si C_C > 50.
    """
    if L_e <= 0 or dimension <= 0:
        raise ValueError("La longueur effective et la dimension doivent être positives (6.5.5.2.2).")

    c_c = L_e / dimension
    if c_c > 50:
        raise ValueError(f"L'élancement (Cc = {c_c:.2f}) ne doit pas dépasser 50 (6.5.5.2.2).")

    return c_c


def P_r(F_c: float, A: float, K_Zc: float, K_C: float) -> float:
    """
    6.5.5.2.4 Résistance pondérée à la compression sous charge axiale, P_r.

    P_r = phi F_c A K_Zc K_C, phi = 0,8

    Args:
        F_c (float): F_c = f_c (K_D K_H K_Sc K_T), MPa.
        A (float): Aire de la section transversale, mm².
        K_Zc (float): Coefficient de dimensions en compression.
        K_C (float): Coefficient d'élancement.

    Returns:
        float: P_r, N.
    """
    phi = 0.8
    return phi * F_c * A * K_Zc * K_C


def F_c(f_c: float, K_D: float = 1, K_H: float = 1, K_Sc: float = 1, K_T: float = 1) -> float:
    """
    6.5.5.2.4 Résistance corrigée en compression parallèle au fil, F_c.

    F_c = f_c (K_D K_H K_Sc K_T)

    Args:
        f_c (float): Résistance prévue en compression parallèle au fil, MPa (tableaux 6.4 à 6.9).
        K_D (float, optional): Coefficient de durée d'application de la charge. Default to 1.
        K_H (float, optional): Coefficient de système. Default to 1.
        K_Sc (float, optional): Coefficient de conditions d'utilisation (compression parallèle).
            Default to 1.
        K_T (float, optional): Coefficient de traitement (« autres propriétés »). Default to 1.

    Returns:
        float: F_c, MPa.
    """
    return f_c * (K_D * K_H * K_Sc * K_T)


def K_Zc(d: float, L: float) -> float:
    """
    6.5.5.2.4 Coefficient de dimensions en compression, K_Zc.

    K_Zc = 6,3 (d L)^-0,13 <= 1,3

    Args:
        d (float): Dimension dans la direction du flambage (grande face ou face étroite), mm.
        L (float): Longueur de l'élément, mm (et non la longueur effective ; voir A.6.5.5.2.4 b)).

    Returns:
        float: K_Zc.

    Raises:
        ValueError: Si une valeur n'est pas positive.
    """
    if d <= 0 or L <= 0:
        raise ValueError("La dimension et la longueur doivent être positives (6.5.5.2.4).")

    return min(6.3 * (d * L) ** -0.13, 1.3)


def K_C(
    F_c: float, K_Zc: float, C_C: float, E_05: float, K_SE: float = 1, K_T: float = 1
) -> float:
    """
    6.5.5.2.5 Coefficient d'élancement, K_C.

    K_C = [1,0 + (F_c K_Zc C_C^3) / (35 E_05 K_SE K_T)]^-1

    Args:
        F_c (float): F_c = f_c (K_D K_H K_Sc K_T), MPa.
        K_Zc (float): Coefficient de dimensions en compression.
        C_C (float): Élancement selon l'axe considéré.
        E_05 (float): Module d'élasticité pour les calculs des éléments en compression, MPa
            (0,82E pour le MSR, 0,75E pour le MEL, tableaux 6.4 à 6.7 pour le bois classé
            visuellement).
        K_SE (float, optional): Coefficient de conditions d'utilisation relatif au module
            d'élasticité. Default to 1.
        K_T (float, optional): Coefficient de traitement des « autres propriétés », le même que
            dans F_c. Default to 1.

    Returns:
        float: K_C.
    """
    return (1 + (F_c * K_Zc * C_C**3) / (35 * E_05 * K_SE * K_T)) ** -1


# VÉRIFICATION
@enregistrer(EDITION, "6.5.5", "Résistance à la compression parallèle au fil")
def verifier_compression_parallele_au_fil(
    b: float,
    d: float,
    L: float,
    L_b: float,
    L_d: float,
    f_c: float,
    E_05: float,
    K_e_b: float = 1,
    K_e_d: float = 1,
    K_D: float = 1,
    K_H: float = 1,
    K_Sc: float = 1,
    K_T: float = 1,
    K_SE: float = 1,
    P_f: float | None = None,
    source_resistances: str = "Tableaux 6.4 à 6.9",
) -> Resultat:
    """
    6.5.5.2 Résistance pondérée à la compression parallèle au fil d'un élément simple, selon les
    deux axes (6.5.5.2.1).

    Args:
        b (float): Largeur de l'élément, mm.
        d (float): Hauteur de l'élément, mm.
        L (float): Longueur de l'élément, mm (pour K_Zc).
        L_b (float): Entraxe des appuis latéraux pour le flambage selon b, mm (pour L_e).
        L_d (float): Entraxe des appuis latéraux pour le flambage selon d, mm (pour L_e).
        f_c (float): Résistance prévue en compression parallèle au fil, MPa.
        E_05 (float): Module d'élasticité pour les éléments en compression, MPa.
        K_e_b, K_e_d (float, optional): Coefficients de longueur effective selon b et selon d
            (tableau A.4). Default to 1.
        K_D, K_H, K_Sc, K_T, K_SE (float, optional): Coefficients de correction. Default to 1.
        P_f (float | None, optional): Charge de compression axiale pondérée, kN. Default to None.
        source_resistances (str, optional): Tableau des résistances prévues (6.3), pour la note de
            calcul (voir art_6_3.tableau_des_resistances()). Default to "Tableaux 6.4 à 6.9".

    Returns:
        Resultat: Trace du calcul. P_r de chaque axe en N ; vérification en kN.

    Raises:
        ValueError: Si une valeur est invalide ou si C_C > 50.
    """
    r = Resultat(NORME, "6.5.5", "Résistance à la compression parallèle au fil", "colonne")
    for donnee in (
        Donnee("b", "Largeur de l'élément", b, "mm", "dimension"),
        Donnee("d", "Hauteur de l'élément", d, "mm", "dimension"),
        Donnee("L", "Longueur de l'élément", L, "mm", "longueur"),
        Donnee("L_b", "Entraxe des appuis latéraux (flambage selon b)", L_b, "mm", "longueur"),
        Donnee("L_d", "Entraxe des appuis latéraux (flambage selon d)", L_d, "mm", "longueur"),
        Donnee("K_{e,b}", "Coefficient de longueur effective selon b", K_e_b, source="Tableau A.4"),
        Donnee("K_{e,d}", "Coefficient de longueur effective selon d", K_e_d, source="Tableau A.4"),
        Donnee("f_c", "Résistance prévue en compression parallèle au fil", f_c, "MPa", "contrainte",
               source_resistances),
        Donnee("E_{05}", "Module d'élasticité pour les éléments en compression", E_05, "MPa",
               "contrainte", source_resistances),
        Donnee("K_D", "Coefficient de durée d'application de la charge", K_D, source="Tableau 5.1"),
        Donnee("K_H", "Coefficient de système", K_H, source="Tableau 6.12"),
        Donnee("K_{Sc}", "Coefficient de conditions d'utilisation (compression)", K_Sc,
               source="Tableau 6.10"),
        Donnee("K_T", "Coefficient de traitement", K_T, source="Tableau 6.11"),
        Donnee("K_{SE}", "Coefficient de conditions d'utilisation (module d'élasticité)", K_SE,
               source="Tableau 6.10"),
    ):
        r.ajouter_donnee(donnee)

    f_c_corrige = r.ajouter_etape(Etape(
        "6.5.5.2.4", "Résistance corrigée en compression parallèle au fil", "F_c",
        r"F_c = f_c \, (K_D \, K_H \, K_{Sc} \, K_T)",
        rf"{cs(f_c)} \times ({cs(K_D)} \times {cs(K_H)} \times {cs(K_Sc)} \times {cs(K_T)})",
        F_c(f_c, K_D, K_H, K_Sc, K_T), "MPa", "contrainte",
    ))
    A = b * d

    resistances = []
    for axe, dimension, K_e, L_appuis in (("b", b, K_e_b, L_b), ("d", d, K_e_d, L_d)):
        l_e = r.ajouter_etape(Etape(
            "6.5.5.1", f"Longueur effective selon {axe}", f"L_{{e,{axe}}}",
            rf"L_{{e,{axe}}} = K_{{e,{axe}}} \, L_{axe}", rf"{cs(K_e)} \times {cs(L_appuis)}",
            L_e(K_e, L_appuis), "mm", "longueur",
        ))
        c_c = r.ajouter_etape(Etape(
            "6.5.5.2.2", f"Élancement selon {axe}", f"C_{{C,{axe}}}",
            rf"C_C = L_{{e,{axe}}} / {axe} \leq 50", rf"{cs(l_e)} / {cs(dimension)}",
            C_C(l_e, dimension),
        ))
        k_zc = r.ajouter_etape(Etape(
            "6.5.5.2.4", f"Coefficient de dimensions selon {axe}", f"K_{{Zc,{axe}}}",
            rf"K_{{Zc}} = 6.3 \, ({axe} \, L)^{{-0.13}} \leq 1.3",
            rf"6.3 \times ({cs(dimension)} \times {cs(L)})^{{-0.13}}",
            K_Zc(dimension, L),
        ))
        k_c = r.ajouter_etape(Etape(
            "6.5.5.2.5", f"Coefficient d'élancement selon {axe}", f"K_{{C,{axe}}}",
            r"K_C = \left[1 + \frac{F_c \, K_{Zc} \, C_C^3}{35 \, E_{05} \, K_{SE} \, K_T}\right]^{-1}",
            rf"\left[1 + \frac{{{cs(f_c_corrige)} \times {cs(k_zc)} \times {cs(c_c)}^3}}"
            rf"{{35 \times {cs(E_05)} \times {cs(K_SE)} \times {cs(K_T)}}}\right]^{{-1}}",
            K_C(f_c_corrige, k_zc, c_c, E_05, K_SE, K_T),
        ))
        resistances.append(r.ajouter_etape(Etape(
            "6.5.5.2.4", f"Résistance pondérée selon {axe}", f"P_{{r,{axe}}}",
            r"P_r = \phi \, F_c \, A \, K_{Zc} \, K_C",
            rf"0.8 \times {cs(f_c_corrige)} \times {cs(A)} \times {cs(k_zc)} \times {cs(k_c)}",
            P_r(f_c_corrige, A, k_zc, k_c), "N",
        )))

    p_r = r.ajouter_etape(Etape(
        "6.5.5.2.1", "Résistance pondérée (plus petite des deux)", "P_r",
        r"P_r = \min(P_{r,b} \, ; \, P_{r,d})",
        rf"\min({cs(resistances[0])} \, ; \, {cs(resistances[1])})",
        min(resistances), "N",
    ))

    if P_f is not None:
        r.verification = verifier_etat_limite_ultime(P_f, p_r / 1000, "P_f", "P_r", "kN", "force")

    return r
