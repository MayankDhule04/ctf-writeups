import re
f = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\tsr_app.js"
js = open(f, "r", encoding="utf-8", errors="replace").read()
out=[]

out.append("=== quoted path-like tokens ===")
for m in sorted(set(re.findall(r'["\'`](/[a-zA-Z0-9_][a-zA-Z0-9_/-]{1,40})["\'`]', js))):
    out.append("  "+m)

out.append("\n=== readable UI text (children/text) ===")
seen=set()
for m in re.findall(r'children:["\']((?:[^"\'\\]|\\.){5,120})["\']', js):
    s=m.strip()
    if s in seen: continue
    seen.add(s)
    if re.search(r'[A-Za-z]{3}', s):
        out.append("  "+s[:140])

out.append("\n=== words of interest ===")
for kw in ["Sign in","Sign In","Signin","Log in","Login","Access","Invite","invite","Request","Pending","Approved","Members","Member","Chapter","Salon","Dossier","Welcome","Enter","passcode","Password","code","Unauthorized","Forbidden","token","email","verify","Join","Apply","Admin","admin","flag","dome"]:
    hits=[mm.start() for mm in re.finditer(re.escape(kw), js)]
    if hits:
        out.append(f"[{kw}] {len(hits)}")

open(r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\tsr_strings.txt","w",encoding="utf-8").write("\n".join(out))
print("wrote", len(out), "lines")
