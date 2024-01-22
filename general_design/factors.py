"""

CSA O86:19: Règles de calcul des charpentes en bois.
Section 5. Conception générale.
-----------------------------------------------

5.3 Conditions et coefficients influant sur la résistance.

    Détermine les différents coefficients relatif aux calculs.
____________________________________________________________________________________________________
    

    auteur: GabPoulin
    email: poulin33@me.com

====================================================================================================
"""

# IMPORTS
import math
from dataclasses import dataclass
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, TEXT, REAL, INTEGER


# DB CONNECTION
# @dataclass
# class LiveLoadsTable(declarative_base()):
#    """Se connecte à la table X de loads.db."""
#
#    __tablename__ = "X"
#    XX: str = Column("XX", TEXT, primary_key=True)
#    XXX: float = Column("XXX", REAL)
#    engine = create_engine("sqlite:///loads.db")
#    Session = sessionmaker(engine)
#    session = Session()


# CODE
@dataclass
class Factors:
    """5.3 Coefficients."""

    def kd(self, load_duration, d=0, l=0, s=0):
        """5.3.2 Coefficient de durée d'application de la charge, Kd.

        Args:
            load_duration: Durée d'application de la charge.
            d: charge de durée d'application continue
            l: surcharge de durée d'application normale
            s: charge de neige de durée d'application normale
        """

        kd = 1
        if load_duration == "Courte":
            kd = 1.15
        elif load_duration == "Continue":
            kd = 0.65
            pl = d
            ps = max(s, l, s + 0.5 * l, 0.5 * s + l)
            if ps > 0:
                if pl > ps:
                    kd = max(1 - (0.5 * math.log(pl / ps, 10)), 0.65)
                else:
                    kd = 1
        kd = min(kd, 1.15)

        return kd


# TESTS
def tests():
    """tests pour la classe SnowLoads."""

    print("------START_TESTS------")

    test1 = Factors().kd(load_duration="Continue", d=1, l=0.5)
    expected_result = 0.8494850021680094
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
