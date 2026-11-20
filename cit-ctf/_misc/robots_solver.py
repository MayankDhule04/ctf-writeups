#!/usr/bin/env python3
"""
Robots Challenge - Beep Boop Decoder

Challenge: "Beep Boop"
Category: MISC

Common interpretations:
1. Beep = 1, Boop = 0 (or vice versa)
2. Binary encoding
3. Morse code
4. Robot language cipher
"""

# If we have the actual challenge text, we can decode it
# For now, let's create decoders for common patterns

def beep_boop_to_binary(text, beep_is_one=True):
    """Convert Beep/Boop to binary"""
    text = text.upper()
    if beep_is_one:
        binary = text.replace('BEEP', '1').replace('BOOP', '0')
    else:
        binary = text.replace('BEEP', '0').replace('BOOP', '1')
    
    # Remove spaces and non-binary chars
    binary = ''.join(c for c in binary if c in '01')
    return binary

def binary_to_text(binary):
    """Convert binary string to ASCII text"""
    result = ''
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:
            result += chr(int(byte, 2))
    return result

def decode_beep_boop(text):
    """Try both interpretations"""
    print(f"Input: {text[:100]}...")
    print()
    
    # Try Beep=1, Boop=0
    print("[*] Trying Beep=1, Boop=0...")
    binary1 = beep_boop_to_binary(text, beep_is_one=True)
    if binary1:
        print(f"    Binary: {binary1[:64]}...")
        try:
            decoded1 = binary_to_text(binary1)
            print(f"    Decoded: {decoded1}")
            if 'CIT{' in decoded1:
                print(f"    [!!!] FLAG FOUND: {decoded1}")
                return decoded1
        except:
            print(f"    Failed to decode")
    
    # Try Beep=0, Boop=1
    print("\n[*] Trying Beep=0, Boop=1...")
    binary2 = beep_boop_to_binary(text, beep_is_one=False)
    if binary2:
        print(f"    Binary: {binary2[:64]}...")
        try:
            decoded2 = binary_to_text(binary2)
            print(f"    Decoded: {decoded2}")
            if 'CIT{' in decoded2:
                print(f"    [!!!] FLAG FOUND: {decoded2}")
                return decoded2
        except:
            print(f"    Failed to decode")
    
    return None

# Example usage
if __name__ == "__main__":
    print("="*70)
    print("ROBOTS - Beep Boop Decoder")
    print("="*70)
    print()
    
    # Test with example
    example = "BEEP BOOP BEEP BEEP BOOP BOOP BEEP BOOP"
    print("Example test:")
    decode_beep_boop(example)
    
    print("\n" + "="*70)
    print("Waiting for actual challenge text...")
    print("="*70)
