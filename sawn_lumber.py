"""
CSA O86:19: Règles de calcul des charpentes en bois.

6 Bois de sciage..
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
import math
from sqlalchemy import orm, create_engine, Column, TEXT, REAL, INTEGER
from moteur.normes.csa_o86_19.base_de_donnees import CHEMIN as _CHEMIN_BD
from moteur.normes.csa_o86_19.ch_6_bois_de_sciage import (
    art_6_2_materiaux as _art_6_2,
    art_6_3_resistances_prevues_et_modules_d_elasticite as _art_6_3,
    art_6_4_coefficients_de_correction as _art_6_4,
)
from moteur.normes.csa_o86_19.annexe_A_renseignements_supplementaires_et_autres_methodes.tableaux import (  # noqa: E501
    tableau_A_3_dimensions_minimales_apres_rabotage_du_bois_d_oeuvre as _tableau_A_3,
)
import general_design


# DB CONNECTION
@dataclass
class SawnLumberStrengths(orm.declarative_base()):
    """
    Se connecte à la table sawn_lumber_strengths de csa_o86_19.db.

    """

    __tablename__ = "sawn_lumber_strengths"
    index: int = Column("index", INTEGER, primary_key=True)  # type: ignore
    category: str = Column("category", TEXT)  # type: ignore
    specie: str = Column("specie", TEXT)  # type: ignore
    grade: str = Column("grade", TEXT)  # type: ignore
    fb: float = Column("fb", REAL)  # type: ignore
    fv: float = Column("fv", REAL)  # type: ignore
    fc: float = Column("fc", REAL)  # type: ignore
    fcp: float = Column("fcp", REAL)  # type: ignore
    ft: float = Column("ft", REAL)  # type: ignore
    e: int = Column("e", INTEGER)  # type: ignore
    e05: int = Column("e05", INTEGER)  # type: ignore
    engine = create_engine(f"sqlite:///{_CHEMIN_BD}")
    Session = orm.sessionmaker(engine)
    session = Session()


@dataclass
class LumberSizes(orm.declarative_base()):
    """
    Se connecte à la table lumber_sizes de csa_o86_19.db.

    """

    __tablename__ = "lumber_sizes"
    nominal: int = Column("nominal", INTEGER, primary_key=True)  # type: ignore
    dry: int = Column("dry", INTEGER)  # type: ignore
    green: int = Column("green", INTEGER)  # type: ignore
    green_timber: int = Column("green_timber", INTEGER)  # type: ignore
    dry_brut: int = Column("dry_brut", INTEGER)  # type: ignore
    green_brut: int = Column("green_brut", INTEGER)  # type: ignore
    engine = create_engine(f"sqlite:///{_CHEMIN_BD}")
    Session = orm.sessionmaker(engine)
    session = Session()


# CODE
def lumber_category(
    width: int, depth: int, is_msr: bool = False, is_mel: bool = False
) -> str:
    """
    6.2 Matériaux. Déplacé dans le nouveau moteur (art_6_2_materiaux.categorie_de_bois).

    Garde l'ancien comportement pour l'interface : au-delà de 412 mm, retourne le message
    « Valider la disponibilité du bois chez les fournisseurs. » au lieu de lever une erreur.

    Raises:
        ValueError: Si les dimensions sont plus petites que 38 mm.
    """
    if min(width, depth) >= 38 and max(width, depth) > _art_6_2.DIMENSION_MAXIMALE:
        return "Valider la disponibilité du bois chez les fournisseurs."
    return _art_6_2.categorie_de_bois(width, depth, msr=is_msr, mel=is_mel)


def specified_strengths(
    category: str, specie: str, grade: str, side: bool = False
) -> tuple[float, float, float, float, float, float, float]:
    """
    6.3 Résistances prévues et modules d'élasticité. Déplacé dans le nouveau moteur
    (art_6_3_resistances_prevues_et_modules_d_elasticite.resistances_prevues).

    Returns:
        tuple: fb, fv, fc, fcp, ft, E, E05, MPa.
    """
    r = _art_6_3.resistances_prevues(category, specie, grade, charges_sur_grande_face=side)
    return r.f_b, r.f_v, r.f_c, r.f_cp, r.f_t, r.E, r.E_05


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
    6.4 Coefficients de correction. Déplacé dans le nouveau moteur
    (art_6_4_coefficients_de_correction : K_S, K_T, K_H, K_Z). K_D reste dans general_design (5.3.2).

    Args:
        prop (str): "flex", "cis_f", "cis_v", "comp_para", "comp_perp", "trac" ou "moe".

    Returns:
        tuple: Kd, Ks, Kt, Kh, Kz. Comportement conservé pour l'interface : Kz = 1 en compression
        (K_Zc et K_Zcp sont calculés à 6.5.5 et 6.5.6) et Kz du cisaillement par fissuration = Kz de la
        flexion.
    """
    propriete = _PROPRIETES_6_4[prop]
    face_etroite = min(width, depth)

    kd = general_design.load_duration(duration)
    ks = _art_6_4.K_S(propriete, wet_service, face_etroite)
    kt = _art_6_4.K_T(propriete, treated, incised, face_etroite, wet_service)
    cas = _art_6_4.cas_de_systeme(_2ft_spacing, connected_subfloor, built_up_beam)
    kh = _art_6_4.K_H(propriete, cas, msr=category == "MSR")
    if propriete in (_art_6_4.COMPRESSION_PARALLELE, _art_6_4.COMPRESSION_PERPENDICULAIRE):
        kz = 1
    elif propriete == _art_6_4.CISAILLEMENT_PAR_FISSURATION:
        kz = _art_6_4.K_Z(_art_6_4.FLEXION, width, depth, category)
    else:
        kz = _art_6_4.K_Z(propriete, width, depth, category)

    return kd, ks, kt, kh, kz


_PROPRIETES_6_4 = {
    "flex": _art_6_4.FLEXION,
    "cis_f": _art_6_4.CISAILLEMENT_PAR_FISSURATION,
    "cis_v": _art_6_4.CISAILLEMENT_LONGITUDINAL,
    "comp_para": _art_6_4.COMPRESSION_PARALLELE,
    "comp_perp": _art_6_4.COMPRESSION_PERPENDICULAIRE,
    "trac": _art_6_4.TRACTION_PARALLELE,
    "moe": _art_6_4.MODULE_D_ELASTICITE,
}


