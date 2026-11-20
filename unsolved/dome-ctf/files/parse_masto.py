import json, re, html

f = r"C:/Users/mayan/.kiro/sessions/583d6e73aa057ab6/sess_a756a6b1-520d-4e05-a397-511ef72c58f2/tool-outputs/web_fetch-5206c389.txt"
raw = open(f, "r", encoding="utf-8", errors="replace").read()
# strip the wrapper, find the JSON array
start = raw.find("[{")
end = raw.rfind("}]")
data = json.loads(raw[start:end+2])

def clean(h):
    t = re.sub(r"<[^>]+>", " ", h)
    t = html.unescape(t)
    return re.sub(r"\s+", " ", t).strip()

print("total statuses:", len(data))
for s in sorted(data, key=lambda x: x["created_at"]):
    txt = clean(s["content"])
    urls = [a["url"] for a in s.get("tags", [])]
    # also extract hrefs from content
    hrefs = re.findall(r'href="([^"]+)"', s["content"])
    card = s.get("card")
    cardurl = card["url"] if card else None
    print(f"[{s['created_at']}] id={s['id']} reply_to={s['in_reply_to_id']}")
    print("   ", txt[:400])
    if hrefs:
        print("   HREFS:", hrefs)
    if cardurl:
        print("   CARD:", cardurl, "|", card.get("title"))
    print()
