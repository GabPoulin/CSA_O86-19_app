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


def test_bois_de_bout_avec_un_x():
    """Convention de dessin : l'élément vu en bout porte un X (figure 6.1) ; les appuis sont hachurés."""
    svg = figure(_appui(R_f=12))
    # X sur l'élément en section (x 196 à 236 ; y 20 à 66) seulement
    assert "M196 20 L236 66 M236 20 L196 66" in svg
    assert "M14 66 L60 90" not in svg  # l'appui en élévation n'a pas de X


def test_element_compose_chaque_pli_avec_son_x():
    """Poutre composée : chaque pli est dessiné vu en bout, avec son X (demande de l'utilisateur)."""
    # 3-2x10 : 3 plis de 38 mm = 114 mm ; largeur d'un pli dans la figure = 76 / 3
    r = _appui(b=114, d=235, largeur_element=114, plis=3)
    svg = figure(r)
    assert svg.count("stroke-width='2.5'/><path") == 3  # 3 rectangles vus en bout, chacun avec un X
    assert any(d.symbole == "n_{plis}" and d.valeur == 3 for d in r.donnees)


def test_un_seul_pli_sans_donnee_de_plis():
    r = _appui()
    assert figure(r).count("stroke-width='2.5'/><path") == 1
    assert all(d.symbole != "n_{plis}" for d in r.donnees)  # pas de ligne inutile dans la note


def _pres_d_un_appui(**kwargs) -> Resultat:
    donnees = dict(b=38, d=184, L_b_appui=89, L_b_charge=38, f_cp=5.3, largeur_element=38)  # mm ; MPa
    donnees.update(kwargs)
    return art_6_5_6.verifier_compression_perpendiculaire_pres_d_un_appui(**donnees)


def test_compression_pres_d_un_appui_cotes_dans_les_deux_unites():
    texte = _texte(figure(_pres_d_un_appui(P_f=5)))  # kN
    # 89 mm / 25.4 mm/po = 3.50 po ; 38 mm / 25.4 = 1.50 po ; 184 mm / 25.4 = 7.24 po
    assert "Lb,appui = 89 mm" in texte and "(3.50 po)" in texte
    assert "Lb,charge = 38 mm" in texte and "(1.50 po)" in texte
    assert "b = 38 mm" in texte and "d = 184 mm" in texte
    # 5 000 N / 4.448 N/lb = 1124 lb -> 1120 lb (3 chiffres significatifs)
    assert "Pf = 5.00 kN" in texte and "(1120 lb)" in texte
    assert "≤ d" in texte  # charge à au plus d du centre de l'appui (6.5.6.3.1)


def test_compression_pres_d_un_appui_sans_charge_et_plis():
    r = _pres_d_un_appui(b=114, d=235, largeur_element=114, plis=3)
    svg = figure(r)
    texte = _texte(svg)
    assert "Pf" in texte and "kN" not in texte
    assert svg.count("stroke-width='2.5'/><path") == 3  # 3 plis vus en bout, chacun avec un X
    assert any(d.symbole == "n_{plis}" and d.valeur == 3 for d in r.donnees)
