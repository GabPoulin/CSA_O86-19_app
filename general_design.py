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

    span: float

    bracing: bool = False
    clt_thickness: int = 0
    glued: bool = False
    gypsum: bool = False
    joist_axial_stiffness: float = 0
    joist_bending_stiffness: float = 0
    joist_depth: float = 0
    joist_mass: float = 0
    joist_spacing: float = 0
    multiple_span: bool = False
    topping: str = "aucun/autre"
    topping_thickness: int = 0

    def floor_vibration(self):
        """5.4.5.2 Vibration des planchers.

        Returns:
            str: validation du critère de vibration.
        """

        span = self.span

        if self.clt_thickness > 0:
            max_span = self._clt_vibration()
        else:
            max_span = self._joist_vibration()

        if span <= max_span:
            message = (
                "Critère de vibration satisfait:\n"
                f"\tPortée maximale\t->\t{max_span} m.\n"
                f"\tPortée actuelle\t->\t{span} m."
            )
        else:
            message = (
                "Critère de vibration non-satisfait:\n"
                f"\tPortée maximale\t->\t{max_span} m.\n"
                f"\tPortée actuelle\t->\t{span} m."
            )

        return message

    def _joist_vibration(self):
        """A.5.4.5 Tenue aux vibrations des planchers en solives en bois.
            A.5.4.5.1 Portée pour le contrôle des vibrations : méthode générale.

        Returns:
            float: lv, portée pour le contrôle des vibrations, m.
        """

        ei_eff = self._bending_stiffness()
        if self.multiple_span and not self.topping == "béton":
            ei_eff *= 1.2
        ktss = self._stiffness_factor()
        ml = self._linear_mass()

        lv = (0.122 * ei_eff**0.284) / (ktss**0.14 * ml**0.15)
        if self.bracing and not self.topping == "béton":
            lv *= 1.05
        if self.gypsum and self.topping == "aucun/autre":
            lv *= 1.05

        return lv

    def _bending_stiffness(self):
        """A.5.4.5.1.1 Rigidité composite en flexion du système de plancher dans la direction de
        la portée des solives.

        Returns:
            float: EIeff, rigidité composite en flexion du système de plancher, N*m2.
        """

        ei_joist = self.joist_bending_stiffness
        eis_perp = 1  # tableau A.1
        tc = self._table_a2()[0]
        ec = self._table_a2()[1]
        eic = (ec * tc**3) / 12
        b1 = self.joist_spacing
        eiu = ei_joist + b1 * (eis_perp + eic)

        eas_perp = 1  # tableau A.1
        eac = ec * tc
        ea1 = eas_perp + eac
        s1 = 5e6
        if self.glued and self.topping == "aucun/autre":
            s1 = 1e8
        l1 = self.span
        if self.topping == "aucun/autre":
            l1 = 1.2192  # panneaux de sous-plancher ayant une largeur de 4'
        ea1_barre = (b1 * ea1) / (1 + 10 * ((b1 * ea1) / (s1 * l1**2)))

        ea_joist = self.joist_axial_stiffness
        a_barre = ea_joist + ea1_barre

        d = self.joist_depth
        ts = 1  # tableau A.1
        h1 = (d / 2) + (
            (eas_perp * (ts / 2) + eac * (ts + (tc / 2))) / (eas_perp + eac)
        )
        y_barre = (h1 * ea1_barre) / a_barre

        ei_eff = eiu + ea1_barre * h1**2 - a_barre * y_barre**2

        return ei_eff

    def _linear_mass(self):
        """A.5.4.5.1.2 Masse linéaire du plancher dans la direction de la portée des solives.

        Returns:
            float: ml, masse linéaire de la section transversale composite du plancher, kg/m.
        """

        mj = self.joist_mass
        rho_s = 1  # tableau A.1
        rho_c = self._table_a2()[2]
        ts = 1  # tableau A.1
        tc = self._table_a2()[0]
        b1 = self.joist_spacing

        ml = mj + (rho_s * ts * b1) + (rho_c * tc * b1)

        return ml

    def _stiffness_factor(self):
        """A.5.4.5.1.3 Coefficient de rigidité transversale du système.

        Returns:
            float: Ktss, coefficient de rigidité transversale.
        """

        span = self.span
        eis_par = 1  # tableau A.1
        b1 = self.joist_spacing
        if self.topping == "aucun/autre":
            kl = (0.585 * span * eis_par) / b1**3
        else:
            eas_par = 1  # tableau A.1
            ec = self._table_a2()[1]
            tc = self.topping_thickness
            eic = (ec * tc**3) / 12
            eac = ec * tc
            ts = 1  # tableau A.1
            tc = self.topping_thickness
            h3 = (ts + tc) / 2
            kl = (
                0.585
                * span
                * (eis_par + eic + ((eac * eas_par) / (eac + eas_par)) * h3**2)
            ) / b1**3

        ei_eff = self._bending_stiffness()
        kj = ei_eff / span**3
        k1 = kj / (kj + kl)

        ktss = 0.0294 + (0.536 * k1**0.25) + (0.516 * k1**0.5) + (0.31 * k1**0.75)

        return ktss

    def _table_a2(self):
        """Tableau A.2.
            Propriétés des matériaux de revêtement.

        Returns:
            float: tc, épaisseur du revêtement, m.
            float: Ec, module d'élasticité du revêtement, N/m2.
            float: Pc, densité du revêtement, kg/m3.
        """

        if self.topping == "aucun/autre":
            tc = 0
            ec = 0
            pc = 0
        elif self.topping == "béton":
            tc = self.topping_thickness
            ec = 22e9
            pc = 2300
        else:
            eisc_perp = 1  # tableau A.1
            tc = 1  # tableau A.1 / 1000
            ec = (12 * eisc_perp) / tc**3
            pc = 1  # tableau A.1

        return tc, ec, pc

    def _clt_vibration(self):  # ajuster
        """A.8.5.3 Tenue aux vibrations des planchers faits de bois lamellé-croisé.

        Returns:
            float: lv, limite de la portée pour le contrôle des vibrations, m.
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

    test_elasticity = elasticity(modulus=70.0, service=0.5, treatment=1)
    expected_result = 35
    if test_elasticity != expected_result:
        print("test_elasticity -> FAILED")
        print("result = ", test_elasticity)
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
        span=2,
        bracing=True,
        clt_thickness=0,
        glued=True,
        gypsum=True,
        joist_axial_stiffness=100,
        joist_bending_stiffness=100,
        joist_depth=0.25,
        joist_mass=100,
        joist_spacing=0.4,
        multiple_span=True,
        topping="béton",
        topping_thickness=20,
    ).floor_vibration()
    expected_result = (
        "Critère de vibration satisfait:\n"
        "\tPortée maximale\t->\tX m.\n"
        "\tPortée actuelle\t->\t2 m."
    )
    if test_floor_vibration_joist != expected_result:
        print("test_floor_vibration_joist -> FAILED")
        print("result = ", test_floor_vibration_joist)
        print("expected = ", expected_result)
    else:
        print("test_floor_vibration_joist -> PASSED")

    test_floor_vibration_clt = Vibration(
        span=2,
        clt_thickness=0.150,
        multiple_span=True,
    ).floor_vibration()
    expected_result = (
        "Critère de vibration satisfait:\n"
        "\tPortée maximale\t->\tX m.\n"
        "\tPortée actuelle\t->\t2 m."
    )
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
