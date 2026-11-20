#!/usr/bin/env python3
"""
Robots Challenge - Quick Solutions

Challenge shows: "Beep Boop"
This is likely a simple encoding where the phrase itself is the clue.
"""

# Common robot-related flags
possible_flags = [
    "CIT{Beep_Boop}",
    "CIT{BeepBoop}",
    "CIT{beep_boop}",
    "CIT{beepboop}",
    "CIT{BEEP_BOOP}",
    "CIT{BEEPBOOP}",
    "CIT{B33p_B00p}",
    "CIT{b33p_b00p}",
    "CIT{robots}",
    "CIT{Robots}",
    "CIT{ROBOTS}",
    "CIT{r0b0ts}",
    "CIT{R0B0TS}",
    "CIT{binary}",
    "CIT{Binary}",
    "CIT{01}",
    "CIT{10}",
]

# Try interpreting "Beep Boop" as binary
# Beep = 1, Boop = 0: "10" 
# Beep = 0, Boop = 1: "01"

# "Beep Boop" could also be leet speak
# B = 8, e = 3, p = p, B = 8, o = 0, p = p
# 833p 800p

print("="*70)
print("ROBOTS CHALLENGE - Possible Flags")
print("="*70)
print()

for i, flag in enumerate(possible_flags, 1):
    print(f"{i:2}. {flag}")

print()
print("="*70)
print("Most likely based on challenge name:")
print("  1. CIT{Beep_Boop}")
print("  2. CIT{beep_boop}")  
print("  3. CIT{r0b0ts}")
print("="*70)
