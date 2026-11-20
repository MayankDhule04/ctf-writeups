import scipy.io.wavfile as wavfile
import numpy as np

rate, data = wavfile.read(r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\GREEK.wav")
if len(data.shape) > 1: data = data[:, 0]

# Amplitude threshold
is_loud = np.abs(data) > 50

# Find where it changes
changes = np.where(is_loud[:-1] != is_loud[1:])[0]

# Add start and end
changes = np.insert(changes, 0, 0)
changes = np.append(changes, len(data))

elements = []
for i in range(len(changes)-1):
    length = (changes[i+1] - changes[i]) / rate
    # If loud segment
    if is_loud[changes[i]+1]:
        elements.append(("LOUD", length))
    else:
        elements.append(("QUIET", length))

# Filter out very short spikes (noise)
filtered_elements = []
for state, length in elements:
    if length > 0.02: # 20ms
        filtered_elements.append((state, length))

print(f"Total elements: {len(filtered_elements)}")
print("First 20 elements:")
for e in filtered_elements[:20]:
    print(f"{e[0]}: {e[1]:.4f}")

morse = ""
for state, length in filtered_elements:
    if state == "LOUD":
        if 0.02 < length < 0.15:
            morse += "."
        elif 0.15 <= length < 0.4:
            morse += "-"
    else:
        if 0.05 < length < 0.2:
            morse += "" # space within char
        elif 0.2 <= length < 0.5:
            morse += " " # space between chars
        elif length >= 0.5:
            morse += " / "

print("\nMorse:")
print(morse[:200])

import urllib.request
# Just simple morse dictionary
MORSE_CODE_DICT = { 'A':'.-', 'B':'-...',
                    'C':'-.-.', 'D':'-..', 'E':'.',
                    'F':'..-.', 'G':'--.', 'H':'....',
                    'I':'..', 'J':'.---', 'K':'-.-',
                    'L':'.-..', 'M':'--', 'N':'-.',
                    'O':'---', 'P':'.--.', 'Q':'--.-',
                    'R':'.-.', 'S':'...', 'T':'-',
                    'U':'..-', 'V':'...-', 'W':'.--',
                    'X':'-..-', 'Y':'-.--', 'Z':'--..',
                    '1':'.----', '2':'..---', '3':'...--',
                    '4':'....-', '5':'.....', '6':'-....',
                    '7':'--...', '8':'---..', '9':'----.',
                    '0':'-----', ', ':'--..--', '.':'.-.-.-',
                    '?':'..--..', '/':'-..-.', '-':'-....-',
                    '(':'-.--.', ')':'-.--.-'}

# inverse dictionary
inv_morse = {v: k for k, v in MORSE_CODE_DICT.items()}

decoded = ""
for word in morse.split(" / "):
    for char in word.split():
        if char in inv_morse:
            decoded += inv_morse[char]
        else:
            decoded += "?"
    decoded += " "
print(f"Decoded: {decoded[:200]}")
