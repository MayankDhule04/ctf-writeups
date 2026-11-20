import importlib.util
spec=importlib.util.spec_from_file_location("emu2", r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\emulate2.py")
emu=importlib.util.module_from_spec(spec); spec.loader.exec_module(emu)

PRINT=[c for c in range(0x21,0x7f) if c!=ord('}')]  # printable, no '}' inside (keep '}' only at end)

# Template: IATCQ{ + 25 inner + }
# Fix inner bytes 6..29 to a readable filler, brute inner[28],[29] (positions 28,29) over printable
# to hit the target. 95*95 ~ 9025 emulator runs — fast.
base = bytearray(b"IATCQ{" + b"_"*25 + b"}")   # 6+25+1 = 32
assert len(base)==32

def try_solve(filler_fn):
    inp = bytearray(base)
    for i in range(6,31):
        inp[i] = filler_fn(i)
    inp[31] = ord('}')
    for a in PRINT:
        inp[28]=a
        for b in PRINT:
            inp[29]=b
            ok,st,fv = emu.run(bytes(inp))
            if ok:
                return bytes(inp)
    return None

# Try several readable fillers so the recovered flag looks natural where possible
import itertools
fillers = [
    (lambda i: ord('_')),
    (lambda i: ord('a')),
    (lambda i: ord('0')),
    (lambda i: ord('A') + ((i-6)%26)),
    (lambda i: ord('a') + ((i*7+3)%26)),
]
for k,f in enumerate(fillers):
    out = try_solve(f)
    if out:
        ok,st,fv = emu.run(out)
        print(f"FILLER {k}: {out.decode('latin1')}  ok={ok} fnv={fv:08x}")
        break
else:
    print("no hit with last-pair brute; widening to last 3 free bytes")
    # widen: brute positions 27,28,29 with filler '_'
    inp=bytearray(base)
    for i in range(6,31): inp[i]=ord('_')
    inp[31]=ord('}')
    found=None
    for a in PRINT:
        inp[27]=a
        for b in PRINT:
            inp[28]=b
            for c in PRINT:
                inp[29]=c
                ok,st,fv=emu.run(bytes(inp))
                if ok:
                    found=bytes(inp); break
            if found: break
        if found: break
    if found:
        ok,st,fv=emu.run(found)
        print("WIDE HIT:", found.decode('latin1'), "ok",ok, hex(fv))
    else:
        print("none")
