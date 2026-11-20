#!/usr/bin/env python3
"""
Farcical Clones - Crib Dragging
Slide common words through the XOR result
"""

cipher1 = [95, 181, 145, 39, 245, 91, 212, 232, 123, 220, 167, 69, 91, 208, 245, 164, 245, 145, 123, 94]
flag_nums = [131, 91, 90, 53, 95, 218, 238, 211, 91, 4, 201, 182, 135, 245, 167, 74, 90, 145, 96, 238]

xor_result = bytes([cipher1[i] ^ flag_nums[i] for i in range(len(cipher1))])

print("="*70)
print("FARCICAL CLONES - CRIB DRAGGING")
print("="*70)

# Common words to try
cribs = [
    b"CIT{",
    b"the ",
    b"and ",
    b"for ",
    b"with",
    b"that",
    b"this",
    b"from",
    b"have",
    b"been",
    b"were",
    b"will",
    b"your",
    b"more",
    b"when",
    b"time",
    b"very",
    b"just",
    b"know",
    b"take",
    b"them",
    b"some",
    b"could",
    b"other",
    b"these",
    b"would",
    b"first",
    b"their",
    b"which",
    b"about",
    b"after",
    b"force",
    b"clone",
    b"jedi",
    b"sith",
    b"yoda",
    b"luke",
    b"vader",
    b"star",
    b"wars",
    b"may",
    b"use",
]

print("[1] Sliding cribs through XOR result:\n")

for crib in cribs:
    for offset in range(len(xor_result) - len(crib) + 1):
        # XOR the crib with the XOR result at this offset
        recovered = bytes([xor_result[offset + i] ^ crib[i] for i in range(len(crib))])
        
        # Check if recovered text is printable
        if all(32 <= b < 127 for b in recovered):
            print(f"Offset {offset:2d}, crib '{crib.decode()}': recovered '{recovered.decode()}'")

print("\n" + "="*70)
print("[2] Trying 'CIT{' at position 0 for flag:")
crib = b"CIT{"
recovered_cipher1 = bytes([xor_result[i] ^ crib[i] for i in range(len(crib))])
print(f"  Cipher1[0:4] would be: {recovered_cipher1.hex()} = {recovered_cipher1}")

print("\n[3] Trying common starts for Cipher1:")
cipher1_starts = [b"May ", b"The ", b"Use ", b"I am", b"Do o", b"Fear", b"In a", b"A lo", b"Once", b"Wars", b"Try ", b"You "]

for start in cipher1_starts:
    recovered_flag = bytes([xor_result[i] ^ start[i] for i in range(len(start))])
    if all(32 <= b < 127 for b in recovered_flag):
        print(f"  Cipher1 starts with '{start.decode()}' -> Flag starts with '{recovered_flag.decode()}'")

print("\n" + "="*70)
