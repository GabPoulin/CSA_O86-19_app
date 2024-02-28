"""
CSA O86:19: Règles de calcul des charpentes en bois.
Section 5. Conception générale.
-----------------------------------------------

5.3 Conditions et coefficients influant sur la résistance.
        Détermine les différents coefficients relatif aux calculs.
        Vérification de la section nette.
    
5.4 Exigences relatives à la tenue en service.
        Calculs pour module d'élasticité.
        Critères de flèche.
        Vérification d'accumulation d'eau.
        Critère de vibration des planchers.
        Mouvements du bâtiment attribuables aux changements de la teneur en humidité.
        
5.5 Effort de contreventement latéral sur les membrures d'âme en compression des
    fermes de toit en bois.
        Calcul de l'effort applicable sur les contreventements.
        
5.6 Résistance au feu.
        Méthode de calcul de la résistance au feu.
    
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
@dataclass
class SubfloorProperties(declarative_base()):
    """Se connecte à la table subfloor_properties de csa_o86_19.db."""

    __tablename__ = "subfloor_properties"
    panel: str = Column("panel", TEXT, primary_key=True)
    ts: float = Column("ts", REAL)
    eis_par: int = Column("EIs_par", INTEGER)
    eis_perp: int = Column("EIs_perp", INTEGER)
    eas_par: float = Column("EAs_par", REAL)
    eas_perp: float = Column("Eas_perp", REAL)
    rho_s: int = Column("rho_s", INTEGER)
    engine = create_engine("sqlite:///csa_o86_19.db")
    Session = sessionmaker(engine)
    session = Session()


# CODE
def load_duration(duration, dead=0, live=0, snow=0):
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

    if duration == "courte":
        kd = 1.15
    elif duration == "continue":
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


def cross_section(net, gross):
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
    """5.4.2 Flèche élastique. / 5.4.3 Déformation permanente.

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
    """5.4.5 Vibration.

    Args:
        span: L = portée du plancher, m.
        bracing: contreventement latéraux = False.
        clt_bending_stiffness: (EI)eff,f = rigidité effective en flexion à plat d'un panneau de 1 m de largeur, N*mm2.
        clt_mass: m = masse linéaire du clt pour un panneau de 1 m de largeur, kg/m.
        glued: sous-plancher collé sur les solives = False.
        gypsum: panneau de gypse directement sous les solives = False.
        joist_axial_stiffness: EAjoist = rigidité axiale de la solive, N.
        joist_bending_stiffness: EIjoist = rigidité apparente en flexion de la solive, N*m2.
        joist_depth: d = hauteur de solive, m.
        joist_mass: mJ = masse par unité de longueur de solive, kg/m.
        joist_spacing: b1 = espacement des solives, m.
        multiple_span: portée multiple = False.
        subfloor: type de sous-plancher = "CSP 5/8" ou Tableau A.1.
        topping: type de revêtement = "aucun/autre", "béton" ou Tableau A.1.
        topping_thickness: tc = épaisseur du revêtement, m.
    """

    span: float
    bracing: bool = False
    clt_bending_stiffness: float = 0
    clt_mass: float = 0
    glued: bool = False
    gypsum: bool = False
    joist_axial_stiffness: float = 0
    joist_bending_stiffness: float = 0
    joist_depth: float = 0
    joist_mass: float = 0
    joist_spacing: float = 0
    multiple_span: bool = False
    subfloor: str = "CSP 5/8"
    topping: str = "aucun/autre"
    topping_thickness: int = 0

    def floor_vibration(self):
        """5.4.5.2 Vibration des planchers.

        Returns:
            str: validation du critère de vibration.
        """

        span = self.span

        if self.clt_mass > 0 or self.clt_bending_stiffness > 0:
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
        eis_perp = self._table_a1().eis_perp
        tc = self._table_a2()[0]
        ec = self._table_a2()[1]
        eic = (ec * tc**3) / 12
        b1 = self.joist_spacing
        eiu = ei_joist + b1 * (eis_perp + eic)

        eas_perp = self._table_a1().eas_perp
        eac = self._table_a2()[3]
        ea1 = eas_perp + eac
        s1 = 5e6
        if self.glued and self.topping == "aucun/autre":
            s1 = 1e8
        l1 = self.span
        if self.topping == "aucun/autre":
            l1 = 1.2192  # panneaux de sous-plancher sont considérés ayant une largeur de 4'
        ea1_barre = (b1 * ea1) / (1 + 10 * ((b1 * ea1) / (s1 * l1**2)))

        ea_joist = self.joist_axial_stiffness
        a_barre = ea_joist + ea1_barre

        d = self.joist_depth
        ts = self._table_a1().ts / 1000
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
        rho_s = self._table_a1().rho_s
        rho_c = self._table_a2()[2]
        ts = self._table_a1().ts / 1000
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
        eis_par = self._table_a1().eis_par
        b1 = self.joist_spacing
        if self.topping == "aucun/autre":
            kl = (0.585 * span * eis_par) / b1**3
        else:
            eas_par = self._table_a1().eas_par
            ec = self._table_a2()[1]
            tc = self._table_a2()[0]
            eic = (ec * tc**3) / 12
            ts = self._table_a1().ts / 1000
            h3 = (ts + tc) / 2
            eac = self._table_a2()[3]
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

    def _table_a1(self):
        """Tableau A.1 Propriétés des panneaux de sous-plancher."""
        return (
            SubfloorProperties.session.query(SubfloorProperties)
            .filter(SubfloorProperties.panel == self.subfloor)
            .first()
        )

    def _table_a2(self):
        """Tableau A.2 Propriétés des matériaux de revêtement.

        Returns:
            float: tc, épaisseur du revêtement, m.
            float: Ec, module d'élasticité du revêtement, N/m2.
            float: Pc, densité du revêtement, kg/m3.
            float: EAc, rigidité axiale d'un panneau de revêtement de 1 m de largeur, N/m.
        """

        if self.topping == "aucun/autre":
            tc = 0
            ec = 0
            pc = 0
            eac = 0
        elif self.topping == "béton":
            tc = self.topping_thickness
            ec = 22e9
            pc = 2300
            eac = ec * self.topping_thickness
        else:
            table_a1 = (
                SubfloorProperties.session.query(SubfloorProperties)
                .filter(SubfloorProperties.panel == self.topping)
                .first()
            )
            eisc_perp = table_a1.eis_perp
            tc = table_a1.ts / 1000
            ec = (12 * eisc_perp) / tc**3
            pc = table_a1.rho_s
            eac = table_a1.eas_perp

        return tc, ec, pc, eac

    def _clt_vibration(self):
        """A.8.5.3 Tenue aux vibrations des planchers faits de bois lamellé-croisé.

        Returns:
            float: lv, limite de la portée pour le contrôle des vibrations, m.
        """

        ei_eff_f = self.clt_bending_stiffness
        m = self.clt_mass
        if self.topping == "béton":
            concrete = self._table_a2()[2] * self.topping_thickness
            if not concrete > 2 * m:
                m += concrete
        lv = 0.11 * (((ei_eff_f / 10**6) ** 0.29) / (m**0.12))

        if self.multiple_span and lv < 8:
            lv = min(1.2 * lv, 8)

        return lv


