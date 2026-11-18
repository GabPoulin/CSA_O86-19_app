"""
CSA O86:19 - Tableau A.11 Valeurs de densité (annexe A, p. 330).

Densité moyenne du bois anhydre, G. Seules les colonnes « Bois de charpente classé visuellement » et
« Classes E du MSR (ou MEL) de É-P-S » sont codées pour l'instant.
"""

# Bois de charpente classé visuellement
_VISUEL = {"df": 0.49, "hf": 0.46, "spf": 0.42, "ns": 0.35}


def G(essence: str, E: float = 0) -> float:
    """
    Tableau A.11 Densité moyenne du bois anhydre, G.

    Bois classé visuellement : selon le groupe d'essences. MSR et MEL (É-P-S) : selon la classe E.
    Pour les autres essences MSR ou MEL, le tableau renvoie aux valeurs du bois classé visuellement
    (l'application utilise É-P-S pour le MSR et le MEL).

    Args:
        essence (str): Groupe d'essences : "df", "hf", "spf", "ns" ; pour le MSR et le MEL :
            "courant", "normal" ou "rare".
        E (float, optional): Module d'élasticité de la classe MSR ou MEL, MPa. Default to 0.

    Returns:
        float: G.

    Raises:
        ValueError: Si l'essence ou la classe E n'est pas au tableau A.11.
    """
    if essence in _VISUEL:
        return _VISUEL[essence]

    if 8300 <= E <= 11700:
        return 0.42
    if 12400 <= E <= 13100:
        return 0.47
    if 13800 <= E <= 16500:
        return 0.50
    raise ValueError(f"Pas de densité au tableau A.11 pour {essence} avec E = {E} MPa.")
