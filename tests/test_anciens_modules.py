"""
Tests des anciens modules (sawn_lumber.py et general_design.py), conservés pendant la migration.

Ils roulent les fonctions _tests() existantes pour que `pytest` vérifie tout le projet.
"""

from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("module", ["sawn_lumber", "general_design"])
def test_module(module, monkeypatch):
    monkeypatch.chdir(RACINE)  # la base de données est lue avec un chemin relatif
    _tests = __import__(module)._tests
    _tests()
