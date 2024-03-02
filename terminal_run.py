"""Permet d'utiliser la CSA O86:19 dans le terminal."""

import general_design

# Initial prompts
print("\t5.3.2 Kd.")
print("\t5.3.8 Validation de la section transversale.")
print("\t5.4.1 Es.")
print("\t5.4.2 Flèche.")
print("\t5.4.4 Accumulation d'eau.")
print("\t5.4.5 Vibration.")
print("\t5.4.6 Changement d'humidité.")
print("\t5.5 Effort latéral sur membrures d'âme des fermes de toit en bois.")
print("\t5.6 Résistance au feu.")

choice = input("\n: ")

# Branch to 5.3.2
if choice == "5.3.2":
    duration = input("Durée. 'courte', 'normale' ou 'continue'.: ")
    kd = general_design.load_duration(duration)

    if duration == "continue":
        dead = input("Charge de durée d'application continue. Defaults to 0.: ")
        live = input("Surcharge de durée d'application normale. Defaults to 0.: ")
        snow = input("Surcharge de neige. Defaults to 0.: ")
        kd = general_design.load_duration(
            duration, float(dead), float(live), float(snow)
        )

    print(f"\tKd = {kd}")

# Branch to 5.3.8
elif choice == "5.3.8":
    message = general_design.cross_section

# Branch to 5.4.1
elif choice == "5.3.8":
    es = general_design.elasticity

# Branch to 5.4.2
elif choice == "5.3.8":
    message = general_design.deflection

# Branch to 5.4.4
elif choice == "5.3.8":
    message = general_design.ponding

# Branch to 5.4.5
elif choice == "5.3.8":
    message = general_design.Vibration.floor_vibration

# Branch to 5.4.6
elif choice == "5.3.8":
    s = general_design.moisture

# Branch to 5.5
elif choice == "5.3.8":
    h = general_design.lateral_brace

# Branch to 5.6
elif choice == "5.3.8":
    i = general_design.FireResistance.effective_section

else:
    print("Entrez le numéro de l'article parmi les choix plus haut")
