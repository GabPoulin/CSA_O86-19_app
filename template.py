"""

CSA O86:19: Règles de calcul des charpentes en bois.
Section 4.1. Charges et méthodes de calcul.
-----------------------------------------------

4.1.6. Charge due à la neige et à la pluie.

    desc.
____________________________________________________________________________________________________
    

    auteur: GabPoulin
    email: poulin33@me.com

====================================================================================================
"""

# IMPORTS
from dataclasses import dataclass
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, TEXT, REAL, INTEGER


# DB CONNECTION
@dataclass
class LiveLoadsTable(declarative_base()):
    """Se connecte à la table X de loads.db."""

    __tablename__ = "X"
    XX: str = Column("XX", TEXT, primary_key=True)
    XXX: float = Column("XXX", REAL)
    engine = create_engine("sqlite:///loads.db")
    Session = sessionmaker(engine)
    session = Session()


# CODE
@dataclass
class SnowLoads:
    """4.1.6. Charge due à la neige et à la pluie.

    Args:
        arg: desc.
    """

    arg: str = "default value"

    def func_name(self):
        """4.1.6.X. desc.

        Args:
            arg: desc.
        """

        return None


# TESTS
def tests():
    """tests pour la classe SnowLoads."""

    print("------START_TESTS------")

    test1 = SnowLoads().func_name()
    expected_result = None
    if test1 != expected_result:
        print("test1 -> FAILED")
        print("result = ", test1)
        print("expected = ", expected_result)
    else:
        print("test1 -> PASSED")

    print("-------END_TESTS-------")


# RUN FILE
if __name__ == "__main__":
    tests()


# END
