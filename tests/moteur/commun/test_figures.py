"""Figures schématiques des vérifications (moteur/commun/figures.py, issue #62)."""

import re

from moteur.commun.figures import figure
from moteur.commun.resultat import Resultat
from moteur.normes.csa_o86_19.ch_6_bois_de_sciage.art_6_5_calcul_des_resistances import (
    art_6_5_6_resistance_a_la_compression_perpendiculaire_au_fil as art_6_5_6,
)


def _texte(svg: str) -> str:
    """Texte visible du SVG, sans balises ni espace sans chasse."""
    return re.sub(r"<[^>]+>", "", svg).replace("​", "")


def _appui(**kwargs) -> Resultat:
    donnees = dict(b=38, d=184, L_b=89, f_cp=5.3, largeur_element=38)  # mm ; MPa
    donnees.update(kwargs)
    return art_6_5_6.verifier_compression_perpendiculaire_au_fil(**donnees)


def test_compression_perpendiculaire_cotes_dans_les_deux_unites():
    svg = figure(_appui(R_f=12))  # kN
    assert svg.startswith("<svg")
    texte = _texte(svg)
    # Données comme dans le tableau de la note : 89 mm / 25.4 mm/po = 3.50 po ;
    # 38 mm / 25.4 = 1.50 po ; 184 mm / 25.4 = 7.24 po
    assert "Lb = 89 mm" in texte and "(3.50 po)" in texte
    assert "b = 38 mm" in texte and "(1.50 po)" in texte
    assert "d = 184 mm" in texte and "(7.24 po)" in texte
    # Charge comme dans la vérification (3 chiffres significatifs) :
    # 12 000 N / 4.448 N/lb = 2698 lb -> 2700 lb
    assert "Rf = 12.0 kN" in texte and "(2700 lb)" in texte


def test_sans_charge_ponderee_symbole_seulement():
    texte = _texte(figure(_appui()))
    assert "Rf" in texte and "kN" not in texte and "lb" not in texte


def test_appui_plus_etroit_que_l_element():
    # b = 30 mm < b_élément = 89 mm : l'appui est dessiné plus étroit que la section (28 contre 40)
    assert "width='28'" in figure(_appui(b=30, largeur_element=89))
    assert "width='28'" not in figure(_appui())


def test_couleurs_du_compte():
    svg = figure(_appui(R_f=12), principale="#112233", accent="#AA5500")
    assert "#112233" in svg and "#AA5500" in svg
    assert "#233614" not in svg and "#9E5A00" not in svg


def test_verification_sans_figure():
    assert figure(Resultat("CSA O86:19", "6.5.3", "Flexion")) is None
    # 6.5.6.3 n'a pas encore de figure : encadré « à venir » dans la note
    r = art_6_5_6.verifier_compression_perpendiculaire_pres_d_un_appui(
        b=38, d=184, L_b_appui=89, L_b_charge=89, f_cp=5.3
    )
    assert figure(r) is None
