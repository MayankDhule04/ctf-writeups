#!/usr/bin/env python3
import re

msg = "095 181 145 039 245 091 212 232 123 220 167 069 091 208 245 164 245 145 123 094, 062 150 094 172 083 135 096 153 002 208 096 172. 201 005 019 {131 091 090 053 095 218 238 211 091 004 201 182 135 245 167 074 090 145 096 238}"
nums = [int(n) for n in re.findall(r'\d+', msg)]

# Best method: mod 95 + 32
decoded = ''.join(chr((n % 95) + 32) for n in nums)
print(f"Decoded: {decoded}")

# The original has { } in it, let's preserve structure
parts = msg.split('{')
if len(parts) > 1:
    before_brace = parts[0]
    after_brace = parts[1].split('}')
    flag_part = after_brace[0]
    
    flag_nums = [int(n) for n in re.findall(r'\d+', flag_part)]
    flag_decoded = ''.join(chr((n % 95) + 32) for n in flag_nums)
    
    print(f"\nFlag content: {flag_decoded}")
    print(f"Flag: {{{flag_decoded}}}")
