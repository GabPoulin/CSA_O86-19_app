"""Permet d'utiliser la CSA O86:19 dans le terminal."""

import general_design
import sawn_lumber

# Validation for correct inputs
ANSWERED = False

# Initial prompts
print("")
print("CSA O86:19: Règles de calcul des charpentes en bois")
print("    5  Conception générale")
print("    6  Bois de sciage")
print("    7  Bois lamellé-collé")
print("    8  Bois lamellé-croisé")
print("    9  Panneaux structuraux")
print("    10 Éléments de charpente composites")
print("    11 Structures résistantes aux charges latérales")
print("    12 Assemblages")
print("    13 Ouvrages en pilots de bois")
print("    14 Ouvrages en poteaux")
print("    15 Produits propriétaires en bois de charpente - Calcul")
print("    16 Produits propriétaires en bois de charpente - Matériaux et évaluation")
print("")
SECTION = input("Section: ")

# Section 5
if SECTION == "5":
    print("    5.1 Calculs aux états limites")
    print("    5.3 Conditions et coefficients influant sur la résistance")
    print("    5.4 Exigences relatives à la tenue en service")
    print("    5.5 Effort de contreventement latéral sur les membrures")
    print("        d'âme en compression des fermes de toit en bois")
    print("    5.6 Résistance au feu")
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
    elif SOUS_SECTION == "3":
        print("    5.3.2 Coefficient de durée d'application de la charge, Kd")
        print("    5.3.8 Validation de la section transversale")
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
        print("    5.4.1 Module d'élasticité")
        print("    5.4.2 Flèche élastique")
        print("    5.4.3 Déformation permanente")
        print("    5.4.4 Accumulation d'eau")
        print("    5.4.5 Vibration")
        print("    5.4.6 Mouvements du bâtiment attribuables au")
        print("          changement de la teneur en humidité")
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
            SPAN = input("\tPortée, mm = ")
            DELTA = input("\tFlèche, mm = ")
            message = general_design.elastic_deflection(float(SPAN), float(DELTA))

            print(f"\t{message}")
            print("")
            ANSWERED = True

        # Clause 5.4.3
        elif CLAUSE == "3":
            SPAN = input("\tPortée, mm = ")
            DELTA = input("\tFlèche, mm = ")
            message = general_design.permanent_deformation(float(SPAN), float(DELTA))

            print(f"\t{message}")
            print("")
            ANSWERED = True

        # Clause 5.4.4
        elif CLAUSE == "4":
            LOAD = input("\tCharge totale spécifiée uniformément répartie, kPa = ")
            DELTA = input("\tFlèche totale du système, mm = ")
            message = general_design.ponding(float(LOAD), float(DELTA))

            print(f"\t{message}")
            print("")
            ANSWERED = True

        # Clause 5.4.5
        elif CLAUSE == "5":
            SPAN = input("\tPortée du plancher, m = ")
            MULTI_SPAN = input("\tPortée multiple? (y/n) = ") == "y"
            CLT_FLOOR = input("\tPlancher en CLT? (y/n) = ") == "y"

            CLT_MASS = 0
            EI_EFF = 0
            TOP_THICK = 0
            J_DEPTH = 0
            J_MASS = 0
            J_SPACING = 0.4064
            EA_J = 0
            EI_J = 0
            BRACE = False
            GYPSE = False
            SUBFLOOR = "CSP 5/8"
            GLUE = False

            if CLT_FLOOR:
                CLT_MASS = input("\tMasse linéaire du clt, kg/m = ")
                EI_EFF = input("\t(EI)eff,f, N*mm2 (voir 8.4.3.2) = ")
                TOPPING = input("\tRevêtement. 'béton' ou 'aucun/autre' = ")
                if TOPPING == "béton":
                    TOP_THICK = input("\tÉpaisseur du revêtement, m = ")
            else:
                J_SPACING = input("\tEspacement des solives, m = ")
                J_DEPTH = input("\tHauteur de solive, m = ")
                J_MASS = input("\tMasse par unité de longueur de solive, kg/m = ")
                EI_J = input("\tEIjoist, N*m2 = ")
                EA_J = input("\tEAjoist, N = ")
                BRACE = input("\tContreventement latéraux? (y/n) = ") == "y"
                GYPSE = input("\tPanneau de gypse sous les solives? (y/n) = ") == "y"
                print("\tSous-plancher. Choisir parmi la liste:")
                print(
                    """
        'OSB 1/2'       'DFP 1/2'        'CSP 1/2'
        'OSB 5/8'       'DFP 5/8'        'CSP 5/8'
        'OSB 3/4'       'DFP 3/4'        'CSP 3/4'
                        'DFP 13/16'      'CSP 13/16'
        'OSB 7/8'       'DFP 7/8'        'CSP 7/8'
                        'DFP 1'          'CSP 1'
        'OSB 1-1/8'     'DFP 1-1/8'      'CSP 1-1/8'
                        'DFP 1-1/4'      'CSP 1-1/4'
                        """
                )
                SUBFLOOR = input("\tSous-plancher = ")
                GLUE = input("\tSous-plancher collé? (y/n) = ") == "y"
                TOPPING = input(
                    "\tRevêtement. 'béton', 'aucun/autre' ou selon la liste de sous-planchers = "
                )
                if TOPPING == "béton":
                    TOP_THICK = input("\tÉpaisseur du revêtement, m = ")
            message = general_design.Vibration(
                float(SPAN),
                BRACE,
                float(EI_EFF),
                float(CLT_MASS),
                GLUE,
                GYPSE,
                float(EA_J),
                float(EI_J),
                float(J_DEPTH),
                float(J_MASS),
                float(J_SPACING),
                MULTI_SPAN,
                SUBFLOOR,
                TOPPING,
                float(TOP_THICK),
            ).floor_vibration()

            print(f"\t{message}")
            print("")
            ANSWERED = True

        # Clause 5.4.6
        elif CLAUSE == "6":
            DIM = input("\tDimension réelle, mm = ")
            MI = input("\tTeneur en humidité initiale, % = ")
            MF = input("\tTeneur en humidité finale, % = ")
            DIR = input("\tDirection du fil du bois ('perp', 'para' ou 'autre') = ")
            if DIR not in ("perp", "para"):
                COEFF = input("\tCoefficient de retrait = ")
            else:
                COEFF = 0
            s = general_design.moisture(
                float(DIM), float(MI), float(MF), DIR, float(COEFF)
            )

            if s >= 0:
                print(f"\tRetrait de la dimension considérée = {s} mm")
            else:
                print(f"\tGonflement de la dimension considérée = {-s} mm")
            print("")
            ANSWERED = True

    # Branch to 5.5
    elif SOUS_SECTION == "5":
        FORCE = input("\tForce, kN = ")
        load = general_design.lateral_brace(float(FORCE))

        print(f"\tEffort applicable au contreventement latéral = {load} kN")
        print("")
        ANSWERED = True

    # Branch to 5.6
    elif SOUS_SECTION == "6":
        DUR = input("\tDurée d'exposition au feu, min = ")
        WIDTH = input("\tLargeur de l'élément, mm = ")
        DEPTH = input("\tHauteur de l'élément, mm = ")
        SIDES = input(
            "\tProtection des faces larges (aucune:'0', 1_face:'1' ou 2_faces:'2') = "
        )
        if SIDES == "1":
            SIDES = "1_face"
        elif SIDES == "2":
            SIDES = "2_faces"
        else:
            SIDES = "aucune"
        TOP = input(
            "\tProtection des faces étroites (aucune:'0', 1_face:'1' ou 2_faces:'2') = "
        )
        if TOP == "1":
            TOP = "1_face"
        elif TOP == "2":
            TOP = "2_faces"
        else:
            TOP = "aucune"
        PROD = input(
            "\tProduit (autre:'0', sciage:'1', glt:'2', clt_v1_v2:'3' ou clt_e1_e2_e3:'4') = "
        )
        if PROD == "1":
            PROD = "sciage"
        elif PROD == "2":
            PROD = "glt"
        elif PROD == "3":
            PROD = "clt_v1_v2"
        elif PROD == "4":
            PROD = "clt_e1_e2_e3"
        else:
            PROD = "autre"
        b, d, phi, kh, kfi = general_design.FireResistance(
            float(DUR), float(WIDTH), float(DEPTH), SIDES, TOP, PROD
        ).effective_section()

        print(f"{b = } mm")
        print(f"{d = } mm")
        print(f"φ = {phi}")
        print(f"Kh = {kh}")
        print(f"Kfi = {kfi}")
        print("")
        ANSWERED = True

