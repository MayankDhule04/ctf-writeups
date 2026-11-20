#!/usr/bin/env python3
"""
Dragonstone Vault - Final Solution
The sequence works: dragons -> oath -> claim -> "Speak the words"
Need to find the exact words that don't trigger buffer overflow
"""

import socket
import time
import re

def fresh_connection():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(15)
    s.connect(("labs.cyberspacevr.in", 30959))
    time.sleep(0.5)
    s.recv(4096)  # Skip banner
    return s

def setup_sequence(s):
    """Execute the setup sequence: dragons -> oath"""
    # Step 1: Dragons
    dragons = ["Drogon", "Rhaegal", "Viserion"]
    for dragon in dragons:
        s.sendall(f"look {dragon}\n".encode())
        time.sleep(0.5)
        s.recv(4096)
    
    # Step 2: Oath
    s.sendall(b"swear fire-and-blood-i-am\n")
    time.sleep(0.5)
    response = s.recv(4096).decode('utf-8', errors='ignore')
    
    return "dragons stir" in response

def try_exact_words():
    """Try very specific words that might be the exact key"""
    print("[+] Trying exact words for 'Speak the words'...")
    
    # Based on Game of Thrones and flag format, try very specific phrases
    exact_words = [
        "dracarys",  # Single word - dragon fire command
        "Fire and Blood",  # House Targaryen words
        "fire and blood",  # lowercase version
        "Aegon",  # Targaryen name
        "Daenerys",  # Dragon queen
        "Targaryen",  # House name
        "Iron Throne",  # The throne itself
        "dragon",  # Simple dragon
        "three dragons",  # The three dragons
        "Drogon Rhaegal Viserion",  # All three names
        "blood of the dragon",  # Targaryen phrase
        "I am the dragon",  # Identity claim
        "fire_and_blood_dracarys",  # Flag format hint
        "SpaceCTF",  # Flag prefix
        "throne",  # Simple throne
        "crown",  # Royal symbol
        "king",  # Royal title
        "queen",  # Royal title
        "victory",  # Success
        "conquest",  # Targaryen history
    ]
    
    for words in exact_words:
        try:
            print(f"\n[+] Trying exact words: '{words}'")
            
            s = fresh_connection()
            
            if not setup_sequence(s):
                print("    Setup failed")
                s.close()
                continue
            
            # Claim
            s.sendall(b"claim\n")
            time.sleep(0.5)
            response = s.recv(4096).decode('utf-8', errors='ignore')
            
            if "Speak the words" not in response:
                print(f"    Unexpected claim response: {response}")
                s.close()
                continue
            
            # Send the exact words
            s.sendall(f"{words}\n".encode())
            time.sleep(1)
            
            response = s.recv(4096).decode('utf-8', errors='ignore')
            
            if "SpaceCTF{" in response:
                flag_match = re.search(r'SpaceCTF\{[^}]+\}', response)
                if flag_match:
                    flag = flag_match.group(0)
                    print(f"\n🎉 FLAG FOUND: {flag}")
                    s.close()
                    return True
            
            if "buffer overflow detected" not in response:
                print(f"    No overflow! Response: {response}")
                
                # If no overflow, try to continue interaction
                try:
                    s.sendall(b"help\n")
                    time.sleep(0.5)
                    help_response = s.recv(4096).decode('utf-8', errors='ignore')
                    
                    if "SpaceCTF{" in help_response:
                        flag_match = re.search(r'SpaceCTF\{[^}]+\}', help_response)
                        if flag_match:
                            flag = flag_match.group(0)
                            print(f"\n🎉 FLAG FOUND: {flag}")
                            s.close()
                            return True
                    
                    print(f"    Help response: {help_response}")
                except:
                    pass
            else:
                print(f"    Buffer overflow detected")
            
            s.close()
            
        except Exception as e:
            print(f"    Error with '{words}': {e}")
    
    return False

def try_empty_or_special_input():
    """Try empty input or special characters"""
    print("[+] Trying empty or special inputs...")
    
    special_inputs = [
        "",  # Empty input
        " ",  # Single space
        "\n",  # Just newline
        ".",  # Single dot
        "!",  # Exclamation
        "?",  # Question mark
        "0",  # Zero
        "1",  # One
        "yes",  # Simple yes
        "no",  # Simple no
        "ok",  # Simple ok
    ]
    
    for inp in special_inputs:
        try:
            print(f"\n[+] Trying special input: '{repr(inp)}'")
            
            s = fresh_connection()
            
            if not setup_sequence(s):
                s.close()
                continue
            
            s.sendall(b"claim\n")
            time.sleep(0.5)
            s.recv(4096)
            
            s.sendall(f"{inp}\n".encode())
            time.sleep(1)
            
            response = s.recv(4096).decode('utf-8', errors='ignore')
            
            if "SpaceCTF{" in response:
                flag_match = re.search(r'SpaceCTF\{[^}]+\}', response)
                if flag_match:
                    flag = flag_match.group(0)
                    print(f"\n🎉 FLAG FOUND: {flag}")
                    s.close()
                    return True
            
            if "buffer overflow detected" not in response:
                print(f"    No overflow! Response: {response}")
            
            s.close()
            
        except Exception as e:
            print(f"    Error with '{repr(inp)}': {e}")
    
    return False

def try_binary_input():
    """Try sending raw binary data"""
    print("[+] Trying raw binary inputs...")
    
    binary_inputs = [
        b"\x00",  # Null byte
        b"\x00\x00\x00\x00\x00\x00\x00\x00",  # 8 null bytes
        b"A",  # Single A
        b"AAAA",  # 4 A's
        b"AAAAAAAA",  # 8 A's (one qword)
    ]
    
    for inp in binary_inputs:
        try:
            print(f"\n[+] Trying binary input: {repr(inp)}")
            
            s = fresh_connection()
            
            if not setup_sequence(s):
                s.close()
                continue
            
            s.sendall(b"claim\n")
            time.sleep(0.5)
            s.recv(4096)
            
            s.sendall(inp + b"\n")
            time.sleep(1)
            
            response = s.recv(4096).decode('utf-8', errors='ignore')
            
            if "SpaceCTF{" in response:
                flag_match = re.search(r'SpaceCTF\{[^}]+\}', response)
                if flag_match:
                    flag = flag_match.group(0)
                    print(f"\n🎉 FLAG FOUND: {flag}")
                    s.close()
                    return True
            
            if "buffer overflow detected" not in response:
                print(f"    No overflow! Response: {response}")
            
            s.close()
            
        except Exception as e:
            print(f"    Error with {repr(inp)}: {e}")
    
    return False

def main():
    print("="*70)
    print("DRAGONSTONE VAULT - FINAL SOLUTION")
    print("Finding the exact words that don't trigger buffer overflow")
    print("="*70)
    
    # Try exact words
    if try_exact_words():
        return
    
    # Try empty or special input
    if try_empty_or_special_input():
        return
    
    # Try binary input
    if try_binary_input():
        return
    
    print("\n❌ All final solution attempts failed")

if __name__ == "__main__":
    main()