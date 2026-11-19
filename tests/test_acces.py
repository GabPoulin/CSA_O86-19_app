"""Tests des comptes et de la connexion (acces.py, issue #56)."""

from unittest import mock

import pytest
from streamlit.testing.v1 import AppTest

import acces
import retours

MOTS_DE_PASSE = {"admin": "mot-admin", "lantier": "mot-lantier"}


@pytest.mark.parametrize(
    ("entre", "attendu"),
    [
        ("mot-admin", acces.ADMIN),
        ("mot-lantier", acces.LANTIER),
        ("mauvais", None),
        ("", None),
        ("MOT-ADMIN", None),  # sensible à la casse
    ],
)
def test_compte_pour(entre, attendu):
    assert acces.compte_pour(entre, MOTS_DE_PASSE) == attendu


def test_compte_inconnu_ou_vide_ignore():
    assert acces.compte_pour("x", {"pirate": "x"}) is None  # compte absent de NOMS_DES_COMPTES
    assert acces.compte_pour("", {"admin": ""}) is None  # mot de passe vide dans les secrets


def test_permis():
    for fonction in acces.FONCTIONS:
        assert acces.permis(fonction, acces.ADMIN)
    assert not acces.permis("flexion", None)  # non connecté
    assert not acces.permis("flexion", "inconnu")
    assert acces.ACCES[acces.LANTIER] <= set(acces.FONCTIONS)  # aucune fonction inventée


def _accueil(secrets=None):
    at = AppTest.from_file("../Accueil.py", default_timeout=60)
    if secrets is not None:
        at.secrets["mots_de_passe"] = secrets
    return at.run()


def test_connexion_non_configuree():
    at = _accueil()
    assert not at.exception
    assert any("Connexion non configurée" in e.value for e in at.error)
    assert not at.header  # la page s'arrête avant le calcul


def test_mauvais_mot_de_passe():
    at = _accueil(MOTS_DE_PASSE)
    at.text_input[0].input("mauvais")
    at.button[0].click().run()
    assert any("Mot de passe invalide" in e.value for e in at.error)
    assert "compte" not in at.session_state


@pytest.mark.parametrize(("mot", "compte"), [("mot-admin", "admin"), ("mot-lantier", "lantier")])
def test_connexion_et_deconnexion(mot, compte):
    at = _accueil(MOTS_DE_PASSE)
    at.text_input[0].input(mot)
    at.button[0].click().run()
    assert not at.exception
    assert at.session_state["compte"] == compte
    assert [h.value for h in at.header][0] == "Bois de Sciage"  # pas de page d'accueil
    assert any(acces.NOMS_DES_COMPTES[compte] in c.value for c in at.sidebar.caption)
    [b for b in at.sidebar.button if b.label == "Se déconnecter"][0].click().run()
    assert "compte" not in at.session_state
    assert not at.header


def test_corps_de_l_issue():
    corps = retours.corps_de_l_issue("Bois de sciage", "Flexion (6.5.3)", "Bravo", "", "lantier")
    assert "**Compte** : Groupe Lantier" in corps
    assert "**Nom** : (non indiqué)" in corps
    assert corps.endswith("Bravo\n")


def test_formulaire_de_commentaire():
    at = _accueil(MOTS_DE_PASSE)
    at.secrets["retours"] = {"jeton": "faux-jeton", "depot": "LeRepere-GP/datum-retours"}
    at.text_input[0].input("mot-lantier")
    at.button[0].click().run()
    with mock.patch.object(retours, "creer_issue", return_value="https://exemple") as envoi:
        at.text_area[0].input("Le ratio devrait être arrondi.")
        [b for b in at.button if b.label == "Envoyer"][0].click().run()
    assert not at.exception
    titre, corps, jeton, depot = envoi.call_args.args
    assert titre == "[Général] Le ratio devrait être arrondi."
    assert "Groupe Lantier" in corps
    assert (jeton, depot) == ("faux-jeton", "LeRepere-GP/datum-retours")
    assert any("Merci" in s.value for s in at.success)


def test_page_bois_de_sciage_protegee():
    at = _accueil(MOTS_DE_PASSE)  # le point d'entrée ouvre directement Bois de sciage
    assert not at.exception
    assert not at.tabs  # rien du calcul avant la connexion
    at.text_input[0].input("mot-admin")
    at.button[0].click().run()
    assert not at.exception
    assert len(at.tabs) == 7  # onglets de calcul affichés une fois connecté


# ACCES_GROUPE_LANTIER.md : cases à cocher lues par l'application (issue #56)
EXEMPLE = """
## Fonctions offertes au compte Groupe Lantier
- [x] `flexion` : Flexion
- [ ] `cisaillement` : Cisaillement
## Fonctions testées convenablement
- [X] `flexion`
- [ ] `cisaillement`
## Autre section
- [x] `compression_oblique`
"""


def test_lire_cases():
    cases = acces.lire_cases(EXEMPLE)
    assert cases["offertes"] == {"flexion"}
    assert cases["testees"] == {"flexion"}  # [X] majuscule accepté ; autre section ignorée


def test_lire_cases_identifiant_inconnu():
    with pytest.raises(ValueError, match="inconnue"):
        acces.lire_cases(EXEMPLE.replace("`cisaillement` :", "`cisaillements` :"))


def test_lire_cases_section_manquante():
    with pytest.raises(ValueError, match="section manquante"):
        acces.lire_cases("## Fonctions offertes au compte Groupe Lantier\n- [x] `flexion`\n")


