#!/usr/bin/env python3
"""
Solve AUTOMATONS_SECRET - decode graph and decrypt flag
"""

import base64
import zlib
import json

print("[*] AUTOMATONS_SECRET Solver")
print("=" * 70)

# Load both files
with open('extracted_encrypted_flag.bin', 'rb') as f:
    encrypted_flag = f.read()

with open('extracted_encoded_graph.bin', 'rb') as f:
    encoded_graph = f.read()

print(f"[*] Encrypted flag: {len(encrypted_flag)} bytes")
print(f"[*] Encoded graph: {len(encoded_graph)} bytes")

# Decode the graph (it's base64 + zlib compressed)
print(f"\n[*] Decoding graph...")
print(f"  First 20 chars: {encoded_graph[:20]}")

try:
    # It's base64 encoded
    decoded = base64.b64decode(encoded_graph)
    print(f"[+] Base64 decoded: {len(decoded)} bytes")
    
    # Now decompress with zlib
    decompressed = zlib.decompress(decoded)
    print(f"[+] Decompressed: {len(decompressed)} bytes")
    
    # Save it
    with open('graph_decompressed.txt', 'wb') as f:
        f.write(decompressed)
    
    # Try to parse as JSON
    try:
        graph_data = json.loads(decompressed)
        print(f"[+] Valid JSON!")
        print(f"  Keys: {list(graph_data.keys())}")
        
        # Save formatted JSON
        with open('graph.json', 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        print(f"[+] Saved as graph.json")
        
    except:
        # Not JSON, maybe it's text
        text = decompressed.decode('utf-8', errors='ignore')
        print(f"[+] Text content (first 500 chars):")
        print(f"{text[:500]}")
        
        # Check if it contains the key
        if 'key' in text.lower() or 'password' in text.lower():
            print(f"\n[+] Found key/password reference!")

except Exception as e:
    print(f"[!] Error decoding graph: {e}")

# Now try to use the graph to decrypt the flag
print(f"\n[*] Encrypted flag:")
print(f"  Hex: {encrypted_flag.hex()}")
print(f"  Length: {len(encrypted_flag)} bytes")

# The graph might contain the decryption key or algorithm
# Let's see what we got

print("\n" + "=" * 70)
