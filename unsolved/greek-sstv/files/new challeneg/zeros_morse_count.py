import scipy.io.wavfile as wavfile
import numpy as np

rate, data = wavfile.read(r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\GREEK.wav")
if len(data.shape) > 1: data = data[:, 0]

zeros = np.where(data == 0)[0]
diffs = np.diff(zeros)

unique_diffs, counts = np.unique(diffs, return_counts=True)
print("Unique diffs and their counts:")
for u, c in zip(unique_diffs, counts):
    if c > 2:
        print(f"{u}: {c}")

d_list = list(diffs)

morse = ""
for d in d_list:
    if d == 441:
        morse += "-"
    elif d == 147:
        morse += "."
    elif d == 1323:
        morse += " "
    elif d == 3087:
        morse += " / "
    else:
        # What is 4429, 4851, 4855 etc?
        pass

print("\nDecoded Morse:") # maybe there are elements separated by spaces
import re

out = ""
for d in d_list:
    if d == 441: out += "-"
    elif d == 147: out += "."
    elif d == 1323: out += " "
    elif d == 3087: out += " / "
print(out)
