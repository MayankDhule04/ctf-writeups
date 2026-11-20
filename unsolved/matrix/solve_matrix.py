#!/usr/bin/env python3
"""
Matrix Image Steganography Solver
Challenge: "A message hides where eyes rarely search"
Author: catty_batty4
"""

from PIL import Image
import os

image_path = "image_sJM6Gg8.jpg"

print("[*] Matrix Steganography Solver")
print("=" * 70)

# 1. Check EXIF data
print("\n[1] Checking EXIF/Metadata...")
try:
    img = Image.open(image_path)
    exif_data = img._getexif()
    if exif_data:
        print("[+] EXIF data found:")
        for tag, value in exif_data.items():
            print(f"    {tag}: {value}")
    else:
        print("[-] No EXIF data found")
except Exception as e:
    print(f"[-] Error reading EXIF: {e}")

# 2. Check for strings in the file
print("\n[2] Searching for readable strings...")
try:
    with open(image_path, 'rb') as f:
        data = f.read()
        # Look for flag pattern
        if b'Kaal{' in data:
            print("[+] Found 'Kaal{' in file!")
            # Extract around it
            idx = data.find(b'Kaal{')
            snippet = data[idx:idx+100]
            print(f"    {snippet}")
        else:
            print("[-] No 'Kaal{{' pattern found")
        
        # Look for common strings
        strings = []
        current = b''
        for byte in data:
            if 32 <= byte <= 126:  # Printable ASCII
                current += bytes([byte])
            else:
                if len(current) >= 4:
                    strings.append(current.decode('ascii', errors='ignore'))
                current = b''
        
        print(f"[*] Found {len(strings)} readable strings")
        # Show interesting ones
        interesting = [s for s in strings if len(s) > 10 or 'flag' in s.lower() or 'kaal' in s.lower()]
        if interesting:
            print("[+] Interesting strings:")
            for s in interesting[:20]:
                print(f"    {s}")
except Exception as e:
    print(f"[-] Error: {e}")

# 3. LSB Steganography
print("\n[3] Checking LSB (Least Significant Bit)...")
try:
    img = Image.open(image_path)
    pixels = img.load()
    width, height = img.size
    
    # Extract LSB from each color channel
    lsb_data = []
    for y in range(min(height, 100)):  # Check first 100 rows
        for x in range(width):
            pixel = pixels[x, y]
            if isinstance(pixel, tuple):
                for color in pixel[:3]:  # RGB only
                    lsb_data.append(color & 1)
    
    # Convert bits to bytes
    lsb_bytes = []
    for i in range(0, len(lsb_data), 8):
        if i + 8 <= len(lsb_data):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | lsb_data[i + j]
            lsb_bytes.append(byte)
    
    lsb_text = bytes(lsb_bytes).decode('ascii', errors='ignore')
    if 'Kaal' in lsb_text or 'flag' in lsb_text.lower():
        print("[+] Found potential flag in LSB:")
        print(f"    {lsb_text[:200]}")
    else:
        print("[-] No obvious flag in LSB data")
        print(f"[*] First 100 chars: {lsb_text[:100]}")
except Exception as e:
    print(f"[-] Error: {e}")

# 4. Check file size and structure
print("\n[4] File Analysis...")
file_size = os.path.getsize(image_path)
print(f"[*] File size: {file_size} bytes")

# Check for appended data
try:
    with open(image_path, 'rb') as f:
        data = f.read()
        # JPEG ends with FF D9
        jpeg_end = data.rfind(b'\xff\xd9')
        if jpeg_end != -1 and jpeg_end < len(data) - 2:
            print(f"[+] Found data after JPEG end marker!")
            appended = data[jpeg_end+2:]
            print(f"    Appended data ({len(appended)} bytes):")
            print(f"    {appended[:200]}")
            if b'Kaal{' in appended:
                print("[+] FLAG FOUND IN APPENDED DATA!")
        else:
            print("[-] No appended data after JPEG")
except Exception as e:
    print(f"[-] Error: {e}")

print("\n" + "=" * 70)
print("[*] Analysis complete!")
