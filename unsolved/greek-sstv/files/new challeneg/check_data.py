import scipy.io.wavfile as wavfile
import numpy as np

rate, data = wavfile.read(r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\GREEK.wav")
if len(data.shape) > 1: data = data[:, 0]

print("First 2000 samples:")
print(data[:2000])

zeros = np.where(data == 0)[0]
if len(zeros) > 1:
    print(f"Index of first zero: {zeros[0]}")
    print(f"Index of second zero: {zeros[1]}")
    
    start, end = zeros[0], zeros[1]
    print(f"Data between first and second zero (length {end-start}):")
    print(data[start:end+1])
