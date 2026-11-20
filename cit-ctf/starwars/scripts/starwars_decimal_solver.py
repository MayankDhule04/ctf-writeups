#!/usr/bin/env python3
"""
Star Wars Force Challenge - Decimal Solver
These might be DECIMAL numbers, not octal!
"""

print("=" * 70)
print("STAR WARS FORCE CHALLENGE - DECIMAL SOLVER")
print("=" * 70)

message = """095 181 145 039 245 091 212 232 123 220 167 069 091 208 245 164 245 145 123 094, 062 150 094 172 083 135 096 153 002 208 096 172. 201 005 019 {131 091 090 053 095 218 238 211 091 004 201 182 135 245 167 074 090 145 096 238}"""

print(f"\n💡 Insight: Numbers contain 8 and 9, so they're DECIMAL, not octal!")

# Parse as decimal numbers
import re
numbers = [int(n) for n in re.findall(r'\d+', message)]

print(f"\n📊 Parsed {len(numbers)} decimal numbers")
print(f"   Range: {min(numbers)} to {max(numbers)}")

# Strategy 1: Direct ASCII
print("\n" + "=" * 70)
print("STRATEGY 1: Direct Decimal to ASCII")
print("=" * 70)

decoded = ""
for n in numbers:
    if 32 <= n <= 126:
        decoded += chr(n)
    else:
        decoded += f"[{n}]"

print(f"Decoded: {decoded}")

# Strategy 2: Extended ASCII (0-255)
print("\n" + "=" * 70)
print("STRATEGY 2: Extended ASCII (0-255)")
print("=" * 70)

decoded = ''.join(chr(n) if n <= 255 else f"[{n}]" for n in numbers)
print(f"Decoded: {decoded}")

# Strategy 3: XOR with single byte
print("\n" + "=" * 70)
print("STRATEGY 3: XOR with Single Byte Keys")
print("=" * 70)

# Try XOR with common keys
for key in range(256):
    decoded = ""
    valid = True
    for n in numbers:
        if n > 255:
            valid = False
            break
        xor_val = n ^ key
        if 32 <= xor_val <= 126:
            decoded += chr(xor_val)
        else:
            decoded += '.'
    
    if valid:
        # Check if it looks like readable text
        readable_ratio = sum(1 for c in decoded if c != '.') / len(decoded)
        if readable_ratio > 0.8:  # At least 80% readable
            print(f"\nXOR key {key} ('{chr(key) if 32 <= key <= 126 else hex(key)}'): {decoded}")
            print(f"   Readable: {readable_ratio*100:.1f}%")

# Strategy 4: Extract and decode flag section
print("\n" + "=" * 70)
print("STRATEGY 4: Flag Section Analysis")
print("=" * 70)

flag_match = re.search(r'\{([^}]+)\}', message)
if flag_match:
    flag_numbers = [int(n) for n in re.findall(r'\d+', flag_match.group(1))]
    print(f"\n🏁 Flag section has {len(flag_numbers)} numbers")
    print(f"   Numbers: {flag_numbers}")
    
    # Direct ASCII
    flag_decoded = ""
    for n in flag_numbers:
        if 32 <= n <= 126:
            flag_decoded += chr(n)
        else:
            flag_decoded += f"[{n}]"
    
    print(f"\n   Direct ASCII: {flag_decoded}")
    
    # Try XOR on flag only
    print(f"\n   XOR attempts on flag:")
    for key in range(256):
        decoded = ""
        valid = True
        for n in flag_numbers:
            if n > 255:
                valid = False
                break
            xor_val = n ^ key
            if 32 <= xor_val <= 126:
                decoded += chr(xor_val)
            else:
                decoded += '.'
        
        if valid:
            readable_ratio = sum(1 for c in decoded if c != '.') / len(decoded)
            if readable_ratio > 0.8:
                print(f"      Key {key}: {decoded}")

# Strategy 5: Subtract offset
print("\n" + "=" * 70)
print("STRATEGY 5: Subtract Offset")
print("=" * 70)

for offset in [0, 32, 64, 128]:
    decoded = ""
    valid = True
    for n in numbers:
        adjusted = n - offset
        if 32 <= adjusted <= 126:
            decoded += chr(adjusted)
        elif adjusted == 10 or adjusted == 13:  # newline/carriage return
            decoded += '\n'
        else:
            decoded += '.'
    
    readable_ratio = sum(1 for c in decoded if c not in '.\n') / len(decoded)
    if readable_ratio > 0.5:
        print(f"\nOffset -{offset}: {decoded}")
        print(f"   Readable: {readable_ratio*100:.1f}%")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
