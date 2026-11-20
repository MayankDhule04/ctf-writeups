import scipy.io.wavfile as wavfile
import numpy as np

rate, data = wavfile.read(r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\GREEK.wav")
if len(data.shape) > 1: data = data[:, 0]

# "rhythm of silence itself"
# Find exact 0 blocks
is_zero = (data == 0)

changes = np.where(is_zero[:-1] != is_zero[1:])[0]
changes = np.insert(changes, 0, 0)
changes = np.append(changes, len(is_zero))

zero_lengths = []
sound_lengths = []

for i in range(len(changes)-1):
    length = (changes[i+1] - changes[i])
    if is_zero[changes[i]+1]:
        zero_lengths.append(length)
    else:
        sound_lengths.append(length)

print("Zero block lengths:")
zero_lengths.sort()
print(zero_lengths[-20:])

# Actually, let's print them in order of occurrence
out = []
for i in range(len(changes)-1):
    length = (changes[i+1] - changes[i])
    if is_zero[changes[i]+1]:
        if length > 10:
            out.append(f"Z:{length}")
    else:
        if length > 10:
            out.append(f"S:{length}")

print("First 50 blocks:")
print(out[:50])

