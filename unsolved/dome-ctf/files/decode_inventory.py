import re, glob, os, base64, urllib.parse, codecs
path = max(glob.glob(r"C:/Users/mayan/.kiro/sessions/**/tool-outputs/web_fetch-*.txt", recursive=True), key=os.path.getsize)
txt = open(path,"r",encoding="utf-8",errors="replace").read()

# collect all non-standard key=value extras (exclude common log keys)
common={"host","facility","severity","trace_id","request_id","peer","cpu_pct","rss_mb","msg",
        "remote","method","uri","status","bytes","upstream","request_time","upstream_time","tls","cipher",
        "upstream_cluster","upstream_host","response_code","response_flags","duration_ms","bytes_sent","protocol"}
extras={}
for m in re.finditer(r'(\b[a-z_]+)=([A-Za-z0-9+/=_%:\-]{8,})', txt):
    k,v=m.group(1),m.group(2)
    if k in common: continue
    extras.setdefault(k,set()).add(v)

def tryall(v):
    outs=[]
    # url
    if "%" in v:
        try: outs.append(("url", urllib.parse.unquote(v)))
        except: pass
    # strip prefix like render:
    vv=v.split(":")[-1] if ":" in v and not v.startswith("http") else v
    for cand in {v,vv}:
        try:
            d=base64.b64decode(cand+"="*(-len(cand)%4)); 
            if all(32<=c<127 for c in d): outs.append(("b64",d.decode()))
        except: pass
        try:
            d=base64.b32decode(cand.upper()+"="*(-len(cand)%8))
            if all(32<=c<127 for c in d): outs.append(("b32",d.decode()))
        except: pass
        try:
            if re.fullmatch(r'[0-9a-fA-F]+',cand) and len(cand)%2==0:
                d=bytes.fromhex(cand)
                if all(32<=c<127 for c in d): outs.append(("hex",d.decode()))
        except: pass
    return outs

print("=== extra fields decoded ===")
for k,vals in extras.items():
    for v in sorted(vals):
        ds=tryall(v)
        if ds:
            for enc,res in ds:
                print(f"[{k}] ({enc}) {res}")
        else:
            print(f"[{k}] (raw) {v[:80]}")
