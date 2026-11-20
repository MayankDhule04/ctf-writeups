import scipy.io.wavfile as wavfile
import numpy as np

filename = r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\GREEK.wav"
rate, data = wavfile.read(filename)
if len(data.shape) > 1: data = data[:, 0]

zeros = np.where(data == 0)[0]
diffs = np.diff(zeros)

# Translate to morse
out = ""
for d in diffs:
    if abs(d - 441) < 10:
        out += "-"
    elif abs(d - 147) < 10:
        out += "."
    elif abs(d - 3087) < 50: # Maybe 7x for word space?
        out += " / "
    elif abs(d - 1323) < 20: # Maybe 3x for letter space?
        out += " "
    else:
        out += f"[{d}]"

print("Morse string:")
print(out)
