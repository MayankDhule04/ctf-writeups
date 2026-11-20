#!/usr/bin/env python3
"""
Wiretap - Alternative approaches
Maybe the tones encode something else, or there's hidden data
"""

import wave
import numpy as np

sequence = "14155551998887*7788*707*87*77*8*7**8877**8**787"

print("="*70)
print("WIRETAP - ALTERNATIVE DECODING")
print("="*70)

print(f"\nSequence: {sequence}")
print(f"Length: {len(sequence)}")

# Remove the phone number prefix
if sequence.startswith("1415555"):
    message_part = sequence[11:]  # Skip "14155551998"
    print(f"\nAfter removing phone number: {message_part}")
else:
    message_part = sequence

# Try interpreting * as separator and numbers as binary or morse
print(f"\n[1] Treating * as word separator:")
words = message_part.split('*')
print(f"  Words: {[w for w in words if w]}")

# Try Morse-like: 7=dit, 8=dah
print(f"\n[2] Morse interpretation (7=dit ., 8=dah -):")
morse_map = {'7': '.', '8': '-', '0': ' '}
morse_parts = []
for word in words:
    if word:
        morse = ''.join(morse_map.get(c, c) for c in word)
        morse_parts.append(morse)
        print(f"  {word} -> {morse}")

# Standard Morse code
morse_to_char = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z'
}

print(f"\n  Morse decode:")
decoded_morse = []
for morse in morse_parts:
    if morse in morse_to_char:
        decoded_morse.append(morse_to_char[morse])
        print(f"    {morse} -> {morse_to_char[morse]}")
    elif morse.strip():
        print(f"    {morse} -> ???")

if decoded_morse:
    morse_text = ''.join(decoded_morse)
    print(f"\n  Decoded: {morse_text}")
    print(f"  FLAG: CIT{{{morse_text.lower()}}}")

# Try binary (7=0, 8=1)
print(f"\n[3] Binary interpretation (7=0, 8=1):")
for word in words:
    if word and all(c in '78' for c in word):
        binary = word.replace('7', '0').replace('8', '1')
        if len(binary) % 8 == 0:
            # Convert to ASCII
            chars = []
            for i in range(0, len(binary), 8):
                byte = binary[i:i+8]
                chars.append(chr(int(byte, 2)))
            text = ''.join(chars)
            print(f"  {word} -> {binary} -> {text}")

# Check audio for LSB steganography
print(f"\n[4] Checking audio for hidden data:")
wav_file = "beep_beep_boop.wav"
with wave.open(wav_file, 'rb') as wav:
    frames = wav.readframes(wav.getnframes())
    audio_data = np.frombuffer(frames, dtype=np.int16)
    
    # Extract LSBs
    lsbs = audio_data & 1
    
    # Try to find patterns
    print(f"  Total samples: {len(lsbs)}")
    print(f"  LSB 0s: {np.sum(lsbs == 0)}")
    print(f"  LSB 1s: {np.sum(lsbs == 1)}")
    
    # Try to extract bytes from LSBs
    lsb_bytes = []
    for i in range(0, min(1000, len(lsbs)), 8):
        if i + 8 <= len(lsbs):
            byte_bits = lsbs[i:i+8]
            byte_val = int(''.join(str(b) for b in byte_bits), 2)
            if 32 <= byte_val < 127:
                lsb_bytes.append(chr(byte_val))
    
    if lsb_bytes:
        lsb_text = ''.join(lsb_bytes[:100])
        print(f"  LSB text (first 100 chars): {lsb_text}")

print(f"\n{'='*70}")
