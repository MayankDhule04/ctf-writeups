import re, base64, codecs, binascii

f = r"C:/Users/mayan/.kiro/sessions/583d6e73aa057ab6/sess_a756a6b1-520d-4e05-a397-511ef72c58f2/tool-outputs/web_fetch-98b8d59d.txt"
with open(f, "r", encoding="utf-8", errors="replace") as fh:
    text = fh.read()

# find all ref=VALUE tokens (export_ref, render_ref, url_ref, snap_ref, etc.)
tokens = re.findall(r'(\w+_ref)=([A-Za-z0-9+/=]{10,})', text)
print("total ref tokens:", len(tokens))

def try_decode(val):
    results = []
    # base64
    try:
        pad = val + "=" * (-len(val) % 4)
        d = base64.b64decode(pad)
        results.append(("b64", d))
    except Exception:
        pass
    # base32
    try:
        pad = val.upper() + "=" * (-len(val) % 8)
        d = base64.b32decode(pad)
        results.append(("b32", d))
    except Exception:
        pass
    # hex
    try:
        if re.fullmatch(r'[0-9a-fA-F]+', val) and len(val) % 2 == 0:
            d = bytes.fromhex(val)
            results.append(("hex", d))
    except Exception:
        pass
    return results

flagish = re.compile(rb'[A-Za-z0-9_.]{2,20}\{[^}]{3,80}\}')
dome_hits = []
all_flag_hits = []
for name, val in tokens:
    for method, d in try_decode(val):
        if flagish.search(d):
            m = flagish.search(d).group().decode(errors='replace')
            all_flag_hits.append((name, method, val[:20], m))
            if m.lower().startswith("dome.ctf") or m.lower().startswith("dome_ctf") or "dome.ctf" in m.lower():
                dome_hits.append((name, method, val, m))
        else:
            # try rot13 on decoded text too
            try:
                s = d.decode('latin1')
                rot = codecs.encode(s, 'rot_13')
                if flagish.search(rot.encode('latin1')):
                    m = flagish.search(rot.encode('latin1')).group().decode(errors='replace')
                    all_flag_hits.append((name, method+"+rot13", val[:20], m))
            except Exception:
                pass
    # also try rot13 first then decode
    rot_val = codecs.encode(val, 'rot_13')
    for method, d in try_decode(rot_val):
        if flagish.search(d):
            m = flagish.search(d).group().decode(errors='replace')
            all_flag_hits.append((name, "rot13+"+method, val[:20], m))
            if "dome.ctf" in m.lower():
                dome_hits.append((name, "rot13+"+method, val, m))

print("\n=== all flag-ish decodes ===")
for h in all_flag_hits:
    print(h)

print("\n=== dome.ctf hits ===")
for h in dome_hits:
    print(h)
