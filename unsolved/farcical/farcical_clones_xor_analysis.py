#!/usr/bin/env python3
"""
Farcical Clones - XOR Analysis
Cipher1 and Flag have same length - this is the key!
"""

cipher1 = "095 181 145 039 245 091 212 232 123 220 167 069 091 208 245 164 245 145 123 094"
cipher2 = "062 150 094 172 083 135 096 153 002 208 096 172"
cipher3 = "201 005 019 {131 091 090 053 095 218 238 211 091 004 201 182 135 245 167 074 090 145 096 238}"

def parse_numbers(s):
    return [int(n) for n in s.replace('{', '').replace('}', '').split()]

nums1 = parse_numbers(cipher1)
nums2 = parse_numbers(cipher2)
nums3 = parse_numbers(cipher3)

# Extract flag content
flag_cipher = "{131 091 090 053 095 218 238 211 091 004 201 182 135 245 167 074 090 145 096 238}"
flag_nums = parse_numbers(flag_cipher)

print("="*70)
print("FARCICAL CLONES - XOR ANALYSIS")
print("="*70)

# XOR cipher1 with flag
print("[1] XOR Cipher1 with Flag:")
print(f"Cipher1: {nums1}")
print(f"Flag:    {flag_nums}")
print()

xor_result = [flag_nums[i] ^ nums1[i] for i in range(len(flag_nums))]
print(f"XOR result (decimal): {xor_result}")
print(f"XOR result (hex): {[hex(x) for x in xor_result]}")
print(f"XOR result (chr): {[''.join(chr(x) if 32 <= x < 127 else f'\\x{x:02x}' for x in xor_result)]}")
print()

# Try to decode as ASCII
try:
    decoded = ''.join(chr(x) if x < 256 else '?' for x in xor_result)
    print(f"As ASCII: {repr(decoded)}")
    print(f"Readable: {decoded}")
except Exception as e:
    print(f"Error: {e}")

print()

# Now try XOR cipher2 with itself repeated
print("[2] Analyzing Cipher2:")
print(f"Cipher2: {nums2}")
print(f"Length: {len(nums2)}")

# Maybe cipher2 is a key to decrypt cipher1?
print("\n[3] XOR Cipher1 with Cipher2 (repeating):")
def xor_with_key(data, key):
    return [data[i] ^ key[i % len(key)] for i in range(len(data))]

result = xor_with_key(nums1, nums2)
print(f"Result: {result}")
try:
    decoded = ''.join(chr(x) if 32 <= x < 127 else f'[{x}]' for x in result)
    print(f"Decoded: {decoded}")
except:
    pass

# Try XOR flag with cipher2
print("\n[4] XOR Flag with Cipher2 (repeating):")
result = xor_with_key(flag_nums, nums2)
print(f"Result: {result}")
try:
    decoded = ''.join(chr(x) if 32 <= x < 127 else f'[{x}]' for x in result)
    print(f"Decoded: {decoded}")
    
    # Check if it looks like a flag
    if all(32 <= x < 127 for x in result):
        clean = ''.join(chr(x) for x in result)
        print(f"CLEAN: {clean}")
        print(f"\nPOSSIBLE FLAG: CIT{{{clean}}}")
except Exception as e:
    print(f"Error: {e}")

# Try the prefix (201 005 019) as part of the key
print("\n[5] Analyzing prefix (201 005 019):")
prefix = nums3[:3]
print(f"Prefix: {prefix}")
print(f"As ASCII: {[chr(x) if 32 <= x < 127 else f'\\x{x:02x}' for x in prefix]}")

# Maybe the whole thing is: prefix + flag, and we need to XOR with cipher1+cipher2?
print("\n[6] Full cipher3 XOR with cipher1:")
# Pad cipher1 to match length
if len(nums3) > len(nums1):
    padded_cipher1 = nums1 + nums1[:len(nums3)-len(nums1)]
else:
    padded_cipher1 = nums1[:len(nums3)]

result = [nums3[i] ^ padded_cipher1[i] for i in range(len(nums3))]
print(f"Result: {result}")
try:
    decoded = ''.join(chr(x) if 32 <= x < 127 else f'[{x}]' for x in result)
    print(f"Decoded: {decoded}")
except:
    pass

print("\n" + "="*70)
