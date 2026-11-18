"""Tests du tableau A.4 : coefficient de longueur effective, K_e (A.6.5.5.1, p. 303-304)."""

import pytest

from moteur.normes.csa_o86_19.annexe_A_renseignements_supplementaires_et_autres_methodes.art_A_6_bois_de_sciage import (  # noqa: E501
    art_A_6_5_5_1_coefficient_de_longueur_effective as art,
)


def test_tableau_A_4_complet_et_dans_l_ordre():
    assert [K_e for _, K_e in art.TABLEAU_A_4] == [0.65, 0.80, 1.00, 1.20, 1.50, 2.00, 2.00]
    assert len(set(art.degres_de_retenue())) == 7


@pytest.mark.parametrize(
    "degre, attendu",
    [
        ("Translation et rotation fixes aux deux extrémités", 0.65),
        ("Translation fixe et rotation libre aux deux extrémités", 1.00),
        ("Translation et rotation fixes à une extrémité, translation et rotation libres à l'autre "
         "extrémité", 2.00),
    ],
)
def test_K_e(degre, attendu):
    assert art.K_e(degre) == attendu


def test_K_e_absent():
    with pytest.raises(ValueError):
        art.K_e("Encastré")
