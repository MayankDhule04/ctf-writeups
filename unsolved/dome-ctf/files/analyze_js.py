import re

f = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\signalroom_app.js"
js = open(f, "r", encoding="utf-8", errors="replace").read()
print("len:", len(js))

# Extract all quoted string literals
strings = re.findall(r'"((?:[^"\\]|\\.){2,200})"', js)
strings += re.findall(r"'((?:[^'\\]|\\.){2,200})'", js)

interesting = []
kw = re.compile(r'(/admin|/private|/login|/logout|/dashboard|/member|/community|/portal|/api|password|passcode|secret|token|bearer|authoriz|invite|access.?code|form_success|\.pdf|dome\.ctf|flag|signalroom|brand.?test|unlock|gate|restricted|login|signin|sign-in|cred)', re.I)

seen = set()
for s in strings:
    if kw.search(s) and s not in seen:
        # skip obvious css/react noise
        if len(s) > 180: 
            continue
        seen.add(s)
        interesting.append(s)

print(f"\n=== {len(interesting)} interesting string literals ===")
for s in interesting:
    print(repr(s))
