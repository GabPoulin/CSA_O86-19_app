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
    assert r["etapes"][-1]["resultat"] == "4085877 N·mm"
    v = r["verification"]
    # 4.0 kN·m / 4.086 kN·m = 97.90 %
    assert v["ratio"] == "97.90 %"
    assert v["respecte"] is True
    assert v["charge"].startswith("4.00 kN·m (")


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
