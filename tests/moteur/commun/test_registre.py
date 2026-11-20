"""Tests de moteur/commun/registre.py : catalogue des calculs par édition."""

import pytest

from moteur.commun import registre

EDITION = "edition_de_test"


def _fonction():
    return None


registre.enregistrer(EDITION, "6.5.10", "Platelage")(_fonction)
registre.enregistrer(EDITION, "6.5.9", "Flexion et charge axiale")(_fonction)
registre.enregistrer(EDITION, "A.6.5.6", "Densité")(_fonction)
registre.enregistrer(EDITION, "6.5.5", "Compression", acces="demonstration")(_fonction)
# Deux calculs du même article : un identifiant est alors donné au deuxième
registre.enregistrer(EDITION, "6.5.4", "Cisaillement")(_fonction)
registre.enregistrer(EDITION, "6.5.4", "Cisaillement à l'entaille", identifiant="6.5.4-entaille")(
    _fonction
)


def test_ordre_de_la_norme():
    assert [c.article for c in registre.calculs(EDITION)] == [
        "6.5.4", "6.5.4", "6.5.5", "6.5.9", "6.5.10", "A.6.5.6"
    ]


def test_calcul_et_acces():
    c = registre.calcul(EDITION, "6.5.5")
    assert c.acces == "demonstration" and c.titre == "Compression" and c.fonction is _fonction
    assert registre.calcul(EDITION, "6.5.9").acces == "abonne"
    assert EDITION in registre.editions()
    assert registre.calcul(EDITION, "6.5.4-entaille").article == "6.5.4"


def test_doublon_refuse():
    with pytest.raises(ValueError):
        registre.enregistrer(EDITION, "6.5.5", "Doublon")(_fonction)


def test_acces_invalide():
    with pytest.raises(ValueError):
        registre.enregistrer(EDITION, "6.5.3", "x", acces="gratuit")


def test_calcul_absent():
    with pytest.raises(KeyError):
        registre.calcul(EDITION, "9.9.9")
    assert registre.calculs("edition_inexistante") == []


def test_nom_de_l_edition():
    assert registre.nom_de_l_edition("csa_o86_19") == "CSA O86:19"
    with pytest.raises(KeyError):
        registre.nom_de_l_edition("csa_o86_99")  # dossier absent
    with pytest.raises(KeyError):
        registre.nom_de_l_edition("commun")  # pas une édition (pas de NORME)
