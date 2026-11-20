import json, re, html

f = r"C:/Users/mayan/.kiro/sessions/583d6e73aa057ab6/sess_a756a6b1-520d-4e05-a397-511ef72c58f2/tool-outputs/web_fetch-3127c53d.txt"
raw = open(f, "r", encoding="utf-8", errors="replace").read()
s = raw.find("[{"); e = raw.rfind("}]")
data = json.loads(raw[s:e+2])

def clean(h):
    t = re.sub(r"<[^>]+>", " ", h)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()

print("count", len(data))
for st in sorted(data, key=lambda x: x["created_at"]):
    c = clean(st["content"])
    hrefs = re.findall(r'href="([^"]+)"', st["content"])
    nonTag = [h for h in hrefs if "/tags/" not in h]
    print(st["created_at"][:16], "|", c[:220])
    if nonTag:
        print("    LINKS:", nonTag)
