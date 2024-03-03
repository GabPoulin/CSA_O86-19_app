"""Permet d'utiliser la CSA O86:19 dans le terminal."""

import general_design
import sawn_lumber

# Validation for correct inputs
ANSWERED = False

# Initial prompts
print("")
print("CSA O86:19: Règles de calcul des charpentes en bois")
print("    5  - Conception générale")
print("    6  - Bois de sciage")
print("    7  - Bois lamellé-collé")
print("    8  - Bois lamellé-croisé")
print("    9  - Panneaux structuraux")
print("    10 - Éléments de charpente composites")
print("    11 - Structures résistantes aux charges latérales")
print("    12 - Assemblages")
print("    13 - Ouvrages en pilots de bois")
print("    14 - Ouvrages en poteaux")
print("    15 - Produits propriétaires en bois de charpente - Calcul")
print("    16 - Produits propriétaires en bois de charpente - Matériaux et évaluation")
print("")
SECTION = input("Section: ")

# Section 5
if SECTION == "5":
    print("    5.1 - Calculs aux états limites")
    print("    5.3 - Conditions et coefficients influant sur la résistance")
    print("    5.4 - Exigences relatives à la tenue en service")
    print("    5.5 - Effort de contreventement latéral sur les membrures")
    print("          d'âme en compression des fermes de toit en bois")
    print("    5.6 - Résistance au feu")
    print("")
    SOUS_SECTION = input("Sous-section: 5.")

    # Sous-section 5.1
    if SOUS_SECTION == "1":
        LOAD = input("\tCharge pondérée ou charge spécifiée = ")
        RESISTANCE = input("\tRésistance correspondante = ")
        message = general_design.limit_states_design(float(LOAD), float(RESISTANCE))

        print(f"\t{message}")
        print("")
        ANSWERED = True

    # Sous-section 5.3
    if SOUS_SECTION == "3":
        print("    5.3.2 - Coefficient de durée d’application de la charge, Kd")
        print("    5.3.8 - Validation de la section transversale")
        print("")
        CLAUSE = input("Clause: 5.3.")

        # Clause 5.3.2
        if CLAUSE == "2":
            DURATION = input(
                "\tDurée d'application de la charge (courte:'s', normale:'n' ou continue:'c') = "
            )
            if DURATION == "s":
                DURATION = "courte"
            elif DURATION == "n":
                DURATION = "normale"
            elif DURATION == "c":
                DURATION = "continue"
            kd = general_design.load_duration(DURATION)

            if DURATION == "continue":
                DEAD = input(
                    "\tCharge de durée d'application continue (Defaults to 0) = "
                )
                if DEAD == "":
                    DEAD = 0
                LIVE = input(
                    "\tSurcharge de durée d'application normale (Defaults to 0) = "
                )
                if LIVE == "":
                    LIVE = 0
                SNOW = input("\tSurcharge de neige (Defaults to 0) = ")
                if SNOW == "":
                    SNOW = 0
                kd = general_design.load_duration(
                    DURATION, float(DEAD), float(LIVE), float(SNOW)
                )

            print(f"\tKd = {kd}")
            print("")
            ANSWERED = True

        # Clause 5.3.8
        elif CLAUSE == "8":
            GROSS = input("\tSection brute = ")
            NET = input("\tSection nette = ")
            message = general_design.cross_section(float(NET), float(GROSS))

            print(f"\t{message}")
            print("")
            ANSWERED = True

    # Sous-section 5.4
    elif SOUS_SECTION == "4":
        print("    5.4.1 - Module d'élasticité")
        print("    5.4.2 - Flèche élastique")
        print("    5.4.3 - Déformation permanente")
        print("    5.4.4 - Accumulation d'eau")
        print("    5.4.5 - Vibration")
        print("    5.4.6 - Mouvements du bâtiment attribuables au")
        print("            changement de la teneur en humidité")
        print("")
        CLAUSE = input("Clause: 5.4.")

        # Clause 5.4.1
        if CLAUSE == "1":
            MODULUS = input("\tModule d'élasticité prévu, MPa = ")
            SERVICE = input("\tCoefficient de conditions d'utilisation = ")
            TREATEMENT = input("\tCoefficient de traitement = ")
            es = general_design.elasticity(
                float(MODULUS), float(SERVICE), float(TREATEMENT)
            )

            print(f"\tEs = {es} MPa")
            print("")
            ANSWERED = True

        # Clause 5.4.2
        elif CLAUSE == "2":
            message = general_design.elastic_deflection
            print("")
            ANSWERED = True

        # Clause 5.4.3
        elif CLAUSE == "3":
            message = general_design.permanent_deformation
            print("")
            ANSWERED = True

        # Clause 5.4.4
        elif CLAUSE == "4":
            message = general_design.ponding
            print("")
            ANSWERED = True

        # Clause 5.4.5
        elif CLAUSE == "5":
            message = general_design.Vibration.floor_vibration
            print("")
            ANSWERED = True

        # Clause 5.4.6
        elif CLAUSE == "6":
            s = general_design.moisture
            print("")
            ANSWERED = True

    # Branch to 5.5
    elif SOUS_SECTION == "5":
        load = general_design.lateral_brace
        print("")
        ANSWERED = True

    # Branch to 5.6
    elif SOUS_SECTION == "6":
        # b, d, phi, kh, kfi = general_design.FireResistance.effective_section
        print("")
        ANSWERED = True

# Section 6
elif SECTION == "6":
    print("    6.2 - Matériaux")
    print("    6.3 - Résistances prévues et modules d'élasticité")
    print("    6.4 - Coefficients de correction")
    print("    6.5 - Calcul des résistances")
    print("    6.6 - États limites de tenue en service")
    print("")
    SOUS_SECTION = input("Sous-section: 6.")
    print("    À venir")
    print("")
    ANSWERED = True

# Section 7
elif SECTION == "7":
    print("    À venir")
    print("")
    ANSWERED = True

# Section 8
elif SECTION == "8":
    print("    À venir")
    print("")
    ANSWERED = True

# Section 9
elif SECTION == "9":
    print("    À venir")
    print("")
    ANSWERED = True

# Section 10
elif SECTION == "10":
    print("    À venir")
    print("")
    ANSWERED = True

# Section 11
elif SECTION == "11":
    print("    À venir")
    print("")
    ANSWERED = True

# Section 12
elif SECTION == "12":
    print("    À venir")
    print("")
    ANSWERED = True

# Section 13
elif SECTION == "13":
    print("    À venir")
    print("")
    ANSWERED = True

# Section 14
elif SECTION == "14":
    print("    À venir")
    print("")
    ANSWERED = True

# Section 15
elif SECTION == "15":
    print("    À venir")
    print("")
    ANSWERED = True

# Section 16
elif SECTION == "16":
    print("    À venir")
    print("")
    ANSWERED = True

if not ANSWERED:
    raise ValueError("Entrez un chiffre correspondant à l'un des éléments de la liste")
