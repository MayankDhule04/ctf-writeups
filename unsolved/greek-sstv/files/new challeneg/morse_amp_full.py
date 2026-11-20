import scipy.io.wavfile as wavfile
import numpy as np

rate, data = wavfile.read(r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\GREEK.wav")
if len(data.shape) > 1: data = data[:, 0]

chunk_size = int(rate * 0.05) # 50ms chunks
max_amps = [int(np.max(np.abs(data[i:i+chunk_size]))) for i in range(0, len(data), chunk_size)]

is_loud = np.array(max_amps) > 25000

# Identify morse elements
changes = np.where(is_loud[:-1] != is_loud[1:])[0]
changes = np.insert(changes, 0, 0)
changes = np.append(changes, len(is_loud))

out = ""
for i in range(len(changes)-1):
    state = "L" if is_loud[changes[i]+1] else "Q"
    length = changes[i+1] - changes[i]
    if state == "L":
        if length < 5: # < 250ms -> dot
            out += "."
        else: # >= 250ms -> dash
            out += "-"
    else:
        if length > 2 and length < 6:
             out += "" # intra char
        elif length >= 6 and length < 12:
             out += " " # inter char
        elif length >= 12:
             if len(out) > 0 and out[-1] != "/":
                 out += " / "

print("Amplitude Morse String:")
print(out)

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
inv_morse = {v: k for k, v in MORSE_CODE_DICT.items()}
decoded = ""
for word in out.split("/"):
    for char in word.strip().split():
        if char in inv_morse:
            decoded += inv_morse[char]
        else:
            decoded += "?"
    decoded += " "
print("Decoded:")
print(decoded)

