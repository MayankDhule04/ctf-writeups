import re, glob, os
path = max(glob.glob(r"C:/Users/mayan/.kiro/sessions/**/tool-outputs/web_fetch-*.txt", recursive=True), key=os.path.getsize)
txt = open(path,"r",encoding="utf-8",errors="replace").read()
lines = txt.splitlines()

def show(pred, label, n=40):
    print(f"\n##### {label} #####")
    c=0
    for ln in lines:
        if pred(ln):
            print(ln[:500]); c+=1
            if c>=n: break

show(lambda l: "uri=" in l or "nginx" in l.lower(), "nginx/uri access lines")
show(lambda l: "inventory" in l.lower() or "upstream" in l.lower() or "envoy" in l.lower(), "envoy/inventory")
show(lambda l: "archive" in l.lower(), "archive")
show(lambda l: re.search(r'[Xx]-(forwarded|real|client|internal|origin|trusted)', l), "forwarding headers")
show(lambda l: "T-484" in l or "T484" in l or "484" in l and ("archive" in l.lower() or "record" in l.lower() or "evidence" in l.lower()), "T-484")
# header-ish key=value tokens in msg
print("\n##### header-like tokens (x_... / *_header / client_ip / forwarded_for) #####")
toks=set(re.findall(r'[A-Za-z][A-Za-z0-9_\-]*(?:forwarded|client|real|origin|internal|trust|header|caller|source)[A-Za-z0-9_\-]*', txt, re.I))
for t in sorted(toks)[:60]: print("  ", t)
