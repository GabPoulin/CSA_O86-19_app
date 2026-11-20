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
import re
from dataclasses import dataclass
from pathlib import Path

import typst

from moteur.commun.figures import figure
from moteur.commun.resultat import Resultat, Verification
from moteur.commun.nombres import cs
from moteur.commun.unites import deux_unites, grandeur, vers_imperial

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


COULEUR_PRINCIPALE = "#233614"  # vert forêt (marque/couleurs.md)
COULEUR_ACCENT = "#9E5A00"  # orange brûlé
LONGUEUR_UNE_LIGNE = 55  # caractères LaTeX : au-delà, la formule s'écrit sur plusieurs lignes


@dataclass(frozen=True)
class Apparence:
    """
    Logo et couleurs de la note (ceux de la marque par défaut ; l'utilisateur peut mettre les siens).

    Args:
        logo (bytes | None): Image du logo (PNG, JPG ou SVG). None : le nom du logiciel (Datum).
        principale (str): Couleur principale, hexadécimale (titres, lignes, en-têtes de tableau).
        accent (str): Couleur d'accent, hexadécimale (articles, sources).
        police_titres (str | None): Famille de police des titres, en majuscules (ex. « Rift »). None :
            police par défaut.
        police_texte (str | None): Famille de police du texte courant (ex. « DIN 2014 »). None :
            police par défaut.
        dossier_polices (Path | None): Dossier des fichiers de polices (.otf, .ttf). Une police absente
            est remplacée par la police par défaut.
    """

    logo: bytes | None = None
    principale: str = COULEUR_PRINCIPALE
    accent: str = COULEUR_ACCENT
    police_titres: str | None = None
    police_texte: str | None = None
    dossier_polices: Path | None = None


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


def formater_resultat(valeur: float, unite: str = "", nom_grandeur: str | None = None) -> str:
    """
    Résultat d'un calcul (étape ou vérification) avec le même nombre de chiffres significatifs partout
    (moteur/commun/nombres.py), et son équivalent impérial si la grandeur est connue.

    Exemple : formater_resultat(11.8, "MPa", "contrainte") -> « 11.80 MPa (1711 psi) ».
    """
    if nom_grandeur is None:
        return f"{cs(valeur)} {unite}".strip()
    g = grandeur(nom_grandeur)
    return (
        f"{cs(valeur)} {g.unite_metrique} "
        f"({cs(vers_imperial(valeur, nom_grandeur))} {g.unite_imperiale})"
    )


def calcul_en_latex(formule: str, substitution: str) -> str:
    """
    Ligne de calcul d'une étape : « formule = substitution ». Si elle est longue, les égalités vont sur
    plusieurs lignes alignées (demande de l'utilisateur, revue de la PR #55) :

        K_N &= [...]
            &= [valeurs]
    """
    if len(formule) + len(substitution) <= LONGUEUR_UNE_LIGNE or " = " not in formule:
        return f"{formule} = {substitution}"
    gauche, droite = formule.split(" = ", 1)
    return (
        r"\begin{aligned} " + gauche + r" &= " + droite + r" \\ &= " + substitution
        + r" \end{aligned}"
    )


def _verification(v: Verification) -> dict:
    return {
        "article": v.article,
        "symbole_charge": v.symbole_charge,
        "symbole_resistance": v.symbole_resistance,
        "charge": formater_resultat(v.charge, v.unite, v.grandeur),
        "resistance": formater_resultat(v.resistance, v.unite, v.grandeur),
        "ratio": f"{v.ratio * 100:.2f} %" if v.resistance > 0 else "—",
        "respecte": v.respecte,
        # Sans le ratio, déjà affiché à part (revue de la PR #55)
        "message": (
            ("État limite respecté" if v.respecte else "État limite dépassé")
            if v.resistance > 0
            else v.message()
        ),
    }