def test_fichier_d_acces_valide():
    texte = acces.FICHIER_ACCES.read_text(encoding="utf-8")
    cases = acces.lire_cases(texte)
    # Garde-fou : une fonction pas encore intégrée au nouveau moteur ne peut pas être offerte
    assert not cases["offertes"] & {"compression_oblique", "traction", "flexion_et_charge_axiale"}
    assert acces.ACCES[acces.LANTIER] == cases["offertes"]


def _connecte(compte, mot):
    at = _accueil(MOTS_DE_PASSE)
    at.text_input[0].input(mot)
    at.button[0].click().run()
    assert not at.exception
    return at


def test_lantier_sans_fonction_offerte():
    with mock.patch.dict(acces.ACCES, {acces.LANTIER: frozenset()}):
        at = _connecte("lantier", "mot-lantier")
    assert not at.tabs
    assert any("Aucune vérification" in i.value for i in at.info)
    assert not [s for s in at.subheader if s.value == "Note de calcul (PDF)"]


def test_lantier_voit_seulement_les_fonctions_offertes():
    with mock.patch.dict(acces.ACCES, {acces.LANTIER: frozenset({"flexion", "note_pdf"})}), \
            mock.patch.object(acces, "TESTEES", frozenset()):
        at = _connecte("lantier", "mot-lantier")
    assert [t.label for t in at.tabs] == ["Moment de flexion"]
    assert any("En test" in w.value for w in at.warning)  # flexion non cochée comme testée


def test_fonction_testee_sans_avertissement():
    with mock.patch.dict(acces.ACCES, {acces.LANTIER: frozenset({"flexion"})}), \
            mock.patch.object(acces, "TESTEES", frozenset({"flexion"})):
        at = _connecte("lantier", "mot-lantier")
    assert not any("En test" in w.value for w in at.warning)


def test_admin_voit_tout():
    at = _connecte("admin", "mot-admin")
    assert len(at.tabs) == 7


def test_note_avec_compression_perpendiculaire():
    with mock.patch.dict(acces.ACCES, {acces.LANTIER: frozenset({"compression_perpendiculaire", "note_pdf"})}):
        at = _connecte("lantier", "mot-lantier")

        def ni(cle):
            return [n for n in at.number_input if n.key == cle][0]

        ni("cp_support_length").set_value(89.0)
        ni("cp_rf").set_value(5.0)
        at.run()
        [c for c in at.checkbox if c.key == "cp_near_load"][0].check()
        at.run()
        ni("cp_load_length").set_value(140.0)
        ni("cp_pf").set_value(3.0)
        at.run()
    assert not at.exception
    cases = [c.label for c in at.checkbox if c.key and c.key.startswith("note_")]
    assert cases == [
        "Compression perpendiculaire au fil (6.5.6.2)",
        "Compression perpendiculaire près d'un appui (6.5.6.3)",
    ]
    assert any(b.label.startswith("Télécharger") for b in at.get("download_button"))


def test_aucune_mention_de_le_repere_avant_la_connexion():
    at = _accueil(MOTS_DE_PASSE)
    textes = [e.value for e in at.title] + [e.value for e in at.caption] + [e.value for e in at.markdown]
    assert "Datum" in textes
    assert not any("Repère" in t for t in textes)


@pytest.mark.parametrize("compte", ["admin", "lantier"])
def test_identite_du_compte(compte):
    import config

    # Chaque compte a son logo pour la barre latérale foncée, son symbole et ses couleurs
    assert config.fichier_du_compte(compte, "logo_renverse.svg")
    assert config.fichier_du_compte(compte, "symbole.svg")
    assert config.fichier_du_compte("", "symbole.svg") is None
    assert config.fichier_du_compte("../x", "symbole.svg") is None
    at = _connecte(compte, f"mot-{compte}")
    textes = [e.value for e in at.title] + [e.value for e in at.caption] + [e.value for e in at.sidebar.caption]
    assert not any("Repère" in t for t in textes)


def test_couleur_du_texte():
    import config

    assert config.couleur_du_texte("#233614") == "#FFFFFF"  # vert forêt : texte blanc
    assert config.couleur_du_texte("#47aeaa") == "#333333"  # sarcelle : texte charbon
    assert config.couleur_du_texte("#9E5A00") == "#FFFFFF"  # orange brûlé : texte blanc


def test_eclaircir():
    import config

    assert config.eclaircir("#273c3c", 0) == "#273C3C"
    assert config.eclaircir("#273c3c", 1) == "#FFFFFF"
    # 0x27 = 39 : 39 + (255 - 39) x 0.5 = 147 = 0x93 ; 0x3c = 60 : 60 + 195 x 0.5 = 157.5 -> 158 = 0x9E
    assert config.eclaircir("#273c3c", 0.5) == "#939E9E"


def test_couleurs_de_l_interface_par_compte():
    import config

    assert config.rvb("#47aeaa") == "71, 174, 170"
    # Admin : couleurs du thème global, rien à remplacer
    assert config.remplacements_du_theme(config.THEME["primaryColor"], None) == []
    assert config.fond_du_compte("admin") is None
    # Groupe Lantier : accents en sarcelle et fond blanc (charte, p. 6)
    assert config.fond_du_compte("lantier") == "#ffffff"
    assert config.remplacements_du_theme("#47aeaa", "#ffffff") == [
        ("158, 90, 0", "71, 174, 170"),  # orange brûlé du thème -> sarcelle
        ("244, 241, 234", "255, 255, 255"),  # sable du thème -> blanc
    ]


def test_fond_invalide(tmp_path):
    import config

    (tmp_path / "x").mkdir()
    (tmp_path / "x" / "couleurs.toml").write_text('fond = "blanc"\n', encoding="utf-8")
    with pytest.raises(ValueError):
        config.fond_du_compte("x", tmp_path)