# Section 6
elif SECTION == "6":
    print("    6.2 Matériaux")
    print("    6.3 Résistances prévues et modules d'élasticité")
    print("    6.4 Coefficients de correction")
    print("    6.5 Calcul des résistances")
    print("    6.6 États limites de tenue en service")
    print("")
    SOUS_SECTION = input("Sous-section: 6.")

    # Sous-section 6.2
    if SOUS_SECTION == "2":
        WIDTH = input("\tLargeur de l'élément, mm = ")
        DEPTH = input("\tHauteur de l'élément, mm = ")
        MSR = input("\tBois MSR? (y/n) = ") == "y"
        MEL = input("\tBois MEL? (y/n) = ") == "y"
        message = sawn_lumber.lumber_category(int(WIDTH), int(DEPTH), MSR, MEL)

        print(f"\tCatégorie de bois d'oeuvre = {message}")
        print("")
        ANSWERED = True

    # Sous-section 6.3
    elif SOUS_SECTION == "3":
        SIDE = False
        CATEGORY = input(
            "\tCatégorie. ('Lumber', 'Light', 'Beam', 'Post', 'MSR' ou 'MEL') = "
        )
        if CATEGORY in ("MSR", "MEL"):
            SPECIE = input("\tGroupe. ('normal', 'courant' ou 'rare') = ")
            if CATEGORY == "MSR":
                GRADE = input(
                    "\tClasse. voir tableau 6.8. (ex: 1200Fb-1.2E = '1200-1.2') = "
                )
            else:
                GRADE = input("\tClasse. voir tableau 6.9. (ex: M-10 = 'm-10') = ")
        else:
            SPECIE = input("\tGroupe d'essence. ('df', 'hf', 'spf' ou 'ns') = ")
            if CATEGORY == "Lumber":
                GRADE = input("\tClasse. ('ss', 'n1-n2' ou 'n3-stud') = ")
            elif CATEGORY == "Light":
                GRADE = input("\tClasse. ('cst' ou 'std') = ")
            else:
                GRADE = input("\tClasse. ('ss', 'n1' ou 'n2') = ")
            if CATEGORY == "Beam":
                SIDE = input("\tCharges appliquées sur la grande face? (y/n) = ") == "y"
        fb, fv, fc, fcp, ft, e, e05 = sawn_lumber.specified_strengths(
            CATEGORY, SPECIE, GRADE, SIDE
        )

        print(f"\tfb  = {fb} MPa")
        print(f"\tfv  = {fv} MPa")
        print(f"\tfc  = {fc} MPa")
        print(f"\tfcp = {fcp} MPa")
        print(f"\tft  = {ft} MPa")
        print(f"\tE   = {e} MPa")
        print(f"\tE05 = {e05} MPa")
        print("")
        ANSWERED = True

    # Sous-section 6.4
    elif SOUS_SECTION == "4":
        WID = input("\tLargeur de l'élément, mm = ")
        DEP = input("\tHauteur de l'élément, mm = ")
        print("\tPropriété évaluée.")
        PRO = input(
            "\t('flex', 'cis_f', 'cis_l', 'comp_para', 'comp_perp', 'trac' ou 'moe') = "
        )
        DUR = input(
            "\tDurée d'application de la charge. ('courte', 'normale' ou 'continue') = "
        )
        MSR = input("\tBois MSR? (y/n) = ") == "y"
        MEL = input("\tBois MEL? (y/n) = ") == "y"
        CAT = sawn_lumber.lumber_category(float(WID), float(DEP), MSR, MEL)
        WET = input("\tUtilisation en milieu humide. (y/n) = ") == "y"
        TRE = input("\tBois traité. (y/n) = ") == "y"
        if TRE:
            INC = input("\tBois incisé. (y/n) = ") == "y"
        else:
            INC = False
        SPA = input("\tL'espacement ne dépasse pas 610 mm. (y/n) = ") == "y"
        if SPA:
            CON = input("\tSous-plancher fixé. (y/n) = ") == "y"
        else:
            CON = False
        BUI = input("\tPoutres composées. (y/n) = ") == "y"
        kd, ks, kt, kh, kz = sawn_lumber.modification_factors(
            float(WID), float(DEP), PRO, DUR, CAT, WET, TRE, INC, SPA, CON, BUI
        )

        print(f"\tKd = {kd}")
        print(f"\tKs = {ks}")
        print(f"\tKt = {kt}")
        print(f"\tKh = {kh}")
        print(f"\tKz = {kz}")
        print("")
        ANSWERED = True

    # Sous-section 6.5
    elif SOUS_SECTION == "5":
        print("    6.5.2 Dimensions")
        print("    6.5.3 Résistance au moment de flexion")
        print("    6.5.4 Résistance au cisaillement")
        print("    6.5.5 Résistance à la compression parallèle au fil")
        print("    6.5.6 Résistance à la compression perpendiculaire au fil")
        print("    6.5.7 Résistance à la compression oblique par rapport au fil")
        print("    6.5.8 Résistance à la traction parallèle au fil")
        print("    6.5.9 Résistance à la flexion et à la charge axiale combinées")
        print("    6.5.10 Platelage")
        print("    6.5.11 Fondations permanentes en bois")
        print("    6.5.12 Applications propres aux fermes")
        print("")
        CLAUSE = input("Clause: 6.5.")

        # Clause 6.5.2
        if CLAUSE == "2":
            DIM = input("\tDimmension nominale, po = ")
            TH = input("\tBois vert (teneur en humidité > 19%). (y/n) = ") == "y"
            BRUT = input("\tDimensions brutes. (y/n) = ") == "y"
            dim_nette = sawn_lumber.Resistances(0, 0).sizes(DIM, TH, BRUT)
            print(f"\tDimension nette = {dim_nette}")
            print("")
            ANSWERED = True

    # Sous-section 6.6
    elif SOUS_SECTION == "6":
        print("    À venir")
        print("")
        ANSWERED = True

