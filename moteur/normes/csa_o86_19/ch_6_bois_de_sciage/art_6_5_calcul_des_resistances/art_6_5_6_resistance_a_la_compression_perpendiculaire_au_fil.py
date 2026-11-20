"""
CSA O86:19 - 6.5.6 Résistance à la compression perpendiculaire au fil (p. 71-73).

    6.5.6.2 Effet de toutes les charges appliquées (Q_r, F_cp)
    6.5.6.3.1 Résistance pondérée sous les charges près d'un appui (Q'_r)
    6.5.6.3.2 Surfaces d'appui inégales sur les faces opposées (A'_b)
    6.5.6.4 Coefficient de dimensions pour l'appui, K_Zcp (tableau 6.15)
    6.5.6.5 Coefficient de longueur d'appui, K_B (tableau 6.16)

Décisions validées avec l'utilisateur :
    - K_B : formule de la note du tableau 6.16, plafonnée à 1,75 ; les conditions a) et b) de 6.5.6.5
      sont vérifiées pour chaque surface d'appui (y compris l'appui du bas).
    - Q'_r avec deux longueurs d'appui différentes : le plus petit des deux K_B.
    - K_Zcp appliqué automatiquement.
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
def Q_r(F_cp: float, A_b: float, K_B: float = 1, K_Zcp: float = 1) -> float:
    """
    6.5.6.2 Résistance pondérée à la compression perpendiculaire au fil, Q_r (toutes les charges).

    Q_r = phi F_cp A_b K_B K_Zcp, phi = 0,8

    Args:
        F_cp (float): F_cp = f_cp (K_D K_Scp K_T), MPa.
        A_b (float): Surface d'appui, mm².
        K_B (float, optional): Coefficient de longueur d'appui. Default to 1.
        K_Zcp (float, optional): Coefficient de dimensions pour l'appui. Default to 1.

    Returns:
        float: Q_r, N.
    """
    phi = 0.8
    return phi * F_cp * A_b * K_B * K_Zcp


def F_cp(f_cp: float, K_D: float = 1, K_Scp: float = 1, K_T: float = 1) -> float:
    """
    6.5.6.2 Résistance corrigée en compression perpendiculaire au fil, F_cp.

    F_cp = f_cp (K_D K_Scp K_T) (pas de K_H)

    Args:
        f_cp (float): Résistance prévue en compression perpendiculaire au fil, MPa.
        K_D (float, optional): Coefficient de durée d'application de la charge. Default to 1.
        K_Scp (float, optional): Coefficient de conditions d'utilisation. Default to 1.
        K_T (float, optional): Coefficient de traitement (« autres propriétés »). Default to 1.

    Returns:
        float: F_cp, MPa.
    """
    return f_cp * (K_D * K_Scp * K_T)


def Q_r_prime(F_cp: float, A_b_prime: float, K_B: float = 1, K_Zcp: float = 1) -> float:
    """
    6.5.6.3.1 Résistance pondérée Q'_r sous les seules charges appliquées à une distance du centre de
    l'appui inférieure ou égale à la hauteur de l'élément.

    Q'_r = (2/3) phi F_cp A'_b K_B K_Zcp, phi = 0,8

    Args:
        F_cp (float): F_cp = f_cp (K_D K_Scp K_T), MPa.
        A_b_prime (float): Surface d'appui moyenne A'_b, mm².
        K_B (float, optional): Coefficient de longueur d'appui (le plus petit des deux). Default to 1.
        K_Zcp (float, optional): Coefficient de dimensions pour l'appui. Default to 1.

    Returns:
        float: Q'_r, N.
    """
    phi = 0.8
    return (2 / 3) * phi * F_cp * A_b_prime * K_B * K_Zcp


def A_b_prime(b: float, L_b1: float, L_b2: float) -> float:
    """
    6.5.6.3.2 Surface d'appui moyenne, A'_b (surfaces d'appui inégales sur les faces opposées).

    A'_b = b (L_b1 + L_b2) / 2 <= 1,5 b L_b1, où L_b1 est la plus petite longueur d'appui.

    Args:
        b (float): Largeur d'appui moyenne (perpendiculaire au fil), mm.
        L_b1 (float): Longueur d'appui d'une face, mm.
        L_b2 (float): Longueur d'appui de la face opposée, mm.

    Returns:
        float: A'_b, mm².

    Raises:
        ValueError: Si une valeur n'est pas positive.
    """
    if b <= 0 or L_b1 <= 0 or L_b2 <= 0:
        raise ValueError("La largeur et les longueurs d'appui doivent être positives (6.5.6.3.2).")

    plus_petite = min(L_b1, L_b2)
    plus_grande = max(L_b1, L_b2)
    return min(b * (plus_petite + plus_grande) / 2, 1.5 * b * plus_petite)


def K_Zcp(largeur: float, hauteur: float) -> float:
    """
    6.5.6.4 Coefficient de dimensions pour l'appui, K_Zcp (tableau 6.15).

    Rapport largeur/hauteur <= 1,0 : 1,00 ; >= 2,0 : 1,15 ; interpolation entre les deux.

    Args:
        largeur (float): Largeur de l'élément, perpendiculaire au sens de la charge, mm.
        hauteur (float): Hauteur de l'élément, parallèle au sens de la charge, mm.

    Returns:
        float: K_Zcp.

    Raises:
        ValueError: Si une dimension n'est pas positive.
    """
    if largeur <= 0 or hauteur <= 0:
        raise ValueError("La largeur et la hauteur doivent être positives (6.5.6.4).")

    rapport = largeur / hauteur
    if rapport <= 1:
        return 1.0
    if rapport >= 2:
        return 1.15
    return 1 + 0.15 * (rapport - 1)


def K_B(
    L_b: float,
    loin_de_l_extremite: bool = False,
    hors_fortes_contraintes_de_flexion: bool = False,
) -> float:
    """
    6.5.6.5 Coefficient de longueur d'appui, K_B (tableau 6.16).

    K_B = (L_b + 9,525) / L_b lorsque L_b < 150 mm (note du tableau 6.16), plafonné à 1,75 (valeur
    du tableau pour L_b <= 12,5 mm) ; K_B = 1,00 lorsque L_b >= 150 mm. K_B ne s'applique que si les
    conditions a) et b) de 6.5.6.5 sont respectées ; sinon K_B = 1,00.

    Args:
        L_b (float): Longueur d'appui (parallèle au fil) ou diamètre de la rondelle, mm.
        loin_de_l_extremite (bool, optional): a) aucune partie de la surface d'appui à moins de
            75 mm de l'extrémité de l'élément. Default to False.
        hors_fortes_contraintes_de_flexion (bool, optional): b) surface d'appui non située à un
            endroit soumis à de fortes contraintes de flexion. Default to False.

    Returns:
        float: K_B.

    Raises:
        ValueError: Si la longueur d'appui n'est pas positive.
    """
    if L_b <= 0:
        raise ValueError("La longueur d'appui doit être positive (6.5.6.5).")

    if not (loin_de_l_extremite and hors_fortes_contraintes_de_flexion) or L_b >= 150:
        return 1.0

    return min((L_b + 9.525) / L_b, 1.75)


# VÉRIFICATIONS
def _donnees_communes(
    r: Resultat, b, largeur_element, d, f_cp, K_D, K_Scp, K_T, source_resistances="Tableaux 6.4 à 6.9",
    source_K_D="Tableau 5.1",
) -> tuple[float, float]:
    """Ajoute les données et les étapes F_cp et K_Zcp communes aux deux vérifications."""
    for donnee in (
        Donnee("b", "Largeur d'appui", b, "mm", "dimension"),
        Donnee("b_{élément}", "Largeur de l'élément", largeur_element, "mm", "dimension"),
        Donnee("d", "Hauteur de l'élément", d, "mm", "dimension"),
        Donnee("f_{cp}", "Résistance prévue en compression perpendiculaire au fil", f_cp, "MPa",
               "contrainte", source_resistances),
        Donnee("K_D", "Coefficient de durée d'application de la charge", K_D, source=source_K_D),
        Donnee("K_{Scp}", "Coefficient de conditions d'utilisation (compression perpendiculaire)",
               K_Scp, source="Tableau 6.10"),
        Donnee("K_T", "Coefficient de traitement", K_T, source="Tableau 6.11"),
    ):
        r.ajouter_donnee(donnee)

    f_cp_corrige = r.ajouter_etape(Etape(
        "6.5.6.2", "Résistance corrigée en compression perpendiculaire au fil", "F_{cp}",
        r"F_{cp} = f_{cp} \, (K_D \, K_{Scp} \, K_T)",
        rf"{cs(f_cp)} \times ({cs(K_D)} \times {cs(K_Scp)} \times {cs(K_T)})",
        F_cp(f_cp, K_D, K_Scp, K_T), "MPa", "contrainte",
    ))
    k_zcp = r.ajouter_etape(Etape(
        "6.5.6.4", "Coefficient de dimensions pour l'appui", "K_{Zcp}",
        r"K_{Zcp} : \text{tableau 6.15, } b_{élément} / d",
        rf"{cs(largeur_element)} / {cs(d)} = {cs(largeur_element / d)}",
        K_Zcp(largeur_element, d),
    ))
    return f_cp_corrige, k_zcp


@enregistrer(EDITION, "6.5.6.2", "Compression perpendiculaire au fil : effet de toutes les charges")
def verifier_compression_perpendiculaire_au_fil(
    b: float,
    d: float,
    L_b: float,
    f_cp: float,
    K_D: float = 1,
    K_Scp: float = 1,
    K_T: float = 1,
    loin_de_l_extremite: bool = False,
    hors_fortes_contraintes_de_flexion: bool = False,
    R_f: float | None = None,
    largeur_element: float | None = None,
    source_resistances: str = "Tableaux 6.4 à 6.9",
    source_K_D: str = "Tableau 5.1",
    plis: int = 1,
) -> Resultat:
    """
    6.5.6.2 Résistance pondérée à la compression perpendiculaire au fil à un appui, Q_r.

    Args:
        b (float): Largeur d'appui (et de l'élément pour K_Zcp), mm.
        d (float): Hauteur de l'élément, mm.
        L_b (float): Longueur d'appui, mm.
        f_cp (float): Résistance prévue en compression perpendiculaire au fil, MPa.
        K_D, K_Scp, K_T (float, optional): Coefficients de correction. Default to 1.
        loin_de_l_extremite, hors_fortes_contraintes_de_flexion (bool, optional): Conditions a) et
            b) de 6.5.6.5 pour K_B. Default to False.
        R_f (float | None, optional): Réaction pondérée à l'appui, kN. Default to None.
        largeur_element (float | None, optional): Largeur de l'élément pour K_Zcp, mm. Par défaut,
            la largeur d'appui b.
        source_resistances (str, optional): Source de f_cp pour la note de calcul (ex. « Tableau 6.4 »,
            ou « A.6.5.6 » si f_cp vient de la densité G). Default to "Tableaux 6.4 à 6.9".
        source_K_D (str, optional): Source de K_D pour la note de calcul : « Tableau 5.1 », ou
            « 5.3.2.2 » si K_D est calculé à partir des charges. Default to "Tableau 5.1".
        plis (int, optional): Nombre de plis de l'élément composé, pour la note et la figure seulement
            (largeur_element est la largeur totale). Default to 1.

    Returns:
        Resultat: Trace du calcul. Q_r en N ; vérification en kN.
    """
    r = Resultat(NORME, "6.5.6.2", "Compression perpendiculaire au fil à l'appui", "appui")
    largeur_element = b if largeur_element is None else largeur_element
    f_cp_corrige, k_zcp = _donnees_communes(
        r, b, largeur_element, d, f_cp, K_D, K_Scp, K_T, source_resistances, source_K_D
    )
    if plis > 1:
        r.ajouter_donnee(Donnee("n", "Nombre de plis", plis))
    r.ajouter_donnee(Donnee("L_b", "Longueur d'appui", L_b, "mm", "dimension"))

    k_b = r.ajouter_etape(Etape(
        "6.5.6.5", "Coefficient de longueur d'appui", "K_B",
        r"K_B = (L_b + 9.525) / L_b \leq 1.75", rf"({cs(L_b)} + 9.525) / {cs(L_b)}",
        K_B(L_b, loin_de_l_extremite, hors_fortes_contraintes_de_flexion),
    ))
    A_b = r.ajouter_etape(Etape(
        "6.5.6.2", "Surface d'appui", "A_b", r"A_b = b \, L_b", rf"{cs(b)} \times {cs(L_b)}",
        b * L_b, "mm²", "aire",
    ))
    q_r = r.ajouter_etape(Etape(
        "6.5.6.2", "Résistance pondérée à la compression perpendiculaire au fil", "Q_r",
        r"Q_r = \phi \, F_{cp} \, A_b \, K_B \, K_{Zcp}",
        rf"0.8 \times {cs(f_cp_corrige)} \times {cs(A_b)} \times {cs(k_b)} \times {cs(k_zcp)}",
        Q_r(f_cp_corrige, A_b, k_b, k_zcp), "N",
    ))
    if R_f is not None:
        r.verification = verifier_etat_limite_ultime(R_f, q_r / 1000, "R_f", "Q_r", "kN", "force")
    return r


@enregistrer(EDITION, "6.5.6.3", "Compression perpendiculaire au fil : charges près d'un appui")
def verifier_compression_perpendiculaire_pres_d_un_appui(
    b: float,
    d: float,
    L_b_appui: float,
    L_b_charge: float,
    f_cp: float,
    K_D: float = 1,
    K_Scp: float = 1,
    K_T: float = 1,
    appui_loin_de_l_extremite: bool = False,
    appui_hors_fortes_contraintes_de_flexion: bool = False,
    charge_loin_de_l_extremite: bool = False,
    charge_hors_fortes_contraintes_de_flexion: bool = False,
    P_f: float | None = None,
    largeur_element: float | None = None,
    source_resistances: str = "Tableaux 6.4 à 6.9",
    source_K_D: str = "Tableau 5.1",
    plis: int = 1,
) -> Resultat:
    """
    6.5.6.3 Résistance pondérée Q'_r sous les seules charges appliquées à une distance du centre de
    l'appui inférieure ou égale à la hauteur de l'élément.

    Args:
        b (float): Largeur d'appui moyenne (et de l'élément pour K_Zcp), mm.
        d (float): Hauteur de l'élément, mm.
        L_b_appui (float): Longueur d'appui à l'appui, mm.
        L_b_charge (float): Longueur d'appui de la charge, mm.
        f_cp (float): Résistance prévue en compression perpendiculaire au fil, MPa.
        K_D, K_Scp, K_T (float, optional): Coefficients de correction. Default to 1.
        appui_..., charge_... (bool, optional): Conditions a) et b) de 6.5.6.5 pour chaque surface.
        P_f (float | None, optional): Charge pondérée près de l'appui, kN. Default to None.
        largeur_element (float | None, optional): Largeur de l'élément pour K_Zcp, mm. Par défaut,
            la largeur d'appui b.
        source_resistances (str, optional): Source de f_cp pour la note de calcul (ex. « Tableau 6.4 »,
            ou « A.6.5.6 » si f_cp vient de la densité G). Default to "Tableaux 6.4 à 6.9".
        source_K_D (str, optional): Source de K_D pour la note de calcul : « Tableau 5.1 », ou
            « 5.3.2.2 » si K_D est calculé à partir des charges. Default to "Tableau 5.1".
        plis (int, optional): Nombre de plis de l'élément composé, pour la note et la figure seulement
            (largeur_element est la largeur totale). Default to 1.

    Returns:
        Resultat: Trace du calcul. Q'_r en N ; vérification en kN.
    """
    r = Resultat(NORME, "6.5.6.3", "Compression perpendiculaire au fil près d'un appui", "appui")
    largeur_element = b if largeur_element is None else largeur_element
    f_cp_corrige, k_zcp = _donnees_communes(
        r, b, largeur_element, d, f_cp, K_D, K_Scp, K_T, source_resistances, source_K_D
    )
    if plis > 1:
        r.ajouter_donnee(Donnee("n", "Nombre de plis", plis))
    # Symboles de 6.5.6.3.2 : L_b1 = longueur d'appui la plus petite, L_b2 = la plus grande. À longueurs
    # égales, L_b1 est celle de la charge (sur le dessus), comme à la figure 6.2.
    if L_b_charge <= L_b_appui:
        (L_b1, ou_1), (L_b2, ou_2) = (L_b_charge, "charge"), (L_b_appui, "appui")
    else:
        (L_b1, ou_1), (L_b2, ou_2) = (L_b_appui, "appui"), (L_b_charge, "charge")
    r.ajouter_donnee(Donnee("L_{b1}", f"Longueur d'appui la plus petite ({ou_1})", L_b1, "mm",
                            "dimension"))
    r.ajouter_donnee(Donnee("L_{b2}", f"Longueur d'appui la plus grande ({ou_2})", L_b2, "mm",
                            "dimension"))

    k_b_appui = K_B(L_b_appui, appui_loin_de_l_extremite, appui_hors_fortes_contraintes_de_flexion)
    k_b_charge = K_B(L_b_charge, charge_loin_de_l_extremite,
                     charge_hors_fortes_contraintes_de_flexion)
    k_b = r.ajouter_etape(Etape(
        "6.5.6.5", "Coefficient de longueur d'appui (le plus petit des deux)", "K_B",
        r"K_B = \min(K_{B,appui} \, ; \, K_{B,charge})",
        rf"\min({cs(k_b_appui)} \, ; \, {cs(k_b_charge)})", min(k_b_appui, k_b_charge),
    ))
    a_b_prime = r.ajouter_etape(Etape(
        "6.5.6.3.2", "Surface d'appui moyenne", "A'_b",
        r"A'_b = \min(b \, (L_{b1} + L_{b2}) / 2 \, ; \, 1.5 \, b \, L_{b1})",
        rf"\min({cs(b)} \times ({cs(L_b1)} + {cs(L_b2)}) / 2 \, ; \, 1.5 \times {cs(b)} \times {cs(L_b1)})",
        A_b_prime(b, L_b_appui, L_b_charge), "mm²", "aire",
    ))
    q_r_prime = r.ajouter_etape(Etape(
        "6.5.6.3.1", "Résistance pondérée sous les charges près de l'appui", "Q'_r",
        r"Q'_r = \frac{2}{3} \, \phi \, F_{cp} \, A'_b \, K_B \, K_{Zcp}",
        rf"\frac{{2}}{{3}} \times 0.8 \times {cs(f_cp_corrige)} \times {cs(a_b_prime)} "
        rf"\times {cs(k_b)} \times {cs(k_zcp)}",
        Q_r_prime(f_cp_corrige, a_b_prime, k_b, k_zcp), "N",
    ))
    if P_f is not None:
        r.verification = verifier_etat_limite_ultime(P_f, q_r_prime / 1000, "P_f", "Q'_r", "kN", "force")
    return r
