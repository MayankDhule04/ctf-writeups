#!/usr/bin/env python3
"""
Robots Challenge - Beep Boop Binary Decoder

Challenge: "Beep Boop"
Category: MISC

Solution: Decode Beep/Boop as binary (Beep=1, Boop=0 or vice versa)
"""

def decode_beep_boop(text):
    """Decode Beep/Boop to text"""
    text = text.upper().strip()
    
    print("="*70)
    print("ROBOTS - Beep Boop Decoder")
    print("="*70)
    print(f"\nInput length: {len(text)} characters")
    print(f"Input preview: {text[:100]}...")
    print()
    
    # Count beeps and boops
    beep_count = text.count('BEEP')
    boop_count = text.count('BOOP')
    print(f"Beep count: {beep_count}")
    print(f"Boop count: {boop_count}")
    print(f"Total bits: {beep_count + boop_count}")
    print()
    
    # Try both interpretations
    for beep_val, boop_val in [('1', '0'), ('0', '1')]:
        print(f"[*] Trying Beep={beep_val}, Boop={boop_val}...")
        
        # Replace Beep/Boop with binary
        binary = text.replace('BEEP', beep_val).replace('BOOP', boop_val)
        
        # Remove non-binary characters
        binary = ''.join(c for c in binary if c in '01')
        
        print(f"    Binary: {binary[:64]}...")
        print(f"    Length: {len(binary)} bits ({len(binary)//8} bytes)")
        
        # Convert to ASCII
        try:
            result = ''
            for i in range(0, len(binary), 8):
                byte = binary[i:i+8]
                if len(byte) == 8:
                    result += chr(int(byte, 2))
            
            print(f"    Decoded: {result}")
            
            if 'CIT{' in result:
                print(f"\n{'='*70}")
                print(f"[!!!] FLAG FOUND: {result}")
                print(f"{'='*70}")
                return result
        except Exception as e:
            print(f"    Error: {e}")
        
        print()
    
    return None

# Test with example
if __name__ == "__main__":
    # Example: "CIT{test}" in binary
    # C=67=01000011, I=73=01001001, T=84=01010100, {=123=01111011
    # t=116=01110100, e=101=01100101, s=115=01110011, t=116=01110100, }=125=01111101
    
    example = """
    BEEP BOOP BEEP BEEP BEEP BEEP BEEP BEEP 
    BEEP BOOP BEEP BEEP BEEP BEEP BEEP BEEP
    BEEP BOOP BEEP BEEP BEEP BEEP BEEP BEEP
    """
    
    print("Example test (should decode to 'CCC'):")
    decode_beep_boop(example)
    
    print("\n" + "="*70)
    print("Paste the actual Beep Boop sequence to decode it")
    print("="*70)
