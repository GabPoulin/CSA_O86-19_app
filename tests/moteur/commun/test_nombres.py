"""Tests du formatage à nombre fixe de chiffres significatifs (moteur/commun/nombres.py)."""

import pytest

from moteur.commun.nombres import CHIFFRES_SIGNIFICATIFS, cs


def test_trois_chiffres_par_defaut():
    assert CHIFFRES_SIGNIFICATIFS == 3  # décision de l'utilisateur (revue de la PR #55)


@pytest.mark.parametrize(
    ("valeur", "attendu"),
    [
        (11.8, "11.8"),  # MPa
        (11.5, "11.5"),
        (0.794512, "0.795"),
        (4085877, "4090000"),  # N·mm
        (349758.333, "350000"),  # mm³
        (44519.6, "44500"),  # N
        (1, "1.00"),
        (38, "38.0"),  # mm
        (2440, "2440"),  # mm
        (9.996, "10.0"),  # l'arrondi ajoute un chiffre
        (0.00123456, "0.00123"),
        (-1.23456, "-1.23"),
        (0, "0"),
    ],
)
def test_cs(valeur, attendu):
    assert cs(valeur) == attendu


def test_cs_autre_nombre_de_chiffres():
    assert cs(11.8, 4) == "11.80"
    assert cs(4085877, 4) == "4086000"
    assert cs(4085877, 2) == "4100000"
