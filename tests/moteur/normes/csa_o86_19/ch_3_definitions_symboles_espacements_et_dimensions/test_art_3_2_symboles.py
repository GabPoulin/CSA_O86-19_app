"""Tests de 3.2 Symboles : définitions exactes de la norme (p. 35 à 38)."""

import pytest

from moteur.normes.csa_o86_19.ch_3_definitions_symboles_espacements_et_dimensions import (
    art_3_2_symboles as s32,
)


@pytest.mark.parametrize(
    "code, definition, unite",
    [
        ("f_c", "résistance prévue en compression parallèle au fil", "MPa"),
        ("E_05", "module d'élasticité pour les calculs des éléments en compression", "MPa"),
        ("K_Zc", "coefficient de dimensions pour la compression du bois de sciage et du bois "
                 "lamellé-croisé", ""),
        ("K_SE", "coefficient de conditions d'utilisation relatif au module d'élasticité", ""),
        ("P_r", "résistance pondérée à la compression parallèle au fil", "N"),
        ("M_r", "résistance pondérée au moment de flexion", "N·mm"),
        ("phi", "coefficient de résistance", ""),
    ],
)
def test_definitions_exactes(code, definition, unite):
    symbole = s32.symbole(code)
    assert (symbole.definition, symbole.unite) == (definition, unite)


def test_codes_valides_et_uniques():
    codes = [symbole.code for symbole in s32._SYMBOLES]
    assert len(codes) == len(set(codes))
    assert all(code.isidentifier() for code in codes)


def test_majuscules_respectees():
    # f_c (prévue) est à 3.2 ; F_c (corrigée) est définie dans les articles, pas à 3.2
    assert "f_c" in s32.SYMBOLES and "F_c" not in s32.SYMBOLES


def test_symbole_absent():
    with pytest.raises(KeyError):
        s32.symbole("X_inconnu")
