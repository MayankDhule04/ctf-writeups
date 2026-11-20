import re, base64, codecs, glob, os

cand = glob.glob(r"C:/Users/mayan/.kiro/sessions/**/tool-outputs/web_fetch-*.txt", recursive=True)
best = max(cand, key=os.path.getsize)
txt = open(best, "r", encoding="utf-8", errors="replace").read()
print("paste file:", os.path.basename(best), len(txt), "bytes")

# 1) direct search for fallback/share/sink/endpoint context lines
print("\n=== lines mentioning fallback/share/sink/endpoint/9f34f9/artifact ===")
for ln in txt.splitlines():
    if re.search(r'fallback|share|sink=|endpoint|9f34f9|artifact-cache|export', ln, re.I):
        print("  ", ln[:400])

# 2) decode ALL *_ref and *=TOKEN fields, look for URLs/domains in decoded output
tokens = re.findall(r'(\w+)=([A-Za-z0-9+/=_-]{12,})', txt)
def tries(v):
    out=[]
    try: out.append(("b64", base64.b64decode(v+"="*(-len(v)%4))))
    except: pass
    try: out.append(("b32", base64.b32decode(v.upper()+"="*(-len(v)%8))))
    except: pass
    try:
        if re.fullmatch(r'[0-9a-fA-F]+',v) and len(v)%2==0: out.append(("hex",bytes.fromhex(v)))
    except: pass
    return out

urlpat = re.compile(rb'(?:https?://|www\.|[a-z0-9-]+\.(?:in|com|net|org|io|xyz|onion|app|site|link|sh|me|co|dev))', re.I)
print("\n=== ref fields decoding to URL/domain-like strings ===")
seen=set()
for key,val in tokens:
    for meth, dec in tries(val):
        if urlpat.search(dec):
            try: s=dec.decode('latin1')
            except: s=repr(dec)
            k=(key,meth,s)
            if k in seen: continue
            seen.add(k)
            print(f"  {key} [{meth}] -> {s[:120]}")
        # rot13 then decode
    rv=codecs.encode(val,'rot_13')
    for meth,dec in tries(rv):
        if urlpat.search(dec):
            s=dec.decode('latin1','replace')
            k=(key,'rot13+'+meth,s)
            if k in seen: continue
            seen.add(k)
            print(f"  {key} [rot13+{meth}] -> {s[:120]}")
