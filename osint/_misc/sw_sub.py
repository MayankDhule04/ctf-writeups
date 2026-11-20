#!/usr/bin/env python3
import re

msg = "095 181 145 039 245 091 212 232 123 220 167 069 091 208 245 164 245 145 123 094, 062 150 094 172 083 135 096 153 002 208 096 172. 201 005 019 {131 091 090 053 095 218 238 211 091 004 201 182 135 245 167 074 090 145 096 238}"
data = [int(n) for n in re.findall(r'\d+', msg)]

print("Testing (x - key) % 256:")
for k in range(256):
    decoded = ''.join(chr((x - k) % 256) for x in data)
    if all(32 <= ord(c) < 127 for c in decoded):
        print(f"Key {k}: {decoded}")
        if '{' in decoded:
            flag_match = re.search(r'\{([^}]+)\}', decoded)
            if flag_match:
                print(f"  🏁 FLAG: {{{flag_match.group(1)}}}")
