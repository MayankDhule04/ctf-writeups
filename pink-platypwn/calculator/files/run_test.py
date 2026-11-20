#!/usr/bin/env python3
import sys, re, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))

lib = open(os.path.join(HERE,"lib_pink.tns.xml"),"rb").read().decode("utf-8","replace")
alphabet = re.search(r'alphabet\s*=\s*"([^"]*)"', lib).group(1)
print("alphabet repr:", repr(alphabet), "len", len(alphabet))
print("ords:", [ord(c) for c in alphabet])

nums = [int(f) for f in re.findall(r'\\u([0-9a-fA-F]{4})', lib)]
print("nums:", nums, "max", max(nums), "len", len(nums))

# emulate program exactly, catching the crash
f = ""
for i, n in enumerate(nums):
    try:
        f += alphabet[n]
    except IndexError:
        f += f"‹IDX{n}›"
print("program output:", f)
