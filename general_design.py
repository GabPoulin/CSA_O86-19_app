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

# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import create_engine, Column, TEXT, REAL, INTEGER


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
def kd(load_duration, dead=0, live=0, snow=0):
    """5.3.2 Coefficient de durée d'application de la charge, Kd.

    Args:
        load_duration: Durée d'application de la charge.
            ("courte", "normale", "continue")
        dead: charge de durée d'application continue.
        live: surcharge de durée d'application normale.
        snow: surcharge de neige.

    Returns:
        float: coefficient de durée d'application de la charge, Kd
    """

    if load_duration == "courte":
        kd = 1.15
    elif load_duration == "continue":
        kd = 0.65
        ps = max(snow, live, snow + 0.5 * live, 0.5 * snow + live)
        if ps > 0:
            pl = dead
            if pl > ps:
                kd = max(1 - 0.5 * math.log(pl / ps, 10), 0.65)
            else:
                kd = 1
    else:
        kd = 1

    kd = min(kd, 1.15)

    return kd


def section(net, gross):
    """5.3.8 Réduction de la section transversale.

    Args:
        net: section nette. (voir 5.3.8.1)
        gross: section brute.

    Returns:
        str: validation de la section nette.
    """

    if net < 0.75 * gross:
        message = (
            f"Section nette non-valide: {net} < {0.75*gross} (75% de la section brute)."
        )
    else:
        message = (
            f"Section nette valide: {net} > {0.75*gross} (75% de la section brute)."
        )

    return message


def elasticity(modulus, service, treatment):
    """5.4.1 Module d'élasticité.

    Args:
        modulus:  module d'élasticité prévu, MPa.
        service: coefficient de conditions d'utilisation.
        treatment: coefficient de traitement.

    Returns:
        float: module d'élasticité, Es (MPa).
    """

    return modulus * (service * treatment)


def deflection(span, delta):
    """5.4.2 Flèche élastique. 5.4.3 Déformation permanente.

    Args:
        span:  Portée, mm.
        delta: Flèche, mm.

    Returns:
        str: critère de flèche obtenu.
    """

    return f"Critère de flèche: L/{int(span / delta)}"


def ponding(load, *delta):
    """5.4.4 Accumulation d'eau.

    Args:
        load: charge totale spécifiée uniformément répartie, kPa.
        delta: flèche pour chaque élément constitutif du système, mm.

    Returns:
        str: satisfait ou non la condition pour accumulation d'eau.
    """

    total = 0
    for i in delta:
        total += i

    verif = total / load
    if verif < 65:
        message = f"Condition pour accumulation d'eau satisfaite: {verif} < 65"
    else:
        message = (
            "Une analyse rationnelle pour assurer la tenue en service en cas d'accumulation "
            f"d'eau est nécessaire!: {verif} > 65"
        )

    return message


@dataclass
class Vibration:
    """5.4.5 Vibration."""

    thickness: int
    multiple_span: bool = False
    floor_topping: bool = False

    def floor_vibration(self, clt=False):
        """5.4.5.2 Vibration des planchers.

        Args:
            clt: True, pour planchers faits de bois lamellé-croisé.

        Returns:
            float: limite de la portée pour le contrôle des vibrations, m.
        """

        if clt:
            span = self._clt_vibration()
        else:
            span = self._span_limit()

        return span

    def _span_limit(self):

        lv = 1

        return lv

    def _clt_vibration(self):
        """A.8.5.3 Tenue aux vibrations des planchers faits de bois lamellé-croisé.

        Returns:
            float: limite de la portée pour le contrôle des vibrations, m
        """

        ei_eff_f = 650e9  # ajuster avec 8.4.3.2
        poids = 5200  # ajuster avec database
        m = (poids * (self.thickness / 1000)) / 9.80665
        lv = 0.11 * (((ei_eff_f / 10**6) ** 0.29) / (m**0.12))

        if self.multiple_span and self.floor_topping and lv < 8:
            lv = min(1.2 * lv, 8)

        return lv


# TESTS
def _tests():
    """tests pour la classe SnowLoads."""

    print("------START_TESTS------")

    test_kd = kd(load_duration="continue", dead=1, live=0.5, snow=0.1)
    expected_result = 0.8701813447471219
    if test_kd != expected_result:
        print("test_kd -> FAILED")
        print("result = ", test_kd)
        print("expected = ", expected_result)
    else:
        print("test_kd -> PASSED")

    test_section = section(net=25, gross=30)
    expected_result = "Section nette valide: 25 > 22.5 (75% de la section brute)."
    if test_section != expected_result:
        print("test_section -> FAILED")
        print("result = ", test_section)
        print("expected = ", expected_result)
    else:
        print("test_section -> PASSED")

    test_es = elasticity(modulus=70.0, service=0.5, treatment=1)
    expected_result = 35
    if test_es != expected_result:
        print("test_es -> FAILED")
        print("result = ", test_es)
        print("expected = ", expected_result)
    else:
        print("test_es -> PASSED")

    test_deflection = deflection(span=1800, delta=10)
    expected_result = "Critère de flèche: L/180"
    if test_deflection != expected_result:
        print("test_deflection -> FAILED")
        print("result = ", test_deflection)
        print("expected = ", expected_result)
    else:
        print("test_deflection -> PASSED")

    test_ponding = ponding(2, 10, 13)
    expected_result = "Condition pour accumulation d'eau satisfaite: 11.5 < 65"
    if test_ponding != expected_result:
        print("test_ponding -> FAILED")
        print("result = ", test_ponding)
        print("expected = ", expected_result)
    else:
        print("test_ponding -> PASSED")

    test_floor_vibration = Vibration(
        thickness=150,
        multiple_span=True,
        floor_topping=True,
    ).floor_vibration(True)
    expected_result = 3.7866043840767682
    if test_floor_vibration != expected_result:
        print("test_floor_vibration -> FAILED")
        print("result = ", test_floor_vibration)
        print("expected = ", expected_result)
    else:
        print("test_floor_vibration -> PASSED")

    print("-------END_TESTS-------")


# RUN FILE
if __name__ == "__main__":
    _tests()


# END