def nominal_sizes() -> list[int]:
    """Tableau A.3. Déplacé dans le nouveau moteur (tableau_A_3.dimensions_nominales)."""
    return _tableau_A_3.dimensions_nominales()


def is_timber(width: float, depth: float) -> bool:
    """Tableau A.3 Gros bois. Déplacé dans le nouveau moteur (tableau_A_3.est_gros_bois)."""
    return _tableau_A_3.est_gros_bois(width, depth)


def sizes(
    dimension: float,
    green: bool = False,
    brut: bool = False,
    timber: bool = False,
) -> int:
    """Tableau A.3 Dimension nette, mm. Déplacé dans le nouveau moteur (tableau_A_3.dimension_nette)."""
    return _tableau_A_3.dimension_nette(dimension, vert=green, brut=brut, gros_bois=timber)


# 6.5.5 ET 6.5.6 : DÉPLACÉS DANS LE NOUVEAU MOTEUR (moteur/normes/csa_o86_19/)
# Ces fonctions gardent leur ancien nom pour l'interface Streamlit et appellent le nouveau moteur.
# Les formules ne sont plus ici. Voir ARCHITECTURE.md, section 14 (migration).
from moteur.normes.csa_o86_19.ch_6_bois_de_sciage.art_6_5_calcul_des_resistances import (  # noqa: E402
    art_6_5_3_resistance_au_moment_de_flexion as _art_6_5_3,
    art_6_5_4_resistance_au_cisaillement as _art_6_5_4,
    art_6_5_5_resistance_a_la_compression_parallele_au_fil as _art_6_5_5,
    art_6_5_6_resistance_a_la_compression_perpendiculaire_au_fil as _art_6_5_6,
)
from moteur.normes.csa_o86_19.annexe_A_renseignements_supplementaires_et_autres_methodes.art_A_6_bois_de_sciage import (  # noqa: E402,E501
    art_A_6_5_6_compression_perpendiculaire_au_fil as _art_A_6_5_6,
)
from moteur.normes.csa_o86_19.annexe_A_renseignements_supplementaires_et_autres_methodes.tableaux import (  # noqa: E402,E501
    tableau_A_11_valeurs_de_densite as _tableau_A_11,
)


def compression_strength(fc, kd=1, kh=1, ksc=1, kt=1):
    """Déplacé : 6.5.5.2.4, F_c (art_6_5_5.F_c)."""
    return _art_6_5_5.F_c(fc, kd, kh, ksc, kt)


def slenderness_ratio(effective_length, dimension):
    """Déplacé : 6.5.5.2.2, C_C (art_6_5_5.C_C)."""
    return _art_6_5_5.C_C(effective_length, dimension)


def compression_size_factor(dimension, length):
    """Déplacé : 6.5.5.2.4, K_Zc (art_6_5_5.K_Zc)."""
    return _art_6_5_5.K_Zc(dimension, length)


def slenderness_factor(fc_modified, kzc, cc, e05, kse=1, kt=1):
    """Déplacé : 6.5.5.2.5, K_C (art_6_5_5.K_C)."""
    return _art_6_5_5.K_C(fc_modified, kzc, cc, e05, kse, kt)


def compression_resistance(fc_modified, area, kzc, kc):
    """Déplacé : 6.5.5.2.4, P_r (art_6_5_5.P_r)."""
    return _art_6_5_5.P_r(fc_modified, area, kzc, kc)


def compression_parallel_axis(
    dimension, length, effective_length, fc_modified, area, e05, kse=1, kt=1
):
    """
    6.5.5.2 P_r selon un axe, à partir des fonctions de art_6_5_5.

    Returns:
        tuple: C_C, K_Zc, K_C, P_r (N).
    """
    cc = _art_6_5_5.C_C(effective_length, dimension)
    kzc = _art_6_5_5.K_Zc(dimension, length)
    kc = _art_6_5_5.K_C(fc_modified, kzc, cc, e05, kse, kt)
    return cc, kzc, kc, _art_6_5_5.P_r(fc_modified, area, kzc, kc)


def bearing_strength(fcp, kd=1, kscp=1, kt=1):
    """Déplacé : 6.5.6.2, F_cp (art_6_5_6.F_cp)."""
    return _art_6_5_6.F_cp(fcp, kd, kscp, kt)


def bearing_size_factor(width, depth):
    """Déplacé : 6.5.6.4, K_Zcp (art_6_5_6.K_Zcp)."""
    return _art_6_5_6.K_Zcp(width, depth)


def bearing_length_factor(bearing_length, far_from_end=False, low_bending_stress=False):
    """Déplacé : 6.5.6.5, K_B (art_6_5_6.K_B)."""
    return _art_6_5_6.K_B(bearing_length, far_from_end, low_bending_stress)


def average_bearing_area(width, length_1, length_2):
    """Déplacé : 6.5.6.3.2, A'_b (art_6_5_6.A_b_prime)."""
    return _art_6_5_6.A_b_prime(width, length_1, length_2)


def bearing_resistance(fcp_modified, area, kb=1, kzcp=1):
    """Déplacé : 6.5.6.2, Q_r (art_6_5_6.Q_r)."""
    return _art_6_5_6.Q_r(fcp_modified, area, kb, kzcp)


def bearing_resistance_near_support(fcp_modified, average_area, kb=1, kzcp=1):
    """Déplacé : 6.5.6.3.1, Q'_r (art_6_5_6.Q_r_prime)."""
    return _art_6_5_6.Q_r_prime(fcp_modified, average_area, kb, kzcp)


def density_table_a11(specie, e=0):
    """Déplacé : tableau A.11, G (tableau_A_11.G)."""
    return _tableau_A_11.G(specie, e)


