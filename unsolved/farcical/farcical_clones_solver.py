#!/usr/bin/env python3
"""
Farcical Clones Challenge Solver
Hint: "May the Force be with you, young padawan"
"""

# The cipher text appears to be octal numbers
cipher1 = "095 181 145 039 245 091 212 232 123 220 167 069 091 208 245 164 245 145 123 094"
cipher2 = "062 150 094 172 083 135 096 153 002 208 096 172"
cipher3 = "201 005 019 {131 091 090 053 095 218 238 211 091 004 201 182 135 245 167 074 090 145 096 238}"

print("="*70)
print("FARCICAL CLONES SOLVER")
print("="*70)
print(f"Hint: May the Force be with you, young padawan")
print(f"Challenge: bootstrap (999 points)")
print()

# Parse numbers (they contain 8 and 9, so they're decimal, not octal)
def parse_number_string(s):
    """Parse space-separated decimal numbers"""
    numbers = s.replace('{', '').replace('}', '').split()
    return [int(n) for n in numbers]

print("[1] Parsing decimal numbers:")
nums1 = parse_number_string(cipher1)
nums2 = parse_number_string(cipher2)
nums3 = parse_number_string(cipher3)

print(f"Cipher 1: {nums1}")
print(f"Cipher 2: {nums2}")
print(f"Cipher 3: {nums3}")
print()

# Try direct ASCII conversion
print("[2] Direct ASCII conversion:")
try:
    text1 = ''.join(chr(n) for n in nums1 if n < 256)
    text2 = ''.join(chr(n) for n in nums2 if n < 256)
    text3 = ''.join(chr(n) for n in nums3 if n < 256)
    
    print(f"Text 1: {repr(text1)}")
    print(f"Text 2: {repr(text2)}")
    print(f"Text 3: {repr(text3)}")
    print()
except Exception as e:
    print(f"Error: {e}")

# Try XOR with common keys
print("[3] Trying XOR with Star Wars themed keys:")

star_wars_keys = [
    "FORCE",
    "JEDI",
    "SITH",
    "YODA",
    "LUKE",
    "VADER",
    "CLONE",
    "PADAWAN",
    "STARWARS",
    "MAYTHEFORCEBEWITHYOU",
]

def xor_decrypt(numbers, key):
    """XOR decrypt with repeating key"""
    key_bytes = [ord(c) for c in key.upper()]
    result = []
    for i, num in enumerate(numbers):
        result.append(num ^ key_bytes[i % len(key_bytes)])
    return bytes(result)

for key in star_wars_keys:
    try:
        decoded1 = xor_decrypt(nums1, key)
        decoded2 = xor_decrypt(nums2, key)
        decoded3 = xor_decrypt(nums3, key)
        
        # Check if it's printable ASCII
        if all(32 <= b < 127 for b in decoded1):
            print(f"\nKey '{key}':")
            print(f"  Text 1: {decoded1.decode('ascii')}")
            print(f"  Text 2: {decoded2.decode('ascii', errors='ignore')}")
            print(f"  Text 3: {decoded3.decode('ascii', errors='ignore')}")
    except:
        pass

# Try single-byte XOR
print("\n[4] Trying single-byte XOR (0-255):")
best_score = 0
best_key = None
best_decoded = None

for key in range(256):
    decoded = bytes([n ^ key for n in nums1])
    
    # Score based on printable ASCII
    score = sum(1 for b in decoded if 32 <= b < 127)
    
    if score > best_score:
        best_score = score
        best_key = key
        best_decoded = decoded

if best_decoded:
    print(f"Best single-byte XOR key: {best_key} (0x{best_key:02x}, '{chr(best_key) if 32 <= best_key < 127 else '?'}')")
    print(f"Score: {best_score}/{len(nums1)}")
    print(f"Decoded 1: {best_decoded}")
    
    # Apply to all three
    decoded2 = bytes([n ^ best_key for n in nums2])
    decoded3 = bytes([n ^ best_key for n in nums3])
    print(f"Decoded 2: {decoded2}")
    print(f"Decoded 3: {decoded3}")

# Try Caesar shift on the octal values
print("\n[5] Trying Caesar shift on octal values:")
for shift in range(1, 26):
    shifted = []
    for n in nums1:
        # Convert to char, shift, convert back
        if n < 256:
            c = chr(n)
            if c.isalpha():
                if c.isupper():
                    shifted.append(chr((ord(c) - ord('A') + shift) % 26 + ord('A')))
                else:
                    shifted.append(chr((ord(c) - ord('a') + shift) % 26 + ord('a')))
            else:
                shifted.append(c)
    
    result = ''.join(shifted)
    if 'CIT' in result or 'FLAG' in result:
        print(f"Shift {shift}: {result}")

# Check if the flag is in cipher3 (it has curly braces)
print("\n[6] Analyzing cipher 3 (contains curly braces):")
print(f"Raw cipher 3: {cipher3}")
print(f"Octal values: {nums3}")

# The structure suggests: [prefix] {[flag content]}
# Let's find where the braces are
brace_start = cipher3.index('{')
brace_end = cipher3.index('}')
flag_part = cipher3[brace_start:brace_end+1]
print(f"Flag portion: {flag_part}")

# Parse just the flag part
flag_nums = parse_number_string(flag_part)
print(f"Flag octal values: {flag_nums}")

# Try XOR on flag part
print("\n[7] XOR decryption on flag part:")
for key in star_wars_keys:
    try:
        decoded = xor_decrypt(flag_nums, key)
        if all(32 <= b < 127 for b in decoded):
            print(f"Key '{key}': {decoded.decode('ascii')}")
    except:
        pass

print("\n" + "="*70)
