"""
Accès à l'application : comptes, connexion par mot de passe et fonctions offertes à chaque compte
(issue #56).

- Deux comptes : « admin » (tout) et « lantier » (Groupe Lantier : seulement les fonctions complètes
  et testées, choisies par l'utilisateur).
- Les mots de passe sont dans les secrets de Streamlit Cloud (section [mots_de_passe]), jamais dans
  le code. En local : .streamlit/secrets.toml (ignoré par git).
- Une fonction « en test » affiche un avertissement, retiré quand l'utilisateur confirme qu'elle est
  testée convenablement.

Aucune logique de calcul ici.
"""

import hmac
from dataclasses import dataclass

import streamlit as st

ADMIN = "admin"
LANTIER = "lantier"
NOMS_DES_COMPTES = {ADMIN: "Administrateur", LANTIER: "Groupe Lantier"}


@dataclass(frozen=True)
class Fonction:
    """
    Une fonction de l'application.

    Args:
        nom (str): Nom affiché (ex. « Flexion (6.5.3) »).
        en_test (bool): True tant qu'elle n'est pas testée convenablement : un avertissement s'affiche.
    """

    nom: str
    en_test: bool = True


# Fonctions de l'application, dans l'ordre de la page. « en_test » : à retirer fonction par fonction
# quand l'utilisateur confirme qu'elle est testée convenablement (issue #56).
FONCTIONS: dict[str, Fonction] = {
    "flexion": Fonction("Flexion (6.5.3)"),
    "cisaillement": Fonction("Cisaillement (6.5.4)"),
    "compression_parallele": Fonction("Compression parallèle au fil (6.5.5)"),
    "compression_perpendiculaire": Fonction("Compression perpendiculaire au fil (6.5.6)"),
    "compression_oblique": Fonction("Compression oblique (6.5.7)"),
    "traction": Fonction("Traction parallèle au fil (6.5.8)"),
    "flexion_et_charge_axiale": Fonction("Flexion et charge axiale combinée (6.5.9)"),
    "note_pdf": Fonction("Note de calcul PDF"),
}

# Fonctions offertes à chaque compte. Groupe Lantier : liste à fournir par l'utilisateur (issue #56).
ACCES: dict[str, frozenset[str]] = {
    ADMIN: frozenset(FONCTIONS),
    LANTIER: frozenset(),
}

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
    if FONCTIONS[fonction].en_test:
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
    st.title("Datum", anchor=False)
    st.caption("par Le Repère Ingénierie")
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
