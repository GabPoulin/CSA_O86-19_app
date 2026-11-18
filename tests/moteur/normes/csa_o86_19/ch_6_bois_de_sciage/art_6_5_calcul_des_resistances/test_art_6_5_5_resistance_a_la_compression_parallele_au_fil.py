"""
Tests de 6.5.5 Résistance à la compression parallèle au fil.

Cas calculé à la main : 2x6 S-P-F n° 1/n° 2 sec (tableau 6.4 : f_c = 11,5 MPa, E_05 = 6500 MPa),
b = 38 mm, d = 140 mm, L = 3000 mm. Axe fort : L_e = 3000 mm. Axe faible : L_e = 1500 mm.
"""

import pytest

from moteur.commun import registre
from moteur.normes.csa_o86_19.ch_6_bois_de_sciage.art_6_5_calcul_des_resistances import (
    art_6_5_5_resistance_a_la_compression_parallele_au_fil as art,
)


def test_F_c():
    assert art.F_c(11.5) == 11.5
    assert art.F_c(11.5, K_D=1.15, K_H=0.9) == pytest.approx(11.9025)  # 11,5 x 1,15 x 0,9
    assert art.F_c(11.5, K_H=1.1, K_Sc=0.69, K_T=0.85) == pytest.approx(7.41923, rel=1e-5)


@pytest.mark.parametrize(
    "L_e, dimension, attendu",
    [(3000, 140, 21.4286), (1500, 38, 39.4737), (1900, 38, 50)],  # 50 exactement : accepté
)
def test_C_C(L_e, dimension, attendu):
    assert art.C_C(L_e, dimension) == pytest.approx(attendu, rel=1e-5)


@pytest.mark.parametrize("L_e, dimension", [(1901, 38), (0, 38), (3000, 0), (-100, 38)])
def test_C_C_invalide(L_e, dimension):
    with pytest.raises(ValueError):
        art.C_C(L_e, dimension)


def test_K_Zc():
    # 6,3 x (140 x 3000)^-0,13 = 6,3 x 0,18577 = 1,1704
    assert art.K_Zc(140, 3000) == pytest.approx(1.1704, rel=1e-4)
    # 6,3 x (38 x 3000)^-0,13 = 1,3868 -> plafonné à 1,3
    assert art.K_Zc(38, 3000) == 1.3
    with pytest.raises(ValueError):
        art.K_Zc(0, 3000)


def test_K_C():
    # [1 + 11,5 x 1,1704 x 21,4286^3 / (35 x 6500)]^-1 = [1 + 0,58212]^-1 = 0,63206
    assert art.K_C(11.5, 1.1704, 3000 / 140, 6500) == pytest.approx(0.63206, rel=1e-4)
    # [1 + 11,5 x 1,3 x 39,4737^3 / 227 500]^-1 = [1 + 4,04187]^-1 = 0,19834
    assert art.K_C(11.5, 1.3, 1500 / 38, 6500) == pytest.approx(0.19834, rel=1e-4)
    # K_SE = 0,94 et K_T = 0,9 au dénominateur : [1 + 4,77753]^-1 = 0,17309
    assert art.K_C(11.5, 1.3, 1500 / 38, 6500, K_SE=0.94, K_T=0.9) == pytest.approx(0.17309, rel=1e-4)
    assert art.K_C(11.5, 1.3, 0, 6500) == 1


def test_P_r():
    # 0,8 x 11,5 x 5320 = 48 944 N
    assert art.P_r(11.5, 5320, 1, 1) == pytest.approx(48944)
    # 0,8 x 11,5 x 5320 x 1,3 x 0,19834 = 12 620 N
    assert art.P_r(11.5, 5320, 1.3, 0.19834) == pytest.approx(12620, rel=1e-3)


def _verifier(**kwargs):
    valeurs = dict(b=38, d=140, L=3000, L_e_b=1500, L_e_d=3000, f_c=11.5, E_05=6500)
    valeurs.update(kwargs)
    return art.verifier_compression_parallele_au_fil(**valeurs)


def test_verification_2x6():
    r = _verifier(P_f=10.0)
    assert r.etape("P_{r,b}").valeur == pytest.approx(12620, rel=1e-3)  # axe faible gouverne
    assert r.etape("P_{r,d}").valeur == pytest.approx(36206, rel=1e-3)
    assert r.etape("P_r").valeur == pytest.approx(12620, rel=1e-3)
    assert r.verification.ratio == pytest.approx(10 / 12.620, rel=1e-3)  # 79.24 %
    assert r.verification.respecte and r.verification.unite == "kN"


def test_verification_milieu_humide_traite_incise():
    # K_H = 1,1 ; K_Sc = 0,69 ; K_T = 0,85 ; K_SE = 0,94 -> P_r = 9 627 N (calcul à la main)
    r = _verifier(K_H=1.1, K_Sc=0.69, K_T=0.85, K_SE=0.94)
    assert r.etape("P_r").valeur == pytest.approx(9627, rel=1e-3)
    assert r.verification is None  # pas de P_f


def test_verification_duree_courte():
    # K_D = 1,15 : F_c = 13,225 ; K_C = 0,17705 ; P_r = 12 955 N
    assert _verifier(K_D=1.15).etape("P_r").valeur == pytest.approx(12955, rel=1e-3)


def test_verification_trace():
    r = _verifier()
    assert r.norme == "CSA O86:19" and r.article == "6.5.5" and r.figure == "colonne"
    assert [e.article for e in r.etapes[:2]] == ["6.5.5.2.4", "6.5.5.2.2"]
    assert all(e.formule and e.substitution for e in r.etapes)


def test_verification_elancement_trop_grand():
    with pytest.raises(ValueError):
        _verifier(L_e_b=3000)  # 3000 / 38 = 78,9 > 50


def test_registre():
    assert registre.calcul("csa_o86_19", "6.5.5").fonction is art.verifier_compression_parallele_au_fil
