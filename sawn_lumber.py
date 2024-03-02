"""
CSA O86:19: Règles de calcul des charpentes en bois.
Section 6. Bois de sciage.
-----------------------------------------------

5.3 Conditions et coefficients influant sur la résistance.
        Détermine les différents coefficients relatif aux calculs.
        Vérification de la section nette.
    
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
    rho_s: int = Column("rho_s", INTEGER)
    engine = create_engine("sqlite:///csa_o86_19.db")
    Session = sessionmaker(engine)
    session = Session()


# CODE
@dataclass
class Vibration:
    """5.4.5 Vibration.

    Args:
        span: L = portée du plancher, m.
    """

    span: float

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
        lv_increase = 1.05 * lv
        if self.bracing and not self.topping == "béton":
            lv = lv_increase
        if self.gypsum and self.topping == "aucun/autre":
            lv = lv_increase

        return lv

    def _table_a1(self):
        """Tableau A.1 Propriétés des panneaux de sous-plancher."""
        return (
            SubfloorProperties.session.query(SubfloorProperties)
            .filter(SubfloorProperties.panel == self.subfloor)
            .first()
        )


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

    print("-------END_TESTS-------")


# RUN FILE
if __name__ == "__main__":
    _tests()


# END
