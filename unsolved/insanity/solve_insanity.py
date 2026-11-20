#!/usr/bin/env python3
"""
Insanity Check Challenge Solver
Challenge: "Are you sane enough?"
Author: HXpl0it (Haardik Bhagtani)
Flag Format: Kaal{}
"""

# Common sanity check patterns
possible_flags = [
    # Direct answers
    "Kaal{yes}",
    "Kaal{no}",
    "Kaal{sane}",
    "Kaal{insane}",
    "Kaal{sanity}",
    "Kaal{insanity}",
    
    # Challenge-related
    "Kaal{are_you_sane_enough}",
    "Kaal{sane_enough}",
    "Kaal{not_sane_enough}",
    "Kaal{i_am_sane}",
    "Kaal{i_am_insane}",
    
    # Author-related
    "Kaal{HXpl0it}",
    "Kaal{Haardik}",
    "Kaal{Haardik_Bhagtani}",
    
    # Misc category common flags
    "Kaal{sanity_check}",
    "Kaal{insanity_check}",
    "Kaal{easy_flag}",
    "Kaal{200_points}",
    
    # Leetspeak variations
    "Kaal{s4n3}",
    "Kaal{1ns4n3}",
    "Kaal{s4n1ty}",
    "Kaal{1ns4n1ty}",
    
    # Reverse
    "Kaal{enas}",
    "Kaal{enasni}",
    
    # ROT13
    "Kaal{fnar}",
    "Kaal{vafnar}",
]

print("[*] Insanity Check - Possible Flags:")
print("=" * 60)
for i, flag in enumerate(possible_flags, 1):
    print(f"{i:2d}. {flag}")

print("\n" + "=" * 60)
print("[!] Since there's no URL or file, this is likely a simple")
print("[!] sanity check where the flag is obvious or requires")
print("[!] minimal transformation.")
print("\n[*] Try submitting these flags one by one!")
