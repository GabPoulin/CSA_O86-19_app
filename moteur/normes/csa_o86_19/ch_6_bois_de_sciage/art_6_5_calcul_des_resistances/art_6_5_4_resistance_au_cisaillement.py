"""
CSA O86:19 - 6.5.4 Résistance au cisaillement (p. 65-68).

    6.5.4.1 Généralités : V_r pour tous les éléments ; F_r en plus pour une entaille sur la rive en
        traction
    6.5.4.3 Résistance au cisaillement (V_r, F_v)
    6.5.4.4.1 Résistance au cisaillement par fissuration à l'entaille (F_r, F_f, f_f = 0,50 MPa)
    6.5.4.4.2 Coefficient d'entaille, K_N (alpha, eta ; d_n <= 0,25 d). Tableau 6.14 : K_N racine(d).

6.5.4.2 (charges près des appuis) touche le calcul de la charge pondérée V_f, pas les résistances.
"""

from moteur.commun.nombres import cs
from moteur.commun.registre import enregistrer
from moteur.commun.resultat import Donnee, Etape, Resultat
from moteur.normes.csa_o86_19 import NORME
from moteur.normes.csa_o86_19.ch_5_conception_generale.art_5_1_calculs_aux_etats_limites import (
    verifier_etat_limite_ultime,
)

EDITION = "csa_o86_19"
PHI = 0.9  # 6.5.4.3 et 6.5.4.4.1
f_f = 0.50  # MPa, 6.5.4.4.1 : pour tous les éléments en bois de sciage
PROFONDEUR_MAXIMALE_ENTAILLE = 0.25  # d_n <= 0,25 d (6.5.4.4.2)


# FONCTIONS SIMPLES (dans l'ordre de la norme)
def F_v(f_v: float, K_D: float = 1, K_H: float = 1, K_Sv: float = 1, K_T: float = 1) -> float:
    """
    6.5.4.3 Résistance corrigée en cisaillement, F_v.

    F_v = f_v (K_D K_H K_Sv K_T)

    Args:
        f_v (float): Résistance prévue en cisaillement, MPa (6.3).
        K_D, K_H, K_Sv, K_T (float, optional): Coefficients de correction. Default to 1.

    Returns:
        float: F_v, MPa.
    """
    return f_v * (K_D * K_H * K_Sv * K_T)


def V_r(F_v: float, A_n: float, K_Zv: float = 1) -> float:
    """
    6.5.4.3 Résistance pondérée au cisaillement, V_r.

    V_r = phi F_v (2 A_n / 3) K_Zv, phi = 0,9

    Args:
        F_v (float): Résistance corrigée en cisaillement, MPa.
        A_n (float): Aire de la section transversale nette, mm² (5.3.8).
        K_Zv (float, optional): Coefficient de dimensions en cisaillement (6.4.5). Default to 1.

    Returns:
        float: V_r, N.
    """
    return PHI * F_v * (2 * A_n / 3) * K_Zv


def F_f(K_D: float = 1, K_H: float = 1, K_Sf: float = 1, K_T: float = 1) -> float:
    """
    6.5.4.4.1 Résistance corrigée en cisaillement par fissuration à une entaille, F_f.

    F_f = f_f (K_D K_H K_Sf K_T), f_f = 0,50 MPa pour tous les éléments en bois de sciage

    Args:
        K_D, K_H, K_Sf, K_T (float, optional): Coefficients de correction. Default to 1.

    Returns:
        float: F_f, MPa.
    """
    return f_f * (K_D * K_H * K_Sf * K_T)


def F_r(F_f: float, A_g: float, K_N: float) -> float:
    """
    6.5.4.4.1 Résistance pondérée au cisaillement par fissuration à l'entaille, F_r.

    F_r = phi F_f A_g K_N, phi = 0,9

    Args:
        F_f (float): Résistance corrigée en cisaillement par fissuration, MPa.
        A_g (float): Aire brute de la section transversale, b x d, mm².
        K_N (float): Coefficient d'entaille (6.5.4.4.2).

    Returns:
        float: F_r, N.
    """
    return PHI * F_f * A_g * K_N


