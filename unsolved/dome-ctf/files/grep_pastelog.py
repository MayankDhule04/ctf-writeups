import re, glob, os

# find the saved pastebin log
cand = glob.glob(r"C:/Users/mayan/.kiro/sessions/**/tool-outputs/web_fetch-*.txt", recursive=True)
# pick the big one (pastebin ~269KB)
best = None; bestsz = 0
for c in cand:
    sz = os.path.getsize(c)
    if sz > bestsz:
        bestsz = sz; best = c
print("using:", best, bestsz)
txt = open(best, "r", encoding="utf-8", errors="replace").read()

# domains / hostnames (not .internal)
hosts = {}
for m in re.findall(r'\b(?:[a-z0-9-]+\.)+[a-z]{2,10}\b', txt, re.I):
    hl = m.lower()
    hosts[hl] = hosts.get(hl, 0)+1
print("\n=== distinct hostnames (excluding .internal) ===")
for h,c in sorted(hosts.items(), key=lambda x:-x[1]):
    if h.endswith(".internal"): continue
    if h in ("pastebin.com",): 
        print(f"  {c:4d} {h}"); continue
    print(f"  {c:4d} {h}")

print("\n=== full URLs ===")
for u in sorted(set(re.findall(r'https?://[^\s"\'<>]{4,120}', txt))):
    print("  ", u)

print("\n=== lead keywords in context ===")
for kw in ["signal","whisper","room","community","members","login","portal","share","invite","onion","dark","vyrqelith","nightlens"]:
    for m in list(re.finditer(kw, txt, re.I))[:2]:
        i=m.start(); print(f"  [{kw}] ...{txt[max(0,i-60):i+70]}...".replace(chr(10)," "))
