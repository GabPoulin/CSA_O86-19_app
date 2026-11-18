"""Tests de A.6.5.6 : f_cp à partir de la densité G (G du tableau A.11, comparé au tableau 6.4)."""

import pytest

from moteur.normes.csa_o86_19.annexe_A_renseignements_supplementaires_et_autres_methodes.art_A_6_bois_de_sciage import (  # noqa: E501
    art_A_6_5_6_compression_perpendiculaire_au_fil as art,
)


@pytest.mark.parametrize(
    "G, attendu",
    [
        (0.42, 5.2703),  # S-P-F : 0,9 x 1,8125 x (942,396 - 473,8) / 145,038 (tableau 6.4 : 5,3)
        (0.49, 7.0368),  # D. Fir-L (tableau 6.4 : 7,0)
        (0.35, 3.5038),  # Essences nordiques (tableau 6.4 : 3,5)
        (0.46, 6.2797),  # Pruche-sapin : plus que le tableau 6.4 (4,6), donc avertissement
    ],
)
def test_f_cp(G, attendu):
    assert art.f_cp(G) == pytest.approx(attendu, rel=1e-4)


def test_f_cp_sans_limite_de_tolerance():
    assert art.f_cp(0.42, limite_de_tolerance=False) == pytest.approx(5.8559, rel=1e-4)


def test_f_cp_invalide():
    with pytest.raises(ValueError):
        art.f_cp(0.2)
