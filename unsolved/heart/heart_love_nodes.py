#!/usr/bin/env python3
"""
Found the nodes! VA pointers point to offsets starting with "LOVE" or "DEAD".
The LOVE/DEAD tagged nodes are at:
  offset 0x40000 -> VA 0x555555440000 (LOVE)
  offset 0x43000 -> VA 0x555555443000 (LOVE)
  offset 0x46000 -> VA 0x555555446000 (LOVE)
  offset 0x49000 -> VA 0x555555449000 (LOVE)
  offset 0x4c000 -> VA 0x55555544c000 (LOVE)
  offset 0x4f000 -> VA 0x55555544f000 (LOVE)
  offset 0x52000 -> VA 0x555555452000 (LOVE)
  offset 0x55000 -> VA 0x555555455000 (LOVE)
  offset 0x58000 -> VA 0x555555458000 (= HEARTLIST!)
  offset 0x5b000 -> VA 0x55555545b000 (LOVE)
  offset 0x5e000 -> VA 0x55555545e000 (DEAD)
  offset 0x61000 -> VA 0x555555461000 (DEAD)

HEARTLIST = 0x555555458000 is at file offset 0x58000!
This means the dump's base is NOT 0x555555400000 but rather
the file represents a subset of memory where:
  file_offset = VA - 0x555555400000  -->  0x58000 maps to HEARTLIST!

Wait: 0x555555458000 - 0x555555400000 = 0x58000. YES!
The original image_base calculation IS correct!
But 0x58000 = 360448, which IS within the 1.5MB file!
(We were looking at the truncated 109424-byte file before!)
"""
import struct

with open('heart_full.dmp', 'rb') as f:
    raw = f.read()

size = len(raw)
image_base = 0x555555400000
VA_LO = image_base
VA_HI = image_base + size

def va_to_off(va):
    return va - image_base

def off_to_va(off):
    return off + image_base

def read_u64(off):
    if 0 <= off <= size - 8:
        return struct.unpack_from('<Q', raw, off)[0]
    return None

# HEARTLIST at file offset 0x58000
heartlist_off = 0x58000
head_ptr = read_u64(heartlist_off)
print(f'HEARTLIST at 0x{heartlist_off:x}: value = 0x{head_ptr:016x}')
head_off = va_to_off(head_ptr)
print(f'Head node file offset: 0x{head_off:x}')
print()

# Look at ALL LOVE/DEAD tagged nodes
print('=== Scanning for LOVE/DEAD tagged nodes ===')
love_offsets = []
dead_offsets = []

for off in range(0, size - 16, 0x1000):  # they seem to be on page boundaries
    if raw[off:off+4] == b'LOVE':
        love_offsets.append(off)
    elif raw[off:off+4] == b'DEAD':
        dead_offsets.append(off)

# Also scan at smaller granularity in case they're not page-aligned
for off in range(0, size - 16, 8):
    if raw[off:off+4] == b'LOVE' and off not in love_offsets:
        love_offsets.append(off)
    elif raw[off:off+4] == b'DEAD' and off not in dead_offsets:
        dead_offsets.append(off)

love_offsets.sort()
dead_offsets.sort()

print(f'LOVE nodes: {len(love_offsets)}')
print(f'DEAD nodes: {len(dead_offsets)}')
print()

# Examine node structure
print('=== LOVE node structure ===')
for off in love_offsets[:3]:
    print(f'\nNode at 0x{off:06x} (VA 0x{off_to_va(off):x}):')
    for i in range(0, min(64, size - off), 8):
        val = read_u64(off + i)
        text = ''.join(chr(b) if 0x20<=b<0x7f else '.' for b in raw[off+i:off+i+8])
        is_va = VA_LO <= val < VA_HI if val else False
        note = f' -> VA (off=0x{va_to_off(val):x})' if is_va else ''
        print(f'  +{i:3d}: {val:016x}  {text}{note}')

print()
print('=== DEAD node structure ===')
for off in dead_offsets[:2]:
    print(f'\nNode at 0x{off:06x} (VA 0x{off_to_va(off):x}):')
    for i in range(0, min(64, size - off), 8):
        val = read_u64(off + i)
        text = ''.join(chr(b) if 0x20<=b<0x7f else '.' for b in raw[off+i:off+i+8])
        is_va = VA_LO <= val < VA_HI if val else False
        note = f' -> VA (off=0x{va_to_off(val):x})' if is_va else ''
        print(f'  +{i:3d}: {val:016x}  {text}{note}')
