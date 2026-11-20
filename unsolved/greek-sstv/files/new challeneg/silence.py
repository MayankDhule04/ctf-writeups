import scipy.io.wavfile as wavfile
import numpy as np

filename = r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\GREEK.wav"
rate, data = wavfile.read(filename)

if len(data.shape) > 1:
    data = data[:, 0]

# "rhythm of silence itself"
# Let's find exactly when the audio is completely silent
# threshold = 0 or very small
is_silent = np.abs(data) <= 5

changes = np.where(is_silent[:-1] != is_silent[1:])[0]
changes = np.insert(changes, 0, 0)
changes = np.append(changes, len(is_silent))

print("Silence lengths (s):")
silences = []
for i in range(len(changes)-1):
    length = changes[i+1] - changes[i]
    if is_silent[changes[i]+1]:
        duration = length / rate
        if duration > 0.05: # ignore micro-silences
            silences.append(duration)

print(silences[:50])

print("Sound lengths (s):")
sounds = []
for i in range(len(changes)-1):
    length = changes[i+1] - changes[i]
    if not is_silent[changes[i]+1]:
        duration = length / rate
        if duration > 0.05:
            sounds.append(duration)
print(sounds[:50])
