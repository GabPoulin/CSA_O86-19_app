"""
CSA O86:19 - Base de données des tableaux de la norme (SQLite).

Accès unique, en lecture seule, avec un chemin absolu (indépendant du dossier de lancement).
"""

import sqlite3
from pathlib import Path

CHEMIN = Path(__file__).resolve().parent / "csa_o86_19.db"


def lire(requete: str, parametres: tuple = ()) -> list[sqlite3.Row]:
    """
    Exécute une requête de lecture et retourne les lignes.

    Args:
        requete (str): Requête SQL (SELECT).
        parametres (tuple, optional): Paramètres de la requête.

    Returns:
        list[sqlite3.Row]: Lignes, accessibles par nom de colonne.
    """
    with sqlite3.connect(f"file:{CHEMIN}?mode=ro", uri=True) as connexion:
        connexion.row_factory = sqlite3.Row
        return connexion.execute(requete, parametres).fetchall()
