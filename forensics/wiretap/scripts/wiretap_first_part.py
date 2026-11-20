#!/usr/bin/env python3
"""
Wiretap - Focus on the first clean part
"""

# The very first part before it gets noisy
first_part = "AD1318A2016A3C141459521938A9A"

print("="*70)
print("WIRETAP - FIRST PART ANALYSIS")
print("="*70)

print(f"\nFirst part: {first_part}")
print(f"Length: {len(first_part)}")

# Try as straight hex
print(f"\n[1] As hexadecimal:")
try:
    hex_bytes = bytes.fromhex(first_part)
    print(f"  Bytes: {hex_bytes}")
    print(f"  As ASCII: {hex_bytes.decode('ascii', errors='ignore')}")
    print(f"  As Latin-1: {hex_bytes.decode('latin-1', errors='ignore')}")
except Exception as e:
    print(f"  Error: {e}")

# Try the second part
second_part = "4321539B1B17ABDA7265"
print(f"\n[2] Second part: {second_part}")
try:
    hex_bytes = bytes.fromhex(second_part)
    print(f"  As ASCII: {hex_bytes.decode('ascii', errors='ignore')}")
except Exception as e:
    print(f"  Error: {e}")

# Combine first few parts
combined = "AD1318A2016A3C141459521938A9A4321539B1B17ABDA7265"
print(f"\n[3] Combined first two parts:")
try:
    hex_bytes = bytes.fromhex(combined)
    text = hex_bytes.decode('ascii', errors='ignore')
    print(f"  As ASCII: {text}")
    
    # Check for flag
    if 'CIT' in text or 'cit' in text.lower():
        print(f"\n  ✓✓ CONTAINS FLAG PATTERN!")
except Exception as e:
    print(f"  Error: {e}")

print(f"\n{'='*70}")
