"""
CSA O86:19 - 3.2 Symboles.

« Les symboles qui suivent doivent s'appliquer dans cette norme. Les symboles qui diffèrent de cet
usage et la nomenclature additionnelle sont signalés le cas échéant. » (p. 35 à 38)

Chaque symbole est défini exactement comme à l'article 3.2. Les symboles sont ajoutés au fur et à
mesure que les articles qui les utilisent sont codés. Dans le code, le `_` sépare le symbole de son
indice (ex. K_Zc), et les majuscules et minuscules de la norme sont respectées.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Symbole:
    """
    Un symbole de la norme.

    Args:
        code (str): Nom utilisé dans le code (ex. "K_Zc").
        latex (str): Écriture LaTeX (ex. "K_{Zc}").
        definition (str): Définition exacte de l'article 3.2.
        unite (str): Unité de l'article 3.2. Vide si sans unité.
    """

    code: str
    latex: str
    definition: str
    unite: str = ""


_SYMBOLES = (
    Symbole("A", "A", "aire de la section transversale", "mm²"),
    Symbole("A_b", "A_b", "surface d'appui", "mm²"),
    Symbole("A_g", "A_g", "aire de la section transversale brute", "mm²"),
    Symbole("A_n", "A_n", "aire de la section transversale nette", "mm²"),
    Symbole("b", "b", "largeur de l'élément", "mm"),
    Symbole("C_B", "C_B", "élancement des éléments en flexion"),
    Symbole("C_C", "C_C", "élancement des éléments en compression"),
    Symbole("d", "d", "hauteur de l'élément", "mm"),
    Symbole("E", "E", "module d'élasticité prévu", "MPa"),
    Symbole(
        "E_05", "E_{05}", "module d'élasticité pour les calculs des éléments en compression", "MPa"
    ),
    Symbole("f_b", "f_b", "résistance prévue en flexion", "MPa"),
    Symbole("f_c", "f_c", "résistance prévue en compression parallèle au fil", "MPa"),
    Symbole("f_cp", "f_{cp}", "résistance prévue en compression perpendiculaire au fil", "MPa"),
    Symbole(
        "f_f", "f_f", "résistance prévue en cisaillement par fissuration à une entaille", "MPa"
    ),
    Symbole("f_t", "f_t", "résistance prévue en traction parallèle au fil", "MPa"),
    Symbole("f_v", "f_v", "résistance prévue en cisaillement", "MPa"),
    Symbole("K_B", "K_B", "coefficient de longueur d'appui"),
    Symbole("K_C", "K_C", "coefficient d'élancement des éléments en compression"),
    Symbole("K_D", "K_D", "coefficient de durée d'application de la charge"),
    Symbole("K_e", "K_e", "coefficient de longueur effective"),
    Symbole("K_H", "K_H", "coefficient de système"),
    Symbole("K_L", "K_L", "coefficient de stabilité latérale des éléments en flexion"),
    Symbole(
        "K_S",
        "K_S",
        "coefficient de conditions d'utilisation, utilisé avec les indices appropriés",
    ),
    Symbole("K_Sb", "K_{Sb}", "coefficient de conditions d'utilisation pour la flexion"),
    Symbole(
        "K_Sc",
        "K_{Sc}",
        "coefficient de conditions d'utilisation pour la compression parallèle au fil",
    ),
    Symbole(
        "K_Scp",
        "K_{Scp}",
        "coefficient de conditions d'utilisation pour la compression perpendiculaire au fil",
    ),
    Symbole(
        "K_SE", "K_{SE}", "coefficient de conditions d'utilisation relatif au module d'élasticité"
    ),
    Symbole(
        "K_Sf",
        "K_{Sf}",
        "coefficient de conditions d'utilisation pour le cisaillement par fissuration",
    ),
    Symbole(
        "K_St", "K_{St}", "coefficient de conditions d'utilisation pour la traction parallèle au fil"
    ),
    Symbole("K_Sv", "K_{Sv}", "coefficient de conditions d'utilisation pour le cisaillement"),
    Symbole("K_T", "K_T", "coefficient de traitement"),
    Symbole("K_Z", "K_Z", "coefficient de dimensions"),
    Symbole("K_Zb", "K_{Zb}", "coefficient de dimensions pour la flexion du bois de sciage"),
    Symbole(
        "K_Zc",
        "K_{Zc}",
        "coefficient de dimensions pour la compression du bois de sciage et du bois lamellé-croisé",
    ),
    Symbole("K_Zcp", "K_{Zcp}", "coefficient de dimensions pour l'appui"),
    Symbole("K_Zt", "K_{Zt}", "coefficient de dimensions pour la traction du bois de sciage"),
    Symbole("K_Zv", "K_{Zv}", "coefficient de dimensions pour le cisaillement du bois de sciage"),
    Symbole("L", "L", "longueur", "mm"),
    Symbole("L_e", "L_e", "longueur effective", "mm"),
    Symbole("M_f", "M_f", "moment de flexion pondéré", "N·mm"),
    Symbole("M_r", "M_r", "résistance pondérée au moment de flexion", "N·mm"),
    Symbole("N_r", "N_r", "résistance pondérée à la compression oblique par rapport au fil", "N"),
    Symbole("P_f", "P_f", "charge de compression axiale pondérée", "N"),
    Symbole("P_r", "P_r", "résistance pondérée à la compression parallèle au fil", "N"),
    Symbole(
        "Q_r",
        "Q_r",
        "résistance pondérée à la compression perpendiculaire au fil ou au plan du panneau",
        "N",
    ),
    Symbole("S", "S", "module de section", "mm³"),
    Symbole("T_f", "T_f", "charge de traction axiale pondérée", "N"),
    Symbole("T_r", "T_r", "résistance pondérée à la traction parallèle au fil", "N"),
    Symbole("V_f", "V_f", "effort tranchant pondéré", "N"),
    Symbole("V_r", "V_r", "résistance pondérée au cisaillement", "N"),
    Symbole("phi", r"\phi", "coefficient de résistance"),
)

SYMBOLES: dict[str, Symbole] = {symbole.code: symbole for symbole in _SYMBOLES}


def symbole(code: str) -> Symbole:
    """
    Retourne un symbole de l'article 3.2.

    Raises:
        KeyError: Si le symbole n'est pas (encore) défini.
    """
    if code not in SYMBOLES:
        raise KeyError(f"Symbole {code!r} absent de 3.2 (ou pas encore ajouté).")
    return SYMBOLES[code]
