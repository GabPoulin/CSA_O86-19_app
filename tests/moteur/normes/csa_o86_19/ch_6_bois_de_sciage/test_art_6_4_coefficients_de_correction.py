"""Tests de 6.4 Coefficients de correction (CSA O86:19, tableaux 6.10 à 6.13, p. 61-63)."""

import pytest

from moteur.normes.csa_o86_19.ch_6_bois_de_sciage import art_6_4_coefficients_de_correction as m
from moteur.normes.csa_o86_19.ch_6_bois_de_sciage.art_6_4_coefficients_de_correction import (
    CAS_1,
    CAS_2,
    CISAILLEMENT_LONGITUDINAL,
    CISAILLEMENT_PAR_FISSURATION,
    COMPRESSION_PARALLELE,
    COMPRESSION_PERPENDICULAIRE,
    FLEXION,
    MODULE_D_ELASTICITE,
    POUTRES_COMPOSEES,
    PROPRIETES,
    TRACTION_PARALLELE,
    K_H,
    K_S,
    K_T,
    K_Z,
    cas_de_systeme,
)


# Tableau 6.10 : (propriété, milieu humide face étroite <= 89 mm, milieu humide > 89 mm)
@pytest.mark.parametrize(
    ("propriete", "humide_89", "humide_plus_89"),
    [
        (FLEXION, 0.84, 1.00),
        (CISAILLEMENT_PAR_FISSURATION, 0.70, 0.70),
        (CISAILLEMENT_LONGITUDINAL, 0.96, 1.00),
        (COMPRESSION_PARALLELE, 0.69, 0.91),
        (COMPRESSION_PERPENDICULAIRE, 0.67, 0.67),
        (TRACTION_PARALLELE, 0.84, 1.00),
        (MODULE_D_ELASTICITE, 0.94, 1.00),
    ],
)
def test_K_S(propriete, humide_89, humide_plus_89):
    assert K_S(propriete) == 1.00  # milieu sec
    assert K_S(propriete, milieu_humide=False, face_etroite=140) == 1.00
    assert K_S(propriete, milieu_humide=True, face_etroite=38) == humide_89  # 38 mm
    assert K_S(propriete, milieu_humide=True, face_etroite=89) == humide_89  # 89 mm : « ou moins »
    assert K_S(propriete, milieu_humide=True, face_etroite=90) == humide_plus_89  # 90 mm > 89 mm
    assert K_S(propriete, milieu_humide=True, face_etroite=140) == humide_plus_89


def test_K_T():
    for propriete in PROPRIETES:
        assert K_T(propriete) == 1.00  # non traité
        assert K_T(propriete, traite=True) == 1.00  # traité, non incisé
        assert K_T(propriete, incise=True) == 1.00  # incisé sans traitement : pas au tableau 6.11
        # traité et incisé, épaisseur 90 mm > 89 mm : pas de réduction au tableau 6.11
        assert K_T(propriete, traite=True, incise=True, epaisseur=90) == 1.00
    # Traité d'au plus 89 mm, incisé : module d'élasticité 0.90 (sec) et 0.95 (humide)
    assert K_T(MODULE_D_ELASTICITE, True, True, 89) == 0.90  # 89 mm : « au plus »
    assert K_T(MODULE_D_ELASTICITE, True, True, 38, milieu_humide=True) == 0.95
    # Autres propriétés : 0.75 (sec) et 0.85 (humide)
    for propriete in set(PROPRIETES) - {MODULE_D_ELASTICITE}:
        assert K_T(propriete, True, True, 38) == 0.75
        assert K_T(propriete, True, True, 89, milieu_humide=True) == 0.85


def test_cas_de_systeme():
    assert cas_de_systeme() is None
    assert cas_de_systeme(espacement_610_mm_ou_moins=True) == CAS_1
    assert cas_de_systeme(True, True) == CAS_2
    assert cas_de_systeme(False, True) is None  # 6.4.4.2 exige aussi les conditions de 6.4.4.1
    # Issue #7 : une poutre composée prend toujours la colonne « Poutres composées »
    assert cas_de_systeme(poutre_composee=True) == POUTRES_COMPOSEES
    assert cas_de_systeme(True, True, True) == POUTRES_COMPOSEES


