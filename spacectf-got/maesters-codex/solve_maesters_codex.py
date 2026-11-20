#!/usr/bin/env python3
"""
Maester's Codex - Final Solution
Re-reading the clues more carefully:
- Stone, Bronze, Iron are the THREE LINKS
- We need to "forge the chain link by link"
- The order matters!
"""

import base64
import codecs

def vigenere_decrypt(text, key):
    """Decrypt Vigenere cipher"""
    result = []
    key = key.upper()
    key_index = 0
    
    for char in text:
        if char.isalpha():
            shift = ord(key[key_index % len(key)]) - ord('A')
            if char.isupper():
                result.append(chr((ord(char) - ord('A') - shift) % 26 + ord('A')))
            else:
                result.append(chr((ord(char) - ord('a') - shift) % 26 + ord('a')))
            key_index += 1
        else:
            result.append(char)
    return ''.join(result)

def solve():
    with open('cipher.txt', 'r') as f:
        ciphertext = f.read().strip()
    
    print("="*70)
    print("MAESTER'S CODEX - FINAL SOLUTION")
    print("="*70)
    print("\nClues:")
    print("- Stone (weathered and old)")
    print("- Bronze (rings when struck)")
    print("- Iron (cold black, Northern wind)")
    print()
    
    # Step 1: Base85 (Stone - old encoding)
    print("[Step 1: STONE] Base85 Decode")
    decoded_b85 = base64.b85decode(ciphertext)
    text1 = decoded_b85.decode('utf-8', errors='ignore')
    print(f"✓ Length: {len(text1)} chars")
    print(f"Preview: {text1[:80]}...")
    
    # Step 2: ROT13 (Bronze - simple substitution that "rings")
    print("\n[Step 2: BRONZE] ROT13")
    text2 = codecs.decode(text1, 'rot_13')
    print(f"✓ Length: {len(text2)} chars")
    print(f"Preview: {text2[:80]}...")
    print(f"Flag area: ...{text2[-60:]}")
    
    # Step 3: Vigenere with "IRON" key (Iron - Northern/cold)
    print("\n[Step 3: IRON] Vigenere with key 'IRON'")
    text3 = vigenere_decrypt(text2, 'IRON')
    print(f"✓ Length: {len(text3)} chars")
    
    if 'SpaceCTF{' in text3:
        start = text3.index('SpaceCTF{')
        end = text3.index('}', start) + 1
        flag = text3[start:end]
        
        print("\n" + "="*70)
        print("🎉 FLAG FOUND!")
        print("="*70)
        print(f"\n{flag}\n")
        print("="*70)
        print("\nFull decoded message:")
        print("-"*70)
        print(text3)
        print("-"*70)
        return flag
    
    # Try other thematic keys
    print("\n❌ 'IRON' didn't work. Trying other keys...")
    
    thematic_keys = [
        'NORTH', 'NORTHERN', 'WIND', 'COLD', 'BLACK',
        'BLACKIRON', 'COLDIRON', 'NORTHERNWIND',
        'STONE', 'BRONZE', 'CHAIN', 'LINK', 'LINKS',
        'STONEBRONZEIRON', 'SBI', 'THREE', 'FORGE',
        'MAESTER', 'CITADEL', 'OLDTOWN', 'CODEX'
    ]
    
    for key in thematic_keys:
        text3 = vigenere_decrypt(text2, key)
        if 'SpaceCTF{' in text3:
            start = text3.index('SpaceCTF{')
            end = text3.index('}', start) + 1
            flag = text3[start:end]
            
            print(f"\n✓ FOUND with key: '{key}'!")
            print("\n" + "="*70)
            print("🎉 FLAG FOUND!")
            print("="*70)
            print(f"\n{flag}\n")
            print("="*70)
            print("\nFull decoded message:")
            print("-"*70)
            print(text3)
            print("-"*70)
            return flag
    
    print("\n❌ No flag found")
    print(f"\nCurrent state: {text2[-100:]}")

if __name__ == "__main__":
    solve()
