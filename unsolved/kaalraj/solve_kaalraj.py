#!/usr/bin/env python3
"""
Two Body One Soul - The second APK has the other half of the flag!
"""

import zipfile

apk_path = "KaalRaj.apk"

print("[*] Two Body One Soul Solver")
print("=" * 70)

# BODY 1: Main APK has these flags
body1_flags = ["IT_My_BE", "GOOD_PROGRESS"]

print(f"[*] BODY 1 (Main APK) flags:")
for flag in body1_flags:
    print(f"  {flag}")

# BODY 2: Encrypted APK - need to decrypt
# The password "VurrAj0" contains "rAj" - this is the key!

print(f"\n[*] BODY 2 (Second APK) - Decrypting with VurrAj0...")

with open('asset_0.bin', 'rb') as f:
    encrypted = f.read()

# Try XOR with VurrAj0
key = b'VurrAj0'
decrypted = bytearray()
for i, byte in enumerate(encrypted):
    decrypted.append(byte ^ key[i % len(key)])

# Save and check
with open('second_body.bin', 'wb') as f:
    f.write(decrypted)

print(f"  First 20 bytes: {bytes(decrypted[:20]).hex()}")

# Check if it's APK
if decrypted[:2] == b'PK':
    print(f"[+] Valid APK!")
    
    with open('second_body.apk', 'wb') as f:
        f.write(decrypted)
    
    # Extract flags from second APK
    with zipfile.ZipFile('second_body.apk', 'r') as second:
        body2_flags = []
        for dex in [f for f in second.namelist() if f.endswith('.dex')]:
            dex_data = second.read(dex)
            if b'Kaal{' in dex_data:
                idx = 0
                while True:
                    idx = dex_data.find(b'Kaal{', idx)
                    if idx == -1:
                        break
                    end = dex_data.find(b'}', idx)
                    if end != -1 and end - idx < 100:
                        flag = dex_data[idx+5:end].decode('utf-8', errors='ignore')  # Extract content only
                        if flag not in body2_flags:
                            body2_flags.append(flag)
                    idx += 1
        
        print(f"\n[*] BODY 2 flags:")
        for flag in body2_flags:
            print(f"  {flag}")
        
        # Combine them
        print(f"\n[*] ONE SOUL (Combined):")
        for f1 in body1_flags:
            for f2 in body2_flags:
                print(f"  Kaal{{{f1}_{f2}}}")
                print(f"  Kaal{{{f2}_{f1}}}")
else:
    print(f"[-] Not a valid APK with VurrAj0")
    
    # Maybe the second body's flag is encoded in the encrypted data itself
    # Or maybe we need to use BOTH fake flags from body 1
    print(f"\n[*] Since second body is encrypted, maybe ONE SOUL means:")
    print(f"  The two fake flags ARE the answer when combined!")
    print(f"\n  Kaal{{IT_My_BE_GOOD_PROGRESS}}")
    print(f"  Kaal{{GOOD_PROGRESS_IT_My_BE}}")
    
    # Or maybe the password IS part of the flag
    print(f"\n[*] Or the password is part of the soul:")
    print(f"  Kaal{{VurrAj0_IT_My_BE}}")
    print(f"  Kaal{{IT_My_BE_VurrAj0}}")
    print(f"  Kaal{{VurrAj0_GOOD_PROGRESS}}")

print("\n" + "=" * 70)