def alpha(d_n: float, d: float) -> float:
    """
    6.5.4.4.2 alpha = 1 - (d_n / d), avec d_n <= 0,25 d.

    Args:
        d_n (float): Profondeur de l'entaille, perpendiculaire à l'axe de l'élément (figure 6.1), mm.
        d (float): Hauteur de la section transversale, mm.

    Returns:
        float: alpha.

    Raises:
        ValueError: Si d_n n'est pas positive ou si d_n > 0,25 d.
    """
    if d_n <= 0:
        raise ValueError("La profondeur de l'entaille d_n doit être positive (6.5.4.4.2).")
    if d_n > PROFONDEUR_MAXIMALE_ENTAILLE * d:
        raise ValueError(
            f"La profondeur de l'entaille (dn = {d_n:g} mm) ne doit pas dépasser 0.25 d = "
            f"{PROFONDEUR_MAXIMALE_ENTAILLE * d:g} mm (6.5.4.4.2)."
        )
    return 1 - d_n / d


def eta(e: float, d: float) -> float:
    """
    6.5.4.4.2 eta = e / d.

    Args:
        e (float): Longueur de l'entaille, parallèle à l'axe de l'élément, du centre de l'appui le plus
            rapproché au coin rentrant de l'entaille (figure 6.1), mm.
        d (float): Hauteur de la section transversale, mm.

    Returns:
        float: eta.

    Raises:
        ValueError: Si e n'est pas positive.
    """
    if e <= 0:
        raise ValueError("La longueur de l'entaille e doit être positive (6.5.4.4.2).")
    return e / d


def K_N(d: float, alpha: float, eta: float) -> float:
    """
    6.5.4.4.2 Coefficient d'entaille, K_N, d'une section transversale rectangulaire.

    K_N = [0,006 d (1,6 (1/alpha - 1) + eta² (1/alpha³ - 1))]^(-1/2)

    Args:
        d (float): Hauteur de la section transversale, mm.
        alpha (float): 1 - d_n / d (voir alpha()).
        eta (float): e / d (voir eta()).

    Returns:
        float: K_N.
    """
    # Parenthèses explicites : (1 / alpha) - 1 et (1 / (alpha**3)) - 1 ; le « - 1 » n'est pas dans
    # l'exposant ni au dénominateur.
    terme_1 = 1.6 * ((1 / alpha) - 1)
    terme_2 = (eta**2) * ((1 / (alpha**3)) - 1)
    return (0.006 * d * (terme_1 + terme_2)) ** (-1 / 2)


