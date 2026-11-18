"""Tests du tableau A.11 Valeurs de densité (p. 336)."""

import pytest

from moteur.normes.csa_o86_19.annexe_A_renseignements_supplementaires_et_autres_methodes.tableaux import (  # noqa: E501
    tableau_A_11_valeurs_de_densite as tableau,
)


@pytest.mark.parametrize(
    "essence, E, attendu",
    [
        ("df", 0, 0.49), ("hf", 0, 0.46), ("spf", 0, 0.42), ("ns", 0, 0.35),
        ("courant", 8300, 0.42), ("normal", 11700, 0.42),
        ("normal", 12400, 0.47), ("rare", 13100, 0.47),
        ("courant", 13800, 0.50), ("normal", 16500, 0.50),
    ],
)
def test_G(essence, E, attendu):
    assert tableau.G(essence, E) == attendu


@pytest.mark.parametrize("E", [8000, 12000, 13500, 17000])
def test_G_hors_tableau(E):
    with pytest.raises(ValueError):
        tableau.G("normal", E)