# Tableau 6.12 : (propriété, cas 1, cas 2 classé visuellement, cas 2 MSR, poutres composées)
@pytest.mark.parametrize(
    ("propriete", "cas_1", "cas_2", "cas_2_msr", "composees"),
    [
        (FLEXION, 1.10, 1.40, 1.20, 1.10),
        (CISAILLEMENT_LONGITUDINAL, 1.10, 1.40, 1.20, 1.10),
        (COMPRESSION_PARALLELE, 1.10, 1.10, 1.10, 1.00),
        (TRACTION_PARALLELE, 1.10, 1.00, 1.00, 1.00),  # cas 2 : « — », 1.00 (issue #7)
        (CISAILLEMENT_PAR_FISSURATION, 1.00, 1.00, 1.00, 1.00),  # autre propriété
        (COMPRESSION_PERPENDICULAIRE, 1.00, 1.00, 1.00, 1.00),
        (MODULE_D_ELASTICITE, 1.00, 1.00, 1.00, 1.00),
    ],
)
def test_K_H(propriete, cas_1, cas_2, cas_2_msr, composees):
    assert K_H(propriete) == 1.00
    assert K_H(propriete, CAS_1) == cas_1
    assert K_H(propriete, CAS_1, msr=True) == cas_1  # MSR au cas 1 : colonne du cas 1 (issue #7)
    assert K_H(propriete, CAS_2) == cas_2
    assert K_H(propriete, CAS_2, msr=True) == cas_2_msr
    assert K_H(propriete, POUTRES_COMPOSEES) == composees
    assert K_H(propriete, POUTRES_COMPOSEES, msr=True) == composees


def test_K_H_cas_inconnu():
    with pytest.raises(ValueError, match="tableau 6.12"):
        K_H(FLEXION, "cas_3")


# Tableau 6.13 : (b mm, d mm, K_Zb = K_Zv, K_Zt)
@pytest.mark.parametrize(
    ("b", "d", "K_Zb", "K_Zt"),
    [
        (38, 38, 1.7, 1.5),  # 38 x 38 mm
        (38, 64, 1.7, 1.5),  # 38 x 64 mm
        (38, 89, 1.7, 1.5),  # 2 x 4 : 38 x 89 mm
        (89, 89, 1.7, 1.5),  # 4 x 4 : 89 x 89 mm, face étroite 89 à 102
        (64, 64, 1.7, 1.5),  # 64 x 64 mm : ligne 64, face étroite 38 à 64
        (38, 114, 1.5, 1.4),  # grande face 114 mm, face étroite 38 à 64
        (89, 114, 1.6, 1.4),  # face étroite 89 à 102
        (114, 114, 1.3, 1.4),  # face étroite 114 ou plus
        (38, 140, 1.4, 1.3),  # 2 x 6
        (89, 140, 1.5, 1.3),  # 4 x 6
        (140, 140, 1.3, 1.3),  # 6 x 6
        (38, 184, 1.2, 1.2),  # 2 x 8
        (89, 184, 1.3, 1.2),
        (140, 191, 1.3, 1.2),  # 6 x 8 vert : 140 x 191 mm
        (38, 235, 1.1, 1.1),  # 2 x 10
        (89, 235, 1.2, 1.1),
        (140, 241, 1.2, 1.1),
        (38, 286, 1.0, 1.0),  # 2 x 12
        (89, 286, 1.1, 1.0),
        (140, 292, 1.1, 1.0),
        (38, 337, 0.9, 0.9),  # 2 x 14
        (89, 337, 1.0, 0.9),
        (140, 343, 1.0, 0.9),
        (38, 387, 0.8, 0.8),  # 2 x 16
        (89, 387, 0.9, 0.8),
        (140, 394, 0.9, 0.8),
        (184, 140, 1.3, 1.2),  # l'ordre b, d ne change rien : 140 x 184 mm, ligne 184 à 191
        (140, 165, 1.3, 1.2),  # 165 mm : ligne supérieure 184 à 191 (décision CLAUDE.md)
        (140, 216, 1.2, 1.1),  # 216 mm : ligne supérieure 235 à 241 (décision CLAUDE.md)
    ],
)
def test_K_Z_bois_classe_visuellement(b, d, K_Zb, K_Zt):
    for categorie in ("Lumber", "Beam", "Post"):
        assert K_Z(FLEXION, b, d, categorie) == K_Zb
        assert K_Z(CISAILLEMENT_LONGITUDINAL, b, d, categorie) == K_Zb  # K_Zv = K_Zb
        assert K_Z(TRACTION_PARALLELE, b, d, categorie) == K_Zt


