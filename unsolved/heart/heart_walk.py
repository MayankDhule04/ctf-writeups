#!/usr/bin/env python3
"""
Walk the heap linked list in heart.dmp
The header tells us:
  - image_base = 0x555555400000
  - HEARTLIST = 0x555555458000  (head pointer)
  - Nodes are LOVE-tagged; freed ones lie
  - Each node is masked (XOR'd)
  - Only one chain is the truth
"""
import struct

with open('heart.dmp', 'rb') as f:
    raw = f.read()

print(f'Dump size: {len(raw)} bytes = 0x{len(raw):x}')
print()

# Parse the header section (first 0x200 or so)
hdr_text = raw[:0x300].decode('ascii', errors='replace')
print('=== Header ===')
for line in hdr_text.split('\n'):
    line = line.strip()
    if line and all(c.isprintable() or c in '\t\r' for c in line):
        if any(c.isalpha() for c in line):
            print(' ', line)
print()

# Key values from header
image_base = 0x555555400000
heartlist_va = 0x555555458000

# The dump is at some base. Figure out how VAs map to file offsets.
# "image_base=0x555555400000" - the dump contains mapped memory
# HEARTLIST=0x555555458000 means the linked list head is at that VA
# 
# Since this isn't an ELF, the mapping must be explicit in the header
# or it's a flat raw dump where VA - image_base = file_offset
# image_base = 0x555555400000, so offset = VA - image_base

def va_to_offset(va):
    return va - image_base

def read_u64(va):
    off = va_to_offset(va)
    if off < 0 or off + 8 > len(raw):
        return None
    return struct.unpack_from('<Q', raw, off)[0]

def read_u8(va):
    off = va_to_offset(va)
    if off < 0 or off >= len(raw):
        return None
    return raw[off]

def read_bytes(va, n):
    off = va_to_offset(va)
    if off < 0 or off + n > len(raw):
        return None
    return raw[off:off+n]

# The HEARTLIST pointer value - the head of the list
heartlist_off = va_to_offset(heartlist_va)
print(f'HEARTLIST VA: 0x{heartlist_va:x}, file offset: 0x{heartlist_off:x}')
print(f'Bytes at HEARTLIST: {raw[heartlist_off:heartlist_off+16].hex()}')

# Read the head pointer (pointer to first node)
head_ptr = read_u64(heartlist_va)
print(f'Head pointer: 0x{head_ptr:x}' if head_ptr else 'Could not read head pointer')
print()

# Let's look at what's around 0x8000 (offset) to understand node structure
# CHAKRA decoy at file offset 0x8000 -> VA 0x555555408000
print('=== Region around decoy CHAKRA (offset 0x7f00-0x8100) ===')
for off in range(0x7f00, 0x8100, 8):
    val = struct.unpack_from('<Q', raw, off)[0] if off + 8 <= len(raw) else 0
    text = raw[off:off+8]
    printable = ''.join(chr(b) if 0x20 <= b < 0x7f else '.' for b in text)
    print(f'  0x{off:06x}: {val:016x}  {printable}')

print()
print('=== Region around second CHAKRA (offset 0x9700-0x9900) ===')
for off in range(0x9700, 0x9900, 8):
    val = struct.unpack_from('<Q', raw, off)[0] if off + 8 <= len(raw) else 0
    text = raw[off:off+8]
    printable = ''.join(chr(b) if 0x20 <= b < 0x7f else '.' for b in text)
    print(f'  0x{off:06x}: {val:016x}  {printable}')
