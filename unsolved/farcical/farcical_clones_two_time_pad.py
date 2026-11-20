#!/usr/bin/env python3
"""
Farcical Clones - Two-Time Pad Attack
If cipher1 and flag are encrypted with the same OTP key, we can XOR them together
to get plaintext1 XOR plaintext2
"""

cipher1 = [95, 181, 145, 39, 245, 91, 212, 232, 123, 220, 167, 69, 91, 208, 245, 164, 245, 145, 123, 94]
flag_nums = [131, 91, 90, 53, 95, 218, 238, 211, 91, 4, 201, 182, 135, 245, 167, 74, 90, 145, 96, 238]

print("="*70)
print("FARCICAL CLONES - TWO-TIME PAD ATTACK")
print("="*70)

# XOR cipher1 with flag to get plaintext1 XOR plaintext2
xor_result = [cipher1[i] ^ flag_nums[i] for i in range(len(cipher1))]
print(f"Cipher1 XOR Flag: {xor_result}")
print(f"As hex: {' '.join(f'{x:02x}' for x in xor_result)}")
print()

# If we know one plaintext, we can recover the other
# The flag format is CIT{...}, so let's assume the flag plaintext starts with "CIT{"

# Try assuming flag starts with "CIT{"
print("[1] Assuming flag plaintext starts with 'CIT{':")
known_flag_start = b"CIT{"
for i, char in enumerate(known_flag_start):
    if i < len(xor_result):
        # plaintext1[i] = xor_result[i] XOR plaintext2[i]
        plaintext1_char = xor_result[i] ^ char
        print(f"  Position {i}: flag='{chr(char)}' -> cipher1_plaintext='{chr(plaintext1_char) if 32 <= plaintext1_char < 127 else f'\\x{plaintext1_char:02x}'}'")

# Let's try to recover the full cipher1 plaintext
print("\n[2] Recovering cipher1 plaintext assuming flag='CIT{...}':")
assumed_flag = "CIT{" + "?"*16  # We know it starts with CIT{

# Try common flag patterns
flag_patterns = [
    "CIT{clones_are_cool}",
    "CIT{may_the_force}",
    "CIT{star_wars}",
    "CIT{farcical_clones}",
    "CIT{bootstrap}",
    "CIT{padawan}",
]

for pattern in flag_patterns:
    if len(pattern) == len(xor_result):
        recovered = ''.join(chr(xor_result[i] ^ ord(pattern[i])) if xor_result[i] ^ ord(pattern[i]) < 256 else '?' for i in range(len(pattern)))
        print(f"  Flag='{pattern}' -> Cipher1='{recovered}'")

# Try the reverse - assume cipher1 is readable text
print("\n[3] Trying common cipher1 plaintexts:")
cipher1_patterns = [
    "May the Force be wit",  # 20 chars
    "Young padawan learns",
    "The clones attack no",
    "Bootstrap the system",
]

for pattern in cipher1_patterns:
    if len(pattern) == len(xor_result):
        recovered = ''.join(chr(xor_result[i] ^ ord(pattern[i])) if xor_result[i] ^ ord(pattern[i]) < 256 else '?' for i in range(len(pattern)))
        print(f"  Cipher1='{pattern}' -> Flag='{recovered}'")

# Analyze the XOR result for patterns
print("\n[4] Analyzing XOR result patterns:")
print(f"  Byte 17 is 0x00 - this means cipher1[17] == flag[17]")
print(f"  Cipher1[17] = {cipher1[17]} = '{chr(cipher1[17])}'")
print(f"  Flag[17] = {flag_nums[17]} = '{chr(flag_nums[17])}'")
print()

# Look for other interesting patterns
print("[5] Looking for space characters (0x20 = 32):")
for i, val in enumerate(xor_result):
    if val == 32:  # Space XOR something
        print(f"  Position {i}: One plaintext has space, other has '{chr(32)}'")
    elif 65 <= val <= 90:  # Uppercase letter
        # Could be space XOR lowercase
        possible = chr(val ^ 32)
        print(f"  Position {i}: Could be space XOR '{possible}' or '{chr(val)}' XOR something")

# Try crib dragging with "CIT{"
print("\n[6] Crib dragging with 'CIT{':")
crib = b"CIT{"
for offset in range(len(xor_result) - len(crib) + 1):
    recovered = []
    for i in range(len(crib)):
        recovered.append(chr(xor_result[offset + i] ^ crib[i]))
    recovered_str = ''.join(recovered)
    if all(32 <= ord(c) < 127 for c in recovered_str):
        print(f"  Offset {offset}: '{recovered_str}'")

print("\n" + "="*70)
