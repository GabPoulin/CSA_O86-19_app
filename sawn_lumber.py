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
from dataclasses import dataclass
from sqlalchemy import orm, create_engine, Column, TEXT, REAL, INTEGER
import general_design


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


@dataclass
class LumberSizes(orm.declarative_base()):
    """
    Se connecte à la table lumber_sizes de csa_o86_19.db.

    """

    __tablename__ = "lumber_sizes"
    nominal: int = Column("nominal", INTEGER, primary_key=True)
    dry: int = Column("dry", INTEGER)
    green: int = Column("green", INTEGER)
    dry_brut: int = Column("dry_brut", INTEGER)
    green_brut: int = Column("green_brut", INTEGER)
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

    if large > 412:
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
    category: str, specie: str, grade: str, side: bool = False
) -> tuple[float, float, float, float, float, float, float]:
    """
    6.3 Résistances prévues et modules d'élasticité.

    Args:
        category (str): Catégorie.
            Choices: "Lumber", "Light", "Beam", "Post", "MSR", "MEL".

        specie (str): Groupe d'essence.
            Choices: "df", "hf", "spf", "ns".
            Pour catégorie MSR et MEL: "normal", "courant", "rare".

        grade (str): Classe.
            Choices: "ss", "n1", "n2".
            Pour catégorie Lumber: "ss", "n1-n2", "n3-stud".
            Pour catégorie Light: "cst", "std".
            Pour catégorie MSR: voir tableau 6.8. (ex: 1200Fb-1.2E = "1200-1.2").
            Pour catégorie MEL: voir tableau 6.9. (ex: M-10 = "m-10").

        side (bool, optional): Charges appliquées sur la grande face. (Default to False).

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
    if side and category == "Beam":
        if grade == "ss":
            fb *= 0.88
        else:
            fb *= 0.77
            e *= 0.9
            e05 *= 0.9

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
            Choices: "flex", "cis_f", "cis_v", "comp_para", "comp_perp", "trac", "moe".

        duration (str): Durée d'application de la charge.
            Choices: "courte", "normale", "continue".

        category (str): Catégorie.
            Choices: "Lumber", "Light", "Beam", "Post", "MSR", "MEL".

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
                "cis_v": 1,
                "comp_para": 0.91,
                "comp_perp": 0.67,
                "trac": 1,
                "moe": 1,
            }[prop]
        else:
            ks = {
                "flex": 0.84,
                "cis_f": 0.7,
                "cis_v": 0.96,
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
                    "cis_v": 1.2,
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
                    "cis_v": 1.4,
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
                "cis_v": 1.1,
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
                "cis_v": 1.1,
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
        if large < 114:
            kz = {
                "flex": 1.7,
                "cis_f": 1.7,
                "cis_v": 1.7,
                "comp_para": 1,
                "comp_perp": 1,
                "trac": 1.5,
                "moe": 1,
            }[prop]
        # Grande face 114
        elif large < 140:
            # Face étroite 114 et +
            if small >= 114:
                kz = {
                    "flex": 1.3,
                    "cis_f": 1.3,
                    "cis_v": 1.3,
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
                    "cis_v": 1.6,
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
                    "cis_v": 1.5,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 1.4,
                    "moe": 1,
                }[prop]
        # Grande face 140
        elif large < 159:
            # Face étroite 114 et +
            if small >= 114:
                kz = {
                    "flex": 1.3,
                    "cis_f": 1.3,
                    "cis_v": 1.3,
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
                    "cis_v": 1.5,
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
                    "cis_v": 1.4,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 1.3,
                    "moe": 1,
                }[prop]
        # Grande face 184 @ 191
        elif large < 210:
            # Face étroite 114 et +
            if small >= 114:
                kz = {
                    "flex": 1.3,
                    "cis_f": 1.3,
                    "cis_v": 1.3,
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
                    "cis_v": 1.3,
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
                    "cis_v": 1.2,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 1.2,
                    "moe": 1,
                }[prop]
        # Grande face 235 @ 241
        elif large < 286:
            # Face étroite 114 et +
            if small >= 114:
                kz = {
                    "flex": 1.2,
                    "cis_f": 1.2,
                    "cis_v": 1.2,
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
                    "cis_v": 1.2,
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
                    "cis_v": 1.1,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 1.1,
                    "moe": 1,
                }[prop]
        # Grande face 286 @ 292
        elif large < 337:
            # Face étroite 114 et +
            if small >= 114:
                kz = {
                    "flex": 1.1,
                    "cis_f": 1.1,
                    "cis_v": 1.1,
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
                    "cis_v": 1.1,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 1,
                    "moe": 1,
                }[prop]
            # Face étroite 38 @ 64
            else:
                kz = 1
        # Grande face 337 @ 343
        elif large < 362:
            # Face étroite 114 et +
            if small >= 114:
                kz = {
                    "flex": 1,
                    "cis_f": 1,
                    "cis_v": 1,
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
                    "cis_v": 1,
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
                    "cis_v": 0.9,
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
                    "cis_v": 0.9,
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
                    "cis_v": 0.9,
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
                    "cis_v": 0.8,
                    "comp_para": 1,
                    "comp_perp": 1,
                    "trac": 0.8,
                    "moe": 1,
                }[prop]

    return kd, ks, kt, kh, kz


@dataclass
class Resistances:
    """
    6.5 Calcul des résistances.

    Args:
        b (int): Largeur de l'élément, mm.
        d (int): Hauteur de l'élément, mm.
        kd (float, optional): Coefficient de durée d'application de la charge.
        kh (float, optional): Coefficient de système.
        kt (float, optional): Coefficient de traitement.
        ply (int, optional): Nombre de plis si élément composée. Default to 1.

    """

    b: int
    d: int
    kd: float = 1
    kh: float = 1
    kt: float = 1
    ply: int = 1

    def sizes(self, dimension: int, green: bool = False, brut: bool = False):
        """
        6.5.2 Dimensions.

        Args:
            dimension (int): Dimension nominale, po.
            green (bool, optional): Bois vert (teneur en humidité > 19%). Default to False.
            brut (bool, optional): Dimensions brutes. Default to False.

        returns:
            int: Dimension nette, mm.

        """
        table = (
            LumberSizes.session.query(LumberSizes)
            .filter(LumberSizes.nominal == dimension)
            .first()
        )

        if not table:
            dim = int(round(dimension * 25.4))
        elif green and brut:
            dim = table.green_brut
        elif brut:
            dim = table.dry_brut
        elif green:
            dim = table.green
        else:
            dim = table.dry

        return dim

    def bending_moment(
        self,
        fb: float,
        ksb: float = 1,
        kzb: float = 1,
        lateral_support: bool = False,
        compressive_edge_support: bool = False,
        tensile_edge_support: bool = False,
        blocking_support: bool = False,
        tie_rods_support: bool = False,
    ):
        """
        6.5.3 Résistance au moment de flexion.

        Args:
            fb (float): Résistance prévue en flexion, MPa.
            ksb (float, optional): Coefficient de conditions d'utilisation pour la flexion.
            kzb (float, optional): Coefficient de dimensions pour la flexion.

            lateral_support (bool, optional): Support latéral aux appuis. Default to False.
            compressive_edge_support (bool, optional): Rive comprimée maintenu. Default to False.
            tensile_edge_support (bool, optional): Rive en tension maintenu. Default to False.
            blocking_support (bool, optional): Entretoises ou entremises. Default to False.
            tie_rods_support (bool, optional): Pannes ou tirants. Default to False.

        Returns:
            float: Mr = Résistance pondérée au moment de flexion, N*mm.

        """
        phi = 0.9

        kd = self.kd
        kh = self.kh
        kt = self.kt
        f_b = fb * (kd * kh * ksb * kt)

        b = self.b * self.ply
        d = self.d
        s = (b * d**2) / 6

        rapport_h_l = d / b
        if lateral_support:
            if compressive_edge_support:
                if tensile_edge_support:
                    criteria = 9
                elif blocking_support:
                    criteria = 7.5
                else:
                    criteria = 6.5
            elif tie_rods_support:
                criteria = 5
            else:
                criteria = 4
        else:
            criteria = 2.5

        if rapport_h_l > criteria:
            kl = 1
            print("\nATTENTION!!!\tValider Kl selon 7.5.6.4\n")
        else:
            kl = 1

        mr = phi * f_b * s * kzb * kl

        return mr

    def shear(
        self,
        fv: float,
        ksv: float = 1,
        ksf: float = 1,
        kzv: float = 1,
        dn: int = 0,
        e: int = 0,
    ):
        """
        6.5.4 Résistance au cisaillement.

        Args:
            fv (float): Résistance prévue en cisaillement, MPa.
            ksv (float, optional): Coefficient de conditions d'utilisation pour le cisaillement.
            ksf (float, optional): Coefficient de conditions d'utilisation pour le cisaillement par fissuration.
            kzv (float, optional): Coefficient de dimensions en cisaillement.
            dn (int, optional): Profondeur de l'entaille, mm. Default to 0.
            e (int, optional): Longueur de l'entaille, mm. Default to 0.

        Returns:
            float: Vr = Résistance pondérée au cisaillement, N.
            float: Fr = Résistance pondérée au cisaillement par fissuration, N.

        Raises:
            ValueError: Lorsque dn > 0.25d.

        """
        phi = 0.9

        kd = self.kd
        kh = self.kh
        kt = self.kt
        f_v = fv * (kd * kh * ksv * kt)
        ff = 0.5
        f_f = ff * (kd * kh * ksf * kt)

        b = self.b * self.ply
        d = self.d
        ag = b * d
        an = ag

        if dn > 0 and e > 0:
            if dn > 0.25 * d:
                raise ValueError(
                    f"La profondeur de l'entaille (dn = {dn} mm) ne doit pas dépasser 0,25d = {0.25 * d} mm."
                )
            an = b * (d - dn)
            a = 1 - (dn / d)
            n = e / d
            kn = (0.006 * d * (1.6 * ((1 / a) - 1) + n**2 * ((1 / a**3) - 1))) ** (
                -1 / 2
            )
        else:
            kn = 0

        vr = phi * f_v * ((2 * an) / 3) * kzv
        fr = phi * f_f * ag * kn

        return vr, fr

    def comp_parallel(
        self,
        l_b: int,
        l_d: int,
        fc: float,
        e05: int,
        ksc: float = 1,
        kse: float = 1,
        end_in_translation: bool = False,
        end_in_rotation: int = 2,
        connectors: str = "clous",
        spacers: bool = False,
        glulam: bool = False,
    ):
        """
        6.5.5 Résistance à la compression parallèle au fil.

        Args:
            l_b (int): Longueur entre les appuis latéraux pour l'axe faible, mm.
            l_d (int): Longueur entre les appuis latéraux pour l'axe fort, mm.

            fc (float): Résistance prévue en compression parallèle au fil, MPa.
            e05 (int): Module d'élasticité pour les calculs des éléments en compression, MPa.

            ksc (float, optional): Coefficient de conditions d'utilisation pour la compression parallèle au fil.
            kse (float, optional): Coefficient de conditions d'utilisation relatif au module d'élasticité.

            end_in_translation (bool, optional): Extrémité libre en translation. Default to False.
            end_in_rotation (int, optional): Extrémités libre en rotation.
                Choices: 0, 1, 2. Default to 2.

            connectors (str, optional): Connecteurs pour élément composé.
                Choices: "clous", "boulons", "anneaux", "aucun". Default to "clous".
            spacers (bool, optional): Éléments assemblés avec cales d'espacement. Default to False.
            glulam (bool, optional): Élément en bois lamellé collé. Default to False.

        Returns:
            float: Pr = Résistance pondérée à la compression parallèle au fil, N.

        Raises:
            ValueError: Lorsque plus de 5 plis pour un élément composé.
            ValueError: Lorsque les conditions d'appuis aux extrémités sont instables.
            ValueError: Lorsque Cc > 50 (ou Cc > 80 si cales d'espacement).

        """
        if self.ply > 5:
            raise ValueError(
                "Un élément composé en compression ne peut avoir plus de 5 plis."
            )

        # A.6.5.5.1 coefficient de longueur effective, Ke.
        if not end_in_translation:
            if end_in_rotation == 0:
                ke = 0.65
            elif end_in_rotation == 1:
                ke = 0.8
            else:
                ke = 1
        else:
            if end_in_rotation == 0:
                ke = 1.5
            elif end_in_rotation == 1:
                ke = 2
            else:
                raise ValueError(
                    "Les conditions d'appuis aux extrémités sont instables."
                )
        le_b = ke * l_b
        le_d = ke * l_d

        if connectors in ("clous", "boulons", "anneaux"):
            b = self.b * self.ply
        else:
            b = self.b
        d = self.d

        cc_b = le_b / b
        cc_d = le_d / d
        if cc_b > 50:
            raise ValueError(
                f"L'élancement selon l'axe faible (Cc = {round(cc_b,1)}) ne doit pas dépasser 50."
            )
        if cc_d > 50:
            raise ValueError(
                f"L'élancement selon l'axe fort (Cc = {round(cc_d,1)}) ne doit pas dépasser 50."
            )

        phi = 0.8

        kd = self.kd
        kh = self.kh
        kt = self.kt
        f_c = fc * (kd * kh * ksc * kt)

        a = b * d

        kzc_b = min((6.3 * (b * l_b) ** (-0.13)), 1.3)
        kzc_d = min((6.3 * (d * l_d) ** (-0.13)), 1.3)

        kc_b = (1 + ((f_c * kzc_b * cc_b**3) / (35 * e05 * kse * kt))) ** (-1)
        kc_d = (1 + ((f_c * kzc_d * cc_d**3) / (35 * e05 * kse * kt))) ** (-1)

        pr_b = phi * f_c * a * kzc_b * kc_b
        pr_d = phi * f_c * a * kzc_d * kc_d
        if self.ply > 1:
            if connectors == "clous":
                pr_b *= 0.6
            elif connectors == "boulons":
                pr_b *= 0.75
            elif connectors == "anneaux":
                pr_b *= 0.8
            else:
                pr_b *= self.ply
                pr_d *= self.ply
        pr = min(pr_b, pr_d)

        # A.6.5.5.3 Éléments en compression assemblés avec cales d’espacement.
        if self.ply > 1 and spacers:
            f_c = fc * (kd * ksc * kt)

            b = self.b * (2 * self.ply - 1)
            a = b * d

            l = max(l_b, l_d)
            if glulam:
                phi = 0.9
                kzc = 1
                k = 2
            else:
                dim = max(b, d)
                kzc = min((6.3 * (dim * l) ** (-0.13)), 1.3)
                k = 1.8

            cc = l / self.b
            ke = 2.5
            ck = ((0.76 * e05 * kse * ke * kt) / f_c) ** (1 / 2)
            if cc <= 10:
                kc = 1
            elif cc < ck:
                kc = 1 - (1 / 3) * (cc / ck) ** 4
            elif cc <= 80:
                kc = (e05 * kse * ke * kt) / (k * cc**2 * f_c)
            else:
                raise ValueError(
                    f"L'élancement pour éléments avec cales d'espacement (Cc = {round(cc,1)}) ne doit pas dépasser 80."
                )

            pr_spacers = phi * f_c * a * kc * kzc
            pr = min(pr_spacers, pr_d)

        return pr

    def comp_perpendicular(
        self,
        fcp: float = 0,
        kscp: float = 1,
        lb2: int = 38,
        d_lb2: int = 0,
        lb1: int = 0,
        d_lb1: int = 0,
        g: float = 0,
    ):
        """
        6.5.6 Résistance à la compression perpendiculaire au fil.

        """
        # A.6.5.6 Compression perpendiculaire au fil.
        if g > 0:
            L = 1.8125
            M = 145.038
            fcp = 0.9 * L * (2243.8 * g - 473.8) / M

        phi = 0.8

        kd = self.kd
        kt = self.kt
        f_cp = fcp * (kd * kscp * kt)

        b = self.b
        ab = b * lb2

        # 6.5.6.4
        d = self.d
        ratio = b / d
        if ratio <= 1:
            kzcp = 1
        elif ratio < 2:
            kzcp = 0.15 * ratio + 0.85
        else:
            kzcp = 1.15

        # 6.5.6.5
        if d_lb2 - lb2 / 2 < 75:
            kb2 = 1

        # 6.5.6.2
        qr = phi * f_cp * ab * kb2 * kzcp

        if d_lb1 <= d:
            lb1 = min(lb1, lb2)
            lb2 = max(lb1, lb2)
            ab_prim = min(b * ((lb1 + lb2) / 2), 1.5 * b * lb1)
            qr_prim = (2 / 3) * phi * f_cp * ab_prim * kb2 * kzcp

        else:
            ab = b * lb1
            qr_prim = phi * f_cp * ab * kb1 * kzcp

        return qr, qr_prim

    def comp_angle(self):
        """
        6.5.7 Résistance à la compression oblique par rapport au fil.

        """

    def tensile_parallel(self):
        """
        6.5.8 Résistance à la traction parallèle au fil.

        """

    def combined_bending_axial(self):
        """
        6.5.9 Résistance à la flexion et à la charge axiale combinées.

        """

    def decking(self):
        """
        6.5.10 Platelage.

        """

    def foundations(self):
        """
        6.5.11 Fondations permanentes en bois.

        """

    def truss(self):
        """
        6.5.12 Applications propres aux fermes.

        """


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
        category="Beam",
        specie="spf",
        grade="ss",
        side=True,
    )
    expected_result = (11.968, 1.2, 9.5, 5.3, 7, 8500, 6000)
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

    # Test modification_factors (2)
    test_modification_factors_2 = modification_factors(
        width=150,
        depth=150,
        prop="flex",
        duration="normale",
        category="MSR",
        wet_service=True,
        treated=True,
        incised=False,
        _2ft_spacing=False,
        connected_subfloor=False,
        built_up_beam=False,
    )
    expected_result = (1, 1, 1, 1, 1)
    assert (
        test_modification_factors_2 == expected_result
    ), f"modification_factors_2 -> FAILED\n {expected_result = }\n {test_modification_factors_2 = }"

    # Test sizes
    test_sizes = Resistances(38, 140).sizes(dimension=5, green=True, brut=False)
    expected_result = 117
    assert (
        test_sizes == expected_result
    ), f"sizes -> FAILED\n {expected_result = }\n {test_sizes = }"

    # Test bending_moment
    test_bending_moment = Resistances(
        b=38,
        d=140,
        kd=1,
        kh=1,
        kt=1,
        ply=1,
    ).bending_moment(
        fb=6,
        ksb=1,
        kzb=1,
        lateral_support=True,
        compressive_edge_support=True,
        tensile_edge_support=True,
        blocking_support=False,
        tie_rods_support=False,
    )
    expected_result = 670320
    assert (
        test_bending_moment == expected_result
    ), f"bending_moment -> FAILED\n {expected_result = }\n {test_bending_moment = }"

    # Test shear
    test_shear = Resistances(
        b=38,
        d=140,
        kd=1,
        kh=1,
        kt=1,
        ply=1,
    ).shear(
        fv=1.2,
        ksv=1,
        kzv=1,
        ksf=1,
        dn=0,
        e=0,
    )
    expected_result = 3830.4, 0
    assert (
        test_shear == expected_result
    ), f"shear -> FAILED\n {expected_result = }\n {test_shear = }"

    # Test comp_parallel
    test_comp_parallel = Resistances(
        b=38,
        d=140,
        kd=1,
        kh=1,
        kt=1,
        ply=4,
    ).comp_parallel(
        l_b=100,
        l_d=1000,
        fc=10,
        e05=10000,
        ksc=1,
        kse=1,
        end_in_translation=False,
        end_in_rotation=2,
        connectors="aucun",
        spacers=False,
        glulam=False,
    )
    expected_result = 95226.62728451275
    assert (
        test_comp_parallel == expected_result
    ), f"comp_parallel -> FAILED\n {expected_result = }\n {test_comp_parallel = }"


# RUN FILE
if __name__ == "__main__":
    _tests()


# END
