#!/usr/bin/env python3
import re, ast, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D7 = open(r"c:\Users\mayan\OneDrive\Desktop\ctf\flashback_scripts\scripts\__Packages\D7.as").read()
MZ = open(r"c:\Users\mayan\OneDrive\Desktop\ctf\flashback_scripts\scripts\__Packages\Maze.as").read()
def arr(src, fn):
    m = re.search(r"static function "+fn+r"\([^)]*\)\s*\{\s*return (\[.*?\]);\s*\}", src, re.S)
    return ast.literal_eval(m.group(1))
q2 = arr(D7,"c"); q3 = arr(D7,"d")

# 1) exact h7 output
h7arr=[9,38,58,176,236,243,153,145,197,161,70,75,9,116,14,10,40,44,175,244,249,135,243,169,176,85,68,105,126,15,117]
h7="".join(chr(h7arr[i]^((i*17+93)&0xFF)) for i in range(len(h7arr)))
print("h7() =", repr(h7))

def decode_q4(level):
    seed=q2[level]%2147483647
    if seed<=0: seed=1
    enc=q3[level]; out=[]
    for i in range(len(enc)):
        seed=seed*48271%2147483647
        out.append(enc[i]^(seed%65536))
    return out

def printable_runs(b, minlen=4):
    return re.findall(rb"[\x20-\x7e]{%d,}"%minlen, b)

for lvl in range(len(q3)):
    q4=decode_q4(lvl)
    variants={
      "hi_lo": bytes(x>>8 for x in q4)+bytes(x&0xff for x in q4),
      "word_be": b"".join(x.to_bytes(2,"big") for x in q4),
      "word_le": b"".join(x.to_bytes(2,"little") for x in q4),
      "lowbyte": bytes(x&0xff for x in q4),
      "highbyte": bytes(x>>8 for x in q4),
    }
    for nm,b in variants.items():
        for run in printable_runs(b,5):
            if b"PINK" in run or b"pink" in run.lower() or len(run)>=10:
                print(f"L{lvl+1} {nm}: {run!r}")
    # bitstream as ascii (8-bit, msb first)
    bits=[]
    for x in q4:
        for k in range(15,-1,-1): bits.append((x>>k)&1)
    for off in range(8):
        bs=bits[off:]
        bts=bytes(int("".join(map(str,bs[i:i+8])),2) for i in range(0,len(bs)-8,8))
        for run in printable_runs(bts,6):
            if b"PINK" in run or b"pink" in run.lower():
                print(f"L{lvl+1} bitstream off={off}: {run!r}")
print("search done")
