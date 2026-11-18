"""Tests de moteur/commun/unites.py : conversions pour l'affichage (valeurs calculées à la main)."""

import pytest

from moteur.commun import unites


@pytest.mark.parametrize(
    "valeur, nom, attendu",
    [
        (38, "dimension", 1.49606),  # 38 / 25,4
        (3000, "longueur", 9.84252),  # 3000 / 304,8
        (5320, "aire", 8.24602),  # 5320 / 645,16
        (12.62, "force", 2837.089),  # 12 620 N / 4,448 221 6 N
        (1, "moment", 8850.746),  # 10^6 N·mm / (4,448 221 6 x 25,4) = lb·po
        (11.5, "contrainte", 1667.937),  # 11,5 / (4,448 221 6 / 645,16)
    ],
)
def test_vers_imperial(valeur, nom, attendu):
    assert unites.vers_imperial(valeur, nom) == pytest.approx(attendu, rel=1e-5)


@pytest.mark.parametrize("nom", sorted(unites.GRANDEURS))
def test_aller_retour(nom):
    assert unites.vers_metrique(unites.vers_imperial(123.456, nom), nom) == pytest.approx(123.456)


def test_facteurs_exacts():
    assert unites.vers_metrique(1, "dimension") == 25.4
    assert unites.vers_metrique(1, "longueur") == pytest.approx(304.8)
    assert unites.vers_metrique(1, "force") == pytest.approx(0.0044482216152605)


@pytest.mark.parametrize(
    "valeur, nom, attendu",
    [
        (38, "dimension", "38 mm (1.50 po)"),
        (3000, "longueur", "3000 mm (9.84 pi)"),
        (12.62, "force", "12.62 kN (2837 lb)"),
        (1, "moment", "1.00 kN·m (8851 lb·po)"),
        (11.5, "contrainte", "11.50 MPa (1668 psi)"),
    ],
)
def test_deux_unites(valeur, nom, attendu):
    assert unites.deux_unites(valeur, nom) == attendu


def test_grandeur_inconnue():
    with pytest.raises(KeyError):
        unites.vers_imperial(1, "vitesse")
