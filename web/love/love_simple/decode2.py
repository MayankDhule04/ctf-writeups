import base64
import requests
import json
import sys

BASE_URL = "https://love-pagal-haiiiiiii.onrender.com"

r = requests.get(f"{BASE_URL}/api/flag", timeout=15)
flag_data = r.json()["flag"]

parts = flag_data.split("||")

with open("flag_analysis.txt", "w", encoding="utf-8") as f:
    f.write(f"Parts count: {len(parts)}\n")
    f.write(f"Part lengths: {set(len(p) for p in parts)}\n\n")
    
    all_decoded = []
    for i, part in enumerate(parts):
        try:
            padded = part + "=" * ((8 - len(part) % 8) % 8)
            decoded = base64.b32decode(padded)
            all_decoded.append(decoded)
            f.write(f"Part {i:3d}: {decoded.hex()}\n")
        except Exception as e:
            f.write(f"Part {i:3d}: ERROR: {e}\n")
            all_decoded.append(b"")
    
    full_decoded = b"".join(all_decoded)
    f.write(f"\nTotal decoded bytes: {len(full_decoded)}\n")
    f.write(f"Full hex: {full_decoded.hex()}\n")
    
    # Pattern analysis
    f.write("\n=== Pattern analysis (skip bytes) ===\n")
    for skip in [1, 2, 3, 4, 5, 10, 15]:
        chars = []
        for b in full_decoded[::skip]:
            if 32 <= b < 127:
                chars.append(chr(b))
            else:
                chars.append('.')
        f.write(f"Skip {skip}: {''.join(chars[:200])}\n")
    
    # XOR analysis
    f.write("\n=== XOR with single byte ===\n")
    for key_byte in range(256):
        result = bytes(b ^ key_byte for b in full_decoded)
        try:
            text = result.decode('ascii')
            if 'TRACE' in text or 'CTF' in text:
                f.write(f"XOR key {key_byte} (0x{key_byte:02x}): {text[:200]}\n")
        except:
            # Check partial
            for j in range(0, len(result) - 10, 1):
                try:
                    chunk = result[j:j+10].decode('ascii')
                    if 'TRACE' in chunk:
                        f.write(f"XOR key {key_byte} at offset {j}: {chunk}\n")
                except:
                    pass
    
    # First char of each part
    first_chars = "".join(p[0] for p in parts if p)
    f.write(f"\nFirst char of each part: {first_chars}\n")
    
    # Each part is 24 chars (base32) = 15 bytes
    # 125 parts, some structure?
    # 125 = 5 * 25
    # Maybe it's a 5x25 grid or 25x5 grid
    
    f.write("\n=== Grid analysis (5x25) ===\n")
    for row in range(5):
        row_parts = parts[row*25:(row+1)*25]
        row_first = "".join(p[0] for p in row_parts)
        f.write(f"Row {row}: {row_first}\n")
    
    f.write("\n=== Grid analysis (25x5) ===\n")
    for row in range(25):
        row_parts = parts[row*5:(row+1)*5]
        row_first = "".join(p[0] for p in row_parts)
        f.write(f"Row {row}: {row_first}\n")
    
    # Try reading column-wise from 5x25
    f.write("\n=== Column-wise from 5x25 ===\n")
    grid_5x25 = [parts[i*25:(i+1)*25] for i in range(5)]
    for col in range(25):
        col_parts = [grid_5x25[row][col] for row in range(5)]
        col_first = "".join(p[0] for p in col_parts)
        f.write(f"Col {col}: {col_first}\n")
    
    # Maybe the answer is in the structure of each decoded part
    # Each 15-byte block could contain something at a specific offset
    f.write("\n=== Byte at position N from each decoded part ===\n")
    for pos in range(15):
        chars = []
        for d in all_decoded:
            if len(d) > pos:
                b = d[pos]
                if 32 <= b < 127:
                    chars.append(chr(b))
                else:
                    chars.append(f"[{b:02x}]")
            else:
                chars.append("?")
        line = "".join(chars)
        f.write(f"Pos {pos:2d}: {line}\n")
        if 'TRACE' in line or 'CTF' in line:
            f.write(f"  *** POTENTIAL FLAG ***\n")

print("Analysis written to flag_analysis.txt")
