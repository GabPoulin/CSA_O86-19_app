"""Tests de 6.5.4 Résistance au cisaillement (CSA O86:19, p. 65-68)."""

import pytest

from moteur.normes.csa_o86_19.ch_6_bois_de_sciage.art_6_5_calcul_des_resistances.art_6_5_4_resistance_au_cisaillement import (  # noqa: E501
    F_f,
    F_r,
    F_v,
    K_N,
    V_r,
    alpha,
    eta,
    verifier_cisaillement,
    verifier_cisaillement_par_fissuration,
)


def test_F_v():
    assert F_v(1.5) == 1.5
    # 1.5 MPa x (1.15 x 1.1 x 0.96 x 0.85) = 1.5 MPa x 1.032240 = 1.548360 MPa
    assert F_v(1.5, 1.15, 1.1, 0.96, 0.85) == pytest.approx(1.548360)


def test_V_r():
    # 0.9 x 1.5 MPa x (2 x 8930 mm² / 3) x 1.1 = 8840.7 N
    assert V_r(1.5, 8930, 1.1) == pytest.approx(8840.7)


def test_F_f():
    assert F_f() == 0.50  # f_f = 0.50 MPa
    # 0.50 MPa x (1.15 x 1.0 x 0.70 x 1.0) = 0.4025 MPa
    assert F_f(1.15, 1.0, 0.70, 1.0) == pytest.approx(0.4025)


def test_F_r():
    # 0.9 x 0.50 MPa x 8930 mm² x 1.8636 = 7488.7 N
    assert F_r(0.5, 8930, 1.8635650) == pytest.approx(7488.74, rel=1e-5)


def test_alpha_et_eta():
    assert alpha(20, 235) == pytest.approx(1 - 20 / 235)  # 0.91489
    assert alpha(58.75, 235) == pytest.approx(0.75)  # d_n = 0.25 d : seuil accepté
    assert eta(100, 235) == pytest.approx(100 / 235)  # 0.42553


def test_alpha_limites():
    with pytest.raises(ValueError, match="0.25 d"):
        alpha(58.76, 235)  # 58.76 mm > 0.25 x 235 mm = 58.75 mm
    with pytest.raises(ValueError, match="positive"):
        alpha(0, 235)


def test_eta_positive():
    with pytest.raises(ValueError, match="positive"):
        eta(0, 235)


# Tableau 6.14 : valeurs de K_N racine(d) (alpha, eta, valeur)
@pytest.mark.parametrize(
    ("a", "n", "valeur"),
    [(0.75, 0.15, 17.2), (0.95, 0.50, 36.4), (0.80, 1.00, 11.1), (0.90, 2.00, 10.0),
     (0.85, 0.60, 18.1), (0.75, 2.00, 5.26), (0.95, 0.15, 43.5)],
)
def test_K_N_tableau_6_14(a, n, valeur):
    d = 235  # mm ; K_N racine(d) ne dépend pas de d
    assert K_N(d, a, n) * d**0.5 == pytest.approx(valeur, rel=0.005)  # 3 chiffres au tableau


def test_K_N_38x235():
    # alpha = 0.914894, eta = 0.425532 :
    # 1.6 (1/0.914894 - 1) + 0.425532² (1/0.914894³ - 1) = 0.148837 + 0.181077 x 0.305843 = 0.204217
    # [0.006 x 235 mm x 0.204217]^(-1/2) = 1.86356
    assert K_N(235, alpha(20, 235), eta(100, 235)) == pytest.approx(1.86356, rel=1e-5)


def test_verifier_cisaillement():
    r = verifier_cisaillement(38, 235, 1.5, K_Zv=1.1, V_f=8.0)
    assert r.etape("A_n").valeur == 8930  # 38 mm x 235 mm
    assert r.etape("V_r").valeur == pytest.approx(8840.7)  # N
    assert r.verification.ratio == pytest.approx(8.0 / 8.8407)  # 8.0 kN / 8.84 kN = 0.905
    assert r.verification.respecte


def test_verifier_cisaillement_entaille_et_plis():
    # Aire nette avec entaille : 2 x 38 mm x (235 mm - 20 mm) = 16 340 mm²
    r = verifier_cisaillement(38, 235, 1.5, plis=2, d_n=20)
    assert r.etape("A_n").valeur == 16_340
    # 0.9 x 1.5 MPa x (2 x 16 340 mm² / 3) = 14 706 N
    assert r.etape("V_r").valeur == pytest.approx(14_706)


def test_verifier_cisaillement_par_fissuration():
    r = verifier_cisaillement_par_fissuration(38, 235, 20, 100, V_f=7.5)
    assert r.etape("F_f").valeur == 0.50
    assert r.etape("A_g").valeur == 8930
    assert r.etape("F_r").valeur == pytest.approx(7488.74, rel=1e-5)  # N
    # 7.5 kN / 7.489 kN = 1.0015 > 1.00 -> non respecté
    assert not r.verification.respecte


def test_verifier_cisaillement_par_fissuration_entaille_trop_profonde():
    with pytest.raises(ValueError, match="0.25 d"):
        verifier_cisaillement_par_fissuration(38, 235, 60, 100)  # 60 mm > 58.75 mm


def test_registre():
    from moteur.commun import registre
    from moteur.normes.csa_o86_19.ch_6_bois_de_sciage.art_6_5_calcul_des_resistances import (  # noqa: F401
        art_6_5_3_resistance_au_moment_de_flexion,
        art_6_5_5_resistance_a_la_compression_parallele_au_fil,
    )

    assert registre.calcul("csa_o86_19", "6.5.4.3").fonction is verifier_cisaillement
    assert registre.calcul("csa_o86_19", "6.5.4.4").fonction is verifier_cisaillement_par_fissuration
    identifiants = [c.identifiant for c in registre.calculs("csa_o86_19")]
    # Ordre naturel de la norme : 6.5.3 < 6.5.4.3 < 6.5.4.4 < 6.5.5
    assert (
        identifiants.index("6.5.3") < identifiants.index("6.5.4.3")
        < identifiants.index("6.5.4.4") < identifiants.index("6.5.5")
    )
