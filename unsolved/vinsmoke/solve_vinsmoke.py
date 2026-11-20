#!/usr/bin/env python3
"""
Vinsmoke Challenge - Complete Solution
"""

import requests
import hashlib

def caesar_decrypt(text, shift):
    """Decrypt Caesar cipher"""
    result = []
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result.append(chr((ord(char) - base - shift) % 26 + base))
        else:
            result.append(char)
    return ''.join(result)

def solve_vinsmoke():
    """Complete solution for Vinsmoke challenge"""
    
    print("="*60)
    print("Vinsmoke Challenge - Complete Solution")
    print("="*60)
    
    # Step 1: Decode the three Caesar cipher texts
    print("\n[Step 1] Decoding Caesar ciphers...")
    
    texts = [
        ("Znk gtyckx roky ot g vrgik ul xkyz.\nCnkxk sotjy lotj vkgik gtj hujoky xkiubkx.\nRuuq lux znk xuus ul jxkgsy.", 6),
        ("Xifsf esfbnt bsf nbef boe tfdsfut bsf lfqu.\nUif qmbdf pg tmvncfs boe tjmfodf.\nUif cfesppn ipmet xibu zpv tffl.\nUif cfesppn jt zpvs eftujobujpo.", 1),
        ("Cqn yujln hxd bnnt qjb j wjvn.\nRc rb bqjanm kh vjwh.\nCqn knmaxxv rb hxda mnbcrwjcrxw.", 9)
    ]
    
    for i, (encrypted, shift) in enumerate(texts, 1):
        decrypted = caesar_decrypt(encrypted, shift)
        print(f"\n[*] Text {i} (shift {shift}):")
        print(decrypted)
    
    # Step 2: Extract the key information
    print("\n[Step 2] Analyzing decoded messages...")
    print("[*] Key phrase from last line of 3rd paragraph:")
    print("    'The bedroom is your destination.'")
    
    # Step 3: Access the endpoint
    print("\n[Step 3] Accessing /thebedroom endpoint...")
    url = "https://vinsmoke-2.onrender.com/thebedroom"
    
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            hash_value = resp.text.strip()
            print(f"[+] Found hash: {hash_value}")
            
            # Check if it's MD5
            if len(hash_value) == 32:
                print(f"[*] Hash type: MD5 (32 characters)")
            
            # Try to crack or identify the hash
            print("\n[Step 4] Analyzing hash...")
            
            # Common words to try
            common_words = [
                'bedroom', 'thebedroom', 'vinsmoke', 'flag', 'password',
                'dreams', 'rest', 'slumber', 'destination', 'answer',
                '619', 'caesar', 'archive'
            ]
            
            print("[*] Trying common words...")
            for word in common_words:
                md5_hash = hashlib.md5(word.encode()).hexdigest()
                if md5_hash == hash_value:
                    print(f"\n[+] CRACKED! Hash is MD5 of: {word}")
                    print(f"[+] FLAG: flag{{{word}}}")
                    return f"flag{{{word}}}"
            
            print("\n[*] Hash not cracked with common words")
            print(f"[*] Try online MD5 databases with: {hash_value}")
            
            return hash_value
            
    except Exception as e:
        print(f"[!] Error: {e}")
        return None

if __name__ == "__main__":
    result = solve_vinsmoke()
    
    if result:
        print("\n" + "="*60)
        print(f"Result: {result}")
        print("="*60)
