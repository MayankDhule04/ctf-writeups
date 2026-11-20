import re, glob, os, base64, urllib.parse, codecs
path = max(glob.glob(r"C:/Users/mayan/.kiro/sessions/**/tool-outputs/web_fetch-*.txt", recursive=True), key=os.path.getsize)
txt = open(path,"r",encoding="utf-8",errors="replace").read()

# grab the interesting elaborate fields
fields=["cache_key","enc_ctx","cryptographic_context","trace_ctx","next","dedupe_key","cache_tag","annotation"]
vals={}
for f in fields:
    for m in re.finditer(rf'{f}=([^\s"]+)', txt):
        vals.setdefault(f,set()).add(m.group(1))

def layers(v, depth=0, trail=""):
    """recursively try to decode and yield readable results"""
    outs=[]
    if depth>3: return outs
    v2=v
    # strip known prefixes
    for pre in ("render:","ttl-","sign:"):
        if v2.startswith(pre): v2=v2[len(pre):]
    cands=set([v,v2])
    # also split on : and take parts
    for part in re.split(r'[:&=]', v2):
        if len(part)>=8: cands.add(part)
    for c in cands:
        # url
        if "%" in c:
            u=urllib.parse.unquote(c)
            if u!=c: outs.append((trail+"url", u)); outs+=layers(u,depth+1,trail+"url>")
        # b64
        try:
            d=base64.b64decode(c+"="*(-len(c)%4))
            s=d.decode("utf-8")
            if sum(32<=ord(ch)<127 for ch in s)>=len(s)*0.8:
                outs.append((trail+"b64",s)); outs+=layers(s,depth+1,trail+"b64>")
        except: pass
        # b32
        try:
            d=base64.b32decode(c.upper()+"="*(-len(c)%8))
            s=d.decode("utf-8")
            if sum(32<=ord(ch)<127 for ch in s)>=len(s)*0.8:
                outs.append((trail+"b32",s)); outs+=layers(s,depth+1,trail+"b32>")
        except: pass
        # hex
        try:
            if re.fullmatch(r'[0-9a-fA-F]+',c) and len(c)%2==0:
                d=bytes.fromhex(c); s=d.decode("utf-8")
                if sum(32<=ord(ch)<127 for ch in s)>=len(s)*0.8:
                    outs.append((trail+"hex",s)); outs+=layers(s,depth+1,trail+"hex>")
        except: pass
    return outs

interest=re.compile(r'http|archive|api/v3|inventory|forwarded|x-real|x-client|spiffe|header|internal|172\.|10\.44|dome\.ctf|T-?484|/v3/', re.I)
for f,vs in vals.items():
    for v in sorted(vs):
        res=layers(v)
        for enc,r in res:
            if interest.search(r):
                print(f"[{f}] {enc}: {r[:160]}  <<<")
            else:
                print(f"[{f}] {enc}: {r[:100]}")
