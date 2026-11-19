"""Tests de 6.5.3 Résistance au moment de flexion (CSA O86:19, p. 64-65)."""

import pytest

from moteur.normes.csa_o86_19.ch_6_bois_de_sciage.art_6_5_calcul_des_resistances.art_6_5_3_resistance_au_moment_de_flexion import (  # noqa: E501
    F_b,
    K_L,
    K_L_poutre_composee,
    espacement_maximal_des_fixations,
    M_r,
    S,
    rapport_hauteur_largeur_maximal,
    verifier_flexion,
)


def test_F_b():
    assert F_b(11.8) == 11.8  # tous les coefficients à 1
    # 11.8 MPa x (1.15 x 1.1 x 0.84 x 0.75) = 11.8 MPa x 0.79695 = 9.40401 MPa
    assert F_b(11.8, 1.15, 1.1, 0.84, 0.75) == pytest.approx(9.40401)


def test_S():
    # 38 mm x (235 mm)² / 6 = 349 758.33 mm³
    assert S(38, 235) == pytest.approx(349_758.333)
    # Poutre de 2 plis : 76 mm x (235 mm)² / 6 = 699 516.67 mm³
    assert S(76, 235) == pytest.approx(699_516.667)


@pytest.mark.parametrize(
    ("supports", "rapport"),
    [
        ({}, 2.5),  # 6.5.3.2.1 : sans support latéral
        ({"rive_comprimee_maintenue": True}, 2.5),  # sans support aux appuis : 6.5.3.2.1
        ({"support_lateral_aux_appuis": True}, 4.0),  # a)
        ({"support_lateral_aux_appuis": True, "pannes_ou_tirants": True}, 5.0),  # b)
        ({"support_lateral_aux_appuis": True, "rive_comprimee_maintenue": True}, 6.5),  # c)
        (
            {"support_lateral_aux_appuis": True, "rive_comprimee_maintenue": True,
             "entretoises_ou_entremises": True},
            7.5,
        ),  # d)
        (
            {"support_lateral_aux_appuis": True, "rive_comprimee_maintenue": True,
             "rive_tendue_maintenue": True},
            9.0,
        ),  # e) les deux rives
        # Rive tendue seule (sans la rive comprimée) : pas le cas e), reste a)
        ({"support_lateral_aux_appuis": True, "rive_tendue_maintenue": True}, 4.0),
        # Entretoises sans rive comprimée : pas le cas d), reste a)
        ({"support_lateral_aux_appuis": True, "entretoises_ou_entremises": True}, 4.0),
    ],
)
def test_rapport_hauteur_largeur_maximal(supports, rapport):
    assert rapport_hauteur_largeur_maximal(**supports) == rapport


@pytest.mark.parametrize("rapport", [2.5, 4.0, 5.0, 6.5, 7.5, 9.0])
def test_K_L_au_seuil(rapport):
    # d/b exactement au seuil : « ne soit pas supérieur » -> K_L = 1
    assert K_L(40, 40 * rapport, rapport) == 1.0
    # 1 mm de plus : K_L selon 7.5.6.4 (à venir)
    with pytest.raises(ValueError, match="7.5.6.4"):
        K_L(40, 40 * rapport + 1, rapport)


def test_M_r():
    # 0.9 x 11.8 MPa x 349 758.33 mm³ x 1.1 = 4 085 877 N·mm
    assert M_r(11.8, 349_758.333, 1.1, 1.0) == pytest.approx(4_085_877, rel=1e-6)


def test_verifier_flexion_38x235():
    # 38 x 235 mm, É-P-S n° 1/n° 2 : f_b = 11.8 MPa, K_Zb = 1.1 ; d/b = 235 mm / 38 mm = 6.18
    # -> rive comprimée maintenue (6.5:1) requise
    r = verifier_flexion(
        38, 235, 11.8, K_Zb=1.1, support_lateral_aux_appuis=True, rive_comprimee_maintenue=True,
        M_f=4.0,
    )
    assert r.etape("M_r").valeur == pytest.approx(4_085_877, rel=1e-6)  # N·mm
    # 4.0 kN·m / 4.086 kN·m = 0.979 -> respecté
    assert r.verification.ratio == pytest.approx(4.0 / 4.085877, rel=1e-6)
    assert r.verification.respecte


def test_verifier_flexion_ratio_depasse():
    # 6.18 > 4 : support aux appuis seulement -> K_L selon 7.5.6.4
    with pytest.raises(ValueError, match="6.18 > 4"):
        verifier_flexion(38, 235, 11.8, support_lateral_aux_appuis=True)


def test_verifier_flexion_poutre_composee():
    # 3 plis de 38 x 235 mm : largeur totale 114 mm, d/b = 235 mm / 114 mm = 2.06 <= 2.5
    r = verifier_flexion(38, 235, 11.8, plis=3, plis_fixes_a_au_plus_4d=True)
    assert r.etape("S").valeur == pytest.approx(114 * 235**2 / 6)  # 1 049 275 mm³
    assert r.etape("K_L").valeur == 1.0
    # 0.9 x 11.8 MPa x 1 049 275 mm³ = 11 143 300.5 N·mm
    assert r.etape("M_r").valeur == pytest.approx(11_143_300.5)
    assert r.verification is None


# 6.5.3.2.4 Poutres composées (issue #48, lecture stricte)
def test_espacement_maximal_des_fixations():
    assert espacement_maximal_des_fixations(286) == 1144  # 4 x 286 mm = 1144 mm


def test_K_L_poutre_composee_au_seuil():
    # 2 plis de 38 mm : largeur totale 76 mm ; d = 2.5 x 76 mm = 190 mm -> d/(n b) = 2.5 : K_L = 1
    assert K_L_poutre_composee(76, 190, True) == 1.0
    # 191 mm / 76 mm = 2.51 > 2.5 -> K_L selon 7.5.6.4
    with pytest.raises(ValueError, match="2.51 > 2.5"):
        K_L_poutre_composee(76, 191, True)


def test_K_L_poutre_composee_plis_non_fixes():
    # 3 plis de 38 x 140 mm : 140 mm / 114 mm = 1.23 <= 2.5, mais plis non fixés à 4 d = 560 mm
    with pytest.raises(ValueError, match="4 d = 560 mm"):
        K_L_poutre_composee(114, 140, False)


def test_poutre_composee_sans_les_rapports_de_6_5_3_2_3():
    # Exemple de #48 : 3 plis de 38 x 286 mm, 286 mm / 114 mm = 2.51 > 2.5. Avant : K_L = 1 avec la
    # rive comprimée maintenue (6.5:1). Maintenant : K_L selon 7.5.6.4, même avec tous les supports.
    with pytest.raises(ValueError, match="2.51 > 2.5"):
        verifier_flexion(
            38, 286, 11.8, plis=3, plis_fixes_a_au_plus_4d=True, support_lateral_aux_appuis=True,
            rive_comprimee_maintenue=True, rive_tendue_maintenue=True,
        )


def test_element_simple_inchange():
    # Un pli : les rapports de 6.5.3.2.3 s'appliquent toujours (38 x 286 mm, 7.53 <= 9)
    r = verifier_flexion(
        38, 286, 11.8, support_lateral_aux_appuis=True, rive_comprimee_maintenue=True,
        rive_tendue_maintenue=True,
    )
    assert r.etape("K_L").valeur == 1.0
