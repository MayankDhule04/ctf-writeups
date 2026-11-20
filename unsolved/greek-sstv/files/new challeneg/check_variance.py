import scipy.io.wavfile as wavfile
import numpy as np

rate, data = wavfile.read(r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\GREEK.wav")
if len(data.shape) > 1: data = data[:, 0]

chunk_size = int(rate * 0.05) # 50ms chunks
vars = [np.var(data[i:i+chunk_size]) for i in range(0, len(data), chunk_size)]

print("Variance in 50ms chunks (first 200 chunks, 10 seconds):")
for i in range(0, min(200, len(vars)), 20):
    print([int(v) for v in vars[i:i+20]])

print(f"Minimum variance: {np.min(vars)}")
print(f"Maximum variance: {np.max(vars)}")

# Count chunks with low variance
low_var = [v for v in vars if v < np.max(vars)*0.1]
print(f"Chunks with <10% max variance: {len(low_var)}")
