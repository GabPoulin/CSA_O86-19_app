"""Tests de 5.3.2 Coefficient de durée d'application de la charge (CSA O86:19, tableau 5.1, p. 41-42)."""

import math

import pytest

from moteur.normes.csa_o86_19.ch_5_conception_generale.art_5_3_conditions_et_coefficients_influant_sur_la_resistance import (  # noqa: E501
    K_D,
    K_D_charge_continue,
    P_s,
)


@pytest.mark.parametrize(("duree", "attendu"), [("courte", 1.15), ("normale", 1.00), ("continue", 0.65)])
def test_K_D_tableau_5_1(duree, attendu):
    assert K_D(duree) == attendu


def test_K_D_duree_inconnue():
    with pytest.raises(ValueError, match="tableau 5.1"):
        K_D("permanente")


def test_K_D_charge_continue():
    # P_L / P_s = 2 : 1.0 - 0.50 x log10(2) = 1.0 - 0.50 x 0.30103 = 0.84949
    assert K_D_charge_continue(2.0, 1.0) == pytest.approx(0.84949, rel=1e-5)
    # P_L / P_s = 1.2 : 1.0 - 0.50 x 0.079181 = 0.96041
    assert K_D_charge_continue(12.0, 10.0) == pytest.approx(0.96041, rel=1e-5)


def test_K_D_charge_continue_minimum():
    # 1.0 - 0.50 log10(r) = 0.65 -> r = 10^0.7 = 5.0119 : K_D = 0.65 au seuil
    assert K_D_charge_continue(10 ** 0.7, 1.0) == pytest.approx(0.65)
    # P_L / P_s = 10 : 1.0 - 0.50 x 1 = 0.50 < 0.65 -> 0.65
    assert K_D_charge_continue(10.0, 1.0) == 0.65


def test_K_D_charge_continue_conditions():
    with pytest.raises(ValueError, match="P_L > P_s"):
        K_D_charge_continue(1.0, 1.0)  # P_L = P_s : 5.3.2.2 ne s'applique pas
    with pytest.raises(ValueError, match="positive"):
        K_D_charge_continue(1.0, 0.0)


def test_K_D_charge_continue_presque_egal():
    # P_L à peine plus grand que P_s : K_D tend vers 1.0
    assert math.isclose(K_D_charge_continue(1.000001, 1.0), 1.0, abs_tol=1e-6)


def test_P_s_maximum_des_quatre_combinaisons():
    # S = 2 kPa, L = 1 kPa : S 2, L 1, S + 0.5L = 2.5, 0.5S + L = 2.0 kPa -> 2.5 kPa
    assert P_s(2.0, 1.0) == pytest.approx(2.5)
    # S = 1 kPa, L = 2 kPa : 0.5S + L = 2.5 kPa
    assert P_s(1.0, 2.0) == pytest.approx(2.5)
    # Neige seule, surcharge seule, aucune charge
    assert P_s(S=3.0) == pytest.approx(3.0)
    assert P_s(L=4.0) == pytest.approx(4.0)
    assert P_s() == 0.0


def test_K_D_avec_P_s_calcule():
    # P_L = 3 kPa, S = 2 kPa, L = 1 kPa : P_s = 2.5 kPa ; K_D = 1 - 0.5 log(1.2) = 0.96041
    assert K_D_charge_continue(3.0, P_s(2.0, 1.0)) == pytest.approx(0.96041, abs=1e-5)
