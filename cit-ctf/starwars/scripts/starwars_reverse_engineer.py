#!/usr/bin/env python3
"""
Star Wars - Reverse Engineer the Encoding
Let's think about what "May the Force be with you" could encode to
"""

print("=" * 70)
print("STAR WARS - REVERSE ENGINEERING")
print("=" * 70)

message_numbers = """095 181 145 039 245 091 212 232 123 220 167 069 091 208 245 164 245 145 123 094, 062 150 094 172 083 135 096 153 002 208 096 172. 201 005 019 {131 091 090 053 095 218 238 211 091 004 201 182 135 245 167 074 090 145 096 238}"""

import re
numbers = [int(n) for n in re.findall(r'\d+', message_numbers)]

print(f"\n📊 We have {len(numbers)} numbers")
print(f"   First 10: {numbers[:10]}")

# Let's assume the message starts with "May the Force" or similar
possible_starts = [
    "May the Force be with you",
    "The Force is strong",
    "Use the Force",
    "CTF{",
    "CIT{",
    "FLAG{",
]

print("\n" + "=" * 70)
print("REVERSE ENGINEERING XOR KEY")
print("=" * 70)

for start_text in possible_starts:
    print(f"\nAssuming message starts with: '{start_text}'")
    
    # Calculate what the XOR key would be
    if len(start_text) <= len(numbers):
        potential_key = []
        for i, char in enumerate(start_text):
            if numbers[i] <= 255:
                key_byte = numbers[i] ^ ord(char)
                potential_key.append(key_byte)
        
        print(f"   Potential XOR key bytes: {potential_key[:10]}")
        
        # Check if key repeats
        if len(potential_key) >= 6:
            # Try to find repeating pattern
            for key_len in [1, 2, 3, 4, 5, 6, 7, 8]:
                if key_len <= len(potential_key):
                    key_pattern = potential_key[:key_len]
                    
                    # Test if this pattern works for the whole message
                    decoded = ""
                    works = True
                    for i, n in enumerate(numbers):
                        if n > 255:
                            works = False
                            break
                        xor_val = n ^ key_pattern[i % key_len]
                        if 32 <= xor_val <= 126:
                            decoded += chr(xor_val)
                        else:
                            decoded += '.'
                    
                    if works:
                        readable = sum(1 for c in decoded if c != '.') / len(decoded)
                        if readable > 0.7:
                            print(f"   ✓ Key length {key_len} works! ({readable*100:.1f}% readable)")
                            print(f"     Key: {key_pattern}")
                            print(f"     Decoded: {decoded}")

# Try assuming the flag section decodes to something specific
print("\n" + "=" * 70)
print("REVERSE ENGINEERING FLAG SECTION")
print("=" * 70)

flag_numbers = [131, 91, 90, 53, 95, 218, 238, 211, 91, 4, 201, 182, 135, 245, 167, 74, 90, 145, 96, 238]

# Common flag patterns
flag_patterns = [
    "flag",
    "FLAG",
    "password",
    "secret",
    "jedi",
    "JEDI",
    "force",
    "FORCE",
    "yoda",
    "YODA",
]

for pattern in flag_patterns:
    if len(pattern) <= len(flag_numbers):
        print(f"\nAssuming flag starts with: '{pattern}'")
        key_bytes = []
        for i, char in enumerate(pattern):
            if flag_numbers[i] <= 255:
                key_byte = flag_numbers[i] ^ ord(char)
                key_bytes.append(key_byte)
        
        print(f"   Key bytes: {key_bytes}")
        
        # Try to decode full flag with this key
        if key_bytes:
            for key_len in range(1, min(len(key_bytes) + 1, 9)):
                key_pattern = key_bytes[:key_len]
                decoded = ""
                for i, n in enumerate(flag_numbers):
                    if n <= 255:
                        xor_val = n ^ key_pattern[i % key_len]
                        if 32 <= xor_val <= 126:
                            decoded += chr(xor_val)
                        else:
                            decoded += '.'
                
                readable = sum(1 for c in decoded if c != '.') / len(decoded)
                if readable > 0.8:
                    print(f"     Key length {key_len}: {decoded} ({readable*100:.1f}%)")

print("\n" + "=" * 70)
