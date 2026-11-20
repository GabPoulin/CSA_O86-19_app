"""Tests de config.apparence_du_compte (logo et couleurs de la note par compte)."""

import pytest

import config
from moteur.commun.note_de_calcul import COULEUR_ACCENT, COULEUR_PRINCIPALE


def test_sans_dossier_valeurs_par_defaut(tmp_path):
    a = config.apparence_du_compte("lantier", tmp_path)
    assert (a.logo, a.principale, a.accent) == (None, COULEUR_PRINCIPALE, COULEUR_ACCENT)


def test_compte_vide_ou_invalide(tmp_path):
    (tmp_path / "x").mkdir()
    assert config.apparence_du_compte("", tmp_path).logo is None
    assert config.apparence_du_compte("../x", tmp_path).logo is None


def test_logo_et_couleurs(tmp_path):
    d = tmp_path / "lantier"
    d.mkdir()
    (d / "logo.png").write_bytes(b"png")
    (d / "logo.svg").write_bytes(b"<svg/>")
    (d / "couleurs.toml").write_text('principale = "#112233"\naccent = "#AABBCC"\n', encoding="utf-8")
    a = config.apparence_du_compte("lantier", tmp_path)
    assert a.logo == b"<svg/>"  # SVG en premier
    assert (a.principale, a.accent) == ("#112233", "#AABBCC")


def test_une_seule_couleur(tmp_path):
    d = tmp_path / "lantier"
    d.mkdir()
    (d / "couleurs.toml").write_text('accent = "#AABBCC"\n', encoding="utf-8")
    a = config.apparence_du_compte("lantier", tmp_path)
    assert (a.logo, a.principale, a.accent) == (None, COULEUR_PRINCIPALE, "#AABBCC")


def test_couleur_invalide(tmp_path):
    d = tmp_path / "lantier"
    d.mkdir()
    (d / "couleurs.toml").write_text('principale = "vert"\n', encoding="utf-8")
    with pytest.raises(ValueError):
        config.apparence_du_compte("lantier", tmp_path)


def test_dossier_lantier_du_depot():
    # Le dossier existe (README seulement tant que les fichiers ne sont pas déposés)
    assert (config.DOSSIER_COMPTES / "lantier").is_dir()
    config.apparence_du_compte("lantier")


def test_polices(tmp_path):
    d = tmp_path / "lantier"
    d.mkdir()
    (d / "polices.toml").write_text('titres = "Rift"\ntexte = "DIN 2014"\n', encoding="utf-8")
    a = config.apparence_du_compte("lantier", tmp_path)
    assert (a.police_titres, a.police_texte) == ("Rift", "DIN 2014")
    assert a.dossier_polices == d / "polices"


def test_charte_groupe_lantier():
    # Charte graphique Groupe Lantier 2021, p. 6 : vert foncé #273c3c, sarcelle #47aeaa
    a = config.apparence_du_compte("lantier")
    assert (a.principale, a.accent) == ("#273c3c", "#47aeaa")
    assert a.logo.startswith(b"<svg")
    assert (a.police_titres, a.police_texte) == ("Rift", "DIN 2014")


def test_ingenieurs_absents(tmp_path):
    assert config.ingenieurs_du_compte("lantier", tmp_path) == []
    assert config.ingenieurs_du_compte("", tmp_path) == []


def test_ingenieurs_du_fichier(tmp_path):
    (tmp_path / "x").mkdir()
    (tmp_path / "x" / "ingenieurs.toml").write_text(
        '[[ingenieur]]\nnom = "A B"\noiq = "123"\n[[ingenieur]]\nnom = " C D "\noiq = 456\n',
        encoding="utf-8",
    )
    assert config.ingenieurs_du_compte("x", tmp_path) == [("A B", "123"), ("C D", "456")]


def test_ingenieur_incomplet(tmp_path):
    (tmp_path / "x").mkdir()
    (tmp_path / "x" / "ingenieurs.toml").write_text('[[ingenieur]]\nnom = "A B"\n', encoding="utf-8")
    with pytest.raises(ValueError):
        config.ingenieurs_du_compte("x", tmp_path)


@pytest.mark.parametrize("compte", ["admin", "lantier"])
def test_ingenieurs_du_depot(compte):
    # datum-retours #6 : liste donnée par l'utilisateur
    assert config.ingenieurs_du_compte(compte) == [
        ("Gabriel Poulin", "5088827"),
        ("Olivier Lantier", "5024123"),
        ("Simon Boucher", "5025799"),
        ("Loïc Blais", "6044886"),
    ]