def test_K_Z_autres_proprietes():
    assert K_Z(MODULE_D_ELASTICITE, 38, 140, "Lumber") == 1.0
    assert K_Z(CISAILLEMENT_PAR_FISSURATION, 38, 140, "Lumber") == 1.0  # « Autre propriété »


def test_K_Z_charpente_legere():
    # 6.4.5.2 : K_Z = 1.00 pour la charpente légère
    for propriete in (FLEXION, CISAILLEMENT_LONGITUDINAL, TRACTION_PARALLELE):
        assert K_Z(propriete, 38, 64, "Light") == 1.0


def test_K_Z_msr_mel():
    # 6.4.5.3 : K_Z = 1.00, sauf K_Zv selon le tableau 6.13
    for categorie in ("MSR", "MEL"):
        assert K_Z(FLEXION, 38, 235, categorie) == 1.0
        assert K_Z(TRACTION_PARALLELE, 38, 235, categorie) == 1.0
        assert K_Z(CISAILLEMENT_LONGITUDINAL, 38, 235, categorie) == 1.1  # 38 x 235 mm : 1.1


@pytest.mark.parametrize("propriete", [COMPRESSION_PARALLELE, COMPRESSION_PERPENDICULAIRE])
def test_K_Z_compression(propriete):
    with pytest.raises(ValueError, match="6.5.5.2.4"):
        K_Z(propriete, 38, 140, "Lumber")


def test_propriete_inconnue():
    for fonction in (K_S, K_T, K_H):
        with pytest.raises(ValueError, match="Propriété inconnue"):
            fonction("flex")
    with pytest.raises(ValueError, match="Propriété inconnue"):
        K_Z("flex", 38, 140, "Lumber")


def test_lignes_du_tableau_6_13():
    assert m.ligne_du_tableau_6_13(38) == "38"
    assert m.ligne_du_tableau_6_13(64) == "64"
    assert m.ligne_du_tableau_6_13(89) == "89"
    assert m.ligne_du_tableau_6_13(114) == "114"
    assert m.ligne_du_tableau_6_13(191) == "184 à 191"
    assert m.ligne_du_tableau_6_13(394) == "387 ou plus"


def test_tableau_6_13_tirets():
    # « — » au tableau 6.13 : colonnes 89 à 102 et 114 ou plus des lignes 38 et 64, colonne 114 ou
    # plus de la ligne 89 (la face étroite ne peut pas dépasser la grande face)
    lignes = {ligne: valeurs for _, ligne, valeurs, _ in m.TABLEAU_6_13}
    assert lignes["38"] == (1.7, None, None)
    assert lignes["64"] == (1.7, None, None)
    assert lignes["89"] == (1.7, 1.7, None)
    assert lignes["114"] == (1.5, 1.6, 1.3)


