#!/usr/bin/env python3
import re

msg = "095 181 145 039 245 091 212 232 123 220 167 069 091 208 245 164 245 145 123 094, 062 150 094 172 083 135 096 153 002 208 096 172. 201 005 019 {131 091 090 053 095 218 238 211 091 004 201 182 135 245 167 074 090 145 096 238}"

nums = [int(n) for n in re.findall(r'\d+', msg)]

# Try: subtract 32, then mod 95 (printable ASCII range)
result = ''.join(chr(((n - 32) % 95) + 32) if n >= 32 else '.' for n in nums)
print(f"Method 1: {result}")

# Try: direct mod 95 + 32
result = ''.join(chr((n % 95) + 32) for n in nums)
print(f"Method 2: {result}")

# Try: XOR with 128
result = ''.join(chr(n ^ 128) if 32 <= (n ^ 128) <= 126 else '.' for n in nums)
print(f"Method 3: {result}")

# Try: Subtract 32
result = ''.join(chr(n - 32) if 32 <= (n - 32) <= 126 else '.' for n in nums)
print(f"Method 4: {result}")

# Try treating as actual octal (valid ones only)
result = ""
for i, s in enumerate(re.findall(r'\d{3}', msg)):
    if all(c in '01234567' for c in s):
        val = int(s, 8)
        result += chr(val) if 32 <= val <= 126 else '.'
    else:
        result += chr(nums[i]) if 32 <= nums[i] <= 126 else '.'
print(f"Method 5: {result}")

# Try: numbers as indices in custom alphabet
alpha = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
result = ''.join(alpha[n % len(alpha)] for n in nums)
print(f"Method 6: {result}")
