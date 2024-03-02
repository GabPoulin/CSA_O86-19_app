"""
CSA O86:19: Règles de calcul des charpentes en bois.
 Section 6. Bois de sciage.
----------------------------------------------------

6.X
    
____________________________________________________________________________________________________
    
    auteur: GabPoulin
    email: poulin33@me.com

"""

# IMPORTS
from dataclasses import dataclass
from sqlalchemy import orm, create_engine, Column, TEXT, REAL, INTEGER


# DB CONNECTION
@dataclass
class SubfloorProperties(orm.declarative_base()):
    """Se connecte à la table subfloor_properties de csa_o86_19.db."""

    __tablename__ = "subfloor_properties"
    panel: str = Column("panel", TEXT, primary_key=True)
    ts: float = Column("ts", REAL)
    rho_s: int = Column("rho_s", INTEGER)
    engine = create_engine("sqlite:///csa_o86_19.db")
    Session = orm.sessionmaker(engine)
    session = Session()


# CODE


# TESTS
def _tests():
    """
    Tests pour les calculs de bois de sciage.

    """
    pass


# RUN FILE
if __name__ == "__main__":
    _tests()


# END
