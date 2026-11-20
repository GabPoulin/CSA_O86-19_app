"""
CSA O86:19 - 6.5.3 Résistance au moment de flexion (p. 64-65).

    6.5.3.1 Généralités (M_r, F_b)
    6.5.3.2 Coefficient de stabilité latérale, K_L
        6.5.3.2.1 Rapport hauteur/largeur <= 2,5:1 : K_L = 1 sans support latéral
        6.5.3.2.2 Rapport > 2,5:1 : support latéral aux appuis et K_L selon 7.5.6.4 (pas encore offert),
            sauf 6.5.3.2.3
        6.5.3.2.3 Exigences relatives aux supports latéraux : K_L = 1 jusqu'à 4:1, 5:1, 6,5:1, 7,5:1 ou 9:1
        6.5.3.2.4 Poutres composées : rapport de 6.5.3.2.1 basé sur la largeur totale

K_L selon 7.5.6.4 n'est pas encore offert : si le rapport hauteur/largeur dépasse la limite, une erreur
est levée (issue #3).

Poutres composées (6.5.3.2.2 et 6.5.3.2.4, lecture stricte validée avec l'utilisateur, issue #48) :
K_L = 1 seulement si les plis sont fixés ensemble à intervalles d'au plus 4 d ET si d / (n b) <= 2,5
(6.5.3.2.1 sur la largeur totale). Les rapports de 6.5.3.2.3 ne s'appliquent pas aux poutres composées
(6.5.3.2.2 : « autres que les poutres composées »). Dans les autres cas, K_L selon 7.5.6.4 (à venir).
"""

from moteur.commun.nombres import cs
from moteur.commun.registre import enregistrer
from moteur.commun.resultat import Donnee, Etape, Resultat
from moteur.normes.csa_o86_19 import NORME
from moteur.normes.csa_o86_19.ch_5_conception_generale.art_5_1_calculs_aux_etats_limites import (
    verifier_etat_limite_ultime,
)

EDITION = "csa_o86_19"
PHI = 0.9  # 6.5.3.1

# 6.5.3.2.1 et 6.5.3.2.3 : rapports hauteur/largeur maximaux pour K_L = 1
RAPPORT_SANS_SUPPORT = 2.5  # 6.5.3.2.1
RAPPORT_SUPPORT_AUX_APPUIS = 4.0  # 6.5.3.2.3 a)
RAPPORT_PANNES_OU_TIRANTS = 5.0  # 6.5.3.2.3 b)
RAPPORT_RIVE_COMPRIMEE = 6.5  # 6.5.3.2.3 c)
RAPPORT_RIVE_COMPRIMEE_ET_ENTRETOISES = 7.5  # 6.5.3.2.3 d)
RAPPORT_DEUX_RIVES = 9.0  # 6.5.3.2.3 e)
ESPACEMENT_FIXATIONS_EN_HAUTEURS = 4  # 6.5.3.2.4 : fixations à intervalles d'au plus 4 d


# FONCTIONS SIMPLES (dans l'ordre de la norme)
def F_b(f_b: float, K_D: float = 1, K_H: float = 1, K_Sb: float = 1, K_T: float = 1) -> float:
    """
    6.5.3.1 Résistance corrigée en flexion, F_b.

    F_b = f_b (K_D K_H K_Sb K_T)

    Args:
        f_b (float): Résistance prévue en flexion, MPa (tableaux 6.4 à 6.9).
        K_D (float, optional): Coefficient de durée d'application de la charge. Default to 1.
        K_H (float, optional): Coefficient de système. Default to 1.
        K_Sb (float, optional): Coefficient de conditions d'utilisation pour la flexion. Default to 1.
        K_T (float, optional): Coefficient de traitement. Default to 1.

    Returns:
        float: F_b, MPa.
    """
    return f_b * (K_D * K_H * K_Sb * K_T)


def S(b: float, d: float) -> float:
    """
    6.5.3.1 Module de section, S, d'une section rectangulaire (6.5.1).

    S = b d² / 6

    Args:
        b (float): Largeur de l'élément (largeur totale pour une poutre composée), mm.
        d (float): Hauteur de l'élément, mm.

    Returns:
        float: S, mm³.
    """
    return b * d**2 / 6