# Section 7
elif SECTION == "7":
    print("    Bois lamellé-collé: À venir")
    print("")
    ANSWERED = True

# Section 8
elif SECTION == "8":
    print("    Bois lamellé-croisé: À venir")
    print("")
    ANSWERED = True

# Section 9
elif SECTION == "9":
    print("    Panneaux structuraux: À venir")
    print("")
    ANSWERED = True

# Section 10
elif SECTION == "10":
    print("    Éléments de charpente composites: À venir")
    print("")
    ANSWERED = True

# Section 11
elif SECTION == "11":
    print("    Structures résistantes aux charges latérales: À venir")
    print("")
    ANSWERED = True

# Section 12
elif SECTION == "12":
    print("    Assemblages: À venir")
    print("")
    ANSWERED = True

# Section 13
elif SECTION == "13":
    print("    Ouvrages en pilots de bois: À venir")
    print("")
    ANSWERED = True

# Section 14
elif SECTION == "14":
    print("    Ouvrages en poteaux: À venir")
    print("")
    ANSWERED = True

# Section 15
elif SECTION == "15":
    print("    Produits propriétaires en bois de charpente - Calcul: À venir")
    print("")
    ANSWERED = True

# Section 16
elif SECTION == "16":
    print(
        "    Produits propriétaires en bois de charpente - Matériaux et évaluation: À venir"
    )
    print("")
    ANSWERED = True

if not ANSWERED:
    raise ValueError("Entrez un chiffre correspondant à l'un des éléments de la liste")
