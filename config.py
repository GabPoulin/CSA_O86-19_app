"""Paramètres partagés de l'interface : nom du produit et image de marque (voir marque/)."""

import json
import re
import tomllib
from pathlib import Path

import streamlit as st

import acces
import retours
from moteur.commun import registre
from moteur.commun.note_de_calcul import Apparence

TITLE = "Datum"  # nom du logiciel : seul nom affiché, sans marque
SOUS_TITRE = "Calculatrice Structurale"  # en petit sous le nom
NOM_COURT = TITLE  # onglet du navigateur
# Logo de Datum : symbole de Le Repère, sans le nom (onglet du navigateur et page de connexion)
SYMBOLE_DE_DATUM = "marque/logos/LeRepere_symbole_gris.svg"
ICONE_PAR_DEFAUT = SYMBOLE_DE_DATUM  # onglet du navigateur avant la connexion
# Thème global de l'interface (.streamlit/config.toml) : couleurs remplacées par celles du compte
THEME = tomllib.loads(
    (Path(__file__).resolve().parent / ".streamlit" / "config.toml").read_text(encoding="utf-8")
)["theme"]

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


def eclaircir(couleur: str, part: float) -> str:
    """Couleur (#RRGGBB) mélangée avec du blanc : part = 0 (inchangée) à 1 (blanc)."""
    canaux = (int(couleur[i : i + 2], 16) for i in (1, 3, 5))
    return "#" + "".join(f"{round(c + (255 - c) * part):02X}" for c in canaux)


def fond_du_compte(compte: str, dossier: Path = DOSSIER_COMPTES) -> str | None:
    """Couleur de fond de l'interface du compte (clé « fond » de couleurs.toml), ou None."""
    fichier = fichier_du_compte(compte, "couleurs.toml", dossier)
    if fichier is None:
        return None
    fond = tomllib.loads(fichier.read_text(encoding="utf-8")).get("fond")
    if fond is not None and not _COULEUR.match(str(fond)):
        raise ValueError(f"{fichier} : couleur « fond » invalide (format #RRGGBB).")
    return fond


def rvb(couleur: str) -> str:
    """« #RRGGBB » -> « R, V, B » (format des couleurs dans le CSS calculé par le navigateur)."""
    return ", ".join(str(int(couleur[i : i + 2], 16)) for i in (1, 3, 5))


def remplacements_du_theme(accent: str, fond: str | None) -> list[tuple[str, str]]:
    """
    Couleurs du thème global à remplacer dans le CSS de la page : couleur principale du thème
    (accents : cases, boutons radio, onglets, liens) par l'accent du compte, et fond par celui du compte.
    """
    paires = [(THEME["primaryColor"], accent)]
    if fond:
        paires.append((THEME["backgroundColor"], fond))
    return [(rvb(a), rvb(b)) for a, b in paires if a.lower() != b.lower()]


# Remplace des couleurs dans toutes les règles CSS de la page (Streamlit en ajoute au fil de l'eau).
# Les couleurs viennent de couleurs.toml, validées au format #RRGGBB : aucune donnée de l'utilisateur.
_SCRIPT_COULEURS = """<script>
(() => {
  const paires = %s;
  const traiter = (regles) => {
    for (const r of regles) {
      if (r.cssRules) traiter(r.cssRules);
      if (!r.style) continue;
      for (let i = 0; i < r.style.length; i++) {
        const p = r.style[i], v = r.style.getPropertyValue(p);
        let n = v;
        for (const [a, b] of paires) n = n.split(a).join(b);
        if (n !== v) r.style.setProperty(p, n, r.style.getPropertyPriority(p));
      }
    }
  };
  const tout = () => { for (const f of document.styleSheets) { try { traiter(f.cssRules); } catch (e) {} } };
  tout();
  clearInterval(window.__datumCouleurs);
  window.__datumCouleurs = setInterval(tout, 400);
})();
</script>"""


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
        page_title=f"{titre_page} | {NOM_COURT}", page_icon=str(symbole) if symbole else ICONE_PAR_DEFAUT
    )
    compte = acces.exiger_connexion()
    logo = fichier_du_compte(compte, "logo_renverse.svg")  # barre latérale foncée
    if logo:
        st.logo(str(logo), size="large", icon_image=str(symbole or logo))
    apparence = apparence_du_compte(compte)
    st.html(
        f"""<style>
        [data-testid="stSidebar"] {{ background-color: {apparence.principale}; }}
        [data-testid="stSidebar"] button {{
            background-color: {eclaircir(apparence.principale, 0.10)};
            border-color: {eclaircir(apparence.principale, 0.30)};
            color: #FFFFFF;
        }}
        [data-testid="stSidebar"] button:hover {{
            background-color: {eclaircir(apparence.principale, 0.20)};
            border-color: {eclaircir(apparence.principale, 0.50)};
        }}
        [data-testid="stBaseButton-primary"] {{
            background-color: {apparence.accent}; border-color: {apparence.accent};
            color: {couleur_du_texte(apparence.accent)};
        }}
        </style>"""
    )
    paires = remplacements_du_theme(apparence.accent, fond_du_compte(compte))
    if paires:
        st.html(_SCRIPT_COULEURS % json.dumps(paires), unsafe_allow_javascript=True)
    retours.formulaire(titre_page)


def choisir_edition() -> str:
    """
    Sélecteur « Norme et édition » dans la barre latérale (issue #72). Les options viennent du
    registre (moteur/commun/registre.py) : une nouvelle édition (ex. csa_o86_24/) y apparaît d'elle-même
    dès qu'elle inscrit un calcul. Le choix est gardé pour la séance (st.session_state["edition"]).

    Returns:
        str: Dossier de l'édition choisie (ex. « csa_o86_19 »).
    """
    editions = []
    for edition in registre.editions():
        try:
            registre.nom_de_l_edition(edition)
        except KeyError:  # calculs inscrits hors d'un dossier de norme (ex. tests du registre)
            continue
        editions.append(edition)
    return st.sidebar.selectbox(
        "Norme et édition",
        options=editions,
        format_func=registre.nom_de_l_edition,
        key="edition",
        help="Seuls les calculs de cette édition sont offerts.",
    )


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
        for cle in ("principale", "accent", "fond"):
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
