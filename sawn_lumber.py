"""
CSA O86:19: Règles de calcul des charpentes en bois.
 6 Bois de sciage.
----------------------------------------------------

6.2 Matériaux.

6.3 Résistances prévues et modules d'élasticité.

6.4 Coefficients de correction.
    6.4.1 Coefficient de durée d'application de la charge, Kd.
     6.4.2 Coefficient de conditions d'utilisation, Ks.
      6.4.3 Coefficient de traitement, Kt.
       6.4.4 Coefficient de système, Kh.
        6.4.5 Coefficient de dimensions, Kz.
        
6.5 Calcul des résistances.
    6.5.2 Dimensions.
     6.5.3 Résistance au moment de flexion.
      6.5.4 Résistance au cisaillement.
       6.5.5 Résistance à la compression parallèle au fil.
        6.5.6 Résistance à la compression perpendiculaire au fil.
         6.5.7 Résistance à la compression oblique par rapport au fil.
          6.5.8 Résistance à la traction parallèle au fil.
           6.5.9 Résistance à la flexion et à la charge axiale combinées.
            6.5.10 Platelage.
             6.5.11 Fondations permanentes en bois.
              6.5.12 Applications propres aux fermes.
              
6.6 États limites de tenue en service.

____________________________________________________________________________________________________
    
    auteur: GabPoulin
    email: poulin33@me.com

"""

# IMPORTS
import general_design
from dataclasses import dataclass
from sqlalchemy import orm, create_engine, Column, TEXT, REAL, INTEGER


# DB CONNECTION
@dataclass
class SawnLumberStrengths(orm.declarative_base()):
    """
    Se connecte à la table sawn_lumber_strengths de csa_o86_19.db.

    """

    __tablename__ = "sawn_lumber_strengths"
    index: int = Column("index", INTEGER, primary_key=True)
    category: str = Column("category", TEXT)
    specie: str = Column("specie", TEXT)
    grade: str = Column("grade", TEXT)
    fb: float = Column("fb", REAL)
    fv: float = Column("fv", REAL)
    fc: float = Column("fc", REAL)
    fcp: float = Column("fcp", REAL)
    ft: float = Column("ft", REAL)
    e: int = Column("e", INTEGER)
    e05: int = Column("e05", INTEGER)
    engine = create_engine("sqlite:///csa_o86_19.db")
    Session = orm.sessionmaker(engine)
    session = Session()


# CODE
def lumber_category(
    width: int, depth: int, is_msr: bool = False, is_mel: bool = False
) -> str:
    """
    6.2 Matériaux.

    Args:
        width (int): Largeur de l'élément, mm.
        depth (int): Hauteur de l'élément, mm.
        is_msr (bool, optional): Bois de charpente classé mécaniquement par résistance (MSR).
        is_mel (bool, optional): Bois de charpente évalué par machine (MEL).

    Returns:
        str: Catégorie de bois d'oeuvre.

    Raises:
        ValueError: Si les dimensions sont trop petites.

    """
    small = min(width, depth)
    large = max(width, depth)

    if small < 38:
        raise ValueError("Les dimensions ne peuvent pas être plus petites que 38 mm.")

    if large > 394:
        print("Valider la disponibilité du bois chez les fournisseurs.")

    if small < 89 and large < 89:
        category = "Light"
    elif small >= 114:
        if large - small >= 51:
            category = "Beam"
        else:
            category = "Post"
    else:
        category = "Lumber"

    if is_mel:
        category = "MEL"

    if is_msr:
        category = "MSR"

    return category


