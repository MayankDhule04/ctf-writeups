#!/usr/bin/env python3
"""Analyze the heart.dmp core dump file"""
import struct
import re

with open('heart.dmp', 'rb') as f:
    data = f.read()

print(f'Size: {len(data)} bytes')
print(f'First 16 bytes (hex): {data[:16].hex()}')
print(f'First 16 bytes (ascii): {repr(data[:16])}')
print()

# Check ELF
if data[:4] == b'\x7fELF':
    ei_class = data[4]   # 1=32-bit, 2=64-bit
    ei_data = data[5]    # 1=LE, 2=BE
    e_type = struct.unpack_from('<H', data, 16)[0]
    print(f'ELF file detected!')
    print(f'  Class: {"64-bit" if ei_class==2 else "32-bit"}')
    print(f'  Endian: {"LE" if ei_data==1 else "BE"}')
    print(f'  Type: {e_type} (4=CORE dump)')
    
    if ei_class == 2:  # 64-bit
        e_phoff = struct.unpack_from('<Q', data, 32)[0]
        e_phentsize = struct.unpack_from('<H', data, 54)[0]
        e_phnum = struct.unpack_from('<H', data, 56)[0]
        print(f'  Program headers: {e_phnum} @ offset {e_phoff} (entry size: {e_phentsize})')
        
        print()
        print('=== Program Headers ===')
        for i in range(e_phnum):
            off = e_phoff + i * e_phentsize
            if off + e_phentsize > len(data):
                print(f'  [{i}] Header beyond file size')
                break
            p_type = struct.unpack_from('<I', data, off)[0]
            p_flags = struct.unpack_from('<I', data, off+4)[0]
            p_offset = struct.unpack_from('<Q', data, off+8)[0]
            p_vaddr = struct.unpack_from('<Q', data, off+16)[0]
            p_filesz = struct.unpack_from('<Q', data, off+32)[0]
            p_memsz = struct.unpack_from('<Q', data, off+40)[0]
            
            type_names = {0:'NULL', 1:'LOAD', 2:'DYNAMIC', 3:'INTERP',
                         4:'NOTE', 5:'SHLIB', 6:'PHDR', 0x70000001:'NOTE'}
            type_str = type_names.get(p_type, f'0x{p_type:x}')
            print(f'  [{i}] type={type_str} offset=0x{p_offset:x} vaddr=0x{p_vaddr:016x} '
                  f'filesz=0x{p_filesz:x} flags={"r" if p_flags&4 else "-"}{"w" if p_flags&2 else "-"}{"x" if p_flags&1 else "-"}')
    else:  # 32-bit
        e_phoff = struct.unpack_from('<I', data, 28)[0]
        e_phentsize = struct.unpack_from('<H', data, 42)[0]
        e_phnum = struct.unpack_from('<H', data, 44)[0]
        print(f'  Program headers: {e_phnum} @ offset {e_phoff} (entry size: {e_phentsize})')
        
        print()
        print('=== Program Headers (32-bit) ===')
        for i in range(e_phnum):
            off = e_phoff + i * e_phentsize
            if off + e_phentsize > len(data):
                print(f'  [{i}] Header beyond file size')
                break
            p_type = struct.unpack_from('<I', data, off)[0]
            p_offset = struct.unpack_from('<I', data, off+4)[0]
            p_vaddr = struct.unpack_from('<I', data, off+8)[0]
            p_filesz = struct.unpack_from('<I', data, off+16)[0]
            p_flags = struct.unpack_from('<I', data, off+24)[0]
            type_names = {0:'NULL', 1:'LOAD', 2:'DYNAMIC', 4:'NOTE'}
            type_str = type_names.get(p_type, f'0x{p_type:x}')
            print(f'  [{i}] type={type_str} offset=0x{p_offset:x} vaddr=0x{p_vaddr:08x} '
                  f'filesz=0x{p_filesz:x}')

print()
print('=== Searching for NOTE segments (raw scan for "CORE" ===')
for i in range(0, min(len(data)-4, 500000), 4):
    if data[i:i+4] == b'CORE':
        print(f'  Found "CORE" at offset 0x{i:x}')
    if data[i:i+8] == b'LINUX\x00\x00\x00':
        print(f'  Found "LINUX" at offset 0x{i:x}')

print()
print('=== String search: CHAKRA ===')
idx = 0
while True:
    idx = data.find(b'CHAKRA', idx)
    if idx == -1:
        break
    print(f'  Found "CHAKRA" at 0x{idx:x}: {data[idx:idx+60]}')
    idx += 1

print()
print('=== Looking for heap-like structures ===')
# Look for consecutive printable strings
printable = bytes(range(0x20, 0x7f))
chunks = []
start = None
for i, b in enumerate(data):
    if b in printable:
        if start is None:
            start = i
    else:
        if start is not None and i - start >= 6:
            s = data[start:i].decode('ascii', errors='replace')
            chunks.append((start, s))
        start = None

print(f'Total printable strings (>=6 chars): {len(chunks)}')
for off, s in chunks[:50]:
    print(f'  0x{off:x}: {s[:80]}')
