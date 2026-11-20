#!/usr/bin/env python3
"""
Goober - Scan high ports for netcat service
"""

import socket
from concurrent.futures import ThreadPoolExecutor

def check_port(host, port):
    """Quick port check"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        result = s.connect_ex((host, port))
        s.close()
        return port if result == 0 else None
    except:
        return None

def interact(host, port):
    """Interact with service"""
    try:
        print(f"\n[*] Connecting to {host}:{port}...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((host, port))
        
        # Receive banner
        data = s.recv(4096)
        print(f"[BANNER]:\n{data.decode('utf-8', errors='ignore')}\n")
        
        # Send some test inputs
        tests = [b"help\n", b"1\n", b"AAAA\n", b"cat flag1\n"]
        for test in tests:
            s.send(test)
            resp = s.recv(4096)
            print(f"[{test.strip()}]: {resp.decode('utf-8', errors='ignore')[:200]}")
        
        s.close()
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    host = "23.179.17.69"
    
    # Scan high ports commonly used for CTF
    ports = list(range(9000, 10000)) + list(range(30000, 32000))
    
    print(f"[*] Scanning {len(ports)} ports...")
    
    open_ports = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(lambda p: check_port(host, p), ports)
        open_ports = [p for p in results if p]
    
    if open_ports:
        print(f"\n[+] Found open ports: {open_ports}")
        for port in open_ports:
            interact(host, port)
    else:
        print("\n[-] No open ports found in high range")
