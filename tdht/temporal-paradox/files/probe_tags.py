"""Create R9CF records with a single module entry each, feed to r9sampler, observe output."""
import struct, os

def crc16(data):
    v=0xffff
    for byte in data:
        v^=(byte<<8); v&=0xffff
        for _ in range(8):
            v=((v<<1)^0x1021)&0xffff if v&0x8000 else (v<<1)&0xffff
    return v

def make_record(lane, entries):
    """entries = list of (tag_byte, payload_bytes)"""
    body = b''
    for tag, payload in entries:
        body += bytes([tag, len(payload)]) + payload
    # R9CF + lane(1) + len_lo + len_hi + 0x00 + body + crc16(2)
    inner = bytes([lane]) + b'\x00\x00\x00' + body  # lane, placeholder len, 0x00
    # total = 4(magic) + 1(lane) + 2(len) + 1(zero) + body + 2(crc)
    total_len = 4 + 1 + 2 + 1 + len(body) + 2
    # Actually looking at rec format: R9CF(4) [4]=lane [5..6]=len_le [7]=0 then entries then crc
    rec = b'R9CF' + bytes([lane]) + struct.pack('<H', total_len) + b'\x00' + body
    c = crc16(rec)
    rec += struct.pack('>H', c)
    return rec

os.makedirs("probes", exist_ok=True)

# Tags observed in the records
tags = [0x22,0x31,0x35,0x38,0x3a,0x3c,0x46,0x49,0x53,0x6b,0x6d,
        0x84,0x90,0x9d,0xa9,0xc0,0xc1,0xd2,0xd3,0xd4,0xd5]

# Create one record per tag with a 1-byte payload = 0x01
for tag in tags:
    rec = make_record(1, [(tag, b'\x01')])
    fname = f"probes/tag_{tag:02x}.bin"
    open(fname, "wb").write(rec)

# Also create a combined record with ALL tags
all_entries = [(tag, b'\x01') for tag in tags]
rec = make_record(1, all_entries)
open("probes/all_tags.bin", "wb").write(rec)

# Write a shell script to test them all
lines = ["#!/bin/bash", "cd /data"]
for tag in tags:
    lines.append(f'echo -n "tag_{tag:02x}: "; /data/extracted/usr/local/sbin/r9sampler /data/probes/tag_{tag:02x}.bin')
lines.append('echo -n "all_tags: "; /data/extracted/usr/local/sbin/r9sampler /data/probes/all_tags.bin')
open("probes/test.sh", "w", newline='\n').write('\n'.join(lines)+'\n')
print("created", len(tags), "probe files + all_tags + test.sh")
