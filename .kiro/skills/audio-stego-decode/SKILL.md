---
name: audio-stego-decode
description: Decode hidden data in audio files (WAV header mismatches, spectrogram text steganography, DTMF/Morse/SSTV tone encoding). Use when a CTF forensics/stego challenge provides a .wav/.mp3 file, especially with a suggestive name or hint implying the audio sounds wrong, garbled, or like noise that isn't what it appears.
---

## Why audio-stego gets its own checklist

This is a recurring, high-value category — multiple past challenges hid
flags in audio using one of a small number of techniques. Work through them
in this order.

## Step 1 — check the WAV header against the actual data (always first)

A WAV file can have a header that LIES about bit depth, causing players to
misinterpret the data and produce garbled "static" noise. Confirmed real
pattern: header declares 16-bit PCM, but `block_align` and `byte_rate`
fields prove it's actually 8-bit.

```python
import struct
data = bytearray(open("file.wav", "rb").read())
# WAV header: byte 34-35 = bits per sample, byte 32-33 = block_align,
# byte 28-31 = byte_rate, byte 24-27 = sample_rate
bits_per_sample = struct.unpack_from("<H", data, 34)[0]
block_align = struct.unpack_from("<H", data, 32)[0]
byte_rate = struct.unpack_from("<I", data, 28)[0]
sample_rate = struct.unpack_from("<I", data, 24)[0]
print(f"declared bits={bits_per_sample} block_align={block_align} byte_rate={byte_rate}")
# If block_align==1 and byte_rate==sample_rate, the real depth is 8-bit
# regardless of what bits_per_sample claims. Fix it:
struct.pack_into("<H", data, 34, 8)
open("file_fixed.wav", "wb").write(data)
```

A challenge named something like "I Can't Hear You" is itself the hint: you
CAN'T hear it correctly (header lies), but you CAN see it (next step).

## Step 2 — generate a spectrogram and look for TEXT, not sound

The single most common real pattern in this category: text is hidden
visually in the spectrogram, not audible in the waveform. Look specifically
in the 3000-8000 Hz band for horizontal bands forming letter shapes.

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
sr, audio = wavfile.read("file_fixed.wav")
if audio.ndim > 1: audio = audio[:, 0]
for nfft in (512, 2048, 4096):   # time-res, balanced, freq-res
    plt.figure(figsize=(20, 8))
    plt.specgram(audio.astype(float), NFFT=nfft, Fs=sr, cmap="gray")
    plt.ylim(0, 8000)
    plt.savefig(f"spectrogram_nfft{nfft}.png", dpi=150)
    plt.close()
```
Inspect each saved PNG visually (read_file / view the image) — don't rely on
OCR alone, visually scanning the 3-8kHz band is more reliable for CTF-style
block text.

## Step 3 — check for an unnaturally narrow dominant frequency band

If step 2 doesn't show text, check whether the "noise" is actually
synthesized tone(s). Real recordings (voice, animal sounds, ambient noise)
spread energy across a wide frequency range; a single sharp peak (e.g.
~495-503 Hz with very low zero-crossing rate) indicates deliberate tone
encoding, not natural sound — strong evidence that this IS the spectrogram
pattern from step 2 even if the first attempt didn't show clear text (retake
with different NFFT/contrast).

## Step 4 — DTMF / Morse / SSTV tone decoding

If the audio is clearly tone-based but not spectrogram-text:
1. **DTMF**: detect via the Goertzel algorithm (standard phone-keypad
   frequency pairs). If the decoded digit sequence doesn't read as a
   sensible phone number/text, don't discard it — try reinterpreting the
   SAME digit sequence as **Morse code** using an informal digit mapping
   (e.g. one digit = dot, another = dash, a third = letter-separator) before
   concluding the detection itself failed.
2. **SSTV** (Slow-Scan TV, encodes an IMAGE in audio): typical calibration
   tones near 1200/1500/1900/2300 Hz. If present, use an SSTV decoder
   (`qsstv` on Linux, or an online decoder) rather than trying to extract
   text — the payload is a picture, not characters.
3. **Extended DTMF** (A/B/C/D/# present): may indicate hex or a custom
   alphabet rather than standard 0-9 — try hex-decoding the detected tone
   sequence as a fallback.

## Step 5 — LSB steganography in raw samples (lower priority, usually a dead end)

Check all bit positions (0 through 15 for 16-bit audio), both LSB and MSB,
with multiple byte-alignment offsets (0-7) — but in this player's history
this has consistently NOT been where the flag was hidden when spectrogram
text or tone encoding was also present. Deprioritize this step if either of
those already shows promising signal.

## Reusable tooling

This player's own `ctf_tool` package (if available in the workspace) has a
dedicated `stego audio` subcommand covering LSB extraction, spectrogram
generation, and Morse detection in one pass — prefer it over writing a new
one-off script:
```bash
ctf_tool stego audio file.wav --all
ctf_tool stego audio file.wav --morse
```
