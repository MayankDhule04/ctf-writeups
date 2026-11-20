#!/usr/bin/env python3
"""
Broken Compass - Hash Collision Solver
Finding two different inputs that produce the same hash
"""

import socket
import hashlib
import re

def solve_pow(prefix, target_prefix):
    """Solve proof of work: sha256(prefix + ???) starts with target_prefix"""
    print(f"[*] Solving PoW: sha256({prefix} + ???) starts with '{target_prefix}'")
    
    counter = 0
    while True:
        test = str(counter)
        hash_input = prefix + test
        hash_result = hashlib.sha256(hash_input.encode()).hexdigest()
        
        if hash_result.startswith(target_prefix):
            print(f"[+] PoW solved: {test}")
            return test
        
        counter += 1
        if counter % 100000 == 0:
            print(f"[*] Tried {counter} attempts...")

def test_hash_function(host, port):
    """Connect and test the hash function to find patterns"""
    print(f"[*] Connecting to {host}:{port}")
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    
    # Receive welcome message
    data = s.recv(4096).decode()
    print(data)
    
    # Extract PoW challenge
    pow_match = re.search(r"sha256\((\d+) \+ \?\?\?\) starts with '(\w+)'", data)
    if pow_match:
        prefix = pow_match.group(1)
        target = pow_match.group(2)
        answer = solve_pow(prefix, target)
        
        # Send PoW answer
        s.send(f"{answer}\n".encode())
        response = s.recv(4096).decode()
        print(response)
    
    # Now test different inputs to understand the hash function
    print("\n[*] Testing hash function with various inputs...")
    
    test_inputs = [
        ("00", "01"),
        ("00", "20"),  # Try XOR with 0x20
        ("00", "40"),
        ("0000", "0001"),
        ("0000", "0020"),
        ("ff", "df"),  # ff XOR 20 = df
        ("aa", "8a"),  # aa XOR 20 = 8a
    ]
    
    for msg1, msg2 in test_inputs:
        print(f"\n[*] Testing: {msg1} vs {msg2}")
        
        # Send first message
        s.send(f"{msg1}\n".encode())
        # Send second message
        s.send(f"{msg2}\n".encode())
        
        # Get response
        response = s.recv(4096).decode()
        print(response)
        
        # Check if collision found
        if "Collision found" in response or "flag" in response.lower():
            print("[+] SUCCESS! Collision found!")
            print(response)
            return
        
        # Reconnect for next attempt
        s.close()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        
        # Handle PoW again
        data = s.recv(4096).decode()
        pow_match = re.search(r"sha256\((\d+) \+ \?\?\?\) starts with '(\w+)'", data)
        if pow_match:
            prefix = pow_match.group(1)
            target = pow_match.group(2)
            answer = solve_pow(prefix, target)
            s.send(f"{answer}\n".encode())
            s.recv(4096)
    
    s.close()

def analyze_hash_difference():
    """Analyze the hash difference pattern"""
    print("\n[*] Analyzing hash patterns:")
    print("Input 00 → Hash 0x29067bff")
    print("Input 01 → Hash 0x29067c1f")
    print(f"Difference: 0x{0x29067c1f - 0x29067bff:x} = {0x29067c1f - 0x29067bff}")
    
    # The difference is 0x20 (32 decimal)
    # This suggests the hash might be vulnerable to bit flipping
    
    print("\n[*] Observations:")
    print("- Hash difference is 0x20 (32 in decimal)")
    print("- This is suspiciously small for a 'collision-resistant' hash")
    print("- Differential cryptanalysis hint suggests looking for input differences")
    print("- that produce predictable output differences")
    
    print("\n[*] Strategies to try:")
    print("1. Find inputs where difference cancels out in the hash")
    print("2. Look for modular arithmetic weaknesses")
    print("3. Try inputs that differ by specific bit patterns")
    print("4. Exploit potential truncation or overflow")

if __name__ == "__main__":
    HOST = "212.2.254.96"
    PORT = 7006
    
    analyze_hash_difference()
    
    print("\n" + "="*60)
    print("Starting collision search...")
    print("="*60)
    
    test_hash_function(HOST, PORT)
