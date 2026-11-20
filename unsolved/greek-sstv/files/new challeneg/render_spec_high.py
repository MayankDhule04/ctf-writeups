import scipy.io.wavfile as wavfile
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np

print("Loading data...")
filename = r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\GREEK.wav"
rate, data = wavfile.read(filename)
if len(data.shape) > 1: data = data[:, 0]

print("Rendering spectrogram...")
f, t, Sxx = signal.spectrogram(data, rate, nperseg=4096, noverlap=3000)

plt.figure(figsize=(24, 4))
plt.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), shading='gouraud')
plt.ylabel('Freq')
plt.title('Spectrogram (High Frequencies)')
plt.ylim([15000, 22000]) # Unseen frequencies

plt.savefig(r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\spec_high.png", bbox_inches='tight', dpi=300)
print("Saved spec_high.png")
