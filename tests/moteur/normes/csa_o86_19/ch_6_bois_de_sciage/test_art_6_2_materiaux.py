"""Tests de 6.2 Matériaux, tableau 6.3 (CSA O86:19, p. 48)."""

import pytest

from moteur.normes.csa_o86_19.ch_6_bois_de_sciage.art_6_2_materiaux import (
    admet_charpente_legere,
    categorie_de_bois,
)


@pytest.mark.parametrize(
    ("b", "d", "attendu"),
    [
        (38, 38, "Lumber"),  # 38 x 38 mm : tableau 6.4 par défaut (issue #34)
        (38, 64, "Lumber"),  # 38 x 64 mm : tableau 6.4 par défaut (issue #34)
        (64, 64, "Lumber"),
        (38, 89, "Lumber"),  # 38 x 89 mm : grande face de 89 mm -> tableau 6.4
        (89, 89, "Lumber"),  # 89 x 89 mm
        (38, 140, "Lumber"),  # 38 x 140 mm : solives et madriers
        (89, 387, "Lumber"),  # 89 x 387 mm : face étroite < 114 mm
        (140, 140, "Post"),  # 140 x 140 mm : 0 mm de plus -> poteaux
        (140, 191, "Post"),  # 191 mm - 140 mm = 51 mm (au plus 51 mm) -> poteaux
        (140, 192, "Beam"),  # 192 mm - 140 mm = 52 mm (plus de 51 mm) -> poutres
        (191, 140, "Post"),  # l'ordre b, d ne change rien
        (140, 241, "Beam"),  # 241 mm - 140 mm = 101 mm -> poutres
        (114, 114, "Post"),  # 114 mm : seuil inférieur du gros bois
        (114, 165, "Post"),  # 165 mm - 114 mm = 51 mm -> poteaux
        (114, 166, "Beam"),  # 166 mm - 114 mm = 52 mm -> poutres
        (38, 412, "Lumber"),  # 412 mm : dimension maximale acceptée
    ],
)
def test_categorie_de_bois(b, d, attendu):
    assert categorie_de_bois(b, d) == attendu


def test_msr_et_mel():
    assert categorie_de_bois(38, 140, msr=True) == "MSR"
    assert categorie_de_bois(38, 140, mel=True) == "MEL"
    assert categorie_de_bois(38, 140, msr=True, mel=True) == "MSR"  # MSR a priorité


def test_moins_de_38_mm():
    with pytest.raises(ValueError, match="38 mm"):
        categorie_de_bois(37, 140)  # 37 mm < 38 mm


def test_plus_de_412_mm():
    with pytest.raises(ValueError, match="fournisseurs"):
        categorie_de_bois(140, 413)  # 413 mm > 412 mm


# Tableau 6.3 et issue #34 : tableau 6.4 par défaut, tableau 6.5 (Const., Std.) au choix pour les
# sections de 38 à 89 mm x 38 à 89 mm, bornes incluses
@pytest.mark.parametrize(
    ("b", "d", "admet"),
    [
        (38, 38, True),
        (38, 64, True),
        (38, 89, True),  # borne de 89 mm incluse
        (89, 89, True),  # borne de 89 mm incluse
        (40, 91, False),  # 91 mm > 89 mm (2 x 4 vert)
        (38, 114, False),
        (89, 140, False),
    ],
)
def test_admet_charpente_legere(b, d, admet):
    assert admet_charpente_legere(b, d) is admet
    assert categorie_de_bois(b, d, charpente_legere=True) == ("Light" if admet else categorie_de_bois(b, d))


def test_charpente_legere_par_defaut_tableau_6_4():
    for b, d in ((38, 38), (38, 64), (38, 89), (64, 89), (89, 89)):
        assert categorie_de_bois(b, d) == "Lumber"  # tableau 6.4 par défaut


def test_charpente_legere_msr_mel_prioritaires():
    assert categorie_de_bois(38, 89, msr=True, charpente_legere=True) == "MSR"
    assert categorie_de_bois(38, 89, mel=True, charpente_legere=True) == "MEL"
