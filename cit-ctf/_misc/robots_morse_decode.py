#!/usr/bin/env python3
"""
Robots Challenge - Morse Code Decoder

If "Beep Boop" represents Morse code:
- Beep = dot (.)
- Boop = dash (-)
"""

# Morse code dictionary
MORSE_TO_CHAR = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z',
    '-----': '0', '.----': '1', '..---': '2', '...--': '3',
    '....-': '4', '.....': '5', '-....': '6', '--...': '7',
    '---..': '8', '----.': '9'
}

def decode_morse(morse_text):
    """Decode morse code to text"""
    result = ''
    for code in morse_text.split():
        if code in MORSE_TO_CHAR:
            result += MORSE_TO_CHAR[code]
        else:
            result += '?'
    return result

print("="*70)
print("ROBOTS - Morse Code Analysis")
print("="*70)
print()

# Try "Beep Boop" as morse
print("[*] Interpreting 'Beep Boop' as Morse Code:")
print("    Beep = . (dot)")
print("    Boop = - (dash)")
print()

morse1 = ". -"  # Beep Boop
decoded1 = decode_morse(morse1)
print(f"    'Beep Boop' = '{morse1}' = '{decoded1}'")

# Try reverse
morse2 = "- ."  # Boop Beep
decoded2 = decode_morse(morse2)
print(f"    'Boop Beep' = '{morse2}' = '{decoded2}'")

print()
print("[*] Analyzing challenge metadata:")
print("    Title: Robots")
print("    Number: 892")
print("    Category: bootstrap")
print("    Likes: 8 (88% liked)")
print()

# Try converting numbers to characters
print("[*] Converting numbers to ASCII:")
print(f"    892 as ASCII: {chr(892) if 892 < 1114112 else 'out of range'}")
print(f"    8 as ASCII: '{chr(8)}' (backspace)")
print(f"    88 as ASCII: '{chr(88)}' = 'X'")
print()

# Try as hex
print("[*] Trying as hex:")
print(f"    0x892 = {int('892', 16)} = '{chr(int('892', 16))}'")
print(f"    0x8 = {int('8', 16)} = '{chr(int('8', 16))}'")
print()

# Bootstrap could be a hint
print("[*] 'bootstrap' could mean:")
print("    - Bootstrap framework (web)")
print("    - Bootstrapping (starting/initializing)")
print("    - Bootstrap class in CSS")
print()

print("="*70)
print("RECOMMENDATION:")
print("Check the page source, inspect element, or look for:")
print("  - Hidden HTML comments")
print("  - CSS classes named 'bootstrap'")
print("  - JavaScript variables")
print("  - Network requests")
print("  - Downloadable files")
print("="*70)