# VÉRIFICATIONS
@enregistrer(EDITION, "6.5.4.3", "Résistance au cisaillement")
def verifier_cisaillement(
    b: float,
    d: float,
    f_v: float,
    plis: int = 1,
    d_n: float = 0,
    K_D: float = 1,
    K_H: float = 1,
    K_Sv: float = 1,
    K_T: float = 1,
    K_Zv: float = 1,
    V_f: float | None = None,
    source_resistances: str = "Tableaux 6.4 à 6.9",
    source_K_D: str = "Tableau 5.1",
) -> Resultat:
    """
    6.5.4.3 Résistance pondérée au cisaillement d'un élément en bois de sciage.

    Args:
        b (float): Largeur d'un pli, mm.
        d (float): Hauteur de l'élément, mm.
        f_v (float): Résistance prévue en cisaillement, MPa.
        plis (int, optional): Nombre de plis. Default to 1.
        d_n (float, optional): Profondeur d'une entaille, mm (aire nette A_n, 5.3.8). Default to 0.
        K_D, K_H, K_Sv, K_T, K_Zv (float, optional): Coefficients de correction. Default to 1.
        V_f (float | None, optional): Effort tranchant pondéré, kN. Default to None.
        source_resistances (str, optional): Tableau des résistances prévues (6.3), pour la note de
            calcul (voir art_6_3.tableau_des_resistances()). Default to "Tableaux 6.4 à 6.9".
        source_K_D (str, optional): Source de K_D pour la note de calcul : « Tableau 5.1 », ou
            « 5.3.2.2 » si K_D est calculé à partir des charges. Default to "Tableau 5.1".

    Returns:
        Resultat: Trace du calcul. V_r en N ; vérification en kN.
    """
    r = Resultat(NORME, "6.5.4.3", "Résistance au cisaillement", "poutre")
    for donnee in (
        Donnee("b", "Largeur d'un pli", b, "mm", "dimension"),
        Donnee("d", "Hauteur de l'élément", d, "mm", "dimension"),
        Donnee("n", "Nombre de plis", plis),
        Donnee("d_n", "Profondeur de l'entaille", d_n, "mm", "dimension"),
        Donnee("f_v", "Résistance prévue en cisaillement", f_v, "MPa", "contrainte", source_resistances),
        Donnee("K_D", "Coefficient de durée d'application de la charge", K_D, source=source_K_D),
        Donnee("K_H", "Coefficient de système", K_H, source="Tableau 6.12"),
        Donnee("K_{Sv}", "Coefficient de conditions d'utilisation (cisaillement)", K_Sv,
               source="Tableau 6.10"),
        Donnee("K_T", "Coefficient de traitement", K_T, source="Tableau 6.11"),
        Donnee("K_{Zv}", "Coefficient de dimensions (cisaillement)", K_Zv, source="Tableau 6.13"),
    ):
        r.ajouter_donnee(donnee)

    f_v_corrige = r.ajouter_etape(Etape(
        "6.5.4.3", "Résistance corrigée en cisaillement", "F_v",
        r"F_v = f_v \, (K_D \, K_H \, K_{Sv} \, K_T)",
        rf"{cs(f_v)} \times ({cs(K_D)} \times {cs(K_H)} \times {cs(K_Sv)} \times {cs(K_T)})",
        F_v(f_v, K_D, K_H, K_Sv, K_T), "MPa", "contrainte",
    ))
    a_n = r.ajouter_etape(Etape(
        "5.3.8", "Aire de la section transversale nette", "A_n",
        r"A_n = n \, b \, (d - d_n)", rf"{plis} \times {cs(b)} \times ({cs(d)} - {cs(d_n)})",
        plis * b * (d - d_n), "mm²",
    ))
    v_r = r.ajouter_etape(Etape(
        "6.5.4.3", "Résistance pondérée au cisaillement", "V_r",
        r"V_r = \phi \, F_v \, \frac{2 \, A_n}{3} \, K_{Zv}",
        rf"0.9 \times {cs(f_v_corrige)} \times \frac{{2 \times {cs(a_n)}}}{{3}} \times {cs(K_Zv)}",
        V_r(f_v_corrige, a_n, K_Zv), "N",
    ))

    if V_f is not None:
        r.verification = verifier_etat_limite_ultime(V_f, v_r / 1000, "V_f", "V_r", "kN", "force")

    return r


