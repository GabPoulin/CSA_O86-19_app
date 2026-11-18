"""
Tests de 6.5.6 Résistance à la compression perpendiculaire au fil.

Cas calculé à la main : 2x6 S-P-F n° 1/n° 2 sec (f_cp = 5,3 MPa), b = 38 mm, d = 140 mm.
"""

import pytest

from moteur.commun import registre
from moteur.normes.csa_o86_19.ch_6_bois_de_sciage.art_6_5_calcul_des_resistances import (
    art_6_5_6_resistance_a_la_compression_perpendiculaire_au_fil as art,
)


def test_F_cp():
    assert art.F_cp(5.3) == 5.3  # MPa
    assert art.F_cp(5.3, K_Scp=0.67, K_T=0.85) == pytest.approx(3.01835)  # 5,3 MPa x 0,67 x 0,85


# largeur (mm), hauteur (mm), K_Zcp attendu (ex. 140 mm / 89 mm = 1,573 -> 1 + 0,15 x 0,573)
@pytest.mark.parametrize(
    "largeur, hauteur, attendu",
    [(38, 140, 1.0), (89, 89, 1.0), (140, 89, 1.08596), (133.5, 89, 1.075), (178, 89, 1.15),
     (286, 38, 1.15)],
)
def test_K_Zcp(largeur, hauteur, attendu):
    assert art.K_Zcp(largeur, hauteur) == pytest.approx(attendu, rel=1e-5)


@pytest.mark.parametrize(
    "L_b, attendu",
    [(150, 1.0), (200, 1.0), (100, 1.09525), (89, 1.10702), (38, 1.25066), (25, 1.381),
     (12.5, 1.75), (5, 1.75)],  # L_b en mm ; (L_b + 9,525 mm) / L_b, plafonnée à 1,75
)
def test_K_B(L_b, attendu):
    assert art.K_B(L_b, True, True) == pytest.approx(attendu, rel=1e-5)


def test_K_B_conditions():
    assert art.K_B(38) == 1  # L_b = 38 mm
    assert art.K_B(38, loin_de_l_extremite=True) == 1  # condition b) manquante
    assert art.K_B(38, hors_fortes_contraintes_de_flexion=True) == 1  # condition a) manquante


def test_A_b_prime():
    assert art.A_b_prime(38, 89, 140) == pytest.approx(4351)  # 38 mm x 114,5 mm = 4351 mm²
    assert art.A_b_prime(38, 140, 89) == pytest.approx(4351)  # ordre indifférent
    assert art.A_b_prime(38, 38, 140) == pytest.approx(2166)  # limité à 1,5 x 38 mm x 38 mm = 2166 mm²


def test_Q_r_et_Q_r_prime():
    assert art.Q_r(5.3, 38 * 89) == pytest.approx(14339.68)  # 0,8 x 5,3 MPa x 3382 mm² = 14 339,68 N
    assert art.Q_r(5.3, 38 * 89, K_B=1.10702) == pytest.approx(15874.4, rel=1e-5)  # N
    # (2/3) x 0,8 x 5,3 MPa x 4351 mm² = 12 298,83 N
    assert art.Q_r_prime(5.3, 4351) == pytest.approx(12298.83, rel=1e-5)


@pytest.mark.parametrize(
    "fonction, args",
    [(art.K_Zcp, (0, 89)), (art.K_B, (0,)), (art.A_b_prime, (38, 0, 89))],
)
def test_valeurs_invalides(fonction, args):
    with pytest.raises(ValueError):
        fonction(*args)


def test_verification_appui():
    r = art.verifier_compression_perpendiculaire_au_fil(38, 140, 89, 5.3, R_f=10.0)
    assert r.etape("Q_r").valeur == pytest.approx(14339.68)
    assert r.verification.message() == "État limite respecté: 69.74%"  # 10 kN / 14,34 kN


def test_verification_appui_avec_K_B():
    r = art.verifier_compression_perpendiculaire_au_fil(38, 140, 89, 5.3, loin_de_l_extremite=True,
                                                        hors_fortes_contraintes_de_flexion=True)
    assert r.etape("Q_r").valeur == pytest.approx(15874.4, rel=1e-5)


def test_verification_largeur_d_appui_plus_petite():
    # Plaque de 20 mm sous un élément de 76 mm (2 plis) : A_b = 20 mm x 89 mm = 1780 mm²,
    # K_Zcp selon 76 mm / 140 mm < 1 -> 1,00
    r = art.verifier_compression_perpendiculaire_au_fil(20, 140, 89, 5.3, largeur_element=76)
    assert r.etape("Q_r").valeur == pytest.approx(7547.2)  # 0,8 x 5,3 MPa x 1780 mm² = 7547,2 N


def test_verification_pres_d_un_appui():
    r = art.verifier_compression_perpendiculaire_pres_d_un_appui(
        38, 140, 89, 140, 5.3,
        appui_loin_de_l_extremite=True, appui_hors_fortes_contraintes_de_flexion=True,
        charge_loin_de_l_extremite=True, charge_hors_fortes_contraintes_de_flexion=True, P_f=5.0,
    )
    # K_B = min(98,525 mm / 89 mm ; 149,525 mm / 140 mm) = 1,06804 ; Q'_r = 12 298,8 N x 1,06804 = 13 135,6 N
    assert r.etape("K_B").valeur == pytest.approx(1.06804, rel=1e-5)
    assert r.etape("Q'_r").valeur == pytest.approx(13135.6, rel=1e-4)
    assert r.verification.respecte


def test_registre():
    assert [c.identifiant for c in registre.calculs("csa_o86_19")][:3] == ["6.5.5", "6.5.6.2", "6.5.6.3"]
