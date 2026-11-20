#!/usr/bin/env python3
d=open(r"c:\Users\mayan\OneDrive\Desktop\ctf\xeno_out.bin","rb").read()
eoi=d.rfind(b"\xff\xd9")
print("len",len(d),"last EOI at",eoi,"trailing after EOI:",len(d)-(eoi+2))
print("trailing bytes:",d[eoi+2:eoi+200])
import re
# strings with flag-ish readable text
for pat in [rb'spooky\{[ -~]{1,90}\}', rb'flag\{[ -~]{1,90}\}', rb'xeno[ -~]{0,90}']:
    for m in re.finditer(pat,d,re.I):
        print("HIT:",m.group()[:120])
# any long ascii runs
runs=re.findall(rb'[ -~]{12,}',d)
print("num ascii runs>=12:",len(runs))
for r in runs[:40]:
    print("  ascii:",r[:120].decode('latin1'))
