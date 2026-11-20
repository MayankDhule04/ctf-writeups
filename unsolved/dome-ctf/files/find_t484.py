import re, glob, os

targets = []
# phone image
img = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\MOBILE-EVIDENCE\MOBILE-EVIDENCE.img"
# carved dbs + bundle + pastebin
others = glob.glob(r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\carved_dbs\*.sqlite")
others += [r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\tsr_fresh.js"]
pb = glob.glob(r"C:/Users/mayan/.kiro/sessions/**/tool-outputs/web_fetch-*.txt", recursive=True)
if pb: others.append(max(pb, key=os.path.getsize))

needles = [b"T-484", b"T484", b"t-484", b"inventory", b"/api/v3", b"archive",
           b"X-Forwarded", b"x-forwarded", b"X-Real", b"restricted", b"artifact-cache",
           b"172.18", b"forwarded-client"]

def scan(path, label, stream=False):
    print(f"\n### {label} ###")
    hits={}
    if stream:
        with open(path,"rb") as fh:
            prev=b""; off=0
            while True:
                d=fh.read(16*1024*1024)
                if not d: break
                buf=prev+d
                for n in needles:
                    s=0
                    while True:
                        i=buf.find(n,s)
                        if i<0: break
                        hits.setdefault(n,[]).append(off-len(prev)+i); s=i+1
                prev=buf[-64:]; off+=len(d)
    else:
        data=open(path,"rb").read()
        for n in needles:
            c=data.count(n)
            if c: hits[n]=c
    for n,v in hits.items():
        print(f"  {n.decode('latin1')}: {v if isinstance(v,int) else len(v)}")
    if not hits: print("  (none)")

scan(img, "PHONE IMAGE", stream=True)
for o in others:
    scan(o, os.path.basename(o))
