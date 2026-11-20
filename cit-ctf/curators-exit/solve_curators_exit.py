#!/usr/bin/env python3
"""
Try passwords from the challenge description
"""

import PyPDF2

pdf_file = "VF0000000011-Enc.pdf"

# Passwords directly from the description
passwords = [
    # Key words from description
    'authorities',
    'Authorities',
    'AUTHORITIES',
    'authority',
    'Authority',
    'AUTHORITY',
    
    # Phrases from description
    'LouvreHeist',
    'louvreheist',
    'Louvre Heist',
    'louvre heist',
    'thelouvreheist',
    'TheLouvreHeist',
    
    # "communication from Interpol"
    'communication',
    'Communication',
    'COMMUNICATION',
    
    # "unsure of the contents"
    'contents',
    'Contents',
    'CONTENTS',
    
    # "information"
    'information',
    'Information',
    'INFORMATION',
    
    # "individual"
    'individual',
    'Individual',
    'INDIVIDUAL',
    
    # Combined
    'InterpolCommunication',
    'interpolcommunication',
    'LouvreThief',
    'louvrethief',
    
    # Title-based
    'TheCuratorsExit',
    'thecuratorsexit',
    'CuratorsExit',
    'curatorsexit',
]

print("="*70)
print("DESCRIPTION-BASED PASSWORD ATTEMPTS")
print("="*70)

try:
    with open(pdf_file, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        print(f"\n[1] Trying passwords from challenge description...")
        
        for password in passwords:
            try:
                result = pdf_reader.decrypt(password)
                if result > 0:
                    print(f"\n  ✓✓✓ PASSWORD FOUND: '{password}'")
                    
                    # Extract text
                    full_text = ""
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        text = page.extract_text()
                        full_text += text + "\n"
                        print(f"\n  === Page {page_num} ===")
                        print(text)
                    
                    # Save
                    with open('curator_decrypted.txt', 'w', encoding='utf-8') as f:
                        f.write(full_text)
                    print(f"\n  Saved to: curator_decrypted.txt")
                    
                    # Find names
                    import re
                    names = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', full_text)
                    
                    print(f"\n[2] Names found:")
                    for name in set(names):
                        print(f"  {name}")
                        print(f"  FLAG: CIT{{{name.replace(' ', '_')}}}")
                    
                    break
            except:
                pass
        else:
            print(f"\n  ✗ No password worked from description")
            
except Exception as e:
    print(f"\n  Error: {e}")

print(f"\n{'='*70}")
