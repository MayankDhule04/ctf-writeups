#!/usr/bin/env python3
"""
Try obscure details and variations
"""

import PyPDF2

pdf_file = "VF0000000011-Enc.pdf"

# Very specific and obscure details
passwords = [
    # Maybe it's about the CURATOR, not the thief
    # Louvre directors/curators around 1911
    'ThéophileHomolle', 'theophileholle',  # Director during theft
    'Homolle', 'homolle', 'HOMOLLE',
    
    # Room/Gallery numbers
    'Room711', 'room711',  # Salon Carré was Room 711
    '711', 
    'Gallery711', 'gallery711',
    
    # Specific painting details
    '77x53', '77x53cm',  # Mona Lisa dimensions
    '7753',
    
    # Frame details
    'poplarwood', 'PoplarWood',  # Mona Lisa painted on poplar
    'poplar', 'Poplar', 'POPLAR',
    
    # Insurance/Value
    '100million', '100Million',
    
    # Day of week
    'Monday', 'monday', 'MONDAY',
    
    # Specific time
    '7am', '7AM', '0700',
    'morning', 'Morning', 'MORNING',
    
    # Paris locations
    'Paris', 'paris', 'PARIS',
    'RuedelHospitalSaintLouis',  # Where Peruggia lived
    
    # Trial details
    'trial', 'Trial', 'TRIAL',
    'court', 'Court', 'COURT',
    
    # Reward offered
    '25000francs', '25000Francs',
    '25000',
    
    # Famous quote/motive
    'patriot', 'Patriot', 'PATRIOT',
    'patriotism', 'Patriotism',
    
    # Maybe it's simpler - just "thief"
    'thief', 'Thief', 'THIEF',
    'thieves', 'Thieves', 'THIEVES',
    
    # Or "curator"
    'curator', 'Curator', 'CURATOR',
    
    # File-related
    'VF0000000011',
    'VF-0000000011',
    'VF 0000000011',
    '0000000011',
    '11',
    
    # Maybe it's the challenge itself
    'TheCuratorsExit',
    'CuratorsExit',
    'curatorsexit',
    
    # Interpol-related
    'interpol', 'Interpol', 'INTERPOL',
    
    # Maybe it's just empty
    '',
    
    # Common CTF
    'flag', 'FLAG', 'Flag',
    'ctf', 'CTF', 'Ctf',
    'password', 'Password', 'PASSWORD',
    
    # Numbers from challenge
    '971',  # Points
    'elemental3', 'elemental',
    
    # Maybe it's about the EXIT
    'exit', 'Exit', 'EXIT',
    'escape', 'Escape', 'ESCAPE',
    
    # Stairwell where frame was found
    'stairwell', 'Stairwell', 'STAIRWELL',
    'stairs', 'Stairs', 'STAIRS',
    
    # The coat he used
    'coat', 'Coat', 'COAT',
    'smock', 'Smock', 'SMOCK',  # He wore a smock
    
    # Nationality
    'Italian', 'italian', 'ITALIAN',
    'Italy', 'italy', 'ITALY',
]

print("="*70)
print("OBSCURE DETAILS ATTEMPT")
print("="*70)

try:
    with open(pdf_file, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        print(f"\n[1] Testing {len(passwords)} obscure passwords...")
        
        for i, password in enumerate(passwords):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(passwords)}", end='\r')
            
            try:
                result = pdf_reader.decrypt(password)
                if result > 0:
                    print(f"\n\n  ✓✓✓ PASSWORD FOUND: '{password}'")
                    
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
            print(f"\n\n  ✗ No password found")
            print(f"\n  This PDF requires professional cracking tools.")
            print(f"  Recommended: pdfcrack with rockyou.txt wordlist")
            
except Exception as e:
    print(f"\n  Error: {e}")

print(f"\n{'='*70}")
