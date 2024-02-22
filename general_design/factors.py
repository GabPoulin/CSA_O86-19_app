"""
CSA O86:19: Règles de calcul des charpentes en bois.
Section 5. Conception générale.
-----------------------------------------------

5.3 Conditions et coefficients influant sur la résistance.
    Détermine les différents coefficients relatif aux calculs.
    Vérification de la section nette.
    
5.4 Exigences relatives à la tenue en service
    Calculs pour module d'élasticité, flèche et vibration.
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
    """5.3 Conditions et coefficients influant sur la résistance."""

    def kd(self, load_duration, d=0, l=0, s=0):
        """5.3.2 Coefficient de durée d'application de la charge, Kd.

        Args:
            load_duration: Durée d'application de la charge.
            d: charge de durée d'application continue.
            l: surcharge de durée d'application normale.
            s: surcharge de neige.

        Returns:
            float|int: Coefficient de durée d’application de la charge, Kd
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
                    kd = max(1 - 0.5 * math.log(pl / ps, 10), 0.65)
                else:
                    kd = 1
        kd = min(kd, 1.15)

        return kd

    def cross_section(self, net, gross):
        """5.3.8 Réduction de la section transversale.

        Args:
            net: section nette. 5.3.8.1
            gross: section brute.

        Returns:
            str: Satisfait ou non la condition.
        """


@dataclass
class Serviceability:
    """5.4 Exigences relatives à la tenue en service."""

    def es(self, e, kse, kt):
        """5.4.1 Module d'élasticité.

        Args:
            e:  module d'élasticité prévu, MPa.
            kse: coefficient de conditions d'utilisation.
            kt: coefficient de traitement.

        Returns:
            float|int: Module d'élasticité, Es.
        """

        return e * (kse * kt)

    def deflection(self, l, delta):
        """5.4.2 Flèche élastique. 5.4.3 Déformation permanente.

        Args:
            l:  Portée, mm.
            delta: Flèche, mm.

        Returns:
            str: Critère de flèche obtenu.
        """

        return f"L/{int(l / delta)}"

    def ponding(self, w, *delta):
        """5.4.4 Accumulation d’eau.

        Args:
            w: charge totale spécifiée uniformément répartie, kPa.
            delta: flèche pour chaque élément constitutif du système, mm.

        Returns:
            str: Satisfait ou non la condition.
        """

        total = 0
        for i in delta:
            total = total + i

        verif = total / w
        if verif < 65:
            message = f"Condition satisfaite: {verif} < 65"
        else:
            message = f"Condition non satisfaite: {verif} !< 65"

        return message


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

    test2 = Serviceability().es(e=70.0, kse=0.5, kt=1)
    expected_result = 35
    if test2 != expected_result:
        print("test2 -> FAILED")
        print("result = ", test2)
        print("expected = ", expected_result)
    else:
        print("test2 -> PASSED")

    test3 = Serviceability().deflection(l=1800, delta=10)
    expected_result = "L/180"
    if test3 != expected_result:
        print("test3 -> FAILED")
        print("result = ", test3)
        print("expected = ", expected_result)
    else:
        print("test3 -> PASSED")

    test4 = Serviceability().ponding(2, 10, 13)
    expected_result = "Condition satisfaite: 11.5 < 65"
    if test4 != expected_result:
        print("test4 -> FAILED")
        print("result = ", test4)
        print("expected = ", expected_result)
    else:
        print("test4 -> PASSED")

    print("-------END_TESTS-------")


# RUN FILE
if __name__ == "__main__":
    tests()


# END