def rapport_hauteur_largeur_maximal(
    support_lateral_aux_appuis: bool = False,
    pannes_ou_tirants: bool = False,
    rive_comprimee_maintenue: bool = False,
    entretoises_ou_entremises: bool = False,
    rive_tendue_maintenue: bool = False,
) -> float:
    """
    6.5.3.2.1 et 6.5.3.2.3 Rapport hauteur/largeur maximal pour lequel K_L = 1.

    Sans support latéral aux appuis : 2,5:1 (6.5.3.2.1). Avec support latéral aux appuis
    (déplacement latéral et rotation empêchés) (6.5.3.2.3) :
        a) 4:1 sans appui intermédiaire additionnel ;
        b) 5:1 alignement maintenu par des pannes ou des tirants ;
        c) 6,5:1 rive comprimée maintenue (platelage fixé directement ou solives à 610 mm ou moins) ;
        d) 7,5:1 c) et entretoises ou entremises à 8 d ou moins ;
        e) 9:1 alignement des deux rives maintenu.

    Args:
        support_lateral_aux_appuis (bool, optional): Support latéral aux points d'appui. Default to False.
        pannes_ou_tirants (bool, optional): Cas b). Default to False.
        rive_comprimee_maintenue (bool, optional): Cas c). Default to False.
        entretoises_ou_entremises (bool, optional): Cas d), avec c). Default to False.
        rive_tendue_maintenue (bool, optional): Cas e), avec c) (les deux rives). Default to False.

    Returns:
        float: Rapport hauteur/largeur maximal (d/b).
    """
    if not support_lateral_aux_appuis:
        return RAPPORT_SANS_SUPPORT
    if rive_comprimee_maintenue:
        if rive_tendue_maintenue:
            return RAPPORT_DEUX_RIVES
        if entretoises_ou_entremises:
            return RAPPORT_RIVE_COMPRIMEE_ET_ENTRETOISES
        return RAPPORT_RIVE_COMPRIMEE
    if pannes_ou_tirants:
        return RAPPORT_PANNES_OU_TIRANTS
    return RAPPORT_SUPPORT_AUX_APPUIS


def K_L(b: float, d: float, rapport_maximal: float) -> float:
    """
    6.5.3.2 Coefficient de stabilité latérale, K_L.

    K_L = 1 si d/b ne dépasse pas le rapport maximal (6.5.3.2.1 et 6.5.3.2.3). Sinon, K_L doit être
    déterminé selon 7.5.6.4 (6.5.3.2.2), pas encore offert.

    Args:
        b (float): Largeur de l'élément (largeur totale pour une poutre composée), mm.
        d (float): Hauteur de l'élément, mm.
        rapport_maximal (float): Voir rapport_hauteur_largeur_maximal().

    Returns:
        float: K_L = 1.

    Raises:
        ValueError: Si d/b dépasse le rapport maximal (K_L selon 7.5.6.4, à venir).
    """
    rapport = d / b
    if rapport > rapport_maximal:
        raise ValueError(
            f"Rapport hauteur/largeur d/b = {rapport:.2f} > {rapport_maximal:g} : KL doit être "
            "déterminé selon l'article 7.5.6.4 (6.5.3.2.2), fonctionnalité à venir. "
            "Ajoutez des supports latéraux (6.5.3.2.3) ou modifiez la section."
        )
    return 1.0


def espacement_maximal_des_fixations(d: float) -> float:
    """
    6.5.3.2.4 Espacement maximal des fixations des plis d'une poutre composée : 4 d.

    Args:
        d (float): Hauteur de la poutre, mm.

    Returns:
        float: Espacement maximal, mm.
    """
    return ESPACEMENT_FIXATIONS_EN_HAUTEURS * d


