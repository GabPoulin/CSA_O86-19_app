"""
Vérification aux états limites : effet pondéré / résistance pondérée.

CSA O86:19, 5.1.2 b) : l'effet de charge pondéré ne doit pas dépasser la résistance pondérée
correspondante. Le ratio est comparé à 1,00 avant d'être arrondi : un ratio exactement égal à 1,00
respecte l'état limite.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Verification:
    """
    Résultat d'une vérification aux états limites ultimes.

    Args:
        article (str): Article qui exige la vérification (ex. "5.1.2").
        symbole_effet (str): Symbole de l'effet pondéré en LaTeX (ex. "P_f").
        effet (float): Effet pondéré, en unités métriques (>= 0).
        symbole_resistance (str): Symbole de la résistance pondérée en LaTeX (ex. "P_r").
        resistance (float): Résistance pondérée, dans la même unité que l'effet.
        unite (str): Unité métrique de l'effet et de la résistance.
        grandeur (str | None): Grandeur pour l'affichage en impérial.
    """

    article: str
    symbole_effet: str
    effet: float
    symbole_resistance: str
    resistance: float
    unite: str = ""
    grandeur: str | None = None

    @property
    def ratio(self) -> float:
        """Ratio effet / résistance. Infini si la résistance est nulle ou négative."""
        if self.resistance <= 0:
            return float("inf")
        return self.effet / self.resistance

    @property
    def respecte(self) -> bool:
        """True si l'effet pondéré ne dépasse pas la résistance pondérée (ratio <= 1,00)."""
        return self.resistance > 0 and self.ratio <= 1

    def message(self) -> str:
        """Message affiché à l'utilisateur, avec le ratio en % (2 décimales)."""
        if self.resistance <= 0:
            return "État limite dépassé: résistance pondérée nulle ou négative"
        if self.respecte:
            return f"État limite respecté: {self.ratio * 100:.2f}%"
        return f"État limite dépassé: {self.ratio * 100:.2f}%"


def verifier(
    effet: float,
    resistance: float,
    symbole_effet: str = "",
    symbole_resistance: str = "",
    unite: str = "",
    grandeur: str | None = None,
    article: str = "5.1.2",
) -> Verification:
    """
    5.1.2 États limites ultimes : vérifie que l'effet pondéré ne dépasse pas la résistance pondérée.

    Args:
        effet (float): Effet pondéré (>= 0, calculs de base en valeurs positives seulement).
        resistance (float): Résistance pondérée correspondante.
        symbole_effet (str, optional): Symbole de l'effet (ex. "P_f").
        symbole_resistance (str, optional): Symbole de la résistance (ex. "P_r").
        unite (str, optional): Unité métrique commune.
        grandeur (str | None, optional): Grandeur pour l'affichage en impérial.
        article (str, optional): Article qui exige la vérification. Default to "5.1.2".

    Returns:
        Verification: Résultat de la vérification.

    Raises:
        ValueError: Si l'effet est négatif.
    """
    if effet < 0:
        raise ValueError("L'effet pondéré doit être positif ou nul (calculs de base).")

    return Verification(
        article=article,
        symbole_effet=symbole_effet,
        effet=effet,
        symbole_resistance=symbole_resistance,
        resistance=resistance,
        unite=unite,
        grandeur=grandeur,
    )
