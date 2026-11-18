"""
Trace des calculs : Resultat.

Chaque fonction de vérification retourne un Resultat. Cette trace est la source unique pour le détail
affiché dans l'interface, la note de calcul PDF et les tests (ARCHITECTURE.md, section 8).

Toutes les valeurs sont en unités métriques, comme dans les normes. Les formules sont écrites en LaTeX.
"""

from dataclasses import dataclass, field

from moteur.commun.verification import Verification


@dataclass(frozen=True)
class Donnee:
    """
    Une donnée d'entrée du calcul (ligne du tableau « Données » de la note de calcul).

    Args:
        symbole (str): Symbole en LaTeX (ex. "f_c").
        description (str): Description (ex. "Résistance prévue en compression parallèle au fil").
        valeur (float | str): Valeur en unités métriques, ou texte (ex. "S-P-F n° 1/n° 2").
        unite (str): Unité métrique (ex. "MPa"). Vide si sans unité.
        grandeur (str | None): Grandeur pour la conversion en impérial (voir unites.GRANDEURS).
            None si la donnée n'a pas d'équivalent impérial.
        source (str): Provenance (ex. "Tableau 6.4"). Vide si entrée par l'utilisateur.
    """

    symbole: str
    description: str
    valeur: float | str
    unite: str = ""
    grandeur: str | None = None
    source: str = ""


@dataclass(frozen=True)
class Etape:
    """
    Une étape de calcul (ligne du tableau « Calcul » de la note de calcul).

    Args:
        article (str): Article de la norme (ex. "6.5.5.2.5").
        description (str): Description (ex. "Coefficient d'élancement").
        symbole (str): Symbole du résultat en LaTeX (ex. "K_C").
        formule (str): Formule avec les symboles, en LaTeX.
        substitution (str): Formule avec les valeurs remplacées, en LaTeX.
        valeur (float): Résultat de l'étape, en unités métriques.
        unite (str): Unité métrique du résultat. Vide si sans unité.
        grandeur (str | None): Grandeur pour l'affichage en impérial, si pertinent.
    """

    article: str
    description: str
    symbole: str
    formule: str
    substitution: str
    valeur: float
    unite: str = ""
    grandeur: str | None = None


@dataclass
class Resultat:
    """
    Trace complète d'une vérification.

    Args:
        norme (str): Norme et édition (ex. "CSA O86:19").
        article (str): Article principal de la vérification (ex. "6.5.5").
        titre (str): Titre de la vérification (ex. "Compression parallèle au fil").
        figure (str | None): Identifiant de la figure schématique (ex. "colonne_compression").
        donnees (list[Donnee]): Données d'entrée.
        etapes (list[Etape]): Étapes de calcul, dans l'ordre.
        verification (Verification | None): Vérification finale (effet / résistance).
    """

    norme: str
    article: str
    titre: str
    figure: str | None = None
    donnees: list[Donnee] = field(default_factory=list)
    etapes: list[Etape] = field(default_factory=list)
    verification: Verification | None = None

    def ajouter_donnee(self, donnee: Donnee) -> float | str:
        """Ajoute une donnée et retourne sa valeur."""
        self.donnees.append(donnee)
        return donnee.valeur

    def ajouter_etape(self, etape: Etape) -> float:
        """Ajoute une étape et retourne sa valeur, pour enchaîner les calculs."""
        self.etapes.append(etape)
        return etape.valeur

    def etape(self, symbole: str) -> Etape:
        """
        Retourne la dernière étape dont le symbole correspond.

        Raises:
            KeyError: Si aucune étape n'a ce symbole.
        """
        for etape in reversed(self.etapes):
            if etape.symbole == symbole:
                return etape
        raise KeyError(f"Aucune étape avec le symbole {symbole!r}.")
