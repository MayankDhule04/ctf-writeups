#!/usr/bin/env python3
"""Recover the exfiltrated .env file from ICMP echo payloads in capture.pcap.

Run: PYTHONPATH=/projects/sandbox/pylibs python3 solve.py
"""
import gzip
import re
from scapy.all import rdpcap, IP, ICMP

SRC, DST = "10.13.37.52", "203.0.113.66"

chunks = {}
for pkt in rdpcap("capture.pcap"):
    if pkt.haslayer(ICMP) and pkt[IP].src == SRC and pkt[IP].dst == DST and pkt[ICMP].type == 8:
        d = bytes(pkt[ICMP].payload)
        # d[0:16]  = normal ping struct timeval (keeps it looking like iputils ping)
        # d[16:18] = chunk index (big-endian), d[18:20] = total chunks (0x0025 = 37)
        # d[20:]   = 36-byte data chunk (last one shorter); retransmits are identical
        idx = int.from_bytes(d[16:18], "big")
        chunks[idx] = d[20:]

blob = b"".join(chunks[i] for i in sorted(chunks))
plain = gzip.decompress(bytes(c ^ 0xE3 for c in blob))  # single-byte XOR, then gzip
open("payload.bin", "wb").write(plain)
print(re.search(rb"ctf7\{[^}]+\}", plain).group().decode())
