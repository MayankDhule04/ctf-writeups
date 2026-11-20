import re
f = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\tsr_app.js"
js = open(f, "r", encoding="utf-8", errors="replace").read()

lits = re.findall(r'"((?:[^"\\]|\\.){4,240})"', js)
lits += re.findall(r"'((?:[^'\\]|\\.){4,240})'", js)
lits += re.findall(r'`((?:[^`\\]|\\.){4,240})`', js)

out=[]
seen=set()
for s in lits:
    if s in seen: continue
    seen.add(s)
    # keep strings that look like human text / messages / codes (has a space OR looks like a sentence/word with meaning)
    if re.search(r'[A-Za-z]', s) and (' ' in s or re.search(r'[A-Z][a-z]{3,}', s)):
        # drop css utility class strings
        if re.fullmatch(r'[\w\s:\-\[\]/.#%()*,>+~&]*', s) and ('flex' in s or 'text-' in s or 'bg-' in s or 'rounded' in s or 'px-' in s or 'py-' in s or 'grid' in s):
            continue
        out.append(s)

open(r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\tsr_allstrings.txt","w",encoding="utf-8").write("\n".join(out))
print("total literals:", len(lits), "kept:", len(out))
