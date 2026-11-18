"""Tests de 6.3 Résistances prévues (CSA O86:19, tableaux 6.4 à 6.8, p. 51-57). Valeurs des tableaux."""

import pytest

from moteur.normes.csa_o86_19.ch_6_bois_de_sciage.art_6_3_resistances_prevues_et_modules_d_elasticite import (  # noqa: E501
    ResistancesPrevues,
    classes,
    coefficients_charges_sur_grande_face,
    resistances_prevues,
)


def test_tableau_6_4_spf_n1_n2():
    # É-P-S n° 1/n° 2 : fb 11.8 MPa, fv 1.5 MPa, fc 11.5 MPa, fcp 5.3 MPa, ft 5.5 MPa,
    # E 9500 MPa, E05 6500 MPa
    assert resistances_prevues("Lumber", "spf", "n1-n2") == ResistancesPrevues(
        11.8, 1.5, 11.5, 5.3, 5.5, 9500, 6500
    )


def test_tableau_6_4_df_ss():
    # D.Fir-L SS : fb 16.5 MPa, fv 1.9 MPa (commun aux classes), fc 19.0 MPa, fcp 7.0 MPa,
    # ft 10.6 MPa, E 12 500 MPa, E05 8500 MPa
    assert resistances_prevues("Lumber", "df", "ss") == ResistancesPrevues(
        16.5, 1.9, 19.0, 7.0, 10.6, 12500, 8500
    )


def test_tableau_6_5_spf_construction():
    # É-P-S Const. : fb 15.3 MPa, fv 2.6 MPa, fc 13.1 MPa, fcp 5.3 MPa, ft 6.2 MPa,
    # E 9000 MPa, E05 5500 MPa
    assert resistances_prevues("Light", "spf", "cst") == ResistancesPrevues(
        15.3, 2.6, 13.1, 5.3, 6.2, 9000, 5500
    )


def test_tableau_6_6_df_ss():
    # D.Fir-L SS : fb 19.5 MPa, fv 1.5 MPa, fc 13.2 MPa, fcp 7.0 MPa, ft 10.0 MPa,
    # E 12 000 MPa, E05 8000 MPa
    assert resistances_prevues("Beam", "df", "ss") == ResistancesPrevues(
        19.5, 1.5, 13.2, 7.0, 10.0, 12000, 8000
    )


def test_coefficients_charges_sur_grande_face():
    assert coefficients_charges_sur_grande_face("ss") == (0.88, 1.0)
    assert coefficients_charges_sur_grande_face("n1") == (0.77, 0.9)
    assert coefficients_charges_sur_grande_face("n2") == (0.77, 0.9)


def test_tableau_6_6_grande_face_ss():
    r = resistances_prevues("Beam", "df", "ss", charges_sur_grande_face=True)
    assert r.f_b == pytest.approx(17.16)  # 19.5 MPa x 0.88 = 17.16 MPa
    assert (r.E, r.E_05) == (12000, 8000)  # x 1.00
    assert (r.f_v, r.f_c, r.f_cp, r.f_t) == (1.5, 13.2, 7.0, 10.0)  # inchangées


def test_tableau_6_6_grande_face_n1():
    r = resistances_prevues("Beam", "spf", "n1", charges_sur_grande_face=True)
    assert r.f_b == pytest.approx(8.47)  # 11.0 MPa x 0.77 = 8.47 MPa
    assert r.E == pytest.approx(7650)  # 8500 MPa x 0.90 = 7650 MPa
    assert r.E_05 == pytest.approx(5400)  # 6000 MPa x 0.90 = 5400 MPa


def test_grande_face_sans_effet_hors_poutres():
    # Le coefficient du tableau 6.6 ne s'applique qu'aux poutres et longerons
    assert resistances_prevues("Lumber", "spf", "ss", charges_sur_grande_face=True) == (
        resistances_prevues("Lumber", "spf", "ss")
    )
    assert resistances_prevues("Post", "df", "n1", charges_sur_grande_face=True) == (
        resistances_prevues("Post", "df", "n1")
    )


def test_tableau_6_8_msr_1500():
    # 1500Fb-1.4E : fb 21.7 MPa, E 9700 MPa, ft 10.1 MPa, fc 17.5 MPa, fcp 5.3 MPa
    r = resistances_prevues("MSR", "normal", "1500-1.4")
    assert (r.f_b, r.E, r.f_t, r.f_c, r.f_cp) == (21.7, 9700, 10.1, 17.5, 5.3)
    assert r.E_05 == pytest.approx(0.82 * 9700)  # 0.82 x 9700 MPa = 7954 MPa


def test_classes():
    assert classes("Lumber", "spf") == ["ss", "n1-n2", "n3-stud"]
    assert classes("Light", "df") == ["cst", "std"]
    assert classes("Beam", "hf") == ["ss", "n1", "n2"]
    assert classes("Post", "ns") == ["ss", "n1", "n2"]
    assert classes("Beam", "inconnu") == []


def test_classe_introuvable():
    with pytest.raises(ValueError, match="introuvable"):
        resistances_prevues("Lumber", "spf", "n1")  # au tableau 6.4 : n1-n2, pas n1
