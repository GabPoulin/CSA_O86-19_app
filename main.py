# test
import general_design

kd = general_design.load_duration("continue", 1.5, 0.5)
print(f"Kd = {kd}")

b, d, phi, kh, kfi = general_design.FireResistance(
    30, 140, 350, product="sciage"
).effective_section()
print(f"b = {b}")
print(f"d = {d}")
print(f"phi = {phi}")
print(f"Kh = {kh}")
print(f"Kfi = {kfi}")