@enregistrer(EDITION, "6.5.4.4", "Résistance au cisaillement par fissuration à l'entaille")
def verifier_cisaillement_par_fissuration(
    b: float,
    d: float,
    d_n: float,
    e: float,
    plis: int = 1,
    K_D: float = 1,
    K_H: float = 1,
    K_Sf: float = 1,
    K_T: float = 1,
    V_f: float | None = None,
    source_K_D: str = "Tableau 5.1",
) -> Resultat:
    """
    6.5.4.4 Résistance pondérée au cisaillement par fissuration d'un élément entaillé à l'appui, à
    la rive en traction.

    Args:
        b (float): Largeur d'un pli, mm.
        d (float): Hauteur de l'élément, mm.
        d_n (float): Profondeur de l'entaille (<= 0,25 d), mm.
        e (float): Longueur de l'entaille (figure 6.1), mm.
        plis (int, optional): Nombre de plis. Default to 1.
        K_D, K_H, K_Sf, K_T (float, optional): Coefficients de correction. Default to 1.
        V_f (float | None, optional): Effort tranchant pondéré à l'appui, kN (6.5.4.4.3).
            Default to None.
        source_K_D (str, optional): Source de K_D pour la note de calcul : « Tableau 5.1 », ou
            « 5.3.2.2 » si K_D est calculé à partir des charges. Default to "Tableau 5.1".

    Returns:
        Resultat: Trace du calcul. F_r en N ; vérification en kN.

    Raises:
        ValueError: Si d_n ou e n'est pas positive, ou si d_n > 0,25 d.
    """
    r = Resultat(NORME, "6.5.4.4", "Résistance au cisaillement par fissuration à l'entaille", "entaille")
    for donnee in (
        Donnee("b", "Largeur d'un pli", b, "mm", "dimension"),
        Donnee("d", "Hauteur de l'élément", d, "mm", "dimension"),
        Donnee("n", "Nombre de plis", plis),
        Donnee("d_n", "Profondeur de l'entaille", d_n, "mm", "dimension"),
        Donnee("e", "Longueur de l'entaille", e, "mm", "dimension"),
        Donnee("K_D", "Coefficient de durée d'application de la charge", K_D, source=source_K_D),
        Donnee("K_H", "Coefficient de système", K_H, source="Tableau 6.12"),
        Donnee("K_{Sf}", "Coefficient de conditions d'utilisation (cisaillement par fissuration)",
               K_Sf, source="Tableau 6.10"),
        Donnee("K_T", "Coefficient de traitement", K_T, source="Tableau 6.11"),
    ):
        r.ajouter_donnee(donnee)

    f_f_corrige = r.ajouter_etape(Etape(
        "6.5.4.4.1", "Résistance corrigée en cisaillement par fissuration", "F_f",
        r"F_f = f_f \, (K_D \, K_H \, K_{Sf} \, K_T)",
        rf"0.50 \times ({cs(K_D)} \times {cs(K_H)} \times {cs(K_Sf)} \times {cs(K_T)})",
        F_f(K_D, K_H, K_Sf, K_T), "MPa", "contrainte",
    ))
    a = r.ajouter_etape(Etape(
        "6.5.4.4.2", "Rapport de la hauteur nette", r"\alpha",
        r"\alpha = 1 - \frac{d_n}{d}", rf"1 - \frac{{{cs(d_n)}}}{{{cs(d)}}}", alpha(d_n, d),
    ))
    rapport_eta = r.ajouter_etape(Etape(
        "6.5.4.4.2", "Rapport de la longueur de l'entaille", r"\eta",
        r"\eta = \frac{e}{d}", rf"\frac{{{cs(e)}}}{{{cs(d)}}}", eta(e, d),
    ))
    k_n = r.ajouter_etape(Etape(
        "6.5.4.4.2", "Coefficient d'entaille", "K_N",
        r"K_N = \left[0.006 \, d \left(1.6 \left(\frac{1}{\alpha} - 1\right) + \eta^2 "
        r"\left(\frac{1}{\alpha^3} - 1\right)\right)\right]^{-1/2}",
        rf"\left[0.006 \times {cs(d)} \left(1.6 \left(\frac{{1}}{{{cs(a)}}} - 1\right) + {cs(rapport_eta)}^2 "
        rf"\left(\frac{{1}}{{{cs(a)}^3}} - 1\right)\right)\right]^{{-1/2}}",
        K_N(d, a, rapport_eta),
    ))
    a_g = r.ajouter_etape(Etape(
        "6.5.4.4.1", "Aire brute de la section transversale", "A_g",
        r"A_g = n \, b \, d", rf"{plis} \times {cs(b)} \times {cs(d)}", plis * b * d, "mm²",
    ))
    f_r = r.ajouter_etape(Etape(
        "6.5.4.4.1", "Résistance pondérée au cisaillement par fissuration", "F_r",
        r"F_r = \phi \, F_f \, A_g \, K_N",
        rf"0.9 \times {cs(f_f_corrige)} \times {cs(a_g)} \times {cs(k_n)}",
        F_r(f_f_corrige, a_g, k_n), "N",
    ))

    if V_f is not None:
        r.verification = verifier_etat_limite_ultime(V_f, f_r / 1000, "V_f", "F_r", "kN", "force")

    return r

