"""Tests de la note de calcul PDF (moteur/commun/note_de_calcul, issue #50)."""

import pytest

from moteur.commun.note_de_calcul import (
    EnTete,
    donnees_de_la_note,
    formater_nombre,
    formater_valeur,
    produire_pdf,
)
from moteur.normes.csa_o86_19.ch_6_bois_de_sciage.art_6_5_calcul_des_resistances import (
    art_6_5_3_resistance_au_moment_de_flexion as art_6_5_3,
    art_6_5_4_resistance_au_cisaillement as art_6_5_4,
)

ENTETE = EnTete("Client", "Projet", "Adresse", "2026-001", "2026-11-19", "Ingénieur", "000000")


def flexion(M_f=4.0):
    # 38 x 235 mm, f_b = 11.8 MPa, K_Zb = 1.1 : M_r = 4 085 877 N·mm (test de 6.5.3)
    return art_6_5_3.verifier_flexion(
        38, 235, 11.8, K_Zb=1.1, support_lateral_aux_appuis=True, rive_comprimee_maintenue=True,
        M_f=M_f,
    )


def test_formater_nombre():
    assert formater_nombre(4085877.0) == "4085877"  # >= 1000 : entier
    assert formater_nombre(349758.333) == "349758"
    assert formater_nombre(11.8) == "11.80"  # 10 à 1000 : 2 décimales, point décimal
    assert formater_nombre(1.1) == "1.1"  # < 10 : 4 chiffres significatifs
    assert formater_nombre(0.794512) == "0.7945"


def test_formater_valeur_deux_unites():
    assert formater_valeur(38, "mm", "dimension") == "38 mm (1.50 po)"  # 38 mm / 25.4 mm/po
    assert formater_valeur(11.8, "MPa") == "11.80 MPa"
    assert formater_valeur("S-P-F") == "S-P-F"


def test_donnees_de_la_note():
    note = donnees_de_la_note([("Solive S-1", flexion())], ENTETE)
    assert note["entete"]["norme"] == "CSA O86:19"
    assert note["entete"]["client"] == "Client"
    r = note["resultats"][0]
    assert (r["titre"], r["element"], r["article"]) == ("Résistance au moment de flexion", "Solive S-1", "6.5.3")
    assert r["donnees"][0]["valeur"] == "38 mm (1.50 po)"  # b
    assert r["etapes"][-1]["symbole"] == "M_r"
    assert r["etapes"][-1]["resultat"] == "4090000 N·mm"  # 4 085 877 N·mm, 3 chiffres significatifs
    v = r["verification"]
    # 4.0 kN·m / 4.086 kN·m = 97.90 %
    assert v["ratio"] == "97.90 %"
    assert v["respecte"] is True
    assert v["charge"].startswith("4.00 kN·m (")  # 3 chiffres significatifs


def test_verification_absente():
    note = donnees_de_la_note([("Solive S-1", flexion(M_f=None))], ENTETE)
    assert note["resultats"][0]["verification"] is None


def test_produire_pdf():
    entaille = art_6_5_4.verifier_cisaillement_par_fissuration(38, 235, 20, 100, V_f=7.5)
    pdf = produire_pdf([("Solive S-1", flexion()), ("Solive S-1", entaille)], ENTETE)
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 10_000  # octets


def test_produire_pdf_sans_verification():
    with pytest.raises(ValueError, match="Aucune vérification"):
        produire_pdf([], ENTETE)


def test_calcul_sur_une_ligne():
    from moteur.commun.note_de_calcul import calcul_en_latex

    assert calcul_en_latex("S = b d^2 / 6", "38 \\times 235^2 / 6") == "S = b d^2 / 6 = 38 \\times 235^2 / 6"


def test_calcul_long_sur_plusieurs_lignes():
    from moteur.commun.note_de_calcul import LONGUEUR_UNE_LIGNE, calcul_en_latex

    formule = "K_N = " + "x" * LONGUEUR_UNE_LIGNE
    calcul = calcul_en_latex(formule, "1.86")
    # Égalités alignées : K_N &= ... \\ &= 1.86
    assert calcul.startswith("\\begin{aligned} K_N &= ")
    assert calcul.endswith(" \\\\ &= 1.86 \\end{aligned}")


def test_apparence_par_defaut_et_personnalisee():
    from moteur.commun.note_de_calcul import Apparence

    defaut = donnees_de_la_note([("S-1", flexion())], ENTETE)["apparence"]
    assert defaut == {"logo": None, "principale": "#233614", "accent": "#9E5A00"}
    logo = bytes([137, 80, 78, 71])  # début d'un fichier PNG
    perso = donnees_de_la_note(
        [("S-1", flexion())], ENTETE, Apparence(logo, "#003366", "#CC0000")
    )["apparence"]
    assert perso == {"logo": [137, 80, 78, 71], "principale": "#003366", "accent": "#CC0000"}


def test_produire_pdf_couleurs_personnalisees():
    from moteur.commun.note_de_calcul import Apparence

    pdf = produire_pdf([("S-1", flexion())], ENTETE, Apparence(principale="#003366", accent="#CC0000"))
    assert pdf.startswith(b"%PDF")


def test_sources_des_donnees():
    # Références à la norme dans le tableau des données (revue de la PR #55)
    r = art_6_5_3.verifier_flexion(
        38, 235, 11.8, support_lateral_aux_appuis=True, rive_comprimee_maintenue=True,
        source_resistances="Tableau 6.4",
    )
    sources = {d.symbole: d.source for d in r.donnees}
    assert sources["f_b"] == "Tableau 6.4"
    assert sources["K_D"] == "Tableau 5.1"
    assert sources["K_{Sb}"] == "Tableau 6.10"
    assert sources["K_T"] == "Tableau 6.11"
    assert sources["K_H"] == "Tableau 6.12"
    assert sources["K_{Zb}"] == "Tableau 6.13"


def test_ratio_une_seule_fois():
    v = donnees_de_la_note([("S-1", flexion())], ENTETE)["resultats"][0]["verification"]
    assert v["ratio"] == "97.90 %"
    assert v["message"] == "État limite respecté"  # sans répéter le ratio
    depasse = donnees_de_la_note([("S-1", flexion(M_f=5.0))], ENTETE)["resultats"][0]["verification"]
    assert depasse["message"] == "État limite dépassé"  # 5.0 kN·m / 4.086 kN·m = 122.37 %


def test_meme_nombre_de_chiffres_significatifs_dans_les_calculs():
    from moteur.commun.note_de_calcul import formater_resultat

    # 11.8 MPa x 145.04 psi/MPa = 1711.4 psi -> 1710 psi (3 chiffres significatifs)
    assert formater_resultat(11.8, "MPa", "contrainte") == "11.8 MPa (1710 psi)"
    assert formater_resultat(0.794512) == "0.795"
    r = donnees_de_la_note([("S-1", flexion())], ENTETE)["resultats"][0]
    # Substitution de M_r : chaque valeur avec 3 chiffres significatifs (349 758 mm³ -> 350000)
    assert r"0.9 \times 11.8 \times 350000 \times 1.10 \times 1.00" in r["etapes"][-1]["calcul"]


def test_avertissement_en_test_dans_la_note():
    note = donnees_de_la_note([("S-1", flexion(), True), ("S-1", flexion())], ENTETE)
    assert [r["en_test"] for r in note["resultats"]] == [True, False]
    assert produire_pdf([("S-1", flexion(), True)], ENTETE).startswith(b"%PDF")
