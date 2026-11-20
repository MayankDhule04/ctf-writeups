#!/usr/bin/env python3
"""
Farcical Clones - Final Crack
Using known positions to recover the plaintexts
"""

cipher1 = [95, 181, 145, 39, 245, 91, 212, 232, 123, 220, 167, 69, 91, 208, 245, 164, 245, 145, 123, 94]
flag_nums = [131, 91, 90, 53, 95, 218, 238, 211, 91, 4, 201, 182, 135, 245, 167, 74, 90, 145, 96, 238]

xor_result = [cipher1[i] ^ flag_nums[i] for i in range(len(cipher1))]

print("="*70)
print("FARCICAL CLONES - FINAL CRACK")
print("="*70)

# We know:
# - Position 8: one has space (0x20)
# - Position 17: both have same character (0x91)
# - Flag likely starts with "CIT{"

# Let's assume flag starts with "CIT{" and see what we get
known_flag = ['?'] * 20
known_cipher1 = ['?'] * 20

# Assume flag starts with "CIT{"
known_flag[0] = 'C'
known_flag[1] = 'I'
known_flag[2] = 'T'
known_flag[3] = '{'

# Recover cipher1 for these positions
for i in range(4):
    known_cipher1[i] = chr(xor_result[i] ^ ord(known_flag[i]))

print("[1] Starting with flag='CIT{':")
print(f"  Cipher1 positions 0-3: {known_cipher1[:4]}")
print()

# Position 8 has space - let's try both possibilities
print("[2] Position 8 analysis (space in one plaintext):")
print(f"  If cipher1[8] = ' ': flag[8] = '{chr(xor_result[8] ^ ord(' '))}'")
print(f"  If flag[8] = ' ': cipher1[8] = '{chr(xor_result[8] ^ ord(' '))}'")
print()

# Let's try: cipher1 = "May the Force..." (has space at position 3, 7)
# Or flag has space at position 8
# If flag[8] = ' ', then cipher1[8] = chr(32 ^ 32) = chr(0) - no
# So cipher1[8] must be ' '

known_cipher1[8] = ' '
known_flag[8] = chr(xor_result[8] ^ ord(' '))

print(f"  Assuming cipher1[8] = ' ': flag[8] = '{known_flag[8]}'")
print()

# Position 17: both are 0x91 (145)
known_cipher1[17] = chr(145)
known_flag[17] = chr(145)
print(f"[3] Position 17: both = '{chr(145)}' (0x91)")
print()

# Now let's try to guess more of cipher1
# "May the Force be with you" is 25 chars, we have 20
# "May the Force be wit" = 20 chars!

test_cipher1 = "May the Force be wit"
print(f"[4] Testing cipher1 = '{test_cipher1}':")
recovered_flag = ''.join(chr(xor_result[i] ^ ord(test_cipher1[i])) for i in range(len(test_cipher1)))
print(f"  Recovered flag: {recovered_flag}")
print(f"  As hex: {' '.join(f'{ord(c):02x}' for c in recovered_flag)}")
print()

# Check if it's printable
if all(32 <= ord(c) < 127 for c in recovered_flag):
    print(f"  ✓ All printable ASCII!")
    print(f"  FLAG: CIT{{{recovered_flag[4:]}}}")  # Remove "CIT{" prefix if it's there
    print()

# Try other variations
variations = [
    "May the force be wit",  # lowercase
    "May The Force Be Wit",  # Title case
    "may the force be wit",  # all lowercase
]

print("[5] Trying variations:")
for var in variations:
    recovered = ''.join(chr(xor_result[i] ^ ord(var[i])) for i in range(len(var)))
    if all(32 <= ord(c) < 127 for c in recovered):
        print(f"  Cipher1='{var}' -> Flag='{recovered}'")

# Try assuming the flag is something specific
print("\n[6] Reverse: trying flag patterns:")
flag_tests = [
    "CIT{the_clones_war}",  # 19 chars
    "CIT{attack_of_clone",  # 20 chars
    "CIT{clone_wars_rule",  # 20 chars
]

for flag_test in flag_tests:
    if len(flag_test) == 20:
        recovered = ''.join(chr(xor_result[i] ^ ord(flag_test[i])) for i in range(len(flag_test)))
        if all(32 <= ord(c) < 127 for c in recovered):
            print(f"  Flag='{flag_test}' -> Cipher1='{recovered}'")

print("\n" + "="*70)
