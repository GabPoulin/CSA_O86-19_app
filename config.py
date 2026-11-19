"""Paramètres partagés de l'interface : nom du produit et image de marque (voir marque/)."""

import re
import tomllib
from pathlib import Path

import streamlit as st

import acces
import retours
from moteur.commun.note_de_calcul import Apparence

TITLE = "Datum"
SOUS_TITRE = "par Le Repère Ingénierie"

# Logo horizontal blanc pour la barre latérale vert forêt ; symbole seul quand elle est repliée
LOGO_BARRE_LATERALE = "marque/logos/LeRepere_logo-horizontal_blanc.svg"
SYMBOLE_BARRE_LATERALE = "marque/logos/LeRepere_symbole_blanc.svg"
# Icône de l'onglet du navigateur
ICONE = "marque/logos/LeRepere_symbole_gris.png"

# Logo et couleurs de la note de calcul propres à un compte : marque/comptes/<compte>/
DOSSIER_COMPTES = Path(__file__).resolve().parent / "marque" / "comptes"
LOGOS_DU_COMPTE = ("logo.svg", "logo.png", "logo.jpg", "logo.jpeg")
_COULEUR = re.compile(r"^#[0-9A-Fa-f]{6}$")


def configurer_page(titre_page: str) -> None:
    """
    Configure la page (titre de l'onglet, icône) et affiche le logo dans la barre latérale.

    Doit être appelée en premier dans chaque page Streamlit. Exige la connexion (acces.py) et ajoute
    le bouton « Commentaire » (retours.py) dans la barre latérale (issue #56).
    """
    st.set_page_config(page_title=f"{titre_page} | {TITLE}", page_icon=ICONE)
    st.logo(LOGO_BARRE_LATERALE, size="large", icon_image=SYMBOLE_BARRE_LATERALE)
    acces.exiger_connexion()
    retours.formulaire(titre_page)


def apparence_du_compte(compte: str, dossier: Path = DOSSIER_COMPTES) -> Apparence:
    """
    Logo et couleurs de la note de calcul d'un compte (marque/comptes/<compte>/, voir son README).

    Le premier fichier trouvé parmi logo.svg, logo.png, logo.jpg et logo.jpeg sert de logo. Les
    couleurs viennent de couleurs.toml (clés « principale » et « accent », ex. "#233614"). Les polices
    viennent de polices.toml (clés « titres » et « texte », noms de familles) et du dossier polices/
    (fichiers .otf ou .ttf, ignoré par git : polices sous licence). Ce qui manque garde la valeur par
    défaut (Le Repère).

    Args:
        compte (str): Identifiant du compte (ex. « lantier »).
        dossier (Path, optional): Dossier des comptes. Default to marque/comptes/.

    Returns:
        Apparence: Logo et couleurs.

    Raises:
        ValueError: Si une couleur de couleurs.toml n'est pas au format #RRGGBB.
    """
    defaut = Apparence()
    if not compte or not re.fullmatch(r"[a-z_]+", compte):
        return defaut
    dossier_du_compte = dossier / compte
    logo = next(
        (f.read_bytes() for nom in LOGOS_DU_COMPTE if (f := dossier_du_compte / nom).is_file()), None
    )
    couleurs = {}
    fichier_couleurs = dossier_du_compte / "couleurs.toml"
    if fichier_couleurs.is_file():
        couleurs = tomllib.loads(fichier_couleurs.read_text(encoding="utf-8"))
        for cle in ("principale", "accent"):
            if cle in couleurs and not _COULEUR.match(str(couleurs[cle])):
                raise ValueError(f"{fichier_couleurs} : couleur « {cle} » invalide (format #RRGGBB).")
    polices = {}
    fichier_polices = dossier_du_compte / "polices.toml"
    if fichier_polices.is_file():
        polices = tomllib.loads(fichier_polices.read_text(encoding="utf-8"))
    return Apparence(
        logo,
        couleurs.get("principale", defaut.principale),
        couleurs.get("accent", defaut.accent),
        polices.get("titres"),
        polices.get("texte"),
        dossier_du_compte / "polices",
    )
