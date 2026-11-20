#!/usr/bin/env python3
"""
Farcical Clones - Analyze the derived key
Key = Flag XOR Cipher1
"""

cipher1 = [95, 181, 145, 39, 245, 91, 212, 232, 123, 220, 167, 69, 91, 208, 245, 164, 245, 145, 123, 94]
cipher2 = [62, 150, 94, 172, 83, 135, 96, 153, 2, 208, 96, 172]
flag_nums = [131, 91, 90, 53, 95, 218, 238, 211, 91, 4, 201, 182, 135, 245, 167, 74, 90, 145, 96, 238]

print("="*70)
print("FARCICAL CLONES - KEY ANALYSIS")
print("="*70)

# Derive the key
key = [flag_nums[i] ^ cipher1[i] for i in range(len(flag_nums))]
print(f"Key (Flag XOR Cipher1): {key}")
print(f"Key as hex: {' '.join(f'{b:02x}' for b in key)}")
print()

# Position 17 is 0x00 - both plaintexts have same char
print(f"Position 17: key=0x00, meaning cipher1[17]=flag[17]={cipher1[17]}=0x{cipher1[17]:02x}")
print(f"  As ASCII: '{chr(cipher1[17]) if 32 <= cipher1[17] < 127 else f'\\x{cipher1[17]:02x}'}'")
print()

# Position 8 is 0x20 (space)
print(f"Position 8: key=0x20 (space)")
print(f"  This means one plaintext has space, other has the XOR result")
print()

# Now XOR this key with cipher2
print("[1] Key XOR Cipher2 (repeating):")
decoded = bytes([key[i] ^ cipher2[i % len(cipher2)] for i in range(len(key))])
print(f"  Result: {decoded}")
print(f"  Hex: {decoded.hex()}")

# Check if printable
printable_count = sum(1 for b in decoded if 32 <= b < 127)
print(f"  Printable: {printable_count}/{len(decoded)}")

if printable_count >= 15:
    try:
        text = ''.join(chr(b) if 32 <= b < 127 else f'[{b:02x}]' for b in decoded)
        print(f"  Text: {text}")
    except:
        pass

# Maybe the key itself is the plaintext of cipher1?
# And flag is encrypted with a different key?
print("\n[2] What if Key is the plaintext of Cipher1?")
print(f"  Then Cipher1 = Key XOR OTP_key")
print(f"  And Flag = ? XOR OTP_key")
print(f"  We need to find what Flag decrypts to")
print()

# Try: if cipher1_plaintext = key, and cipher1 = key XOR otp
# then otp = cipher1 XOR key = cipher1 XOR (flag XOR cipher1) = flag
print("  OTP = Cipher1 XOR Key = Cipher1 XOR (Flag XOR Cipher1) = Flag")
print("  This is circular - not helpful")
print()

# Let's try a different approach
# What if cipher2 is actually the OTP key (or part of it)?
print("[3] If Cipher2 is the OTP key:")
print(f"  Cipher1 XOR Cipher2 = {bytes([cipher1[i] ^ cipher2[i % len(cipher2)] for i in range(len(cipher1))])}")
print(f"  Flag XOR Cipher2 = {bytes([flag_nums[i] ^ cipher2[i % len(cipher2)] for i in range(len(flag_nums))])}")
print()

# Check the key for patterns
print("[4] Analyzing key patterns:")
print(f"  Key bytes: {key}")
print(f"  Unique bytes: {len(set(key))}")
print(f"  Most common: {max(set(key), key=key.count)} (appears {key.count(max(set(key), key=key.count))} times)")

# Check if key has readable parts
print("\n[5] Key as ASCII (where printable):")
key_ascii = ''.join(chr(b) if 32 <= b < 127 else f'[{b:02x}]' for b in key)
print(f"  {key_ascii}")

# The key is: dc ee cb 12 aa 81 3a 3b 20 d8 6e f3 dc 25 52 ee af 00 1b b0
# Positions with printable ASCII: 6(':'), 7(';'), 8(' '), 10('n'), 13('%'), 14('R'), 17(0x00)

print("\n[6] Printable positions in key:")
for i, b in enumerate(key):
    if 32 <= b < 127:
        print(f"  Position {i:2d}: 0x{b:02x} = '{chr(b)}'")

# Maybe we need to look at this as a crib-dragging problem
# We know position 8 has space in one message
# We know position 17 has same character in both

print("\n[7] Crib dragging analysis:")
print("  Position 8: One message has space")
print("  Position 17: Both messages have 0x91")
print()
print("  If we assume Flag plaintext is 'CIT{...}':")
print("  Position 0: C (0x43) -> Cipher1_plaintext = 0xdc ^ 0x43 = 0x9f")
print("  Position 1: I (0x49) -> Cipher1_plaintext = 0xee ^ 0x49 = 0xa7")
print("  Position 2: T (0x54) -> Cipher1_plaintext = 0xcb ^ 0x54 = 0x9f")
print("  Position 3: { (0x7b) -> Cipher1_plaintext = 0x12 ^ 0x7b = 0x69 = 'i'")
print()
print("  So Cipher1 might start with: [0x9f][0xa7][0x9f]i...")

print("\n" + "="*70)