def K_L_poutre_composee(b_totale: float, d: float, plis_fixes_a_au_plus_4d: bool) -> float:
    """
    6.5.3.2.4 Coefficient de stabilité latérale, K_L, d'une poutre composée (au moins deux plis de même
    hauteur).

    K_L = 1 si les plis sont fixés ensemble à intervalles d'au plus 4 d et si d / (n b) <= 2,5 (rapport de
    6.5.3.2.1 basé sur la largeur totale). « Dans d'autres cas », K_L selon 7.5.6.4 (pas encore offert).
    Les rapports de 6.5.3.2.3 ne s'appliquent pas (6.5.3.2.2, issue #48).

    Args:
        b_totale (float): Largeur totale de la poutre, n b, mm.
        d (float): Hauteur de la poutre, mm.
        plis_fixes_a_au_plus_4d (bool): Plis solidement fixés ensemble à intervalles d'au plus 4 d.

    Returns:
        float: K_L = 1.

    Raises:
        ValueError: Si les plis ne sont pas fixés à au plus 4 d, ou si d / (n b) > 2,5 (K_L selon
            7.5.6.4, à venir).
    """
    if not plis_fixes_a_au_plus_4d:
        raise ValueError(
            "Poutre composée : les plis doivent être fixés ensemble à intervalles d'au plus "
            f"4 d = {espacement_maximal_des_fixations(d):g} mm (6.5.3.2.4). Sinon, KL doit être "
            "déterminé selon l'article 7.5.6.4, fonctionnalité à venir."
        )
    rapport = d / b_totale
    if rapport > RAPPORT_SANS_SUPPORT:
        raise ValueError(
            f"Poutre composée : d/(n b) = {rapport:.2f} > {RAPPORT_SANS_SUPPORT:g} : KL doit être "
            "déterminé selon l'article 7.5.6.4 (6.5.3.2.4), fonctionnalité à venir. Les rapports de "
            "6.5.3.2.3 ne s'appliquent pas aux poutres composées (6.5.3.2.2)."
        )
    return 1.0


def M_r(F_b: float, S: float, K_Zb: float = 1, K_L: float = 1) -> float:
    """
    6.5.3.1 Résistance pondérée au moment de flexion, M_r.

    M_r = phi F_b S K_Zb K_L, phi = 0,9

    Args:
        F_b (float): Résistance corrigée en flexion, MPa.
        S (float): Module de section, mm³.
        K_Zb (float, optional): Coefficient de dimensions en flexion (6.4.5). Default to 1.
        K_L (float, optional): Coefficient de stabilité latérale (6.5.3.2). Default to 1.

    Returns:
        float: M_r, N·mm.
    """
    return PHI * F_b * S * K_Zb * K_L


