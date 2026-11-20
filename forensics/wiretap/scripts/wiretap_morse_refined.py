#!/usr/bin/env python3
"""
Wiretap - Refined Morse Code Decoding
7 = dit (.), 8 = dah (-), * = letter separator, 0 = word separator
"""

sequence = "14155551998887*7788*707*87*77*8*7**8877**8**787"

# Remove phone number
message = sequence[11:]  # Skip "14155551998"

print("="*70)
print("WIRETAP - MORSE CODE DECODER")
print("="*70)

print(f"\nFull sequence: {sequence}")
print(f"Message part: {message}")

# Morse code table
morse_to_char = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z', '-----': '0', '.----': '1', '..---': '2', '...--': '3',
    '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8',
    '----.': '9'
}

# Convert to Morse: 7=., 8=-, 0=space, *=letter separator
print(f"\n[1] Converting to Morse code:")
print(f"  7 = . (dit)")
print(f"  8 = - (dah)")
print(f"  * = letter separator")
print(f"  0 = word space")

# Split by * to get individual letters
letters = message.split('*')
decoded = []

print(f"\n[2] Decoding each letter:")
for i, letter_code in enumerate(letters):
    if not letter_code:
        continue
    
    # Convert to Morse
    morse = letter_code.replace('7', '.').replace('8', '-').replace('0', ' ')
    
    # Try to decode
    if morse in morse_to_char:
        char = morse_to_char[morse]
        decoded.append(char)
        print(f"  {letter_code:10s} -> {morse:10s} -> {char}")
    elif morse.strip() == '':
        decoded.append(' ')
        print(f"  {letter_code:10s} -> (space)")
    else:
        print(f"  {letter_code:10s} -> {morse:10s} -> ???")

result = ''.join(decoded)

print(f"\n{'='*70}")
print(f"DECODED MESSAGE: {result}")
print(f"{'='*70}")

# Check if it's a flag
if result:
    print(f"\nPossible flag: CIT{{{result.lower()}}}")
    
    # Try reversed
    reversed_result = result[::-1]
    print(f"Reversed: {reversed_result}")
    print(f"Reversed flag: CIT{{{reversed_result.lower()}}}")

print(f"\n{'='*70}")
