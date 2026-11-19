"""
Accès à l'application : comptes, connexion par mot de passe et fonctions offertes à chaque compte
(issue #56).

- Deux comptes : « admin » (tout) et « lantier » (Groupe Lantier : seulement les fonctions complètes
  et testées, choisies par l'utilisateur).
- Les mots de passe sont dans les secrets de Streamlit Cloud (section [mots_de_passe]), jamais dans
  le code. En local : .streamlit/secrets.toml (ignoré par git).
- Les fonctions offertes au compte Groupe Lantier et les fonctions testées sont lues dans
  ACCES_GROUPE_LANTIER.md : l'utilisateur coche les cases (demande dans l'issue #56).
- Une fonction non cochée comme « testée » affiche un avertissement « en test ».

Aucune logique de calcul ici.
"""

import hmac
import re
from dataclasses import dataclass
from pathlib import Path

import streamlit as st

ADMIN = "admin"
LANTIER = "lantier"
NOMS_DES_COMPTES = {ADMIN: "Administrateur", LANTIER: "Groupe Lantier"}


FICHIER_ACCES = Path(__file__).resolve().parent / "ACCES_GROUPE_LANTIER.md"
SECTION_OFFERTES = "## Fonctions offertes au compte Groupe Lantier"
SECTION_TESTEES = "## Fonctions testées convenablement"
_CASE = re.compile(r"^- \[([ xX])\] `([a-z_]+)`")


@dataclass(frozen=True)
class Fonction:
    """
    Une fonction de l'application.

    Args:
        nom (str): Nom affiché (ex. « Flexion (6.5.3) »).
    """

    nom: str


# Fonctions de l'application, dans l'ordre de la page (identifiants de ACCES_GROUPE_LANTIER.md)
FONCTIONS: dict[str, Fonction] = {
    "flexion": Fonction("Flexion (6.5.3)"),
    "cisaillement": Fonction("Cisaillement (6.5.4)"),
    "compression_parallele": Fonction("Compression parallèle au fil (6.5.5)"),
    "compression_perpendiculaire": Fonction("Compression perpendiculaire au fil (6.5.6)"),
    "compression_oblique": Fonction("Compression oblique par rapport au fil (6.5.7)"),
    "traction": Fonction("Traction parallèle au fil (6.5.8)"),
    "flexion_et_charge_axiale": Fonction("Flexion et charge axiale combinée (6.5.9)"),
    "note_pdf": Fonction("Note de calcul PDF"),
}


def lire_cases(texte: str) -> dict[str, frozenset[str]]:
    """
    Cases cochées de ACCES_GROUPE_LANTIER.md, par section.

    Args:
        texte (str): Contenu du fichier.

    Returns:
        dict[str, frozenset[str]]: {"offertes": ..., "testees": ...} (identifiants cochés).

    Raises:
        ValueError: Si une section manque ou si un identifiant est inconnu.
    """
    sections = {SECTION_OFFERTES: "offertes", SECTION_TESTEES: "testees"}
    cochees: dict[str, set[str]] = {"offertes": set(), "testees": set()}
    trouvees, courante = set(), None
    for ligne in texte.splitlines():
        if ligne.startswith("## "):
            courante = sections.get(ligne.strip())
            if courante:
                trouvees.add(courante)
            continue
        case = _CASE.match(ligne.strip())
        if case and courante:
            identifiant = case.group(2)
            if identifiant not in FONCTIONS:
                raise ValueError(f"Fonction inconnue dans ACCES_GROUPE_LANTIER.md : {identifiant!r}.")
            if case.group(1) in "xX":
                cochees[courante].add(identifiant)
    if trouvees != {"offertes", "testees"}:
        raise ValueError("ACCES_GROUPE_LANTIER.md : section manquante.")
    return {cle: frozenset(valeurs) for cle, valeurs in cochees.items()}


