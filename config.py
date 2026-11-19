"""Paramètres partagés de l'interface : nom du produit et image de marque (voir marque/)."""

import re
import tomllib
from pathlib import Path

import streamlit as st

import acces
import retours
from moteur.commun.note_de_calcul import Apparence

TITLE = "Datum"  # nom du logiciel : seul nom affiché, sans marque (chaque compte a la sienne)
ICONE_PAR_DEFAUT = ":material/architecture:"  # onglet du navigateur avant la connexion

# Image de marque propre à chaque compte : marque/comptes/<compte>/ (logo, couleurs, polices)
DOSSIER_COMPTES = Path(__file__).resolve().parent / "marque" / "comptes"
LOGOS_DU_COMPTE = ("logo.svg", "logo.png", "logo.jpg", "logo.jpeg")
_COULEUR = re.compile(r"^#[0-9A-Fa-f]{6}$")


def fichier_du_compte(compte: str, nom: str, dossier: Path = DOSSIER_COMPTES) -> Path | None:
    """
    Fichier d'image de marque d'un compte (ex. « logo_renverse.svg »), ou None s'il n'existe pas.

    Args:
        compte (str): Identifiant du compte (ex. « lantier »).
        nom (str): Nom du fichier.
        dossier (Path, optional): Dossier des comptes. Default to marque/comptes/.

    Returns:
        Path | None: Chemin du fichier.
    """
    if not compte or not re.fullmatch(r"[a-z_]+", compte):
        return None
    fichier = dossier / compte / nom
    return fichier if fichier.is_file() else None


def couleur_du_texte(fond: str) -> str:
    """Blanc ou charbon, selon ce qui contraste le plus avec la couleur de fond (#RRGGBB)."""
    r, v, b = (int(fond[i : i + 2], 16) / 255 for i in (1, 3, 5))
    luminance = 0.2126 * r + 0.7152 * v + 0.0722 * b
    return "#FFFFFF" if luminance < 0.5 else "#333333"


def configurer_page(titre_page: str) -> None:
    """
    Configure la page à l'image du compte connecté : titre de l'onglet, icône, logo de la barre
    latérale et couleurs. Seul le nom du logiciel (Datum) est affiché avant la connexion.

    Doit être appelée en premier dans chaque page Streamlit. Exige la connexion (acces.py) et ajoute
    le bouton « Commentaire » (retours.py) dans la barre latérale (issue #56).
    """
    compte = st.session_state.get("compte", "")
    symbole = fichier_du_compte(compte, "symbole.svg")
    st.set_page_config(
        page_title=f"{titre_page} | {TITLE}", page_icon=str(symbole) if symbole else ICONE_PAR_DEFAUT
    )
    compte = acces.exiger_connexion()
    logo = fichier_du_compte(compte, "logo_renverse.svg")  # barre latérale foncée
    if logo:
        st.logo(str(logo), size="large", icon_image=str(symbole or logo))
    apparence = apparence_du_compte(compte)
    st.html(
        f"""<style>
        [data-testid="stSidebar"] {{ background-color: {apparence.principale}; }}
        [data-testid="stBaseButton-primary"] {{
            background-color: {apparence.accent}; border-color: {apparence.accent};
            color: {couleur_du_texte(apparence.accent)};
        }}
        </style>"""
    )
    retours.formulaire(titre_page)


def apparence_du_compte(compte: str, dossier: Path = DOSSIER_COMPTES) -> Apparence:
    """
    Logo et couleurs de la note de calcul d'un compte (marque/comptes/<compte>/, voir son README).

    Le premier fichier trouvé parmi logo.svg, logo.png, logo.jpg et logo.jpeg sert de logo. Les
    couleurs viennent de couleurs.toml (clés « principale » et « accent », ex. "#233614"). Les polices
    viennent de polices.toml (clés « titres » et « texte », noms de familles) et du dossier polices/
    (fichiers .otf ou .ttf, ignoré par git : polices sous licence). Ce qui manque garde la valeur par
    défaut.

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
