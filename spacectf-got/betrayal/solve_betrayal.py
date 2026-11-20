#!/usr/bin/env python3
"""
Betrayal Challenge Solver
"""

import hashlib
import base64
import requests

print("="*70)
print("BETRAYAL CHALLENGE SOLVER")
print("="*70)

# From the JavaScript source
username_hash = 'aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d'  # SHA-1
password_hash = '707b10ba2d8020957997e4127c99147091087a71'  # SHA-1
comment_token = 'KRgda0-jlu6DtCQ8dUE5XyMJHI23ubzxASpu9fzy8V8='

print("\n[*] Found credentials in JavaScript:")
print(f"    Username SHA-1: {username_hash}")
print(f"    Password SHA-1: {password_hash}")
print(f"    Comment token: {comment_token}")

# Crack the hashes
print("\n[1] Cracking SHA-1 hashes...")

common_words = [
    'admin', 'password', 'root', 'user', 'test', 'guest', 'demo',
    '123456', 'password123', 'admin123', 'letmein', 'welcome',
    'hello', 'world', 'secret', 'pass', 'qwerty', '12345',
]

username = None
password = None

for word in common_words:
    h = hashlib.sha1(word.encode()).hexdigest()
    if h == username_hash:
        username = word
        print(f"  [+] Username: {word}")
    if h == password_hash:
        password = word
        print(f"  [+] Password: {word}")

# Decode the comment token
print("\n[2] Decoding comment token...")
try:
    decoded = base64.b64decode(comment_token).decode('utf-8', errors='ignore')
    print(f"  [+] Base64 decoded: {decoded}")
except Exception as e:
    print(f"  [!] Error: {e}")

# Decode the main encrypted token
encrypted_token = "SpSkjxA0b6VamrI9Be5tJQdSKPJ0GDQ6v8oYEKxGm_6DjsPQC023ozS_5yEuObxQLckTDAOBIc_j3liJ59OawLGpSDajKwvFeJYGVcxNDethuFUJmJnoLC3Oa-8HHf2JWm-J57v0CGbR8LemUJ07pUb4yfJaasomxoB7"

print("\n[3] Analyzing main encrypted token...")
print(f"  Length: {len(encrypted_token)}")
print(f"  Contains: _ and - (URL-safe base64)")

# Try base64 decoding
try:
    # URL-safe base64
    decoded = base64.urlsafe_b64decode(encrypted_token + '==')
    print(f"  [+] URL-safe base64 decoded (hex): {decoded.hex()}")
    print(f"  [+] URL-safe base64 decoded (raw): {decoded}")
    
    # Try as text
    try:
        text = decoded.decode('utf-8')
        print(f"  [+] As text: {text}")
    except:
        pass
except Exception as e:
    print(f"  [!] Decoding error: {e}")

# Try standard base64
try:
    decoded = base64.b64decode(encrypted_token)
    print(f"  [+] Standard base64 decoded: {decoded}")
except:
    pass

# Check if it's a JWT
if encrypted_token.count('.') == 2:
    print("\n[4] Looks like a JWT token!")
    parts = encrypted_token.split('.')
    for i, part in enumerate(parts):
        try:
            decoded = base64.urlsafe_b64decode(part + '==')
            print(f"  Part {i}: {decoded}")
        except:
            pass

# Try XOR with common keys
print("\n[5] Trying XOR decryption...")
for key in ['admin', 'password', 'secret', 'key', username or '', password or '']:
    if not key:
        continue
    try:
        decoded_bytes = base64.urlsafe_b64decode(encrypted_token + '==')
        result = bytes([b ^ ord(key[i % len(key)]) for i, b in enumerate(decoded_bytes)])
        if b'Kaal{' in result or b'flag' in result.lower():
            print(f"  [+] XOR with '{key}': {result}")
    except:
        pass

print("\n" + "="*70)
print("Analysis complete")
print("="*70)

if username and password:
    print(f"\n[*] Try logging in with:")
    print(f"    Username: {username}")
    print(f"    Password: {password}")
