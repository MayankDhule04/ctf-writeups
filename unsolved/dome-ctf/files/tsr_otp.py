import re
js = open(r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\tsr_fresh.js","r",encoding="utf-8",errors="replace").read()

# full anon JWT (3 segments)
m = re.search(r'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+', js)
print("ANON KEY:", m.group() if m else "NOT FOUND")

# supabase.from("table") reads
print("\n=== .from(\"table\") ===")
for t in sorted(set(re.findall(r'\.from\(["\']([^"\']+)["\']\)', js))):
    print("  ", t)

# functions.invoke(...)
print("\n=== functions.invoke ===")
for t in sorted(set(re.findall(r'functions\.invoke\(["\']([^"\']+)["\']', js))):
    print("  ", t)

# dump wide context around each custom-otp usage
print("\n=== custom-otp contexts ===")
for m in re.finditer(r'custom-otp', js):
    i=m.start()
    print("----")
    print(js[max(0,i-400):i+700])
