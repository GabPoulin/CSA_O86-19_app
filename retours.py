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
# Champs du formulaire dans la barre latérale : fond pâle et texte foncé (le thème de la barre latérale
# donnait du texte pâle sur fond pâle, ou foncé sur fond foncé).
STYLE_DES_CHAMPS = """<style>
[data-testid="stSidebar"] [data-testid="stExpander"] :is(input, textarea),
[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stSelectbox"] [role="group"],
[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stSelectbox"] [role="group"] button,
[data-testid="stSidebar"] [data-testid="stExpander"] :is([data-baseweb="textarea"], [data-baseweb="input"]) {
    background-color: #FFFFFF !important; color: #333333 !important;
    -webkit-text-fill-color: #333333 !important; caret-color: #333333 !important;
    border-color: #FFFFFF !important;
}
/* Liste déroulante de « Fonction » : affichée hors de la barre latérale, mais avec son texte pâle */
[data-testid="stSelectboxVirtualDropdown"] [role="option"] {
    color: #333333 !important;
}
</style>"""


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
    Formulaire « Commentaire » dans la barre latérale : l'utilisateur voit la page (et l'erreur) à
    droite pendant qu'il écrit. Les champs ont un fond pâle et un texte foncé, lisibles sur la barre
    latérale foncée de tous les comptes.
    """
    try:
        secrets = st.secrets["retours"]
        jeton, depot = secrets["jeton"], secrets["depot"]
    except (KeyError, FileNotFoundError):
        return  # commentaires non configurés : pas de formulaire
    compte = st.session_state.get("compte", "")
    fonctions = [f.nom for cle, f in acces.FONCTIONS.items() if acces.permis(cle, compte)]
    st.sidebar.html(STYLE_DES_CHAMPS)
    with st.sidebar.expander("Commentaire", icon=":material/chat:"):
        with st.form("commentaire", clear_on_submit=True, border=False):
            fonction = st.selectbox("Fonction", ["Général"] + fonctions)
            commentaire = st.text_area("Commentaire, erreur ou suggestion")
            nom = st.text_input("Votre nom (facultatif)")
            if st.form_submit_button("Envoyer", icon=":material/send:"):
                if not commentaire.strip():
                    st.warning("Écrivez un commentaire avant d'envoyer.")
                    return
                titre = f"[{fonction}] {commentaire.strip().splitlines()[0][:60]}"
                try:
                    creer_issue(
                        titre, corps_de_l_issue(page, fonction, commentaire, nom, compte), jeton, depot
                    )
                except OSError:
                    st.error("L'envoi a échoué. Réessayez plus tard.")
                else:
                    st.success("Merci ! Votre commentaire a été envoyé.")