def specified_strengths(
    category: str, specie: str, grade: str
) -> tuple[float, float, float, float, float, float, float]:
    """
    6.3 Résistances prévues et modules d'élasticité.

    Args:
        category (str): Catégorie. "Lumber", "Light", "Beam", "Post", "MSR" ou "MEL".
        specie (str): Groupe d'essence. "df", "hf", "spf" ou "ns".
            Pour catégorie MSR et MEL. "normal", "courant" ou "rare".
        grade (str): Classe. "ss", "n1", "n1-n2", "n2", "n3-stud", "cst" ou "std"
            Pour catégorie MSR, voir tableau 6.8. (ex: 1200Fb-1.2E = "1200-1.2")
            Pour catégorie MEL, voir tableau 6.9. (ex: M-10 = "m-10")

    Returns:
        float: fb = Résistance prévue en flexion, MPa.
        float: fv = Résistance prévue en cisaillement longitudinal, MPa.
        float: fc = Résistance prévue en compression parallèle au fil, MPa.
        float: fcp = Résistance prévue en compression perpendiculaire au fil, MPa.
        float: ft = Résistance prévue en traction parallèle au fil, MPa.
        float: E = Module d'élasticité prévu, MPa.
        float: E05 = Module d'élasticité pour les calculs des éléments en compression, MPa.

    """
    strengths = (
        SawnLumberStrengths.session.query(SawnLumberStrengths)
        .filter(SawnLumberStrengths.category == category)
        .filter(SawnLumberStrengths.specie == specie)
        .filter(SawnLumberStrengths.grade == grade)
        .first()
    )
    fb = strengths.fb
    fv = strengths.fv
    fc = strengths.fc
    fcp = strengths.fcp
    ft = strengths.ft
    e = strengths.e
    e05 = strengths.e05

    return fb, fv, fc, fcp, ft, e, e05


