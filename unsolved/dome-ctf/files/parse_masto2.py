import json, re, html

f = r"C:/Users/mayan/.kiro/sessions/583d6e73aa057ab6/sess_a756a6b1-520d-4e05-a397-511ef72c58f2/tool-outputs/web_fetch-5206c389.txt"
raw = open(f, "r", encoding="utf-8", errors="replace").read()
start = raw.find("[{"); end = raw.rfind("}]")
data = json.loads(raw[start:end+2])

oct8 = [s for s in data if s["created_at"].startswith("2026-10-08")]
oct8.sort(key=lambda x: x["created_at"])
for s in oct8:
    print("="*60)
    print("id", s["id"], s["created_at"])
    print("content raw:", repr(s["content"]))
    print("media:", json.dumps(s.get("media_attachments"), indent=2)[:1500])
    print("card:", json.dumps(s.get("card"))[:500])
    print("tags:", [t.get("name") for t in s.get("tags",[])])
