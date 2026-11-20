import scipy.io.wavfile as wavfile
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np

print("Loading data...")
filename = r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\GREEK.wav"
rate, data = wavfile.read(filename)
if len(data.shape) > 1: data = data[:, 0]

print("Rendering spectrogram...")
f, t, Sxx = signal.spectrogram(data, rate, nperseg=4096, noverlap=2048)

plt.figure(figsize=(24, 8))
plt.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), shading='gouraud')
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
plt.title('Spectrogram')
# Limit to ultrasound? "frequencies seen and unseen" 
# Usually unseen means high frequency > 15kHz
plt.ylim([0, 22000])

plt.savefig(r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\spec.png", bbox_inches='tight', dpi=300)
print("Saved spec.png")
