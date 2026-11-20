import re
f = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\signalroom_app.js"
js = open(f, "r", encoding="utf-8", errors="replace").read()

# React compiled JSX uses children:"..." for text. Grab those.
children = re.findall(r'children:"((?:[^"\\]|\\.){6,300})"', js)
# also title/label/name/alt/placeholder values
others = re.findall(r'(?:name|title|label|alt|placeholder|role|verdict|tag):"((?:[^"\\]|\\.){4,120})"', js)

def clean(s):
    return s.encode().decode("unicode_escape", "replace") if "\\u" in s else s

out = []
seen = set()
out.append("=== substantial text (children) ===")
for c in children:
    c2 = c.strip()
    if len(c2) < 8: continue
    if re.fullmatch(r'[\w\s:/\-\[\].#%]+', c2) and ' ' not in c2: continue
    if c2 in seen: continue
    seen.add(c2)
    out.append("  " + c2[:220])

out.append("\n=== names/labels/verdicts ===")
for o in sorted(set(others)):
    out.append("  " + o[:120])

open(r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\site_text.txt", "w", encoding="utf-8").write("\n".join(out))
print("wrote site_text.txt lines:", len(out))
