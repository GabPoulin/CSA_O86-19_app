"""
Note de calcul PDF (ARCHITECTURE.md, section 8 ; issue #50).

Transforme une ou plusieurs traces de calcul (Resultat) en PDF, avec le gabarit Typst gabarit.typ
(format Lettre, 8.5 x 11 po). Aucune logique de calcul ici : les valeurs viennent telles quelles de la
trace. Les données et les résultats sont affichés dans les deux unités (ex. « 38 mm (1.50 po) ») ; les
étapes intermédiaires restent en métrique, comme dans la norme.

Les formules LaTeX de la trace sont rendues par l'extension Typst « mitex » 0.2.7 (licence Apache-2.0),
incluse dans le dossier mitex/ pour ne dépendre d'aucun téléchargement.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import typst

from moteur.commun.resultat import Resultat, Verification
from moteur.commun.unites import deux_unites

DOSSIER = Path(__file__).resolve().parent
GABARIT = DOSSIER / "gabarit.typ"
RACINE = DOSSIER.parents[2]  # racine du dépôt : le gabarit lit le logo dans marque/


@dataclass(frozen=True)
class EnTete:
    """
    Champs de l'en-tête, répétés sur chaque page (format validé, ARCHITECTURE.md, section 8).

    Args:
        client (str): Nom du client.
        projet (str): Nom du projet.
        adresse (str): Adresse du projet.
        dossier (str): Numéro de dossier (ou de projet).
        date (str): Date de la note (ex. « 2026-11-19 »).
        ingenieur (str): Nom de l'ingénieur.
        oiq (str): Numéro de membre de l'Ordre des ingénieurs du Québec.
    """

    client: str = ""
    projet: str = ""
    adresse: str = ""
    dossier: str = ""
    date: str = ""
    ingenieur: str = ""
    oiq: str = ""


def formater_nombre(valeur: float) -> str:
    """
    Nombre affiché avec un point décimal (CLAUDE.md) : entier au-delà de 1000, 2 décimales de 10 à 1000,
    et 4 chiffres significatifs en dessous de 10 (ex. coefficients).
    """
    absolue = abs(valeur)
    if absolue >= 1000:
        return f"{valeur:.0f}"
    if absolue >= 10:
        return f"{valeur:.2f}"
    return f"{valeur:.4g}"


def formater_valeur(valeur: float | str, unite: str = "", grandeur: str | None = None) -> str:
    """Valeur avec son unité ; avec l'équivalent impérial si la grandeur est connue."""
    if isinstance(valeur, str):
        return valeur
    if grandeur is not None:
        return deux_unites(valeur, grandeur)
    return f"{formater_nombre(valeur)} {unite}".strip()


def _en_latex(texte: str) -> str:
    """Résultat formaté (nombre, unités) en texte LaTeX, en gras : \textbf{...}."""
    return r"\textbf{" + texte.replace("%", r"\%") + "}"


def _verification(v: Verification) -> dict:
    return {
        "article": v.article,
        "symbole_charge": v.symbole_charge,
        "symbole_resistance": v.symbole_resistance,
        "charge": formater_valeur(v.charge, v.unite, v.grandeur),
        "resistance": formater_valeur(v.resistance, v.unite, v.grandeur),
        "ratio": f"{v.ratio * 100:.2f} %" if v.resistance > 0 else "—",
        "respecte": v.respecte,
        "message": v.message(),
    }


def donnees_de_la_note(resultats: list[tuple[str, Resultat]], entete: EnTete) -> dict:
    """
    Données transmises au gabarit Typst (aussi utilisées par les tests).

    Args:
        resultats (list[tuple[str, Resultat]]): (nom de l'élément, trace), dans l'ordre de la note.
        entete (EnTete): Champs de l'en-tête.

    Returns:
        dict: Données sérialisables en JSON.
    """
    normes = sorted({r.norme for _, r in resultats})
    note = {"entete": {**vars(entete), "norme": ", ".join(normes)}, "resultats": []}
    for element, r in resultats:
        note["resultats"].append({
            "norme": r.norme,
            "article": r.article,
            "titre": r.titre,
            "element": element,
            "figure": r.figure or "",
            "donnees": [
                {
                    "symbole": d.symbole,
                    "description": d.description,
                    "valeur": formater_valeur(d.valeur, d.unite, d.grandeur),
                    "source": d.source,
                }
                for d in r.donnees
            ],
            "etapes": [
                {
                    "article": e.article,
                    "description": e.description,
                    "symbole": e.symbole,
                    "formule": e.formule,
                    "substitution": e.substitution,
                    "resultat": formater_valeur(e.valeur, e.unite, e.grandeur),
                    "resultat_latex": _en_latex(formater_valeur(e.valeur, e.unite, e.grandeur)),
                }
                for e in r.etapes
            ],
            "verification": _verification(r.verification) if r.verification else None,
        })
    return note


def produire_pdf(resultats: list[tuple[str, Resultat]], entete: EnTete) -> bytes:
    """
    Produit la note de calcul PDF.

    Args:
        resultats (list[tuple[str, Resultat]]): (nom de l'élément, trace), dans l'ordre de la note.
        entete (EnTete): Champs de l'en-tête.

    Returns:
        bytes: Contenu du fichier PDF.

    Raises:
        ValueError: Si aucune vérification n'est fournie.
    """
    if not resultats:
        raise ValueError("Aucune vérification à mettre dans la note de calcul.")
    donnees = json.dumps(donnees_de_la_note(resultats, entete), ensure_ascii=False)
    return typst.compile(str(GABARIT), root=str(RACINE), sys_inputs={"donnees": donnees})
