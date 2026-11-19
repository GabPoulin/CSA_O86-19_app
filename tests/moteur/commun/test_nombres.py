"""Tests du formatage à nombre fixe de chiffres significatifs (moteur/commun/nombres.py)."""

import pytest

from moteur.commun.nombres import cs


@pytest.mark.parametrize(
    ("valeur", "attendu"),
    [
        (11.8, "11.80"),  # MPa
        (0.794512, "0.7945"),
        (4085877, "4086000"),  # N·mm
        (349758.333, "349800"),  # mm³
        (1, "1.000"),
        (38, "38.00"),  # mm
        (2440, "2440"),  # mm
        (9.99961, "10.00"),  # l'arrondi ajoute un chiffre
        (0.00123456, "0.001235"),
        (-1.23456, "-1.235"),
        (0, "0"),
    ],
)
def test_cs(valeur, attendu):
    assert cs(valeur) == attendu


def test_cs_autre_nombre_de_chiffres():
    assert cs(11.8, 3) == "11.8"
    assert cs(4085877, 3) == "4090000"
