"""
Source de K_D dans la note de calcul (issue #58) : « Tableau 5.1 » par défaut, « 5.3.2.2 » quand K_D est
calculé à partir des charges. La valeur de K_D vient de l'appelant ; seule la source change.
"""

import pytest

from moteur.normes.csa_o86_19.ch_6_bois_de_sciage.art_6_5_calcul_des_resistances import (
    art_6_5_3_resistance_au_moment_de_flexion as art_6_5_3,
    art_6_5_4_resistance_au_cisaillement as art_6_5_4,
    art_6_5_5_resistance_a_la_compression_parallele_au_fil as art_6_5_5,
    art_6_5_6_resistance_a_la_compression_perpendiculaire_au_fil as art_6_5_6,
)

# 2x4 S-P-F n° 1/n° 2 (38 mm x 89 mm), valeurs du tableau 6.4 (MPa)
VERIFICATIONS = {
    "flexion": lambda **k: art_6_5_3.verifier_flexion(38, 89, 11.8, **k),
    "cisaillement": lambda **k: art_6_5_4.verifier_cisaillement(38, 89, 1.5, **k),
    "fissuration": lambda **k: art_6_5_4.verifier_cisaillement_par_fissuration(38, 89, 10, 50, **k),
    "compression parallèle": lambda **k: art_6_5_5.verifier_compression_parallele_au_fil(
        38, 89, 2400, 1200, 2400, 11.5, 6500, **k  # C_C = 1200 mm / 38 mm = 31.6 <= 50
    ),
    "compression perpendiculaire": lambda **k: art_6_5_6.verifier_compression_perpendiculaire_au_fil(
        38, 89, 89, 5.3, **k
    ),
    "près d'un appui": lambda **k: art_6_5_6.verifier_compression_perpendiculaire_pres_d_un_appui(
        38, 89, 89, 140, 5.3, **k
    ),
}


def _k_d(resultat):
    return [d for d in resultat.donnees if d.symbole == "K_D"][0]


@pytest.mark.parametrize("nom", VERIFICATIONS)
def test_source_par_defaut_tableau_5_1(nom):
    assert _k_d(VERIFICATIONS[nom](K_D=0.65)).source == "Tableau 5.1"


@pytest.mark.parametrize("nom", VERIFICATIONS)
def test_source_5_3_2_2(nom):
    # P_L = 3 kPa, S = 2 kPa, L = 1 kPa : P_s = 2.5 kPa ; K_D = 1 - 0.5 log(1.2) = 0.96041
    donnee = _k_d(VERIFICATIONS[nom](K_D=0.96041, source_K_D="5.3.2.2"))
    assert donnee.source == "5.3.2.2"
    assert donnee.valeur == pytest.approx(0.96041)
