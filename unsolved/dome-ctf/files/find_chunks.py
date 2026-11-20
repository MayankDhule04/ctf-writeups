import re
f = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\signalroom_app.js"
js = open(f, "r", encoding="utf-8", errors="replace").read()

chunks = sorted(set(re.findall(r'assets/[\w.-]+\.js', js)))
print("CHUNK PATHS:")
for c in chunks: print("  ", c)

files = sorted(set(re.findall(r'([\w]+-[A-Za-z0-9_-]{8}\.js)', js)))
print("\nHASHED JS FILE REFS:")
for c in files: print("  ", c)

paths = sorted(set(re.findall(r'path:\s*["\']([^"\']{1,50})["\']', js)))
print("\nREACT-ROUTER PATHS:")
for p in paths: print("  ", repr(p))

# dynamic import markers
imp = sorted(set(re.findall(r'import\(["\']([^"\']+)["\']\)', js)))
print("\nDYNAMIC IMPORTS:")
for p in imp: print("  ", p)