def bearing_strength_from_density(density, tolerance_limit=True):
    """Déplacé : A.6.5.6, f_cp à partir de G (art_A_6_5_6.f_cp)."""
    return _art_A_6_5_6.f_cp(density, tolerance_limit)


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
        plies_fastened: bool = False,
    ):
        """
        6.5.3 Résistance au moment de flexion. Déplacé dans le nouveau moteur
        (art_6_5_3_resistance_au_moment_de_flexion : F_b, S, K_L, M_r).

        Returns:
            float: Mr = Résistance pondérée au moment de flexion, N*mm.

        Raises:
            ValueError: Si d/b dépasse la limite de 6.5.3.2 (KL selon 7.5.6.4, à venir), ou, pour une
                poutre composée, si les plis ne sont pas fixés à au plus 4 d (plies_fastened).
        """
        b = self.b * self.ply
        if self.ply > 1:
            # 6.5.3.2.4 (issue #48) : plis fixés à au plus 4 d et d/(n b) <= 2.5
            kl = _art_6_5_3.K_L_poutre_composee(b, self.d, plies_fastened)
        else:
            rapport_maximal = _art_6_5_3.rapport_hauteur_largeur_maximal(
                lateral_support, tie_rods_support, compressive_edge_support, blocking_support,
                tensile_edge_support,
            )
            kl = _art_6_5_3.K_L(b, self.d, rapport_maximal)
        f_b = _art_6_5_3.F_b(fb, self.kd, self.kh, ksb, self.kt)
        return _art_6_5_3.M_r(f_b, _art_6_5_3.S(b, self.d), kzb, kl)

    def shear(
        self,
        fv: float,
        ksv: float = 1,
        ksf: float = 1,
        kzv: float = 1,
        dn: int | None = None,
        e: int | None = None,
    ):
        """
        6.5.4 Résistance au cisaillement. Déplacé dans le nouveau moteur
        (art_6_5_4_resistance_au_cisaillement : F_v, V_r, F_f, F_r, alpha, eta, K_N).

        Returns:
            float: Vr = Résistance pondérée au cisaillement, N.
            float: Fr = Résistance pondérée au cisaillement par fissuration, N (0 sans entaille).

        Raises:
            ValueError: Lorsque dn > 0.25d.
        """
        b = self.b * self.ply
        d = self.d
        a_g = b * d
        a_n = a_g
        k_n = 0
        if dn and e and dn > 0 and e > 0:
            a = _art_6_5_4.alpha(dn, d)
            k_n = _art_6_5_4.K_N(d, a, _art_6_5_4.eta(e, d))
            a_n = b * (d - dn)

        f_v = _art_6_5_4.F_v(fv, self.kd, self.kh, ksv, self.kt)
        f_f = _art_6_5_4.F_f(self.kd, self.kh, ksf, self.kt)
        return _art_6_5_4.V_r(f_v, a_n, kzv), _art_6_5_4.F_r(f_f, a_g, k_n)

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

            ksc (float, optional): Coefficient de conditions d'utilisation pour la compression parallèle au fil. Default to 1.
            kse (float, optional): Coefficient de conditions d'utilisation relatif au module d'élasticité. Default to 1.

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
        lb1: int = 0,
        d_lb1: int = 0,
        lb2: int = 38,
        d_lb2: int = 0,
        kscp: float = 1,
        fcp: float = 0,
        g: float = 0,
        flex: bool = False,
    ):
        """
        6.5.6 Résistance à la compression perpendiculaire au fil.

        Args:
            lb1 (int, optional): Longueur d'appui haut, mm. Default to 0.
            d_lb1 (int, optional): Distance entre l'extrémité de l'appui haut et l'extrémité de l'élément, mm. Default to 0.

            lb2 (int, optional): Longueur d'appui bas, mm. Default to 38.
            d_lb2 (int, optional): Distance entre l'extrémité de l'appui bas et l'extrémité de l'élément, mm. Default to 0.

            kscp (float, optional): Coefficient de conditions d'utilisation pour la compression perpendiculaire au fil.

            fcp (float, optional): Résistance prévue en compression perpendiculaire au fil, MPa. Default to 0.
            g (float, optional): Densité moyenne du bois anhydre. Default to 0.

            flex (bool, optional): Surface d'appui 1 aux endroits soumis à de fortes contraintes de flexion. Default to False.

        Returns:
            float: Qr = Résistance pondérée à la compression perpendiculaire au fil à l'appui, N.
            float: Qr' = Résistance pondérée à la compression perpendiculaire au fil au point de charge, N.

        """
        # A.6.5.6 Compression perpendiculaire au fil.
        if g > 0:
            L = 1.8125
            M = 145.038
            fcp = 0.9 * L * (2243.8 * g - 473.8) / M

        # 6.5.6.4
        b = self.b * self.ply
        d = self.d
        ratio = b / d
        if ratio <= 1:
            kzcp = 1
        elif ratio < 2:
            kzcp = 0.15 * ratio + 0.85
        else:
            kzcp = 1.15

        # 6.5.6.5
        if lb2 < 150:
            if d_lb2 < 75:
                kb = 1
            else:
                kb = (lb2 + 9.525) / lb2
        else:
            kb = 1

        if lb1 < 150 and not flex:
            if d_lb1 < 75:
                kb1 = 1
            else:
                kb1 = (lb1 + 9.525) / lb1
        else:
            kb1 = 1

        # 6.5.6.2
        phi = 0.8

        kd = self.kd
        kt = self.kt
        f_cp = fcp * (kd * kscp * kt)

        ab = b * lb2

        qr = phi * f_cp * ab * kb * kzcp

        # 6.5.6.3
        if d_lb1 + (lb1 / 2) - (lb2 / 2) <= d:

            # 6.5.6.3.2
            ab_prim = min(b * ((lb1 + lb2) / 2), 1.5 * b * min(lb1, lb2))

            # 6.5.6.3.1
            kb = min(kb, kb1)
            qr_prim = (2 / 3) * phi * f_cp * ab_prim * kb * kzcp

        # 6.5.6.2
        else:
            ab = b * lb1

            qr_prim = phi * f_cp * ab * kb1 * kzcp

        return qr, qr_prim

    def tensile_parallel(
        self,
        ft: float,
        kst: float = 1,
        kzt: float = 1,
        reduct_b: int = 0,
        reduct_d: int = 0,
    ):
        """
        6.5.8 Résistance à la traction parallèle au fil.

        Args:
            ft (float): Résistance prévue en traction parallèle au fil, MPa.
            kst (float, optional): Coefficient de conditions d'utilisation pour la traction parallèle au fil. Default to 1.
            kzt (float, optional): Coefficient de dimensions en traction. Default to 1.
            reduct_b (int, optional): Longueur à réduire sur la largeur, mm. Default to 0.
            reduct_d (int, optional): Longueur à réduire sur la hauteur, mm. Default to 0.

        Returns:
            float: Tr = Résistance pondérée à la traction parallèle au fil, N.

        """
        phi = 0.9

        kd = self.kd
        kh = self.kh
        kt = self.kt
        f_t = ft * (kd * kh * kst * kt)

        b = self.b * self.ply
        d = self.d
        ab = b * d

        # 5.3.8
        if reduct_d > 0 or reduct_d > 0:
            an = (b - reduct_b) * (d - reduct_d)
            general_design.cross_section(an, ab)
        else:
            an = ab

        tr = phi * f_t * an * kzt

        return tr


