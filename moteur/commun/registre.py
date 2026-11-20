"""
Registre : catalogue des calculs offerts par chaque édition de norme.

Chaque fonction de vérification s'inscrit au registre avec le décorateur `enregistrer`. L'interface
n'affiche que les calculs de l'édition choisie (ARCHITECTURE.md, section 9). Le niveau d'accès sert à
la future version de démonstration (ARCHITECTURE.md, section 11).
"""

import importlib
from collections.abc import Callable
from dataclasses import dataclass

ACCES = ("demonstration", "abonne")


@dataclass(frozen=True)
class Calcul:
    """
    Un calcul offert par une édition.

    Args:
        edition (str): Dossier de l'édition (ex. "csa_o86_19").
        identifiant (str): Identifiant unique dans l'édition. Par défaut, le numéro d'article.
        article (str): Article de la norme (ex. "6.5.5").
        titre (str): Titre (ex. "Résistance à la compression parallèle au fil").
        fonction (Callable): Fonction de vérification, qui retourne un Resultat.
        acces (str): "demonstration" ou "abonne".
    """

    edition: str
    identifiant: str
    article: str
    titre: str
    fonction: Callable
    acces: str = "abonne"


_REGISTRE: dict[str, dict[str, Calcul]] = {}


def _cle_article(article: str) -> tuple:
    """Clé de tri dans l'ordre de la norme (6.5.10 après 6.5.9 ; annexes A, B à la fin)."""
    morceaux = []
    for morceau in article.split("."):
        morceaux.append((0, int(morceau), "") if morceau.isdigit() else (1, 0, morceau))
    return tuple(morceaux)


def enregistrer(
    edition: str,
    article: str,
    titre: str,
    acces: str = "abonne",
    identifiant: str | None = None,
) -> Callable:
    """
    Décorateur qui inscrit une fonction de vérification au registre.

    Args:
        edition (str): Dossier de l'édition (ex. "csa_o86_19").
        article (str): Article de la norme (ex. "6.5.5").
        titre (str): Titre du calcul.
        acces (str, optional): "demonstration" ou "abonne". Par défaut, réservé aux abonnés.
        identifiant (str | None, optional): Seulement si deux calculs viennent du même article
            (ex. "12.4.4-a"). Par défaut, le numéro d'article.

    Raises:
        ValueError: Si l'accès est invalide ou si l'identifiant existe déjà dans l'édition.
    """
    if acces not in ACCES:
        raise ValueError(f"Accès invalide : {acces!r}. Choix : {ACCES}.")

    identifiant = article if identifiant is None else identifiant

    def decorateur(fonction: Callable) -> Callable:
        calculs_edition = _REGISTRE.setdefault(edition, {})
        if identifiant in calculs_edition:
            raise ValueError(f"Le calcul {identifiant!r} existe déjà dans {edition!r}.")
        calculs_edition[identifiant] = Calcul(edition, identifiant, article, titre, fonction, acces)
        return fonction

    return decorateur


def editions() -> list[str]:
    """Éditions qui ont au moins un calcul inscrit."""
    return sorted(_REGISTRE)


def nom_de_l_edition(edition: str) -> str:
    """
    Nom affiché d'une édition : constante NORME de son dossier (ex. "csa_o86_19" -> "CSA O86:19").

    Args:
        edition (str): Dossier de l'édition (ex. "csa_o86_19").

    Returns:
        str: Norme et édition.

    Raises:
        KeyError: Si l'édition n'existe pas ou n'a pas de constante NORME.
    """
    try:
        return importlib.import_module(f"moteur.normes.{edition}").NORME
    except (ImportError, AttributeError) as erreur:
        raise KeyError(f"L'édition {edition!r} n'existe pas ou n'a pas de NORME.") from erreur


def calculs(edition: str) -> list[Calcul]:
    """Calculs d'une édition, dans l'ordre des articles de la norme."""
    return sorted(_REGISTRE.get(edition, {}).values(), key=lambda c: _cle_article(c.article))


def calcul(edition: str, identifiant: str) -> Calcul:
    """
    Retourne un calcul.

    Raises:
        KeyError: Si le calcul n'existe pas dans l'édition.
    """
    try:
        return _REGISTRE[edition][identifiant]
    except KeyError as erreur:
        raise KeyError(f"Le calcul {identifiant!r} n'existe pas dans {edition!r}.") from erreur
