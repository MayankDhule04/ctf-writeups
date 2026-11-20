#!/usr/bin/env python3
"""
Wiretap Challenge - Audio Forensics
Hint: "they're listening to the phones" - likely DTMF tones
"""

import wave
import struct
import numpy as np

wav_file = "beep_beep_boop.wav"

print("="*70)
print("WIRETAP - AUDIO FORENSICS")
print("="*70)

# Read WAV file
with wave.open(wav_file, 'rb') as wav:
    print(f"\n[1] WAV File Information:")
    print(f"  Channels: {wav.getnchannels()}")
    print(f"  Sample Width: {wav.getsampwidth()} bytes")
    print(f"  Frame Rate: {wav.getframerate()} Hz")
    print(f"  Frames: {wav.getnframes()}")
    print(f"  Duration: {wav.getnframes() / wav.getframerate():.2f} seconds")
    
    # Read audio data
    frames = wav.readframes(wav.getnframes())
    
# Convert to numpy array
if wav.getsampwidth() == 2:
    audio_data = np.frombuffer(frames, dtype=np.int16)
elif wav.getsampwidth() == 1:
    audio_data = np.frombuffer(frames, dtype=np.uint8)
else:
    audio_data = np.frombuffer(frames, dtype=np.int32)

print(f"\n[2] Audio Data:")
print(f"  Samples: {len(audio_data)}")
print(f"  Min: {audio_data.min()}, Max: {audio_data.max()}")

# DTMF frequency pairs
# Each DTMF tone is a combination of two frequencies
DTMF_FREQS = {
    '1': (697, 1209), '2': (697, 1336), '3': (697, 1477), 'A': (697, 1633),
    '4': (770, 1209), '5': (770, 1336), '6': (770, 1477), 'B': (770, 1633),
    '7': (852, 1209), '8': (852, 1336), '9': (852, 1477), 'C': (852, 1633),
    '*': (941, 1209), '0': (941, 1336), '#': (941, 1477), 'D': (941, 1633),
}

print(f"\n[3] Attempting DTMF Detection:")
print("  (DTMF = Dual-Tone Multi-Frequency - phone keypad tones)")

# Try to detect DTMF tones using FFT
# Split audio into chunks and analyze each
sample_rate = wav.getframerate()
chunk_size = int(sample_rate * 0.1)  # 100ms chunks
hop_size = int(sample_rate * 0.05)   # 50ms hop

detected_tones = []

for i in range(0, len(audio_data) - chunk_size, hop_size):
    chunk = audio_data[i:i+chunk_size]
    
    # Apply FFT
    fft = np.fft.fft(chunk)
    freqs = np.fft.fftfreq(len(chunk), 1/sample_rate)
    
    # Get magnitude spectrum (positive frequencies only)
    magnitude = np.abs(fft[:len(fft)//2])
    freqs = freqs[:len(freqs)//2]
    
    # Find peaks
    threshold = np.max(magnitude) * 0.3
    peaks = []
    for j in range(1, len(magnitude)-1):
        if magnitude[j] > threshold and magnitude[j] > magnitude[j-1] and magnitude[j] > magnitude[j+1]:
            peaks.append((freqs[j], magnitude[j]))
    
    # Sort by magnitude
    peaks.sort(key=lambda x: x[1], reverse=True)
    
    # Check if we have DTMF tones
    if len(peaks) >= 2:
        freq1, freq2 = sorted([peaks[0][0], peaks[1][0]])
        
        # Match to DTMF
        for digit, (f1, f2) in DTMF_FREQS.items():
            if abs(freq1 - f1) < 50 and abs(freq2 - f2) < 50:
                if not detected_tones or detected_tones[-1] != digit:
                    detected_tones.append(digit)
                    print(f"  Time {i/sample_rate:.2f}s: Detected '{digit}' ({freq1:.0f}Hz, {freq2:.0f}Hz)")
                break

if detected_tones:
    result = ''.join(detected_tones)
    print(f"\n[4] Detected DTMF Sequence:")
    print(f"  {result}")
    
    # Try to decode as phone number or text
    # Phone keypad mapping (T9)
    phone_map = {
        '2': 'ABC', '3': 'DEF', '4': 'GHI', '5': 'JKL',
        '6': 'MNO', '7': 'PQRS', '8': 'TUV', '9': 'WXYZ',
        '0': ' ', '1': '', '*': '', '#': ''
    }
    
    print(f"\n[5] Possible Interpretations:")
    print(f"  As phone number: {result}")
    
    # Try multi-tap decoding (like old phone texting)
    # This is complex, so just show the mapping
    print(f"\n  Phone keypad mapping:")
    for digit in result:
        if digit in phone_map:
            print(f"    {digit} -> {phone_map[digit]}")
    
    # Check if it looks like a flag
    if 'CIT' in result or 'FLAG' in result:
        print(f"\n  ✓ Contains flag pattern!")
else:
    print("  No DTMF tones detected")

print("\n" + "="*70)
