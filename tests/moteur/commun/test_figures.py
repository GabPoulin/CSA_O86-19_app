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


def test_compression_perpendiculaire_symboles_sans_valeurs():
    """Symboles seulement : les valeurs sont dans le tableau des données (demande de l'utilisateur)."""
    svg = figure(_appui(R_f=12))  # kN
    assert svg.startswith("<svg")
    texte = _texte(svg)
    for symbole in ("Lb", "Rf", "b", "d"):
        assert symbole in texte
    assert not any(c.isdigit() for c in texte)  # aucun chiffre dans l'image
    assert "mm" not in texte and "kN" not in texte


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


def test_compression_pres_d_un_appui_symboles_sans_valeurs():
    texte = _texte(figure(_pres_d_un_appui(P_f=5)))  # kN
    for symbole in ("Pf", "≤ d", "b"):
        assert symbole in texte
    # Aucun chiffre dans l'image, sauf les indices de L_b1 et L_b2 (symboles de 6.5.6.3.2)
    assert not any(c.isdigit() for c in texte.replace("Lb1", "").replace("Lb2", ""))


def test_l_b1_est_la_plus_petite_longueur_d_appui():
    """6.5.6.3.2 (p. 72) : L_b1 = longueur d'appui la plus petite, L_b2 = la plus grande."""
    # Charge 38 mm < appui 89 mm : L_b1 sur le dessus (charge), L_b2 à l'appui
    r = _pres_d_un_appui(L_b_appui=89, L_b_charge=38)  # mm
    donnees = {d.symbole: (d.valeur, d.description) for d in r.donnees}
    assert donnees["L_{b1}"] == (38, "Longueur d'appui la plus petite (charge)")
    assert donnees["L_{b2}"] == (89, "Longueur d'appui la plus grande (appui)")
    svg = figure(r)
    assert svg.index(">L<tspan dy='4' font-size='75%'>b1<") < svg.index(">L<tspan dy='4' font-size='75%'>b2<")
    # Appui 38 mm < charge 89 mm : les symboles s'inversent
    r = _pres_d_un_appui(L_b_appui=38, L_b_charge=89)  # mm
    donnees = {d.symbole: (d.valeur, d.description) for d in r.donnees}
    assert donnees["L_{b1}"] == (38, "Longueur d'appui la plus petite (appui)")
    assert donnees["L_{b2}"] == (89, "Longueur d'appui la plus grande (charge)")
    svg = figure(r)
    assert svg.index(">L<tspan dy='4' font-size='75%'>b2<") < svg.index(">L<tspan dy='4' font-size='75%'>b1<")
    # Longueurs égales : L_b1 est celle de la charge, comme à la figure 6.2 (p. 71)
    r = _pres_d_un_appui(L_b_appui=89, L_b_charge=89)  # mm
    assert dict((d.symbole, d.description) for d in r.donnees)["L_{b1}"].endswith("(charge)")
    # A'_b inchangé : 38 mm x (38 mm + 89 mm) / 2 = 2413 mm² <= 1.5 x 38 mm x 38 mm = 2166 mm²
    # -> A'_b = 2166 mm² dans les deux cas
    for appui, charge in ((89, 38), (38, 89)):
        r = _pres_d_un_appui(L_b_appui=appui, L_b_charge=charge)
        assert r.etape("A'_b").valeur == 2166


def test_compression_pres_d_un_appui_plis():
    r = _pres_d_un_appui(b=114, d=235, largeur_element=114, plis=3)
    svg = figure(r)
    assert svg.count("stroke-width='2.5'/><path") == 3  # 3 plis vus en bout, chacun avec un X
    assert any(d.symbole == "n_{plis}" and d.valeur == 3 for d in r.donnees)

