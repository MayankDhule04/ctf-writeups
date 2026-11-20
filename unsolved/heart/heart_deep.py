#!/usr/bin/env python3
"""Deep analysis of heart.dmp - custom heap format"""
import struct
import re

with open('heart.dmp', 'rb') as f:
    raw = f.read()

size = len(raw)
print(f'Dump size: {size} bytes = 0x{size:x}')

# Parse the full header
# Find all printable regions in first 0x600 bytes
header_end = 0x600
hdr = raw[:header_end]

print('\n=== Full header bytes (hex + ascii) ===')
for off in range(0, header_end, 16):
    chunk = raw[off:off+16]
    hex_str = ' '.join(f'{b:02x}' for b in chunk)
    asc_str = ''.join(chr(b) if 0x20 <= b < 0x7f else '.' for b in chunk)
    print(f'  0x{off:04x}: {hex_str:<48}  {asc_str}')
