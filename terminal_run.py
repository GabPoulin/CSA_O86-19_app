"""Permet d'utiliser la CSA O86:19 dans le terminal."""

import general_design

# Validation for correct inputs
ANSWERED = False

# Initial prompts
print("")
print("CSA O86:19: Règles de calcul des charpentes en bois")
print("    5 - Conception générale")
print("    6 - Bois de sciage")
print("")
section = input("Section: ")

# Section 5
if section == "5":
    print("    5.3 - Conditions et coefficients influant sur la résistance")
    print("    5.4 - Exigences relatives à la tenue en service")
    print("    5.5 - Effort de contreventement latéral sur les membrures")
    print("          d’âme en compression des fermes de toit en bois")
    print("    5.6 - Résistance au feu")
    print("")
    sous_section = input("Sous-section: 5.")

    # Sous-section 5.3
    if sous_section == "3":
        print("    5.3.2 - Coefficient de durée d’application de la charge, Kd")
        print("    5.3.8 - Validation de la section transversale")
        print("")
        clause = input("Clause: 5.3.")

        # Clause 5.3.2
        if clause == "2":
            duration = input(
                "\tDurée d'application de la charge ('courte', 'normale' ou 'continue') = "
            )
            kd = general_design.load_duration(duration)

            if duration == "continue":
                dead = input(
                    "\tCharge de durée d'application continue (Defaults to 0) = "
                )
                if dead == "":
                    dead = 0
                live = input(
                    "\tSurcharge de durée d'application normale (Defaults to 0) = "
                )
                if live == "":
                    live = 0
                snow = input("\tSurcharge de neige (Defaults to 0) = ")
                if snow == "":
                    snow = 0
                kd = general_design.load_duration(
                    duration, float(dead), float(live), float(snow)
                )

            print(f"\tKd = {kd}")
            print("")
            ANSWERED = True

        # Clause 5.3.8
        elif clause == "8":
            gross = input("\tSection brute = ")
            net = input("\tSection nette = ")
            message = general_design.cross_section(float(net), float(gross))

            print(f"\t{message}")
            print("")
            ANSWERED = True

    # Sous-section 5.4
    elif sous_section == "4":
        print("    5.4.1 - Module d'élasticité")
        print("    5.4.2 - Flèche")
        print("    5.4.4 - Accumulation d'eau")
        print("    5.4.5 - Vibration")
        print("    5.4.6 - Mouvements du bâtiment attribuables au")
        print("            changement de la teneur en humidité")
        print("")
        clause = input("Clause: 5.4.")

        # Clause 5.4.1
        if clause == "1":
            modulus = input("\tModule d'élasticité prévu, MPa = ")
            service = input("\tCoefficient de conditions d'utilisation = ")
            treatment = input("\tCoefficient de traitement = ")
            es = general_design.elasticity(
                float(modulus), float(service), float(treatment)
            )

            print(f"\tEs = {es} MPa")
            print("")
            ANSWERED = True

        # Clause 5.4.2
        elif clause == "2":
            message = general_design.deflection
            print("")
            ANSWERED = True

        # Clause 5.4.4
        elif clause == "4":
            message = general_design.ponding
            print("")
            ANSWERED = True

        # Clause 5.4.5
        elif clause == "5":
            message = general_design.Vibration.floor_vibration
            print("")
            ANSWERED = True

        # Clause 5.4.6
        elif clause == "6":
            s = general_design.moisture
            print("")
            ANSWERED = True

    # Branch to 5.5
    elif sous_section == "5":
        h = general_design.lateral_brace
        print("")
        ANSWERED = True

    # Branch to 5.6
    elif sous_section == "6":
        i = general_design.FireResistance.effective_section
        print("")
        ANSWERED = True

# Section 6
elif section == "6":
    print("    À venir")
    print("")
    ANSWERED = True

# Section 7
elif section == "7":
    print("    À venir")
    print("")
    ANSWERED = True

# Section 8
elif section == "8":
    print("    À venir")
    print("")
    ANSWERED = True

# Section 9
elif section == "9":
    print("    À venir")
    print("")
    ANSWERED = True

# Section 10
elif section == "10":
    print("    À venir")
    print("")
    ANSWERED = True

# Section 11
elif section == "11":
    print("    À venir")
    print("")
    ANSWERED = True

# Section 12
elif section == "12":
    print("    À venir")
    print("")
    ANSWERED = True

if not ANSWERED:
    print("")
    print("!!Entrée non reconnue!!")
    print("    Entrez un chiffre correspondant à l'un des éléments")
    print("    de la liste ci-haut pour effectuer la sélection.")
    print("")
