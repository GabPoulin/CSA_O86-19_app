"""
CSA O86:19 - 6.3 Résistances prévues et modules d'élasticité (p. 49-59).

    6.3.1 Bois de charpente classé visuellement (tableaux 6.4 à 6.7)
    6.3.2 Bois MSR et MEL (tableaux 6.8 et 6.9)

Les valeurs des tableaux sont dans la base de données de l'édition (vérifiées une par une avec la
norme, PR #14 et #15). Les valeurs sont pour une durée normale et des conditions sèches.
"""

from dataclasses import dataclass

from moteur.normes.csa_o86_19.base_de_donnees import lire


@dataclass(frozen=True)
class ResistancesPrevues:
    """
    Résistances prévues et modules d'élasticité d'une classe de bois, MPa.

    Args:
        f_b (float): Résistance prévue en flexion, MPa.
        f_v (float): Résistance prévue en cisaillement, MPa.
        f_c (float): Résistance prévue en compression parallèle au fil, MPa.
        f_cp (float): Résistance prévue en compression perpendiculaire au fil, MPa.
        f_t (float): Résistance prévue en traction parallèle au fil, MPa.
        E (float): Module d'élasticité prévu, MPa.
        E_05 (float): Module d'élasticité pour les calculs des éléments en compression, MPa.
    """

    f_b: float
    f_v: float
    f_c: float
    f_cp: float
    f_t: float
    E: float
    E_05: float


def classes(categorie: str, essence: str) -> list[str]:
    """
    Classes offertes pour une catégorie et un groupe d'essences, dans l'ordre des tableaux.

    Args:
        categorie (str): Code de la catégorie (voir art_6_2_materiaux).
        essence (str): Groupe d'essences ("df", "hf", "spf", "ns") ; pour le MSR et le MEL :
            "courant", "normal" ou "rare".

    Returns:
        list[str]: Codes des classes (ex. "ss", "n1-n2", "n3-stud").
    """
    lignes = lire(
        'SELECT grade FROM sawn_lumber_strengths WHERE category = ? AND specie = ? ORDER BY "index"',
        (categorie, essence),
    )
    return [ligne["grade"] for ligne in lignes]


def coefficients_charges_sur_grande_face(classe: str) -> tuple[float, float]:
    """
    Tableau 6.6 (fin, p. 54) : coefficients des poutres et longerons chargés sur leur grande face.

    « Structure choisie » : f_b x 0,88 ; E et E_05 x 1,00.
    « n° 1 ou n° 2 » : f_b x 0,77 ; E et E_05 x 0,90.

    Args:
        classe (str): Code de la classe ("ss", "n1" ou "n2").

    Returns:
        tuple[float, float]: Coefficient pour f_b, coefficient pour E et E_05.
    """
    return (0.88, 1.0) if classe == "ss" else (0.77, 0.9)


def resistances_prevues(
    categorie: str,
    essence: str,
    classe: str,
    charges_sur_grande_face: bool = False,
) -> ResistancesPrevues:
    """
    6.3 Résistances prévues et modules d'élasticité (tableaux 6.4 à 6.9).

    Args:
        categorie (str): Code de la catégorie (voir art_6_2_materiaux).
        essence (str): Groupe d'essences (voir classes()).
        classe (str): Code de la classe (voir classes()).
        charges_sur_grande_face (bool, optional): Poutres et longerons chargés sur leur grande face
            (tableau 6.6, note *). Default to False.

    Returns:
        ResistancesPrevues: f_b, f_v, f_c, f_cp, f_t, E et E_05, MPa.

    Raises:
        ValueError: Si la combinaison catégorie, essence et classe n'existe pas.
    """
    lignes = lire(
        "SELECT * FROM sawn_lumber_strengths WHERE category = ? AND specie = ? AND grade = ?",
        (categorie, essence, classe),
    )
    if not lignes:
        raise ValueError(f"Classe introuvable : {categorie}, {essence}, {classe} (tableaux 6.4 à 6.9).")

    ligne = lignes[0]
    f_b, E, E_05 = ligne["fb"], ligne["e"], ligne["e05"]
    if charges_sur_grande_face and categorie == "Beam":
        coefficient_f_b, coefficient_E = coefficients_charges_sur_grande_face(classe)
        f_b *= coefficient_f_b
        if coefficient_E != 1.0:
            E *= coefficient_E
            E_05 *= coefficient_E

    return ResistancesPrevues(
        f_b=f_b,
        f_v=ligne["fv"],
        f_c=ligne["fc"],
        f_cp=ligne["fcp"],
        f_t=ligne["ft"],
        E=E,
        E_05=E_05,
    )