def modification_factors(
    width: int,
    depth: int,
    prop: str,
    duration: str,
    category: str,
    wet_service: bool = False,
    treated: bool = False,
    incised: bool = False,
    _2ft_spacing: bool = False,
    connected_subfloor: bool = False,
    built_up_beam: bool = False,
) -> tuple[float, float, float, float, float]:
    """
    6.4 Coefficients de correction.

    Args:
        width (int): Largeur de l'élément, mm.
        depth (int): Hauteur de l'élément, mm.
        prop (str): Propriété évaluée.
            "flex", "cis_f", "cis_l", "comp_para", "comp_perp", "trac" ou "moe".
        duration (str): Durée d'application de la charge. "courte", "normale" ou "continue".
        category (str): Catégorie. "Lumber", "Light", "Beam", "Post", "MSR" ou "MEL".
        wet_service (bool, optional): Utilisation en milieu humide, Default to False.
        treated (bool, optional): Bois traité, Default to False.
        incised (bool, optional): Bois incisé, Default to False.
        _2ft_spacing (bool, optional): L'espacement ne dépasse pas 610 mm, Default to False.
        connected_subfloor (bool, optional): Sous-plancher fixé, Default to False.
        built_up_beam (bool, optional): Poutres composées, Default to False.

    Returns:
        float: Kd = Coefficient de durée d'application de la charge.
        float: Ks = Coefficient de conditions d'utilisation.
        float: Kt = Coefficient de traitement.
        float: Kh = Coefficient de système.
        float: Kz = Coefficient de dimensions.

    """
    small = min(width, depth)
    large = max(width, depth)

    # 6.4.1 Coefficient de durée d'application de la charge, Kd.
    kd = general_design.load_duration(duration)

    # 6.4.2 Coefficient de conditions d'utilisation, Ks (tableau 6.10)
    if wet_service:
        if small > 89:
            ks = {
                "flex": 1,
                "cis_f": 0.7,
                "cis_l": 1,
                "comp_para": 0.91,
                "comp_perp": 0.67,
                "trac": 1,
                "moe": 1,
            }[prop]
        else:
            ks = {
                "flex": 0.84,
                "cis_f": 0.7,
                "cis_l": 0.96,
                "comp_para": 0.69,
                "comp_perp": 0.67,
                "trac": 0.84,
                "moe": 0.94,
            }[prop]
    else:
        ks = 1

    # 6.4.3 Coefficient de traitement, Kt (tableau 6.11)
    if treated and incised and small <= 89:
        if wet_service:
            if prop == "moe":
                kt = 0.95
            else:
                kt = 0.85
        else:
            if prop == "moe":
                kt = 0.90
            else:
                kt = 0.75
    else:
        kt = 1

    # 6.4.4 Coefficient de système, Kh (tableau 6.12)
    if _2ft_spacing:
        if connected_subfloor:
            if category == "MSR":
                # Cas 2 MSR
                kh = {
                    "flex": 1.2,
                    "cis_f": 1,
                    "cis_l": 1.2,
                    "comp_para": 1.1,
                    "comp_perp": 1,
                    "trac": 1,
                    "moe": 1,
                }[prop]
            else:
                # Cas 2
                kh = {
                    "flex": 1.4,
                    "cis_f": 1,
                    "cis_l": 1.4,
                    "comp_para": 1.1,
                    "comp_perp": 1,
                    "trac": 1,
                    "moe": 1,
                }[prop]
        else:
            # Cas 1
            kh = {
                "flex": 1.1,
                "cis_f": 1,
                "cis_l": 1.1,
                "comp_para": 1.1,
                "comp_perp": 1,
                "trac": 1.1,
                "moe": 1,
            }[prop]
    else:
        if built_up_beam:
            # Cas poutres composées
            kh = {
                "flex": 1.1,
                "cis_f": 1,
                "cis_l": 1.1,
                "comp_para": 1,
                "comp_perp": 1,
                "trac": 1,
                "moe": 1,
            }[prop]
        else:
            kh = 1

    # 6.4.5 Coefficient de dimensions, Kz (tableau 6.13)
    if category in ("Light", "MSR", "MEL"):
        kz = 1
    else:
        # Grande face 38, 64, 89
        if large <= 89:
            kz = {
                "flex": 1.7,
                "cis_f": 1.7,
                "cis_l": 1.7,
                "comp_para": 1,
                "comp_perp": 1,
                "trac": 1.5,
                "moe": 1,
            }[prop]
        # Grande face 114
        elif large <= 114:
            # Face étroite 114 et +
            if small >= 114:
                kz = {
                    "flex": 1.3,
                    "cis_f": 1.3,
                    "cis_l": 1.3,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 1.4,
                    "moe": 1,
                }[prop]
            # Face étroite 89 @ 102
            elif small >= 89:
                kz = {
                    "flex": 1.6,
                    "cis_f": 1.6,
                    "cis_l": 1.6,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 1.4,
                    "moe": 1,
                }[prop]
            # Face étroite 38 @ 64
            else:
                kz = {
                    "flex": 1.5,
                    "cis_f": 1.5,
                    "cis_l": 1.5,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 1.4,
                    "moe": 1,
                }[prop]
        # Grande face 140
        elif large <= 140:
            # Face étroite 114 et +
            if small >= 114:
                kz = {
                    "flex": 1.3,
                    "cis_f": 1.3,
                    "cis_l": 1.3,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 1.3,
                    "moe": 1,
                }[prop]
            # Face étroite 89 @ 102
            elif small >= 89:
                kz = {
                    "flex": 1.5,
                    "cis_f": 1.5,
                    "cis_l": 1.5,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 1.3,
                    "moe": 1,
                }[prop]
            # Face étroite 38 @ 64
            else:
                kz = {
                    "flex": 1.4,
                    "cis_f": 1.4,
                    "cis_l": 1.4,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 1.3,
                    "moe": 1,
                }[prop]
        # Grande face 184 @ 191
        elif large <= 191:
            # Face étroite 114 et +
            if small >= 114:
                kz = {
                    "flex": 1.3,
                    "cis_f": 1.3,
                    "cis_l": 1.3,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 1.2,
                    "moe": 1,
                }[prop]
            # Face étroite 89 @ 102
            elif small >= 89:
                kz = {
                    "flex": 1.3,
                    "cis_f": 1.3,
                    "cis_l": 1.3,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 1.2,
                    "moe": 1,
                }[prop]
            # Face étroite 38 @ 64
            else:
                kz = {
                    "flex": 1.2,
                    "cis_f": 1.2,
                    "cis_l": 1.2,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 1.2,
                    "moe": 1,
                }[prop]
        # Grande face 235 @ 241
        elif large <= 241:
            # Face étroite 114 et +
            if small >= 114:
                kz = {
                    "flex": 1.2,
                    "cis_f": 1.2,
                    "cis_l": 1.2,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 1.1,
                    "moe": 1,
                }[prop]
            # Face étroite 89 @ 102
            elif small >= 89:
                kz = {
                    "flex": 1.2,
                    "cis_f": 1.2,
                    "cis_l": 1.2,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 1.1,
                    "moe": 1,
                }[prop]
            # Face étroite 38 @ 64
            else:
                kz = {
                    "flex": 1.1,
                    "cis_f": 1.1,
                    "cis_l": 1.1,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 1.1,
                    "moe": 1,
                }[prop]
        # Grande face 286 @ 292
        elif large <= 292:
            # Face étroite 114 et +
            if small >= 114:
                kz = {
                    "flex": 1.1,
                    "cis_f": 1.1,
                    "cis_l": 1.1,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 1,
                    "moe": 1,
                }[prop]
            # Face étroite 89 @ 102
            elif small >= 89:
                kz = {
                    "flex": 1.1,
                    "cis_f": 1.1,
                    "cis_l": 1.1,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 1,
                    "moe": 1,
                }[prop]
            # Face étroite 38 @ 64
            else:
                kz = 1
        # Grande face 337 @ 343
        elif large <= 343:
            # Face étroite 114 et +
            if small >= 114:
                kz = {
                    "flex": 1,
                    "cis_f": 1,
                    "cis_l": 1,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 0.9,
                    "moe": 1,
                }[prop]
            # Face étroite 89 @ 102
            elif small >= 89:
                kz = {
                    "flex": 1,
                    "cis_f": 1,
                    "cis_l": 1,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 0.9,
                    "moe": 1,
                }[prop]
            # Face étroite 38 @ 64
            else:
                kz = {
                    "flex": 0.9,
                    "cis_f": 0.9,
                    "cis_l": 0.9,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 0.9,
                    "moe": 1,
                }[prop]
        # Grande face 387 et +
        else:
            # Face étroite 114 et +
            if small >= 114:
                kz = {
                    "flex": 0.9,
                    "cis_f": 0.9,
                    "cis_l": 0.9,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 0.8,
                    "moe": 1,
                }[prop]
            # Face étroite 89 @ 102
            elif small >= 89:
                kz = {
                    "flex": 0.9,
                    "cis_f": 0.9,
                    "cis_l": 0.9,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 0.8,
                    "moe": 1,
                }[prop]
            # Face étroite 38 @ 64
            else:
                kz = {
                    "flex": 0.8,
                    "cis_f": 0.8,
                    "cis_l": 0.8,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 0.8,
                    "moe": 1,
                }[prop]

    return kd, ks, kt, kh, kz


