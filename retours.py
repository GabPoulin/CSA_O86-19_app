"""
Commentaires des utilisateurs (issue #56) : un formulaire dans la barre latérale crée une issue dans un
dépôt GitHub privé (secrets [retours] : jeton et depot). Les utilisateurs n'ont pas besoin de compte
GitHub, et les commentaires ne sont pas publics.

Aucune logique de calcul ici.
"""

import json
import urllib.request

import streamlit as st

import acces

API_GITHUB = "https://api.github.com"
ETIQUETTE = "retour"
OUVERT = "commentaire_ouvert"  # fenêtre de dialogue ouverte (session)


def corps_de_l_issue(page: str, fonction: str, commentaire: str, nom: str, compte: str) -> str:
    """Texte de l'issue créée dans le dépôt des commentaires."""
    return (
        f"**Page** : {page}\n"
        f"**Fonction** : {fonction}\n"
        f"**Compte** : {acces.NOMS_DES_COMPTES.get(compte, compte)}\n"
        f"**Nom** : {nom or '(non indiqué)'}\n\n"
        f"{commentaire}\n"
    )


def creer_issue(titre: str, corps: str, jeton: str, depot: str) -> str:
    """
    Crée l'issue dans le dépôt des commentaires (API GitHub).

    Returns:
        str: Adresse de l'issue créée.
    """
    requete = urllib.request.Request(
        f"{API_GITHUB}/repos/{depot}/issues",
        data=json.dumps({"title": titre, "body": corps, "labels": [ETIQUETTE]}).encode(),
        headers={
            "Authorization": f"Bearer {jeton}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "datum",
        },
        method="POST",
    )
    with urllib.request.urlopen(requete, timeout=15) as reponse:
        return json.load(reponse)["html_url"]


def formulaire(page: str) -> None:
    """
    Bouton « Commentaire » dans la barre latérale. Il ouvre une fenêtre de dialogue (thème clair de
    la page : le texte des champs d'un popover de la barre latérale était illisible).
    """
    try:
        secrets = st.secrets["retours"]
        jeton, depot = secrets["jeton"], secrets["depot"]
    except (KeyError, FileNotFoundError):
        return  # commentaires non configurés : pas de bouton
    if st.sidebar.button("Commentaire", icon=":material/chat:", use_container_width=True):
        st.session_state[OUVERT] = True
    if st.session_state.get(OUVERT):
        _dialogue(page, jeton, depot)


def _fermer() -> None:
    st.session_state[OUVERT] = False


@st.dialog("Commentaire", on_dismiss=_fermer)
def _dialogue(page: str, jeton: str, depot: str) -> None:
    """Formulaire d'envoi d'un commentaire (crée une issue dans le dépôt privé des commentaires)."""
    compte = st.session_state.get("compte", "")
    fonctions = [f.nom for cle, f in acces.FONCTIONS.items() if acces.permis(cle, compte)]
    with st.form("commentaire", clear_on_submit=True, border=False):
        fonction = st.selectbox("Fonction", ["Général"] + fonctions)
        commentaire = st.text_area("Commentaire, erreur ou suggestion")
        nom = st.text_input("Votre nom (facultatif)")
        if st.form_submit_button("Envoyer", icon=":material/send:", type="primary"):
            if not commentaire.strip():
                st.warning("Écrivez un commentaire avant d'envoyer.")
                return
            titre = f"[{fonction}] {commentaire.strip().splitlines()[0][:60]}"
            try:
                creer_issue(titre, corps_de_l_issue(page, fonction, commentaire, nom, compte), jeton, depot)
            except OSError:
                st.error("L'envoi a échoué. Réessayez plus tard.")
            else:
                st.success("Merci ! Votre commentaire a été envoyé.")