_CASES = lire_cases(FICHIER_ACCES.read_text(encoding="utf-8"))

# Fonctions offertes à chaque compte : admin voit tout ; Groupe Lantier, les cases cochées.
ACCES: dict[str, frozenset[str]] = {
    ADMIN: frozenset(FONCTIONS),
    LANTIER: _CASES["offertes"],
}
TESTEES: frozenset[str] = _CASES["testees"]


def en_test(fonction: str) -> bool:
    """True si la fonction n'est pas encore cochée comme testée (ACCES_GROUPE_LANTIER.md)."""
    return fonction not in TESTEES


MESSAGE_EN_TEST = (
    "En test : vérifiez les résultats avant de les utiliser dans un dossier. Vos commentaires sont "
    "les bienvenus (bouton « Commentaire » dans la barre latérale)."
)


def compte_pour(mot_de_passe: str, mots_de_passe: dict[str, str]) -> str | None:
    """
    Compte correspondant à un mot de passe, ou None.

    Compare tous les mots de passe en temps constant (hmac.compare_digest), sans s'arrêter au premier,
    pour ne rien révéler par le temps de réponse.

    Args:
        mot_de_passe (str): Mot de passe entré.
        mots_de_passe (dict[str, str]): Compte -> mot de passe (secrets).

    Returns:
        str | None: ADMIN, LANTIER ou None.
    """
    trouve = None
    for compte, attendu in mots_de_passe.items():
        if compte in NOMS_DES_COMPTES and attendu and hmac.compare_digest(
            mot_de_passe.encode(), str(attendu).encode()
        ):
            trouve = compte
    return trouve


def permis(fonction: str, compte: str | None = None) -> bool:
    """True si la fonction est offerte au compte (par défaut : le compte connecté)."""
    compte = compte if compte is not None else st.session_state.get("compte")
    return fonction in ACCES.get(compte, frozenset())


def avertir_si_en_test(fonction: str) -> None:
    """Affiche l'avertissement « en test » si la fonction n'est pas encore testée convenablement."""
    if en_test(fonction):
        st.warning(MESSAGE_EN_TEST, icon=":material/science:", width=650)


def _mots_de_passe() -> dict[str, str]:
    try:
        return dict(st.secrets["mots_de_passe"])
    except (KeyError, FileNotFoundError):
        return {}


def exiger_connexion() -> str:
    """
    Affiche l'écran de connexion et arrête la page tant que l'utilisateur n'est pas connecté.

    Returns:
        str: Compte connecté (ADMIN ou LANTIER).
    """
    if st.session_state.get("compte") in NOMS_DES_COMPTES:
        compte = st.session_state["compte"]
        with st.sidebar:
            st.caption(f"Connecté : {NOMS_DES_COMPTES[compte]}")
            if st.button("Se déconnecter", icon=":material/logout:"):
                del st.session_state["compte"]
                st.rerun()
        return compte

    mots_de_passe = _mots_de_passe()
    with st.container(horizontal=True, vertical_alignment="center", gap="small"):
        st.image(str(Path(__file__).resolve().parent / "marque" / "logos" / "LeRepere_symbole_gris.svg"),
                 width=56)
        with st.container(gap=None):
            st.title("Datum", anchor=False)
            st.caption("Calculatrice Structurale")
    if not mots_de_passe:
        st.error(
            "Connexion non configurée : ajoutez la section [mots_de_passe] aux secrets de "
            "l'application (voir l'issue #56).",
            icon=":material/lock:",
        )
        st.stop()
    with st.form("connexion", width=400):
        mot_de_passe = st.text_input("Mot de passe", type="password")
        if st.form_submit_button("Se connecter", icon=":material/login:"):
            compte = compte_pour(mot_de_passe, mots_de_passe)
            if compte is None:
                st.error("Mot de passe invalide.", icon=":material/error:")
            else:
                st.session_state["compte"] = compte
                st.rerun()
    st.stop()
