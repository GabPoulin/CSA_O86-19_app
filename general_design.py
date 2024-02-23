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

    bracing: bool = False
    clt_thickness: int = 0
    concrete_thickness: int = 0
    gypsum: bool = False
    joist_mass: float = 0
    multiple_span: bool = False
    spacing: float = 16
    topping_thickness: int = 0

    def floor_vibration(self):
        """5.4.5.2 Vibration des planchers.

        Returns:
            float: limite de la portée pour le contrôle des vibrations, m.
        """

        if self.clt_thickness > 0:
            span = self._clt_vibration()
        else:
            span = self._joist_vibration()

        return span

    def _joist_vibration(self):
        """A.5.4.5 Tenue aux vibrations des planchers en solives en bois.
            A.5.4.5.1 Portée pour le contrôle des vibrations : méthode générale.

        Returns:
            float: portée pour le contrôle des vibrations, m.
        """

        ei_eff = self._bending_stiffness()
        if self.multiple_span and not self.concrete_thickness > 0:
            ei_eff *= 1.2
        ktss = self._stiffness_factor()
        ml = self._linear_mass()
        lv = (0.122 * ei_eff**0.284) / (ktss**0.14 * ml**0.15)
        if self.bracing and not self.concrete_thickness > 0:
            lv *= 1.05
        if (
            self.gypsum
            and not self.concrete_thickness > 0
            and not self.topping_thickness > 0
        ):
            lv *= 1.05

        return lv

    def _bending_stiffness(self):
        """A.5.4.5.1.1 Rigidité composite en flexion du système de plancher dans la direction de
        la portée des solives.

        Returns:
            float: rigidité composite en flexion du système de plancher, N*m2.
        """

        ei_eff = 10e3

        return ei_eff

    def _linear_mass(self):
        """A.5.4.5.1.2 Masse linéaire du plancher dans la direction de la portée des solives.

        Returns:
            float: masse linéaire de la section transversale composite du plancher, kg/m.
        """

        mj = self.joist_mass
        rho_s = 500  # tableau A.1
        ts = 15.5 / 1000  # tableau A.1
        rho_c = 2300
        tc = self.concrete_thickness
        rho_w = 600
        tw = self.topping_thickness
        b1 = self.spacing * 0.0254

        ml = mj + rho_s * ts * b1 + rho_c * tc * b1 + rho_w * tw * b1

        return ml

    def _stiffness_factor(self):
        """A.5.4.5.1.3 Coefficient de rigidité transversale du système.

        Returns:
            float: coefficient de rigidité transversale, Ktss.
        """

        ktss = 1

        return ktss

    def _clt_vibration(self):
        """A.8.5.3 Tenue aux vibrations des planchers faits de bois lamellé-croisé.

        Returns:
            float: limite de la portée pour le contrôle des vibrations, m.
        """

        ei_eff_f = 650e9  # ajuster avec 8.4.3.2
        poids = 5200 / 9.80665  # ajuster avec database
        m = poids * self.clt_thickness
        lv = 0.11 * (((ei_eff_f / 10**6) ** 0.29) / (m**0.12))

        if self.multiple_span and lv < 8:
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

    test_floor_vibration_joist = Vibration(
        bracing=True,
        clt_thickness=0,
        concrete_thickness=0,
        gypsum=True,
        joist_mass=100,
        multiple_span=True,
        spacing=16,
        topping_thickness=20,
    ).floor_vibration()
    expected_result = 1
    if test_floor_vibration_joist != expected_result:
        print("test_floor_vibration_joist -> FAILED")
        print("result = ", test_floor_vibration_joist)
        print("expected = ", expected_result)
    else:
        print("test_floor_vibration_joist -> PASSED")

    test_floor_vibration_clt = Vibration(
        clt_thickness=0.150,
        multiple_span=True,
    ).floor_vibration()
    expected_result = 3.7866043840767682
    if test_floor_vibration_clt != expected_result:
        print("test_floor_vibration_clt -> FAILED")
        print("result = ", test_floor_vibration_clt)
        print("expected = ", expected_result)
    else:
        print("test_floor_vibration_clt -> PASSED")

    print("-------END_TESTS-------")


# RUN FILE
if __name__ == "__main__":
    _tests()


# END
