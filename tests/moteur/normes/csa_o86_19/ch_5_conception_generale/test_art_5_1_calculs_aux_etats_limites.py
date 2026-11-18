"""Tests de 5.1.2 États limites ultimes : ratio charge / résistance comparé à 1,00 avant l'arrondi."""

import pytest

from moteur.normes.csa_o86_19.ch_5_conception_generale.art_5_1_calculs_aux_etats_limites import (
    verifier_etat_limite_ultime,
)


# (charge pondérée en kN, résistance pondérée en kN, message attendu) : ratios calculés à la main
@pytest.mark.parametrize(
    "charge, resistance, attendu",
    [
        (12.3, 27, "État limite respecté: 45.56%"),  # 12,3 kN / 27 kN = 0,45556
        (26.9, 27, "État limite respecté: 99.63%"),  # 26,9 kN / 27 kN = 0,99630
        (27, 27, "État limite respecté: 100.00%"),  # 27 kN / 27 kN = 1,00 : ne dépasse pas
        (27.0001, 27, "État limite dépassé: 100.00%"),  # 27,0001 kN / 27 kN = 1,0000037 > 1
        (30, 27, "État limite dépassé: 111.11%"),  # 30 kN / 27 kN = 1,11111
        (0, 27, "État limite respecté: 0.00%"),  # 0 kN / 27 kN
        (5, 0, "État limite dépassé: résistance pondérée nulle ou négative"),  # 5 kN / 0 kN
        (0, 0, "État limite dépassé: résistance pondérée nulle ou négative"),  # 0 kN / 0 kN
    ],
)
def test_message(charge, resistance, attendu):
    assert verifier_etat_limite_ultime(charge, resistance).message() == attendu


def test_ratio_et_respecte():
    # P_f = 10 kN, P_r = 12,62 kN : ratio = 0,79239
    v = verifier_etat_limite_ultime(10.0, 12.62, "P_f", "P_r", "kN", "force")
    assert v.ratio == pytest.approx(0.79239, rel=1e-4)
    assert v.respecte and v.article == "5.1.2"
    assert (v.symbole_charge, v.symbole_resistance, v.unite) == ("P_f", "P_r", "kN")


def test_resistance_nulle():
    v = verifier_etat_limite_ultime(5, 0)  # 5 kN / 0 kN
    assert v.ratio == float("inf") and not v.respecte


def test_charge_negative_refusee():
    with pytest.raises(ValueError):
        verifier_etat_limite_ultime(-1, 27)  # -1 kN
