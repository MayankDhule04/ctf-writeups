#!/usr/bin/env python3
"""
Re-examine heart.dmp from scratch.

Facts established:
1. File is 109424 bytes, custom format (not ELF)
2. Header contains text: image_base=0x555555400000, HEARTLIST=0x555555458000
3. "nodes are LOVE-tagged; the freed ones lie"
4. CHAKRA decoy at file offset 0x8000 (plaintext)
5. CHAKRA hint at file offset 0x9800 (plaintext: "th3_r34l_0n3_1s_x0r3d_p3r_n0d3")
6. "The confession was never stored in one place. It lives as a chain of
    little notes in the heap, each masked so a casual glance sees nothing,
    linked by pointers into an address space that no longer exists."
7. "Plenty of feelings in there are lies. Only one chain is the truth."

Key insight from item 5: "th3_r34l_0n3_1s_x0r3d_p3r_n0d3"
= "the real one is xored per node"

So each node stores one character of the flag, XOR'd with some key.
The key is PER-NODE (different for each node).

From item 2: HEARTLIST=0x555555458000 -> file offset = 0x58000 = 360448 > file size.
This means the head pointer is stored outside the dump (in a region not captured).
OR the HEARTLIST VALUE (not the variable) is embedded in the dump differently.

Let me look for a different structure:
- The file might have a "page table" or "segment table" that maps VAs
- Or nodes might be at fixed intervals based on their VA

Actually: HEARTLIST=0x555555458000 is the VALUE of the pointer variable,
stored AT some location in the heap. The header line tells us WHERE the list head is.
The list head itself is at file offset: 0x555555458000 - 0x555555400000 = 0x58000.
Since 0x58000 > 0x1AB70 (file size), the head pointer is not in the file.

BUT: what if the HEARTLIST address IS pointing into the file through a different mapping?
What if the file represents a DIFFERENT VA range?

Let me try: what if the file represents VA range starting at 0x555555440000?
Then HEARTLIST = 0x555555458000 -> offset = 0x18000
File offset 0x18000 = 98304, which IS within file (109424 > 98304)!

Let's check:
0x555555458000 - 0x555555440000 = 0x18000 = 98304

And CHAKRA decoy at file 0x8000:
VA = 0x555555440000 + 0x8000 = 0x555555448000

And second CHAKRA at file 0x9800:
VA = 0x555555440000 + 0x9800 = 0x555555449800
"""
import struct

with open('heart.dmp', 'rb') as f:
    raw = f.read()

size = len(raw)
# Try alternative image base: maybe the dump starts at 0x555555440000
image_base_alt = 0x555555440000
heartlist_va = 0x555555458000
heartlist_off = heartlist_va - image_base_alt
print(f'Alt image_base: 0x{image_base_alt:x}')
print(f'HEARTLIST offset with alt base: 0x{heartlist_off:x} = {heartlist_off}')
print(f'File size: 0x{size:x} = {size}')
print(f'HEARTLIST in file: {0 <= heartlist_off < size}')
print()

if 0 <= heartlist_off < size:
    head_ptr = struct.unpack_from('<Q', raw, heartlist_off)[0]
    print(f'Head pointer value: 0x{head_ptr:016x}')
    head_off = head_ptr - image_base_alt
    print(f'Head node offset: 0x{head_off:x}')
    print(f'Head in file: {0 <= head_off < size}')
    
    # Show bytes around HEARTLIST
    print(f'\nBytes at HEARTLIST (0x{heartlist_off:x}):')
    for off in range(max(0, heartlist_off-32), min(size, heartlist_off+96), 8):
        val = struct.unpack_from('<Q', raw, off)[0]
        text = ''.join(chr(b) if 0x20<=b<0x7f else '.' for b in raw[off:off+8])
        marker = ' <-- HEARTLIST' if off == heartlist_off else ''
        print(f'  0x{off:06x}: 0x{val:016x}  {text}{marker}')

print()
print('=== Trying to walk the list with alt base ===')
VA_LO = image_base_alt
VA_HI = image_base_alt + size

def off_to_va(off):
    return off + image_base_alt

def va_to_off(va):
    return va - image_base_alt

# Find VA-like values in the file
print('VA-like values found in dump (alt base):')
va_refs = []
for off in range(0, size - 8, 8):
    val = struct.unpack_from('<Q', raw, off)[0]
    if VA_LO <= val < VA_HI:
        va_refs.append((off, val, va_to_off(val)))
        
print(f'Total: {len(va_refs)}')
for off, val, target in va_refs[:30]:
    ttext = ''.join(chr(b) if 0x20<=b<0x7f else '.' for b in raw[target:target+8])
    print(f'  0x{off:06x}: VA=0x{val:x} -> off=0x{target:x}  [{ttext}]')

# Check all possible image base offsets
print()
print('=== Trying all possible image bases (where HEARTLIST falls in file) ===')
# HEARTLIST = 0x555555458000
# file_off = 0x555555458000 - image_base
# We need 0 <= file_off < 0x1AB70
# So 0x555555458000 - 0x1AB70 < image_base <= 0x555555458000
# 0x555555458000 - 0x1AB70 = 0x555555438490
# So image_base in range [0x555555438490, 0x555555458000]

for offset_guess in [0x8000, 0x9800, 0x58000, 0x40000, 0x50000, 0x18000, 0x10000, 0x20000]:
    ib = heartlist_va - offset_guess
    if 0 <= offset_guess < size:
        val = struct.unpack_from('<Q', raw, offset_guess)[0]
        if ib != 0x555555400000:  # Skip the main one we already know
            # Is val a valid VA with this base?
            head_off = val - ib
            in_file = 0 <= head_off < size
            print(f'  image_base=0x{ib:x} (HEARTLIST at file:0x{offset_guess:x}) -> head_ptr=0x{val:x} -> head_off=0x{head_off:x} {"IN FILE" if in_file else ""}')
