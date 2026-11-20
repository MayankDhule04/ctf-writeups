import scipy.io.wavfile as wavfile
import numpy as np

rate, data = wavfile.read(r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\GREEK.wav")
if len(data.shape) > 1: data = data[:, 0]

chunk_size = int(rate * 0.05) # 50ms chunks
max_amps = [int(np.max(np.abs(data[i:i+chunk_size]))) for i in range(0, len(data), chunk_size)]

print("Max amplitudes in 50ms chunks (first 200 chunks, 10 seconds):")
for i in range(0, min(200, len(max_amps)), 20):
    print(max_amps[i:i+20])
