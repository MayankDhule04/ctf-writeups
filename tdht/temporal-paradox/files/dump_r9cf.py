import os
p=r"Temporal Paradox/gateway_snapshot.img"
b=open(p,"rb").read()
offs=[0x15cf30a,0x15d030a,0x15d130a,0x15d230a,0x15d330a,0x15d430a,0x15d530a,0x15d630a,0x15d730a,0x15d830a,0x15d930a,0x15da30a]
os.makedirs("r9cf",exist_ok=True)
for i,o in enumerate(offs):
    ln=b[o+5]|(b[o+6]<<8)
    rec=b[o:o+ln]
    open(f"r9cf/rec{i:02d}.bin","wb").write(rec)
    print(i, hex(o), "len",ln, "sha", rec.hex()[:32])
# also dump the two .cal decoys region at 0x15e2000
for i,o in enumerate([0x15e2000,0x15e3000]):
    # find C9TR record length ~40
    rec=b[o:o+40]
    open(f"r9cf/cal{i}.bin","wb").write(rec)
    print("cal",i,hex(o),rec.hex())