def comp_angle(
    theta: int,
    pr: int,
    qr: int,
):
    """
    6.5.7 Résistance à la compression oblique par rapport au fil.

    Args:
        theta (int): angle entre la direction du fil et la direction de la charge, degrés.
        pr (int): résistance pondérée à la compression parallèle au fil, N.
        (voir l'article 6.5.5.2.4, en supposant que Kc = 1,00)
        qr (int): ésistance pondérée à la compression perpendiculaire au fil, N.
        (voir l'article 6.5.6.2)

    Returns:
        float: Nr = Résistance à la compression oblique par rapport au fil, N.

    """
    theta = math.radians(theta)  # type: ignore
    nr = (pr * qr) / (pr * math.sin(theta) ** 2 + qr * math.cos(theta) ** 2)

    return nr


def combined_bending_axial(
    f: int,
    r: int,
    mf: int,
    mr: int,
    compression: bool = True,
    e05: int = 0,
    _i: int = 0,
    l: int = 0,
    ke: int = 1,
    kse: int = 1,
    kt: int = 1,
):
    """
    6.5.9 Résistance à la flexion et à la charge axiale combinées.

    Args:
        f (int): charge axiale pondérée en compression ou en traction, N.
        r (int): résistance pondérée à la compression ou à la traction parallèle au fil, N.
        mf (int): moment de flexion pondéré, N*mm.
        mr (int): résistance pondérée au moment de flexion, N*mm.
        compression (bool, optional): True pour compression, False pour tension. Default to True.
        e05 (int, optional): module d'élasticité pour le calcul des éléments en compression, Mpa. Default to 0
        _i (int, optional): moment d'inertie dans le plan du moment appliqué, mm4. Default to 0
        l (int, optional): longueur effective dans le plan du moment appliqué, mm. Default to 0
        ke (int, optional): coefficient de longueur effective. Default to 1.
        kse (int, optional): coefficient de condition d'utilisation. Default to 1.
        kt (int, optional): coefficient de traitement. Default to 1.

    Returns:
        float: ratio pour la résistance combiné.

    """
    if compression:
        le = l * ke
        pe = (math.pi**2 * e05 * kse * kt * _i) / le**2
        ratio = (f / r) ** 2 + (mf / mr) * (1 / (1 - f / pe))
    else:
        ratio = f / r + mf / mr

    return ratio


def decking():
    """
    6.5.10 Platelage.
    """


def foundations():
    """
    6.5.11 Fondations permanentes en bois.
    """


