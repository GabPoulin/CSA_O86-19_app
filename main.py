# test
import general_design

kd = general_design.load_duration("continue", 1.5, 0.5)
print(f"{kd = }")
print("")

b, d, phi, kh, kfi = general_design.FireResistance(
    duration=30,
    width=140,
    depth=350,
    product="sciage",
).effective_section()
print(f"{b = }")
print(f"{d = }")
print(f"{phi = }")
print(f"{kh = }")
print(f"{kfi = }")
print("")