def donnees_de_la_note(
    resultats: list[tuple],
    entete: EnTete,
    apparence: Apparence = Apparence(),
    commentaires: str = "",
) -> dict:
    """
    Données transmises au gabarit Typst (aussi utilisées par les tests).

    Args:
        resultats (list[tuple]): (nom de l'élément, trace) ou (nom de l'élément, trace, en test), dans
            l'ordre de la note. « en test » (bool) : affiche l'avertissement de la fonction en test
            (acces.py, issue #56).
        entete (EnTete): Champs de l'en-tête.
        apparence (Apparence, optional): Logo et couleurs. Default to ceux de la marque.
        commentaires (str, optional): Commentaires de l'ingénieur, en bas à gauche de la première
            page, à côté de la vérification et du sceau (datum-retours #3). Default to "" (aucun).

    Returns:
        dict: Données sérialisables en JSON.
    """
    normes = sorted({r[1].norme for r in resultats})
    note = {
        "entete": {**vars(entete), "norme": ", ".join(normes)},
        "apparence": {
            "logo": list(apparence.logo) if apparence.logo else None,  # octets, pour Typst
            "principale": apparence.principale,
            "accent": apparence.accent,
            "police_titres": apparence.police_titres,
            "police_texte": apparence.police_texte,
        },
        "commentaires": commentaires.strip(),
        "resultats": [],
    }
    for element, r, *option in resultats:
        note["resultats"].append({
            "en_test": bool(option and option[0]),
            "norme": r.norme,
            "article": r.article,
            "titre": r.titre,
            "element": element,
            "figure": r.figure or "",
            # Figure schématique dans les couleurs du compte (issue #62) ; None : pas encore de figure
            "figure_svg": figure(r, apparence.principale, apparence.accent),
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
                    "calcul": calcul_en_latex(e.formule, e.substitution),
                    "resultat": formater_resultat(e.valeur, e.unite, e.grandeur),
                }
                for e in r.etapes
            ],
            "verification": _verification(r.verification) if r.verification else None,
        })
    return note


def nom_du_pdf(titre: str, date: str = "", dossier: str = "") -> str:
    """
    Nom du fichier PDF (datum-retours #4) : « AAAAMMJJ_NUMERO-AA-XXX_titre.pdf », soit la date, le
    numéro de dossier et le titre de la note, séparés par « _ ». Une partie vide est omise, avec son
    « _ ». Les caractères interdits dans un nom de fichier (/ \\ : * ? " < > |) deviennent « - ».
    Les espaces du titre deviennent « _ » ; ceux du numéro de dossier, « - ».

    Exemple : nom_du_pdf("Poutre P-1 : 3-2x10", "2026-11-20", "LR-26-012")
    -> « 20261120_LR-26-012_Poutre_P-1-3-2x10.pdf ».

    Args:
        titre (str): Titre de la note.
        date (str, optional): Date de la note, AAAA-MM-JJ. Default to "" (omise).
        dossier (str, optional): Numéro de dossier. Default to "" (omis).

    Returns:
        str: Nom du fichier, avec l'extension .pdf ; « note_de_calcul.pdf » si tout est vide.
    """

    def nettoyer(partie: str, espace: str) -> str:
        partie = re.sub(r'\s*[/\\:*?"<>|-]+\s*', "-", partie.strip())  # interdits -> « - »
        partie = re.sub(r"\s+", espace, partie)
        return re.sub(r"([-_])\1+", r"\1", partie).strip(" .-_")

    parties = [nettoyer(date.replace("-", ""), "-"), nettoyer(dossier, "-"), nettoyer(titre, "_")]
    nom = "_".join(p for p in parties if p)
    return f"{nom or 'note_de_calcul'}.pdf"


def produire_pdf(
    resultats: list[tuple],
    entete: EnTete,
    apparence: Apparence = Apparence(),
    commentaires: str = "",
) -> bytes:
    """
    Produit la note de calcul PDF.

    Args:
        resultats (list[tuple]): Voir donnees_de_la_note().
        entete (EnTete): Champs de l'en-tête.
        apparence (Apparence, optional): Logo et couleurs. Default to ceux de la marque.
        commentaires (str, optional): Voir donnees_de_la_note().

    Returns:
        bytes: Contenu du fichier PDF.

    Raises:
        ValueError: Si aucune vérification n'est fournie.
    """
    if not resultats:
        raise ValueError("Aucune vérification à mettre dans la note de calcul.")
    donnees = json.dumps(donnees_de_la_note(resultats, entete, apparence, commentaires), ensure_ascii=False)
    polices = (
        [str(apparence.dossier_polices)]
        if apparence.dossier_polices and apparence.dossier_polices.is_dir()
        else []
    )
    return typst.compile(
        str(GABARIT), root=str(RACINE), font_paths=polices, sys_inputs={"donnees": donnees}
    )
