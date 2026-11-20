#!/usr/bin/env python3
"""
The Three-Eyed Raven - Challenge Explorer
Multi-stage challenge requiring tokens from all previous challenges:
1. Iron Bank token (we have: THE_WATCH_HOLDS_THE_LINE)
2. Face JWT (we have: SpaceCTF{valar_morghulis_face_no_man_2ZD66Q})
3. Dragon breath (need from Dragonstone Vault)
"""

import socket
import time
import base64
import json
import jwt

def connect_to_raven():
    """Connect to The Three-Eyed Raven service"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(15)
    s.connect(("labs.cyberspacevr.in", 30116))
    time.sleep(0.5)
    banner = s.recv(4096).decode('utf-8', errors='ignore')
    print(f"[+] Banner:\n{banner}")
    return s

def explore_commands():
    """Explore available commands"""
    print("[+] Exploring The Three-Eyed Raven commands...")
    
    try:
        s = connect_to_raven()
        
        # Try each command mentioned in the description
        commands = [
            "guest",
            "status", 
            "help",
        ]
        
        for cmd in commands:
            print(f"\n[+] Testing command: {cmd}")
            s.sendall(f"{cmd}\n".encode())
            time.sleep(0.5)
            response = s.recv(4096).decode('utf-8', errors='ignore')
            print(f"Response: {response}")
        
        s.close()
        
    except Exception as e:
        print(f"Error exploring commands: {e}")

def try_iron_bank_token():
    """Try the Iron Bank token we have"""
    print("[+] Trying Iron Bank token...")
    
    # From Take the Black challenge, we got: THE_WATCH_HOLDS_THE_LINE
    iron_token = "THE_WATCH_HOLDS_THE_LINE"
    
    try:
        s = connect_to_raven()
        
        print(f"[+] Offering iron token: {iron_token}")
        s.sendall(f"offer iron {iron_token}\n".encode())
        time.sleep(1)
        response = s.recv(4096).decode('utf-8', errors='ignore')
        print(f"Iron response: {response}")
        
        # Check status after offering iron
        s.sendall(b"status\n")
        time.sleep(0.5)
        status = s.recv(4096).decode('utf-8', errors='ignore')
        print(f"Status after iron: {status}")
        
        s.close()
        
    except Exception as e:
        print(f"Error with iron token: {e}")

def try_face_jwt():
    """Try the Face JWT we have"""
    print("[+] Trying Face JWT...")
    
    # We need to create a JWT with name="many-faced" using the algorithm confusion attack
    # But first let's get a guest JWT to see the format
    
    try:
        s = connect_to_raven()
        
        # Get guest JWT first
        s.sendall(b"guest\n")
        time.sleep(0.5)
        guest_response = s.recv(4096).decode('utf-8', errors='ignore')
        print(f"Guest JWT response: {guest_response}")
        
        # Extract JWT from response if present
        if "eyJ" in guest_response:  # JWT starts with eyJ
            import re
            jwt_match = re.search(r'eyJ[A-Za-z0-9+/=._-]+', guest_response)
            if jwt_match:
                guest_jwt = jwt_match.group(0)
                print(f"Extracted guest JWT: {guest_jwt}")
                
                # Decode to see structure
                try:
                    decoded = jwt.decode(guest_jwt, options={"verify_signature": False})
                    print(f"Guest JWT payload: {decoded}")
                except Exception as e:
                    print(f"Error decoding guest JWT: {e}")
        
        # Now try to offer a face JWT
        # We'll need to create one with the right format
        face_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoibWFueS1mYWNlZCJ9.signature"  # Placeholder
        
        s.sendall(f"offer face {face_jwt}\n".encode())
        time.sleep(1)
        face_response = s.recv(4096).decode('utf-8', errors='ignore')
        print(f"Face response: {face_response}")
        
        s.close()
        
    except Exception as e:
        print(f"Error with face JWT: {e}")

def try_dragon_breath():
    """Try dragon breath - need to figure out what this should be"""
    print("[+] Trying dragon breath...")
    
    # The description mentions "breath of a dragon carried from Dragonstone"
    # This likely needs to be base64 encoded bytes from the Dragonstone challenge
    
    # Try some possibilities
    dragon_candidates = [
        "dracarys",
        "fire and blood",
        "SpaceCTF{fire_and_blood_dracarys_",
        "Drogon Rhaegal Viserion",
    ]
    
    try:
        s = connect_to_raven()
        
        for candidate in dragon_candidates:
            print(f"[+] Trying dragon breath: {candidate}")
            
            # Encode as base64
            b64_candidate = base64.b64encode(candidate.encode()).decode()
            
            s.sendall(f"offer dragon {b64_candidate}\n".encode())
            time.sleep(1)
            response = s.recv(4096).decode('utf-8', errors='ignore')
            print(f"Dragon response for '{candidate}': {response}")
        
        s.close()
        
    except Exception as e:
        print(f"Error with dragon breath: {e}")

def check_weirwood_binary():
    """Check if we have the weirwood binary mentioned in the challenge"""
    print("[+] Looking for weirwood binary...")
    
    import os
    
    # Look for weirwood file in current directory
    if os.path.exists("weirwood"):
        print("[+] Found weirwood binary!")
        
        # Try to run it
        try:
            import subprocess
            result = subprocess.run(["./weirwood"], capture_output=True, text=True, timeout=10)
            print(f"Weirwood output: {result.stdout}")
            if result.stderr:
                print(f"Weirwood stderr: {result.stderr}")
        except Exception as e:
            print(f"Error running weirwood: {e}")
    else:
        print("[-] Weirwood binary not found")

def main():
    print("="*70)
    print("THE THREE-EYED RAVEN - CHALLENGE EXPLORER")
    print("="*70)
    
    # Explore basic commands
    explore_commands()
    
    # Try our known tokens
    try_iron_bank_token()
    try_face_jwt()
    try_dragon_breath()
    
    # Check for weirwood binary
    check_weirwood_binary()

if __name__ == "__main__":
    main()