# Issue #45 : dimensions réelles absentes du tableau 6.13 (bois vert, mode brut)
# (b mm, d mm, ligne, K_Zb = K_Zv, K_Zt)
@pytest.mark.parametrize(
    ("b", "d", "ligne", "K_Zb", "K_Zt"),
    [
        (40, 66, "89", 1.7, 1.5),  # 2 x 3 vert : 66 mm -> ligne 89
        (40, 91, "114", 1.5, 1.4),  # 2 x 4 vert : 91 mm > 89 mm -> ligne 114, face étroite 38 à 64
        (40, 117, "140", 1.4, 1.3),  # 2 x 5 vert : 117 mm -> ligne 140
        (40, 143, "184 à 191", 1.2, 1.2),  # 2 x 6 vert : 143 mm -> ligne « 184 à 191 »
        (40, 190, "184 à 191", 1.2, 1.2),  # 2 x 8 vert : 190 mm, dans « 184 à 191 »
        (40, 191, "184 à 191", 1.2, 1.2),  # 191 mm : borne supérieure incluse
        (40, 192, "235 à 241", 1.1, 1.1),  # 192 mm : ligne supérieure
        (40, 150, "184 à 191", 1.2, 1.2),  # brut 150 mm -> ligne « 184 à 191 »
        (40, 260, "286 à 292", 1.0, 1.0),  # brut 260 mm -> ligne « 286 à 292 »
        (40, 344, "387 ou plus", 0.8, 0.8),  # brut 344 mm -> ligne « 387 ou plus »
        (40, 393, "387 ou plus", 0.8, 0.8),  # 2 x 16 vert : 393 mm
        (91, 143, "184 à 191", 1.3, 1.2),  # 4 x 6 vert : face étroite 91 mm (89 à 102)
    ],
)
def test_K_Z_dimensions_absentes(b, d, ligne, K_Zb, K_Zt):
    assert m.ligne_du_tableau_6_13(max(b, d)) == ligne
    assert K_Z(FLEXION, b, d, "Lumber") == K_Zb
    assert K_Z(CISAILLEMENT_LONGITUDINAL, b, d, "Lumber") == K_Zb
    assert K_Z(TRACTION_PARALLELE, b, d, "Lumber") == K_Zt


@pytest.mark.parametrize(
    ("face_etroite", "colonnes"),
    [(38, (0,)), (64, (0,)), (65, (0, 1)), (66, (0, 1)), (88, (0, 1)), (89, (1,)), (102, (1,)),
     (103, (1, 2)), (113, (1, 2)), (114, (2,)), (394, (2,))],
)
def test_colonnes_du_tableau_6_13(face_etroite, colonnes):
    assert m.colonnes_du_tableau_6_13(face_etroite) == colonnes


@pytest.mark.parametrize(
    ("b", "d", "K_Zb"),
    [
        (66, 114, 1.5),  # face étroite 66 mm, ligne 114 : min(1.5 ; 1.6) = 1.5
        (66, 143, 1.2),  # 3 x 6 vert, ligne « 184 à 191 » : min(1.2 ; 1.3) = 1.2
        (76, 140, 1.4),  # brut 76 mm (3 po), ligne 140 : min(1.4 ; 1.5) = 1.4
        (105, 140, 1.3),  # brut 105 mm, ligne 140 : min(1.5 ; 1.3) = 1.3
        (110, 191, 1.3),  # brut 110 mm, ligne « 184 à 191 » : min(1.3 ; 1.3) = 1.3
        (110, 114, 1.3),  # brut 110 x 114 mm, ligne 114 : min(1.6 ; 1.3) = 1.3
        (70, 89, 1.7),  # 70 x 89 mm, ligne 89 : min(1.7 ; 1.7) = 1.7
    ],
)
def test_K_Z_face_etroite_entre_deux_colonnes(b, d, K_Zb):
    assert K_Z(FLEXION, b, d, "Lumber") == K_Zb
    assert K_Z(CISAILLEMENT_LONGITUDINAL, b, d, "Beam") == K_Zb


def test_K_Zv_msr_dimension_absente():
    # 6.4.5.3 : K_Zv du tableau 6.13 pour le MSR, même règle (38 x 143 mm -> ligne « 184 à 191 »)
    assert K_Z(CISAILLEMENT_LONGITUDINAL, 38, 143, "MSR") == 1.2
