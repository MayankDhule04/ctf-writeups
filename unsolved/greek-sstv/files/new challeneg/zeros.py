import scipy.io.wavfile as wavfile
import numpy as np

filename = r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\GREEK.wav"
rate, data = wavfile.read(filename)
if len(data.shape) > 1: data = data[:, 0]

zeros = np.where(data == 0)[0]
print(f"Total zeros: {len(zeros)}")

if len(zeros) > 0:
    diffs = np.diff(zeros)
    print("Differences between zero-crossings (up to 50):", diffs[:50])

print("Let's look for Morse code or other patterns in the diffs.")
