"""Tests de moteur/commun/verification.py : 5.1.2, ratio comparé à 1,00 avant l'arrondi."""

import pytest

from moteur.commun.verification import verifier


# (effet, résistance, message attendu) : ratios calculés à la main
@pytest.mark.parametrize(
    "effet, resistance, attendu",
    [
        (12.3, 27, "État limite respecté: 45.56%"),  # 12,3 / 27 = 0,45556
        (26.9, 27, "État limite respecté: 99.63%"),  # 0,99630
        (27, 27, "État limite respecté: 100.00%"),  # ratio = 1,00 : ne dépasse pas (5.1.2 b))
        (27.0001, 27, "État limite dépassé: 100.00%"),  # 1,0000037 > 1
        (30, 27, "État limite dépassé: 111.11%"),  # 30 / 27 = 1,11111
        (0, 27, "État limite respecté: 0.00%"),
        (5, 0, "État limite dépassé: résistance pondérée nulle ou négative"),
        (0, 0, "État limite dépassé: résistance pondérée nulle ou négative"),
    ],
)
def test_message(effet, resistance, attendu):
    assert verifier(effet, resistance).message() == attendu


def test_ratio_et_respecte():
    v = verifier(10.0, 12.62, "P_f", "P_r", "kN", "force")
    assert v.ratio == pytest.approx(0.79239, rel=1e-4)  # 10 / 12,62
    assert v.respecte
    assert v.article == "5.1.2"
    assert (v.symbole_effet, v.symbole_resistance, v.unite) == ("P_f", "P_r", "kN")


def test_ratio_exactement_un_respecte():
    assert verifier(27, 27).respecte


def test_resistance_nulle():
    v = verifier(5, 0)
    assert v.ratio == float("inf")
    assert not v.respecte


def test_effet_negatif_refuse():
    with pytest.raises(ValueError):
        verifier(-1, 27)
