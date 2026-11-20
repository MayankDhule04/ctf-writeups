import glob, os
path = max(glob.glob(r"C:/Users/mayan/.kiro/sessions/**/tool-outputs/web_fetch-*.txt", recursive=True), key=os.path.getsize)
lines = open(path, "r", encoding="utf-8", errors="replace").read().splitlines()
# skip the wrapper header (first few lines are web_fetch metadata)
# find where the actual log starts
start = 0
for i, l in enumerate(lines):
    if l.startswith("2026-"):
        start = i; break
log = lines[start:]
print(f"log starts at wrapper line {start}, total log lines: {len(log)}")

# line 484 of the log
for offset in [483, 484, 485]:  # 0-indexed vs 1-indexed
    if offset < len(log):
        print(f"\n=== log line {offset+1} ===")
        print(log[offset][:500])

# also search for req-00001484
print("\n=== req containing 484 ===")
for l in log:
    if "1484" in l or "484" in l[:80]:
        print(l[:500])
        print("---")
