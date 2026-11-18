"""Tests du tableau A.3 (CSA O86:19, annexe A, p. 302-303). Valeurs lues dans le tableau."""

import pytest

from moteur.normes.csa_o86_19.annexe_A_renseignements_supplementaires_et_autres_methodes.tableaux.tableau_A_3_dimensions_minimales_apres_rabotage_du_bois_d_oeuvre import (  # noqa: E501
    dimension_nette,
    dimensions_nominales,
    est_gros_bois,
)


def test_dimensions_nominales():
    # 2 à 16 po ; 7 et 9 po seulement pour le gros bois vert ; pas de 11, 13, 15 po
    assert dimensions_nominales() == [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16]


@pytest.mark.parametrize(
    ("b", "d", "attendu"),
    [
        (5, 5, True),  # 5 x 5 po : face étroite 5 po (114 mm vert) -> gros bois
        (6, 8, True),
        (8, 6, True),  # l'ordre b, d ne change rien
        (4, 6, False),  # face étroite 4 po (89 mm) -> bois de dimension
        (2, 12, False),
    ],
)
def test_est_gros_bois(b, d, attendu):
    assert est_gros_bois(b, d) is attendu


@pytest.mark.parametrize(
    ("nominale", "vert", "attendu"),
    [
        (2, False, 38),  # 2 po sec : 38 mm
        (2, True, 40),  # 2 po vert : 40 mm
        (4, False, 89),  # 4 po sec : 89 mm
        (4, True, 91),  # 4 po vert : 91 mm
        (6, False, 140),  # 6 po sec : 140 mm
        (6, True, 143),  # 6 po vert : 143 mm
        (10, False, 235),  # 10 po sec : 235 mm
        (12, True, 292),  # 12 po vert : 292 mm
        (16, False, 387),  # 16 po sec : 387 mm
    ],
)
def test_dimension_nette_bois_de_dimension(nominale, vert, attendu):
    assert dimension_nette(nominale, vert=vert) == attendu


@pytest.mark.parametrize(
    ("nominale", "attendu"),
    [(5, 114), (6, 140), (7, 165), (8, 191), (9, 216), (10, 241), (12, 292), (14, 343), (16, 394)],
)
def test_dimension_nette_gros_bois_vert(nominale, attendu):
    # Gros bois vert : 5 po = 114 mm ... 16 po = 394 mm (tableau A.3, fin)
    assert dimension_nette(nominale, vert=True, gros_bois=True) == attendu


def test_gros_bois_sec_prend_les_dimensions_du_bois_de_dimension():
    # Gros bois sec : pas de valeur au tableau A.3 pour le gros bois, on garde 6 po sec = 140 mm
    assert dimension_nette(6, vert=False, gros_bois=True) == 140


@pytest.mark.parametrize("nominale", [7, 9])
def test_7_et_9_po_seulement_en_gros_bois_vert(nominale):
    with pytest.raises(ValueError, match="seulement pour le gros bois vert"):
        dimension_nette(nominale)
    with pytest.raises(ValueError, match="seulement pour le gros bois vert"):
        dimension_nette(nominale, vert=True)  # vert, mais pas du gros bois


@pytest.mark.parametrize("nominale", [1, 11, 13, 15, 2.5])
def test_dimension_absente(nominale):
    with pytest.raises(ValueError, match="n'est pas offerte"):
        dimension_nette(nominale)


def test_mode_brut():
    # Dimension absente de la base de données : 3.5 po x 25.4 mm/po = 88.9 mm -> 89 mm
    assert dimension_nette(3.5, brut=True) == 89
    # Dimension absente : 11 po x 25.4 mm/po = 279.4 mm -> 279 mm
    assert dimension_nette(11, brut=True) == 279
