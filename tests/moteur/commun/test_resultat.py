"""Tests de moteur/commun/resultat.py : trace d'une vérification."""

import pytest

from moteur.commun.resultat import Donnee, Etape, Resultat
from moteur.commun.verification import verifier


def _resultat():
    r = Resultat("CSA O86:19", "6.5.5", "Compression parallèle au fil", figure="colonne")
    r.ajouter_donnee(Donnee("f_c", "Résistance prévue", 11.5, "MPa", "contrainte", "Tableau 6.4"))
    r.ajouter_etape(Etape("6.5.5.2.2", "Élancement", "C_C", "C_C = L_e / b", "1500 / 38", 39.47))
    r.ajouter_etape(Etape("6.5.5.2.2", "Élancement", "C_C", "C_C = L_e / d", "3000 / 140", 21.43))
    r.verification = verifier(10, 12.62, "P_f", "P_r", "kN", "force")
    return r


def test_ajouter_retourne_la_valeur():
    r = Resultat("CSA O86:19", "6.5.5", "Test")
    assert r.ajouter_etape(Etape("6.5.5.2.4", "F_c", "F_c", "f_c", "11.5", 11.5, "MPa")) == 11.5
    assert r.ajouter_donnee(Donnee("b", "Largeur", 38, "mm", "dimension")) == 38


def test_trace_complete():
    r = _resultat()
    assert r.norme == "CSA O86:19" and r.figure == "colonne"
    assert len(r.donnees) == 1 and len(r.etapes) == 2
    assert r.verification.respecte


def test_etape_retourne_la_derniere():
    assert _resultat().etape("C_C").valeur == 21.43


def test_etape_absente():
    with pytest.raises(KeyError):
        _resultat().etape("P_r")
