import scipy.io.wavfile as wavfile
import numpy as np
import struct
import math
import os

filename = r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\GREEK.wav"

print("Loading audio...")
rate, data = wavfile.read(filename)

# Ensure mono
if len(data.shape) > 1:
    data = data[:, 0]

print(f"Loaded. Rate: {rate}, Samples: {len(data)}")

# --- Layer 1: Spectrogram (Frequencies Seen) ---
print("\n--- Scanning Spectrogram ---")
try:
    from scipy import signal
    f, t, Sxx = signal.spectrogram(data, rate, nperseg=1024)
    # Sxx shape is (freq_bins, time_bins)
    # Let's find freq_bins with high energy over time
    # To ascii art, we bin into 40 rows and 100 cols
    
    row_bins = 40
    col_bins = 120
    
    f_step = Sxx.shape[0] // row_bins
    t_step = Sxx.shape[1] // col_bins
    
    ascii_chars = " .:-=+*#%@"
    
    print("ASCII Spectrogram:")
    for r in range(row_bins-1, -1, -1):
        row_str = ""
        for c in range(col_bins):
            # average energy in this block
            block = Sxx[r*f_step:(r+1)*f_step, c*t_step:(c+1)*t_step]
            val = np.mean(block)
            row_str += f"{val:10.2e} "
            
        # Instead of raw values, let's normalize and print chars
        pass # Too noisy to print raw. Let's do properly
        
    Sxx_log = np.log10(Sxx + 1e-10)
    Sxx_norm = (Sxx_log - np.min(Sxx_log)) / (np.max(Sxx_log) - np.min(Sxx_log))
    
    for r in range(row_bins-1, -1, -1):
        row_str = ""
        for c in range(col_bins):
            block = Sxx_norm[r*f_step:(r+1)*f_step, c*t_step:(c+1)*t_step]
            val = np.mean(block)
            idx = int(val * (len(ascii_chars)-1))
            row_str += ascii_chars[idx]
        print(row_str)
        
except Exception as e:
    print("Spectrogram fail:", e)

# --- Layer 2: Morse Code in Silence/Amplitude (Rhythm of Silence) ---
print("\n--- Scanning for Morse Code (Amplitude variations) ---")
# Envelope detection
env = np.abs(data)

# Smoothing
window_size = rate // 10 # 0.1s
window = np.ones(window_size) / window_size
env_smooth = np.convolve(env, window, mode='same')

threshold = np.max(env_smooth) * 0.2
is_loud = env_smooth > threshold

# Find lengths of loud and quiet segments
changes = np.where(is_loud[:-1] != is_loud[1:])[0]
changes = np.insert(changes, 0, 0)
changes = np.append(changes, len(is_loud))

morse = ""
for i in range(len(changes)-1):
    length = changes[i+1] - changes[i]
    duration = length / rate
    if is_loud[changes[i]+1]:
        # Loud part (dot or dash)
        if 0.05 < duration < 0.2:
            morse += "."
        elif 0.2 <= duration < 0.6:
            morse += "-"
    else:
        # Quiet part (intra-char, inter-char, space)
        if 0.2 < duration < 0.6:
            morse += " "
        elif duration >= 0.6:
            morse += " / "

print("Extracted Morse-like sequence:")
print(morse[:1000]) # Print first 1000 chars

# --- Layer 3: Smallest Bits (LSB Steganography) ---
print("\n--- Scanning LSB ---")
lsb_bits = np.bitwise_and(data, 1)

# Pack into bytes
bytes_list = np.packbits(lsb_bits)
print(f"Extracted {len(bytes_list)} bytes from LSB.")

with open(r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\lsb.bin", "wb") as f:
    f.write(bytes_list.tobytes())

# Check signature
signature = bytes_list[:16].tobytes()
print(f"File signature (hex): {signature.hex()}")

# Print first few chars if ASCII
ascii_start = bytes_list[:200].tobytes()
print("First 200 bytes as ASCII:", ascii_start)
import string
printable = bytes_list.tobytes()
print("Searching for 'flag', 'part', 'ctf' in LSB...")
idx = printable.lower().find(b"ctf")
if idx != -1:
    print("Found 'ctf' in LSB:", printable[max(0, idx-20):min(len(printable), idx+50)])
idx = printable.lower().find(b"flag")
if idx != -1:
    print("Found 'flag' in LSB:", printable[max(0, idx-20):min(len(printable), idx+50)])
idx = printable.lower().find(b"part")
if idx != -1:
    print("Found 'part' in LSB:", printable[max(0, idx-20):min(len(printable), idx+50)])