# VÉRIFICATION
@enregistrer(EDITION, "6.5.3", "Résistance au moment de flexion")
def verifier_flexion(
    b: float,
    d: float,
    f_b: float,
    plis: int = 1,
    K_D: float = 1,
    K_H: float = 1,
    K_Sb: float = 1,
    K_T: float = 1,
    K_Zb: float = 1,
    support_lateral_aux_appuis: bool = False,
    pannes_ou_tirants: bool = False,
    rive_comprimee_maintenue: bool = False,
    entretoises_ou_entremises: bool = False,
    rive_tendue_maintenue: bool = False,
    plis_fixes_a_au_plus_4d: bool = False,
    M_f: float | None = None,
    source_resistances: str = "Tableaux 6.4 à 6.9",
    source_K_D: str = "Tableau 5.1",
) -> Resultat:
    """
    6.5.3 Résistance pondérée au moment de flexion d'un élément en bois de sciage.

    Args:
        b (float): Largeur d'un pli, mm.
        d (float): Hauteur de l'élément, mm.
        f_b (float): Résistance prévue en flexion, MPa.
        plis (int, optional): Nombre de plis (poutre composée, 6.4.4.3 et 6.5.3.2.4). Default to 1.
        K_D, K_H, K_Sb, K_T, K_Zb (float, optional): Coefficients de correction. Default to 1.
        support_lateral_aux_appuis, pannes_ou_tirants, rive_comprimee_maintenue,
            entretoises_ou_entremises, rive_tendue_maintenue (bool, optional): Supports latéraux
            (voir rapport_hauteur_largeur_maximal()), éléments simples seulement. Default to False.
        plis_fixes_a_au_plus_4d (bool, optional): Poutre composée : plis fixés ensemble à intervalles
            d'au plus 4 d (6.5.3.2.4). Default to False.
        M_f (float | None, optional): Moment de flexion pondéré, kN·m. Default to None.
        source_resistances (str, optional): Tableau des résistances prévues (6.3), pour la note de
            calcul (voir art_6_3.tableau_des_resistances()). Default to "Tableaux 6.4 à 6.9".
        source_K_D (str, optional): Source de K_D pour la note de calcul : « Tableau 5.1 », ou
            « 5.3.2.2 » si K_D est calculé à partir des charges. Default to "Tableau 5.1".

    Returns:
        Resultat: Trace du calcul. M_r en N·mm ; vérification en kN·m.

    Raises:
        ValueError: Si d/b dépasse le rapport maximal (K_L selon 7.5.6.4, à venir).
    """
    r = Resultat(NORME, "6.5.3", "Résistance au moment de flexion", "poutre")
    for donnee in (
        Donnee("b", "Largeur d'un pli", b, "mm", "dimension"),
        Donnee("d", "Hauteur de l'élément", d, "mm", "dimension"),
        Donnee("n", "Nombre de plis", plis),
        Donnee("f_b", "Résistance prévue en flexion", f_b, "MPa", "contrainte", source_resistances),
        Donnee("K_D", "Coefficient de durée d'application de la charge", K_D, source=source_K_D),
        Donnee("K_H", "Coefficient de système", K_H, source="Tableau 6.12"),
        Donnee("K_{Sb}", "Coefficient de conditions d'utilisation (flexion)", K_Sb, source="Tableau 6.10"),
        Donnee("K_T", "Coefficient de traitement", K_T, source="Tableau 6.11"),
        Donnee("K_{Zb}", "Coefficient de dimensions (flexion)", K_Zb, source="Tableau 6.13"),
    ):
        r.ajouter_donnee(donnee)

    largeur = b * plis
    f_b_corrige = r.ajouter_etape(Etape(
        "6.5.3.1", "Résistance corrigée en flexion", "F_b",
        r"F_b = f_b \, (K_D \, K_H \, K_{Sb} \, K_T)",
        rf"{cs(f_b)} \times ({cs(K_D)} \times {cs(K_H)} \times {cs(K_Sb)} \times {cs(K_T)})",
        F_b(f_b, K_D, K_H, K_Sb, K_T), "MPa", "contrainte",
    ))
    module = r.ajouter_etape(Etape(
        "6.5.3.1", "Module de section", "S",
        r"S = \frac{(n \, b) \, d^2}{6}", rf"\frac{{({plis} \times {cs(b)}) \times {cs(d)}^2}}{{6}}",
        S(largeur, d), "mm³",
    ))
    if plis > 1:
        k_l = r.ajouter_etape(Etape(
            "6.5.3.2.4", "Coefficient de stabilité latérale (poutre composée)", "K_L",
            r"K_L = 1 \text{ si fixations} \leq 4 \, d \text{ et } \frac{d}{n \, b} \leq 2.5",
            rf"4 \times {cs(d)} = {cs(espacement_maximal_des_fixations(d))} \text{{ mm}} ; "
            rf"\frac{{{cs(d)}}}{{{cs(largeur)}}} = {cs(d / largeur)} \leq 2.5",
            K_L_poutre_composee(largeur, d, plis_fixes_a_au_plus_4d),
        ))
    else:
        rapport_maximal = rapport_hauteur_largeur_maximal(
            support_lateral_aux_appuis, pannes_ou_tirants, rive_comprimee_maintenue,
            entretoises_ou_entremises, rive_tendue_maintenue,
        )
        k_l = r.ajouter_etape(Etape(
            "6.5.3.2", "Coefficient de stabilité latérale", "K_L",
            rf"K_L = 1 \text{{ si }} \frac{{d}}{{b}} \leq {rapport_maximal:g}",
            rf"\frac{{{cs(d)}}}{{{cs(largeur)}}} = {cs(d / largeur)} \leq {rapport_maximal:g}",
            K_L(largeur, d, rapport_maximal),
        ))
    m_r = r.ajouter_etape(Etape(
        "6.5.3.1", "Résistance pondérée au moment de flexion", "M_r",
        r"M_r = \phi \, F_b \, S \, K_{Zb} \, K_L",
        rf"0.9 \times {cs(f_b_corrige)} \times {cs(module)} \times {cs(K_Zb)} \times {cs(k_l)}",
        M_r(f_b_corrige, module, K_Zb, k_l), "N·mm",
    ))

    if M_f is not None:
        r.verification = verifier_etat_limite_ultime(M_f, m_r / 1e6, "M_f", "M_r", "kN·m", "moment")

    return r
