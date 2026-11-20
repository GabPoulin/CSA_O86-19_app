"""Page Bois de sciage : K_D calculé à partir des charges (5.3.2.2, issue #58)."""

from tests.test_acces import _connecte


def _qr(at):
    return [m.value for m in at.markdown if m.value.startswith("$Qr")]


def _preparer(p_l, neige, surcharge):
    at = _connecte("admin", "mot-admin")
    [r for r in at.radio if r.label.startswith("Durée")][0].set_value("Continue (permanente)").run()
    [c for c in at.checkbox if c.key == "kd_charges"][0].check().run()
    for cle, valeur in (("kd_p_l", p_l), ("kd_s", neige), ("kd_l", surcharge)):
        [n for n in at.number_input if n.key == cle][0].set_value(valeur)
    at.run()
    for cle, valeur in (("cp_support_length", 89.0), ("cp_rf", 5.0)):  # mm ; kN
        [n for n in at.number_input if n.key == cle][0].set_value(valeur)
    return at.run()


def test_k_d_par_les_charges():
    # P_L = 3 kPa, S = 2 kPa, L = 1 kPa : P_s = max(2, 1, 2 + 0.5, 1 + 1) = 2.5 kPa
    # K_D = 1 - 0.5 log(3 / 2.5) = 1 - 0.5 x 0.07918 = 0.96041
    at = _preparer(3.0, 2.0, 1.0)
    assert not at.exception
    assert any("P_s = 2.50" in m.value and "K_D = 0.960" in m.value for m in at.markdown)
    # 2x6 S-P-F n° 1/n° 2 (f_cp = 5.3 MPa), appui 38 mm x 89 mm, K_B = K_Zcp = 1.00 :
    # Q_r = 0.8 x 5.3 MPa x 0.96041 x 3382 mm² = 13 772 N = 13.77 kN
    assert _qr(at) == ["$Qr = 13.77 kN$"]


def test_charge_continue_qui_ne_domine_pas():
    # P_L = 2 kPa <= P_s = 2.5 kPa : K_D = 1.00 (5.3.2.2 ne s'applique pas), avec un avertissement
    at = _preparer(2.0, 2.0, 1.0)
    assert not at.exception
    assert any("K_D = 1.000" in m.value for m in at.markdown)
    assert any("ne domine pas" in w.value for w in at.warning)
    # Q_r = 0.8 x 5.3 MPa x 1.00 x 3382 mm² = 14 340 N = 14.34 kN
    assert _qr(at) == ["$Qr = 14.34 kN$"]


def test_sans_charges_tableau_5_1():
    # Durée continue sans charges : K_D = 0.65 (tableau 5.1)
    at = _connecte("admin", "mot-admin")
    [r for r in at.radio if r.label.startswith("Durée")][0].set_value("Continue (permanente)").run()
    [c for c in at.checkbox if c.key == "kd_charges"][0].check().run()
    for cle, valeur in (("cp_support_length", 89.0), ("cp_rf", 5.0)):
        [n for n in at.number_input if n.key == cle][0].set_value(valeur)
    at.run()
    assert not at.exception
    assert any("tableau 5.1" in i.value for i in at.info)
    # Q_r = 0.8 x 5.3 MPa x 0.65 x 3382 mm² = 9 321 N = 9.32 kN
    assert _qr(at) == ["$Qr = 9.32 kN$"]



def _images(noeud) -> int:
    """Nombre d'images (st.image) dans la page."""
    enfants = getattr(noeud, "children", {}).values()
    return sum((getattr(e, "type", None) == "image") + _images(e) for e in enfants)


def test_figure_de_la_compression_perpendiculaire():
    """Issue #62 : la figure de 6.5.6.2 s'affiche dans l'onglet une fois L_b entrée."""
    at = _connecte("admin", "mot-admin")
    avant = _images(at._tree)
    [n for n in at.number_input if n.key == "cp_support_length"][0].set_value(89.0).run()  # mm
    assert not at.exception
    assert _images(at._tree) == avant + 1


def test_figure_d_un_element_compose():
    """Issue #62 : avec 3 plis, la page passe le nombre de plis à la trace (figure)."""
    at = _connecte("admin", "mot-admin")
    [r for r in at.radio if r.label.startswith("Élément composé")][0].set_value(3).run()
    [n for n in at.number_input if n.key == "cp_support_length"][0].set_value(89.0).run()  # mm
    assert not at.exception
    assert _images(at._tree) >= 1