def truss():
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

    # Test specified_strengths MSR 1500Fb-1,4E (tableau 6.8) : E = 9700 MPa, E05 = 0,82E = 7954 MPa
    test_msr_1500 = specified_strengths("MSR", "normal", "1500-1.4")
    expected_result = (21.7, 1.5, 17.5, 5.3, 10.1, 9700, 7954)
    assert (
        test_msr_1500 == expected_result
    ), f"specified_strengths MSR 1500 -> FAILED\n {expected_result = }\n {test_msr_1500 = }"

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
    # KH = 1,1 : élément composé -> colonne « Poutres composées » même au cas 2 (6.4.4.2, 6.4.4.3,
    # issue #7). Ce test attendait 1,4 avant la correction.
    expected_result = (0.65, 0.84, 0.85, 1.1, 1.4)
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

    # Test modification_factors : KZ selon la catégorie (6.4.5.2, 6.4.5.3, tableau 6.13)
    # 2x6 (38 x 140) : tableau 6.13, grande face 140, face étroite 38 à 64 -> KZb = KZv = 1,4
    for category, prop, expected_kz in (
        ("Lumber", "flex", 1.4),
        ("Lumber", "cis_v", 1.4),
        ("MSR", "cis_v", 1.4),  # 6.4.5.3 : KZv selon le tableau 6.13
        ("MEL", "cis_v", 1.4),  # 6.4.5.3 : KZv selon le tableau 6.13
        ("MSR", "flex", 1),  # 6.4.5.3 : KZ = 1,00
        ("MEL", "flex", 1),
        ("MSR", "trac", 1),
        ("MEL", "cis_f", 1),
        ("Light", "cis_v", 1),  # 6.4.5.2 : KZ = 1,00
        ("Light", "flex", 1),
    ):
        kz_test = modification_factors(38, 140, prop, "normale", category)[4]
        assert (
            kz_test == expected_kz
        ), f"modification_factors KZ ({category}, {prop}) -> FAILED {kz_test = } {expected_kz = }"
    # 2x10 (38 x 235) MSR : tableau 6.13, grande face 235 à 241, face étroite 38 à 64 -> KZv = 1,1
    kz_test = modification_factors(38, 235, "cis_v", "normale", "MSR")[4]
    assert kz_test == 1.1, f"modification_factors KZv MSR 2x10 -> FAILED {kz_test = }"

    # Test lumber_category : frontière poteaux / poutres (tableaux 6.6 et 6.7, note 1)
    for width, depth, expected_result in (
        (140, 191, "Post"),  # 6x8 vert gros bois : écart = 51 mm -> au plus 51 -> poteau
        (140, 192, "Beam"),  # écart = 52 mm -> plus de 51 -> poutre
        (140, 184, "Post"),  # 6x8 sec : écart = 44 mm
        (140, 241, "Beam"),  # 6x10
        (114, 114, "Post"),
        (89, 140, "Lumber"),
        (38, 64, "Light"),
    ):
        test_category = lumber_category(width=width, depth=depth)
        assert (
            test_category == expected_result
        ), f"lumber_category({width}, {depth}) -> FAILED {expected_result = } {test_category = }"

    # Test modification_factors : KH selon le tableau 6.12 (6.4.4.1 à 6.4.4.3, issue #7)
    # (catégorie, 3 éléments <= 610 mm, revêtement, composé, propriété, KH attendu)
    kh_cases = [
        ("Lumber", False, False, False, "flex", 1),
        ("Lumber", True, False, False, "flex", 1.1),  # cas 1
        ("Lumber", True, False, False, "trac", 1.1),  # cas 1
        ("Lumber", True, True, False, "flex", 1.4),  # cas 2, classé visuellement
        ("Lumber", True, True, False, "comp_para", 1.1),
        ("MSR", True, True, False, "flex", 1.2),  # cas 2, MSR
        ("MSR", True, False, False, "flex", 1.1),  # cas 1 (la colonne MSR est au cas 2)
        ("Lumber", True, True, False, "trac", 1),  # cas 2 : « — » au tableau -> 1,00
        ("MSR", True, True, False, "trac", 1),  # cas 2 : « — » au tableau -> 1,00
        ("Lumber", False, False, True, "flex", 1.1),  # poutre composée seule
        ("Lumber", True, False, True, "flex", 1.1),  # composée + cas 1 -> poutres composées
        ("Lumber", True, False, True, "comp_para", 1),  # composée + cas 1 -> 1,00 (et non 1,10)
        ("Lumber", True, False, True, "trac", 1),  # composée + cas 1 -> 1,00 (et non 1,10)
        ("Lumber", True, True, True, "flex", 1.1),  # composée + cas 2 -> 1,10 (et non 1,40)
        ("Lumber", True, True, True, "cis_v", 1.1),  # composée + cas 2 -> 1,10 (et non 1,40)
        ("MSR", True, True, True, "flex", 1.1),  # MSR composé + cas 2 -> 1,10 (et non 1,20)
    ]
    for category, spacing, sheathing, built_up, prop, expected_kh in kh_cases:
        kh_test = modification_factors(
            38, 140, prop, "normale", category,
            _2ft_spacing=spacing, connected_subfloor=sheathing, built_up_beam=built_up,
        )[3]
        assert kh_test == expected_kh, (
            f"modification_factors KH {category, spacing, sheathing, built_up, prop} -> FAILED "
            f"{kh_test = } {expected_kh = }"
        )

    # Test sizes (tableau A.3)
    # (nominal, vert, brut, gros bois, attendu)
    sizes_cases = [
        (2, False, False, False, 38),
        (2, True, False, False, 40),
        (6, False, False, False, 140),
        (6, True, False, False, 143),  # bois de dimension vert (ex. 2x6)
        (5, True, False, False, 117),  # grande face 114 vert, bois de dimension (ex. 2x5)
        (5, True, False, True, 114),  # gros bois vert (ex. 5x5) : 114
        (6, True, False, True, 140),  # gros bois vert (ex. 6x6) : 140 (et non 143)
        (8, True, False, True, 191),  # gros bois vert (ex. 8x8) : 191 (et non 190)
        (10, True, False, True, 241),
        (12, True, False, True, 292),
        (14, True, False, True, 343),
        (16, True, False, True, 394),  # gros bois vert : 394 (et non 393)
        (16, False, False, True, 387),  # gros bois sec : dimension sèche du bois de dimension
        (8, False, False, False, 184),
        (2, False, True, False, 51),  # brut : convention de l'utilisateur
        (2, True, True, False, 53),
        (7, False, True, False, 178),  # 7 po : mode brut seulement
        (9, True, True, False, 235),  # 9 po : mode brut seulement
        (5.5, False, True, False, 140),  # brut hors table : 5,5 x 25,4 = 139,7 -> 140
        (7, True, False, True, 165),  # gros bois vert 7 po (tableau A.3)
        (9, True, False, True, 216),  # gros bois vert 9 po (tableau A.3)
    ]
    for nominal, green, brut, timber, expected_result in sizes_cases:
        test_sizes = sizes(dimension=nominal, green=green, brut=brut, timber=timber)
        assert (
            test_sizes == expected_result
        ), f"sizes{nominal, green, brut, timber} -> FAILED {expected_result = } {test_sizes = }"
    # Refusés : hors tableau, et 7 ou 9 po hors gros bois vert (sec, ou bois de dimension)
    for kwargs in (
        {"dimension": 1},
        {"dimension": 11},
        {"dimension": 13},
        {"dimension": 15},
        {"dimension": 18},
        {"dimension": 5.5},
        {"dimension": 7},
        {"dimension": 9},
        {"dimension": 7, "timber": True},  # gros bois sec : pas de valeur au tableau A.3
        {"dimension": 9, "timber": True},
        {"dimension": 7, "green": True},  # vert, mais bois de dimension
        {"dimension": 9, "green": True},
    ):
        try:
            sizes(**kwargs)
            raise AssertionError(f"sizes({kwargs}) aurait dû lever ValueError")
        except ValueError:
            pass
    assert nominal_sizes() == [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16], "nominal_sizes -> FAILED"
    assert is_timber(5, 5) and is_timber(6, 8) and is_timber(8, 6), "is_timber -> FAILED"
    assert not is_timber(4, 6) and not is_timber(2, 12), "is_timber -> FAILED"

    # Test bending_moment
    test_bending_moment = Resistances(
        b=38,
        d=89,
        kd=1,
        kh=1,
        kt=1,
        ply=1,
    ).bending_moment(
        fb=11.8,
        ksb=1,
        kzb=1.7,
        lateral_support=False,
        compressive_edge_support=True,
        tensile_edge_support=False,
        blocking_support=False,
        tie_rods_support=False,
    )
    expected_result = 905702.9820000001
    assert (
        test_bending_moment == expected_result
    ), f"bending_moment -> FAILED\n {expected_result = }\n {test_bending_moment = }"

    # Test bending_moment : limites de d/b pour KL = 1 (6.5.3.2.1 et 6.5.3.2.3)
    # (b, d, supports, limite) ; d/b égal à la limite -> accepté ; juste au-dessus -> ValueError
    kl_cases = [
        ({}, 2.5),
        ({"lateral_support": True}, 4),
        ({"lateral_support": True, "tie_rods_support": True}, 5),
        ({"lateral_support": True, "compressive_edge_support": True}, 6.5),
        ({"lateral_support": True, "compressive_edge_support": True, "blocking_support": True}, 7.5),
        ({"lateral_support": True, "compressive_edge_support": True, "tensile_edge_support": True}, 9),
    ]
    for supports, limit in kl_cases:
        Resistances(b=40, d=int(40 * limit)).bending_moment(fb=10, **supports)  # d/b = limite : OK
        try:
            Resistances(b=40, d=int(40 * limit) + 1).bending_moment(fb=10, **supports)
            raise AssertionError(f"bending_moment {supports} d/b > {limit} aurait dû lever ValueError")
        except ValueError:
            pass

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
        b=89,
        d=89,
        kd=1,
        kh=1,
        kt=1,
        ply=1,
    ).comp_parallel(
        l_b=10,
        l_d=10,
        fc=9.9,
        e05=4500,
        ksc=0.91,
        kse=1,
        end_in_translation=False,
        end_in_rotation=2,
        connectors="clous",
        spacers=False,
        glulam=False,
    )
    expected_result = 74214.69273184793
    assert (
        test_comp_parallel == expected_result
    ), f"comp_parallel -> FAILED\n {expected_result = }\n {test_comp_parallel = }"

    # Test comp_perpendicular
    test_comp_perpendicular = Resistances(
        b=38,
        d=140,
        kd=1,
        kh=1,
        kt=1,
        ply=3,
    ).comp_perpendicular(
        lb1=150,
        d_lb1=100,
        lb2=100,
        d_lb2=0,
        kscp=1,
        fcp=5.3,
        g=0,
        flex=False,
    )
    expected_result = (48336, 40280)
    assert (
        test_comp_perpendicular == expected_result
    ), f"comp_perpendicular -> FAILED\n {expected_result = }\n {test_comp_perpendicular = }"

    # Test comp_angle
    test_comp_angle = comp_angle(
        theta=10,
        pr=10000,
        qr=1000,
    )
    expected_result = 7865.44918098836
    assert (
        test_comp_angle == expected_result
    ), f"comp_angle -> FAILED\n {expected_result = }\n {test_comp_angle = }"

    # Test combined_bending_axial_1
    test_combined_bending_axial_1 = combined_bending_axial(
        f=50,
        r=1000,
        mf=50,
        mr=1000,
        compression=False,
        e05=1000,
        _i=1000,
        l=5000,
        ke=1,
        kse=1,
        kt=1,
    )
    expected_result = 0.1
    assert (
        test_combined_bending_axial_1 == expected_result
    ), f"combined_bending_axial_1 -> FAILED\n {expected_result = }\n {test_combined_bending_axial_1 = }"

    # Test combined_bending_axial_2
    test_combined_bending_axial_2 = combined_bending_axial(
        f=50,
        r=1000,
        mf=50,
        mr=1000,
        compression=True,
        e05=1000,
        _i=1000,
        l=5000,
        ke=1,
        kse=1,
        kt=1,
    )
    expected_result = 0.002102073925608327
    assert (
        test_combined_bending_axial_2 == expected_result
    ), f"combined_bending_axial_2 -> FAILED\n {expected_result = }\n {test_combined_bending_axial_2 = }"
    # Tests 6.5.5 - fonctions simples de compression parallèle au fil
    # Cas calculé à la main : 2x6 S-P-F n° 1/n° 2 sec (tableau 6.4 : fc = 11,5, E05 = 6500 MPa),
    # b = 38 mm, d = 140 mm, L = 3000 mm, KD = KH = KSc = KT = KSE = 1.
    # Axe fort : Le = 3000 mm. Axe faible : retenu à mi-hauteur, Le = 1500 mm.
    def close(value, expected, rel=1e-4):
        return math.isclose(value, expected, rel_tol=rel)

    fc_mod = compression_strength(fc=11.5)
    assert fc_mod == 11.5, f"compression_strength -> FAILED {fc_mod = }"
    # Fc = 11,5 x 1,15 x 0,9 x 1,0 x 1,0 = 11,9025
    fc_mod_2 = compression_strength(fc=11.5, kd=1.15, kh=0.9)
    assert close(fc_mod_2, 11.9025), f"compression_strength_2 -> FAILED {fc_mod_2 = }"

    # Cc = 3000 / 140 = 21,4286 ; 1500 / 38 = 39,4737 ; 1900 / 38 = 50 (limite, accepté)
    assert close(slenderness_ratio(3000, 140), 21.4286), "slenderness_ratio_d -> FAILED"
    assert close(slenderness_ratio(1500, 38), 39.4737), "slenderness_ratio_b -> FAILED"
    assert slenderness_ratio(1900, 38) == 50, "slenderness_ratio = 50 -> FAILED"
    for bad in ((1901, 38), (0, 38), (3000, 0), (-100, 38)):
        try:
            slenderness_ratio(*bad)
            raise AssertionError(f"slenderness_ratio{bad} aurait dû lever ValueError")
        except ValueError:
            pass

    # KZc axe fort = 6,3 x (140 x 3000)^-0,13 = 6,3 x 0,18577 = 1,1704
    # KZc axe faible = 6,3 x (38 x 3000)^-0,13 = 6,3 x 0,22013 = 1,3868 -> plafonné à 1,3
    kzc_d = compression_size_factor(140, 3000)
    kzc_b = compression_size_factor(38, 3000)
    assert close(kzc_d, 1.1704), f"compression_size_factor_d -> FAILED {kzc_d = }"
    assert kzc_b == 1.3, f"compression_size_factor_b (plafond 1,3) -> FAILED {kzc_b = }"
    for bad in ((0, 3000), (140, 0)):
        try:
            compression_size_factor(*bad)
            raise AssertionError(f"compression_size_factor{bad} aurait dû lever ValueError")
        except ValueError:
            pass

    # KC axe fort = [1 + 11,5 x 1,1704 x 21,4286^3 / (35 x 6500)]^-1
    #             = [1 + 11,5 x 1,1704 x 9839,7 / 227500]^-1 = [1 + 0,58212]^-1 = 0,63206
    # KC axe faible = [1 + 11,5 x 1,3 x 39,4737^3 / 227500]^-1
    #               = [1 + 14,95 x 61506,8 / 227500]^-1 = [1 + 4,04187]^-1 = 0,19834
    kc_d = slenderness_factor(11.5, kzc_d, 3000 / 140, 6500)
    kc_b = slenderness_factor(11.5, kzc_b, 1500 / 38, 6500)
    assert close(kc_d, 0.63206), f"slenderness_factor_d -> FAILED {kc_d = }"
    assert close(kc_b, 0.19834), f"slenderness_factor_b -> FAILED {kc_b = }"
    # Cc = 0 -> KC = 1
    assert slenderness_factor(11.5, 1.3, 0, 6500) == 1, "slenderness_factor Cc=0 -> FAILED"
    # KSE et KT au dénominateur : KSE = 0,94, KT = 0,9 -> 35 x 6500 x 0,94 x 0,9 = 192465
    # KC = [1 + 11,5 x 1,3 x 39,4737^3 / 192465]^-1 = [1 + 4,77753]^-1 = 0,17309
    kc_b_2 = slenderness_factor(11.5, 1.3, 1500 / 38, 6500, kse=0.94, kt=0.9)
    assert close(kc_b_2, 0.17309), f"slenderness_factor_kse_kt -> FAILED {kc_b_2 = }"

    # Pr axe fort = 0,8 x 11,5 x 5320 x 1,1704 x 0,63206 = 36 206 N
    # Pr axe faible = 0,8 x 11,5 x 5320 x 1,3 x 0,19834 = 12 620 N -> gouverne
    pr_d = compression_resistance(11.5, 38 * 140, kzc_d, kc_d)
    pr_b = compression_resistance(11.5, 38 * 140, kzc_b, kc_b)
    assert close(pr_d, 36206, rel=1e-3), f"compression_resistance_d -> FAILED {pr_d = }"
    assert close(pr_b, 12620, rel=1e-3), f"compression_resistance_b -> FAILED {pr_b = }"
    # Sans élancement (KC = 1, KZc = 1) : Pr = 0,8 x 11,5 x 5320 = 48 944 N
    assert close(compression_resistance(11.5, 5320, 1, 1), 48944), "compression_resistance -> FAILED"

    # Test compression_parallel_axis : mêmes valeurs que les fonctions simples ci-dessus
    cc_d2, kzc_d2, kc_d2, pr_d2 = compression_parallel_axis(140, 3000, 3000, 11.5, 5320, 6500)
    assert close(cc_d2, 21.4286) and close(kzc_d2, 1.1704), "compression_parallel_axis_d -> FAILED"
    assert close(kc_d2, 0.63206) and close(pr_d2, 36206, rel=1e-3), "compression_parallel_axis_d -> FAILED"
    cc_b2, kzc_b2, kc_b2, pr_b2 = compression_parallel_axis(38, 3000, 1500, 11.5, 5320, 6500)
    assert close(cc_b2, 39.4737) and kzc_b2 == 1.3, "compression_parallel_axis_b -> FAILED"
    assert close(kc_b2, 0.19834) and close(pr_b2, 12620, rel=1e-3), "compression_parallel_axis_b -> FAILED"
    # Bois traité incisé, milieu humide, 2x6, cas 1 (KH = 1,1) - calcul à la main :
    # KD = 1, KH = 1,10, KSc = 0,69, KT = 0,85 (autres propriétés), KSE = 0,94
    # Fc = 11,5 x 1,10 x 0,69 x 0,85 = 7,41923 MPa
    # Axe faible : Cc = 39,4737 ; KZc = 1,3
    # KC = [1 + 7,41923 x 1,3 x 61506,8 / (35 x 6500 x 0,94 x 0,85)]^-1
    #    = [1 + 593 236 / 181 772,5]^-1 = [1 + 3,26359]^-1 = 0,23454
    # Pr = 0,8 x 7,41923 x 5320 x 1,3 x 0,23454 = 9 627 N
    fc_wet = compression_strength(11.5, kh=1.1, ksc=0.69, kt=0.85)
    assert close(fc_wet, 7.41923), f"compression_strength_wet -> FAILED {fc_wet = }"
    _, _, kc_wet, pr_wet = compression_parallel_axis(38, 3000, 1500, fc_wet, 5320, 6500, kse=0.94, kt=0.85)
    assert close(kc_wet, 0.23454), f"compression_parallel_axis_wet KC -> FAILED {kc_wet = }"
    assert close(pr_wet, 9627, rel=1e-3), f"compression_parallel_axis_wet Pr -> FAILED {pr_wet = }"
    # Cc > 50 refusé : 2x4 (38 mm) avec Le = 2000 mm -> Cc = 52,6
    try:
        compression_parallel_axis(38, 2000, 2000, 11.5, 38 * 89, 6500)
        raise AssertionError("compression_parallel_axis Cc > 50 aurait dû lever ValueError")
    except ValueError:
        pass

    # Tests 6.5.6 - fonctions simples de compression perpendiculaire au fil (calculs à la main)
    # Fcp = 5,3 x 1,0 x 0,67 x 0,85 = 3,01835 MPa (milieu humide, traité incisé)
    assert close(bearing_strength(5.3, kscp=0.67, kt=0.85), 3.01835), "bearing_strength -> FAILED"
    assert bearing_strength(5.3) == 5.3, "bearing_strength -> FAILED"

    # KZcp (tableau 6.15) : rapport <= 1 -> 1,00 ; >= 2 -> 1,15 ; interpolation entre les deux
    for width, depth, expected in (
        (38, 140, 1.0),  # 2x6 sur chant
        (89, 89, 1.0),  # rapport = 1,0
        (140, 89, 1.08596),  # 1 + 0,15 x (140/89 - 1) = 1 + 0,15 x 0,57303 = 1,08596
        (133.5, 89, 1.075),  # rapport = 1,5 -> 1,075
        (178, 89, 1.15),  # rapport = 2,0
        (286, 38, 1.15),  # 2x12 à plat
    ):
        kzcp = bearing_size_factor(width, depth)
        assert close(kzcp, expected), f"bearing_size_factor({width}, {depth}) -> FAILED {kzcp = }"

    # KB (tableau 6.16 et sa note) : formule plafonnée à 1,75, conditions a) et b) requises
    for lb, expected in (
        (150, 1.0),
        (200, 1.0),
        (100, 1.09525),  # 109,525 / 100
        (89, 1.10702),  # 98,525 / 89
        (38, 1.25066),  # 47,525 / 38 (tableau : 1,25)
        (25, 1.381),  # 34,525 / 25 (tableau : 1,38)
        (12.5, 1.75),  # formule : 1,762 -> plafonné à 1,75 (tableau : 1,75)
        (5, 1.75),  # formule : 2,905 -> plafonné à 1,75
    ):
        kb = bearing_length_factor(lb, far_from_end=True, low_bending_stress=True)
        assert close(kb, expected), f"bearing_length_factor({lb}) -> FAILED {kb = }"
    assert bearing_length_factor(38) == 1, "KB sans conditions -> FAILED"
    assert bearing_length_factor(38, far_from_end=True) == 1, "KB condition b) -> FAILED"
    assert bearing_length_factor(38, low_bending_stress=True) == 1, "KB condition a) -> FAILED"

    # A'b = b (Lb1 + Lb2) / 2 <= 1,5 b Lb1
    # b = 38, Lb = 89 et 140 : 38 x 114,5 = 4351 ; 1,5 x 38 x 89 = 5073 -> 4351
    # b = 38, Lb = 38 et 140 : 38 x 89 = 3382 ; 1,5 x 38 x 38 = 2166 -> 2166
    assert close(average_bearing_area(38, 89, 140), 4351), "average_bearing_area -> FAILED"
    assert close(average_bearing_area(38, 140, 89), 4351), "average_bearing_area (ordre) -> FAILED"
    assert close(average_bearing_area(38, 38, 140), 2166), "average_bearing_area (limite) -> FAILED"
    assert close(average_bearing_area(38, 89, 89), 3382), "average_bearing_area (égales) -> FAILED"

    # Qr = 0,8 x 5,3 x (38 x 89) x KB x KZcp
    #    = 0,8 x 5,3 x 3382 = 14 339,7 N ; avec KB = 1,10702 : 15 874,4 N
    assert close(bearing_resistance(5.3, 38 * 89), 14339.68), "bearing_resistance -> FAILED"
    assert close(bearing_resistance(5.3, 38 * 89, kb=1.10702), 15874.4), "bearing_resistance KB -> FAILED"
    # Q'r = (2/3) x 0,8 x 5,3 x 4351 = 12 298,8 N
    assert close(
        bearing_resistance_near_support(5.3, 4351), 12298.83
    ), "bearing_resistance_near_support -> FAILED"

    # A.6.5.6 : fcp à partir de G (tableau A.11)
    # S-P-F G = 0,42 : 0,9 x 1,8125 x (942,396 - 473,8) / 145,038 = 5,2703 (tableau 6.4 : 5,3)
    # D. Fir-L G = 0,49 : 0,9 x 1,8125 x 625,662 / 145,038 = 7,0368 (tableau 6.4 : 7,0)
    # Ess. nordiques G = 0,35 : 0,9 x 1,8125 x 311,53 / 145,038 = 3,5038 (tableau 6.4 : 3,5)
    # Sans la limite de tolérance (densité marquée NLGA) : 5,2703 / 0,9 = 5,8559
    assert close(bearing_strength_from_density(0.42), 5.2703), "fcp G S-P-F -> FAILED"
    assert close(bearing_strength_from_density(0.49), 7.0368), "fcp G D.Fir-L -> FAILED"
    assert close(bearing_strength_from_density(0.35), 3.5038), "fcp G NS -> FAILED"
    assert close(bearing_strength_from_density(0.42, tolerance_limit=False), 5.8559), "fcp G NLGA -> FAILED"
    for bad in (
        lambda: bearing_strength_from_density(0.2),
        lambda: bearing_size_factor(0, 89),
        lambda: bearing_length_factor(0),
        lambda: average_bearing_area(38, 0, 89),
    ):
        try:
            bad()
            raise AssertionError("aurait dû lever ValueError")
        except ValueError:
            pass

    # Test density_table_a11 (tableau A.11)
    for args, expected in (
        (("df",), 0.49), (("hf",), 0.46), (("spf",), 0.42), (("ns",), 0.35),
        (("courant", 8300), 0.42), (("normal", 11700), 0.42),
        (("normal", 12400), 0.47), (("rare", 13100), 0.47),
        (("courant", 13800), 0.50), (("normal", 16500), 0.50),
    ):
        assert density_table_a11(*args) == expected, f"density_table_a11{args} -> FAILED"
    for e in (8000, 12000, 13500, 17000):
        try:
            density_table_a11("normal", e)
            raise AssertionError(f"density_table_a11 E = {e} aurait dû lever ValueError")
        except ValueError:
            pass
    # Toutes les classes MSR et MEL de la base ont une densité au tableau A.11
    for row in SawnLumberStrengths.session.query(SawnLumberStrengths).filter(
        SawnLumberStrengths.category.in_(("MSR", "MEL"))  # type: ignore
    ):
        density_table_a11(row.specie, row.e)

    print("All tests passed.")


# RUN FILE
if __name__ == "__main__":
    _tests()


# END
