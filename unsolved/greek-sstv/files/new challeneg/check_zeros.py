import scipy.io.wavfile as wavfile
import numpy as np

rate, data = wavfile.read(r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\GREEK.wav")
if len(data.shape) > 1: data = data[:, 0]

zeros = np.where(data == 0)[0]
print(f"Total zeros: {len(zeros)}")
print(f"First zero index: {zeros[0]}")
print(f"Last zero index: {zeros[-1]}")
print(f"Total samples: {len(data)}")

# What proportion of the audio has exact zeros?
print(f"Exact zeros end at {(zeros[-1] / len(data)) * 100:.2f}% of the audio.")