# TESTS
def _tests():
    """
    Tests pour les calculs de bois de sciage.

    """
    # Test lumber_category
    test_lumber_category = lumber_category(
        width=38,
        depth=140,
        is_msr=False,
        is_mel=False,
    )
    expected_result = "Lumber"
    assert (
        test_lumber_category == expected_result
    ), f"lumber_category -> FAILED\n {expected_result = }\n {test_lumber_category = }"

    # Test specified_strengths
    test_specified_strengths = specified_strengths(
        category="MSR",
        specie="courant",
        grade="1650-1.5",
    )
    expected_result = (23.9, 1.5, 18.1, 5.3, 11.4, 10300, 0)
    assert (
        test_specified_strengths == expected_result
    ), f"specified_strengths -> FAILED\n {expected_result = }\n {test_specified_strengths = }"

    # Test modification_factors
    test_modification_factors = modification_factors(
        width=38,
        depth=140,
        prop="flex",
        duration="continue",
        category="Lumber",
        wet_service=True,
        treated=True,
        incised=True,
        _2ft_spacing=True,
        connected_subfloor=True,
        built_up_beam=True,
    )
    expected_result = (0.65, 0.84, 0.85, 1.4, 1.4)
    assert (
        test_modification_factors == expected_result
    ), f"modification_factors -> FAILED\n {expected_result = }\n {test_modification_factors = }"


# RUN FILE
if __name__ == "__main__":
    _tests()


# END