def moisture(dimension, init_mc, final_mc, direction="perp", coefficient=0):
    """5.4.6 Mouvements du bâtiment attribuables au changement de la teneur en humidité.

    Args:
        dimension: D = dimension réelle (épaisseur, largeur ou longueur), mm.
        init_mc: Mi = teneur en humidité initiale, %.
        final_mc: Mf = teneur en humidité finale, %.
        direction: direction du fil pour le bois d'oeuvre = "perp", "para" ou "autre".
        coefficient: c = coefficient de retrait.

    Returns:
        float: S = retrait ou gonflement de la dimension considérée, mm.
    """

    d = dimension
    mi = min(init_mc, 28)
    mf = final_mc
    if direction == "perp":
        c = 0.002
    elif direction == "para":
        c = 0.00005
    else:
        c = coefficient
    s = d * (mi - mf) * c

    return s


def lateral_brace(force):
    """5.5 Effort de contreventement latéral sur les membrures d'âme en
        compression des fermes de toit en bois.

    Args:
        force: force de compression axiale qui s'exerce sur la membrure d'âme, kN.

    Returns:
        float: effort applicable au contreventement latéral, kN.
    """

    return 0.0125 * force


@dataclass
class FireResistance:
    """5.6 Résistance au feu."""

    def function1(self):
        pass


# TESTS
def _tests():
    """tests pour les calculs de conception générale."""

    print("------START_TESTS------")

    test_load_duration = load_duration(duration="continue", dead=1, live=0.5, snow=0.1)
    expected_result = 0.8701813447471219
    if test_load_duration != expected_result:
        print("test_load_duration -> FAILED")
        print("result = ", test_load_duration)
        print("expected = ", expected_result)
    else:
        print("test_load_duration -> PASSED")

    test_section = cross_section(net=25, gross=30)
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
        print("test_elasticity -> PASSED")

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
        glued=True,
        gypsum=True,
        joist_axial_stiffness=100,
        joist_bending_stiffness=100,
        joist_depth=0.3,
        joist_mass=100,
        joist_spacing=0.4,
        multiple_span=True,
        subfloor="OSB 5/8",
        topping="béton",
        topping_thickness=0.03,
    ).floor_vibration()
    expected_result = (
        "Critère de vibration non-satisfait:\n"
        "\tPortée maximale\t->\t1.2597785160882118 m.\n"
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
        clt_bending_stiffness=6.5e12,
        clt_mass=1000,
        multiple_span=True,
    ).floor_vibration()
    expected_result = (
        "Critère de vibration satisfait:\n"
        "\tPortée maximale\t->\t5.44902505257897 m.\n"
        "\tPortée actuelle\t->\t2 m."
    )
    if test_floor_vibration_clt != expected_result:
        print("test_floor_vibration_clt -> FAILED")
        print("result = ", test_floor_vibration_clt)
        print("expected = ", expected_result)
    else:
        print("test_floor_vibration_clt -> PASSED")

    test_moisture = moisture(
        dimension=150,
        init_mc=35,
        final_mc=12,
        direction="autre",
        coefficient=0.002,
    )
    expected_result = 4.8
    if test_moisture != expected_result:
        print("test_moisture -> FAILED")
        print("result = ", test_moisture)
        print("expected = ", expected_result)
    else:
        print("test_moisture -> PASSED")

    test_lateral_brace = lateral_brace(force=100)
    expected_result = 1.25
    if test_lateral_brace != expected_result:
        print("test_lateral_brace -> FAILED")
        print("result = ", test_lateral_brace)
        print("expected = ", expected_result)
    else:
        print("test_lateral_brace -> PASSED")

    print("-------END_TESTS-------")


# RUN FILE
if __name__ == "__main__":
    _tests()


# END
