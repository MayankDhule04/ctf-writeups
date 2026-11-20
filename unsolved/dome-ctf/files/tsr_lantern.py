import re
js = open(r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\tsr_fresh.js","r",encoding="utf-8",errors="replace").read()

print("lantern occurrences:", len(re.findall(r'lantern', js, re.I)))
for m in re.finditer(r'lantern', js, re.I):
    i=m.start(); print("  ...", js[max(0,i-150):i+200].replace("\n"," "))

print("\n=== all functions.invoke names ===")
for t in sorted(set(re.findall(r'\.invoke\(["\']([^"\']+)["\']', js))): print("  ", t)

print("\n=== .rpc( names ===")
for t in sorted(set(re.findall(r'\.rpc\(["\']([^"\']+)["\']', js))): print("  ", t)

print("\n=== /functions/v1/ paths ===")
for t in sorted(set(re.findall(r'functions/v1/[A-Za-z0-9_\-]+', js))): print("  ", t)

print("\n=== route paths ===")
for t in sorted(set(re.findall(r'path:["\']([^"\']{1,40})["\']', js))): print("  ", repr(t))

print("\n=== storage buckets (.from in storage) ===")
for t in sorted(set(re.findall(r'storage[^;]{0,60}?\.from\(["\']([^"\']+)["\']', js))): print("  ", t)
for t in sorted(set(re.findall(r'\.getPublicUrl\(|\.download\(|\.createSignedUrl\(', js))): print("  storageop:", t)
