#!/usr/bin/env python3
"""
Rotor Rooter - Enigma/Rotor Cipher Challenge
Ciphertext: KLEGCKRGGONTBNBVPIIZVWXQQEZYAXXWQMGIZDNEWWUTOVZRWOMZKGWNKWZBQXOGZSTVCGUFL
Hint: "Spin it till it drains" - rotor cipher
"""

ciphertext = "KLEGCKRGGONTBNBVPIIZVWXQQEZYAXXWQMGIZDNEWWUTOVZRWOMZKGWNKWZBQXOGZSTVCGUFL"

print("="*70)
print("ROTOR ROOTER - CIPHER SOLVER")
print("="*70)
print(f"\nCiphertext: {ciphertext}")
print(f"Length: {len(ciphertext)}")

# Try simple Caesar shifts first
print("\n[*] Trying Caesar shifts:")
for shift in range(1, 26):
    decoded = ''
    for char in ciphertext:
        if char.isalpha():
            if char.isupper():
                decoded += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            else:
                decoded += chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
        else:
            decoded += char
    
    # Check if it looks like English
    if any(word in decoded.lower() for word in ['the', 'and', 'for', 'you', 'that', 'with', 'have', 'this', 'from']):
        print(f"    Shift {shift:2d}: {decoded}")

# Try ROT13
print("\n[*] ROT13:")
rot13 = ciphertext.translate(str.maketrans(
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
    'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'
))
print(f"    {rot13}")

# Try Atbash
print("\n[*] Atbash:")
atbash = ''
for char in ciphertext:
    if char.isupper():
        atbash += chr(ord('Z') - (ord(char) - ord('A')))
    elif char.islower():
        atbash += chr(ord('z') - (ord(char) - ord('a')))
    else:
        atbash += char
print(f"    {atbash}")

# For Enigma, we need to try different rotor settings
# Let's try a simple implementation
print("\n[*] Trying simple rotor cipher (Enigma-like):")

# Try common Enigma rotor wirings
# Rotor I wiring
rotor_I = "EKMFLGDQVZNTOWYHXUSPAIBRCJ"
rotor_II = "AJDKSIRUXBLHWTMCQGZNPYFVOE"
rotor_III = "BDFHJLCPRTXVZNYEIWGAKMUSQO"

def simple_rotor_decrypt(text, rotor, start_pos=0):
    result = ''
    pos = start_pos
    for char in text:
        if char.isalpha():
            # Find position in rotor
            idx = (ord(char) - ord('A') + pos) % 26
            # Reverse lookup
            plain_idx = rotor.index(chr(idx + ord('A')))
            result += chr((plain_idx - pos) % 26 + ord('A'))
            pos = (pos + 1) % 26
        else:
            result += char
    return result

# Try different starting positions
for start in range(26):
    decoded = simple_rotor_decrypt(ciphertext, rotor_I, start)
    if 'THE' in decoded or 'AND' in decoded:
        print(f"    Rotor I, start {start}: {decoded[:50]}...")

print("\n" + "="*70)
