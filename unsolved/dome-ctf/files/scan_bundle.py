import re
f = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\signalroom_app.js"
js = open(f, "r", encoding="utf-8", errors="replace").read()

print("=== flag-ish / story terms ===")
for t in ["dome", "nightfall", "ctf{", "flag", "signal room", "signalroom", "vyrqelith",
          "member", "invite", "passcode", "credential", "beagle", ".onion", "tor", "render", "share"]:
    hits = [m.start() for m in re.finditer(re.escape(t), js, re.I)]
    if hits:
        print(f"\n[{t}] {len(hits)} hits")
        for i in hits[:3]:
            print("   ...", js[max(0,i-70):i+90].replace("\n"," "), "...")

print("\n=== .pdf / download / file paths ===")
for m in sorted(set(re.findall(r'[\w./-]*\.(?:pdf|zip|json|txt|md)\b', js))):
    print("  ", m)

print("\n=== long base64-ish literals (>=24) ===")
for s in sorted(set(re.findall(r'["\x27]([A-Za-z0-9+/]{24,}={0,2})["\x27]', js))):
    if not re.fullmatch(r'[0-9a-f]+', s):  # skip pure hex hashes maybe
        print("  ", s[:80])

print("\n=== JS comments ===")
for m in re.finditer(r'/\*[^*][\s\S]{0,200}?\*/', js):
    c = m.group()
    if 'license' not in c.lower() and 'react' not in c.lower() and 'copyright' not in c.lower():
        print("  ", c[:160].replace("\n"," "))
