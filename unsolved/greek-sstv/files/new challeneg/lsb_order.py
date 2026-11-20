import scipy.io.wavfile as wavfile
import numpy as np

rate, data = wavfile.read(r"c:\Users\mayan\OneDrive\Desktop\ctf\new challeneg\GREEK.wav")
if len(data.shape) > 1: data = data[:, 0]

lsb_bits = np.bitwise_and(data, 1)

# Padded to multiple of 8
bits_padded = np.pad(lsb_bits, (0, (8 - len(lsb_bits) % 8) % 8))
byte_array = bits_padded.reshape(-1, 8)

# Try LSB first
byte_array_lsb = byte_array[:, ::-1]
bytes_lsb = np.packbits(byte_array_lsb, axis=1).reshape(-1).tobytes()

print(f"Signature (LSB first): {bytes_lsb[:16].hex()}")

# Try searching for text
import re
ascii_text = "".join([chr(b) for b in bytes_lsb if 32 <= b <= 126])

matches_lsb = re.finditer(r'.{0,30}(flag|ctf|part).{0,30}', ascii_text, re.IGNORECASE)
print("Matches:")
for m in matches_lsb:
    print(m.group(0))

import string
printable = bytes_lsb
idx = printable.lower().find(b"part")
if idx != -1:
    print("Found 'part' in bytes:")
    print(printable[max(0, idx-50):min(len(printable), idx+50)])
    
idx2 = printable.lower().find(b"ctf")
if idx2 != -1:
    print("Found 'ctf' in bytes:")
    print(printable[max(0, idx2-50):min(len(printable), idx2+50)])
