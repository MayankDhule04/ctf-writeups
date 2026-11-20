import scipy.io.wavfile as wavfile
from scipy import signal
import numpy as np

print("Loading data...")
filename = r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\GREEK.wav"
rate, data = wavfile.read(filename)
if len(data.shape) > 1: data = data[:, 0]

f, t, Sxx = signal.spectrogram(data, rate, nperseg=4096)
# Look for 1200 Hz sync pulse
idx_1200 = np.argmin(np.abs(f - 1200))
print(f"Freq bin at {f[idx_1200]} Hz")

energy_1200 = Sxx[idx_1200, :]
if np.max(energy_1200) > np.median(energy_1200) * 10:
    print("Found strong 1200Hz signal! This could be SSTV.")
else:
    print("No strong 1200Hz SSTV sync found.")

# Look for high frequency text > 15kHz (Unseen frequencies)
high_f_idx = f > 15000
energy_high = np.sum(Sxx[high_f_idx, :], axis=0)
if np.max(energy_high) > np.median(energy_high) * 5:
    print("Found strong high frequency activity! This is the Spectrogram (unseen) text.")
else:
    print("No strong high frequency.")
