#!/usr/bin/env python3
"""
Wiretap - Complete audio scan for all DTMF tones
"""

import wave
import numpy as np

def goertzel(samples, sample_rate, target_freq):
    n = len(samples)
    k = int(0.5 + (n * target_freq) / sample_rate)
    omega = (2.0 * np.pi * k) / n
    cosine = np.cos(omega)
    coeff = 2.0 * cosine
    
    q0, q1, q2 = 0.0, 0.0, 0.0
    
    for sample in samples:
        q0 = coeff * q1 - q2 + sample
        q2 = q1
        q1 = q0
    
    magnitude = np.sqrt(q1**2 + q2**2 - q1*q2*coeff)
    return magnitude

def detect_dtmf_tone(samples, sample_rate):
    low_freqs = [697, 770, 852, 941]
    high_freqs = [1209, 1336, 1477, 1633]
    
    dtmf_table = [
        ['1', '2', '3', 'A'],
        ['4', '5', '6', 'B'],
        ['7', '8', '9', 'C'],
        ['*', '0', '#', 'D']
    ]
    
    low_mags = [goertzel(samples, sample_rate, f) for f in low_freqs]
    high_mags = [goertzel(samples, sample_rate, f) for f in high_freqs]
    
    low_idx = np.argmax(low_mags)
    high_idx = np.argmax(high_mags)
    
    threshold = 800000  # Lower threshold to catch more
    if low_mags[low_idx] > threshold and high_mags[high_idx] > threshold:
        return dtmf_table[low_idx][high_idx]
    
    return None

print("="*70)
print("WIRETAP - COMPLETE AUDIO SCAN")
print("="*70)

# Read WAV
wav_file = "beep_beep_boop.wav"
with wave.open(wav_file, 'rb') as wav:
    sample_rate = wav.getframerate()
    n_frames = wav.getnframes()
    frames = wav.readframes(n_frames)
    duration = n_frames / sample_rate

print(f"\nAudio: {duration:.1f}s @ {sample_rate}Hz")

audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float64)

# Detect all tones with timestamps
chunk_size = int(sample_rate * 0.05)
hop_size = int(sample_rate * 0.02)

all_detections = []
last_tone = None
last_time = -1

print("\nScanning entire audio file...")
print("(Showing all detections with timestamps)\n")

for i in range(0, len(audio_data) - chunk_size, hop_size):
    chunk = audio_data[i:i+chunk_size]
    tone = detect_dtmf_tone(chunk, sample_rate)
    
    current_time = i / sample_rate
    
    if tone and tone != last_tone:
        if current_time - last_time > 0.08:  # 80ms gap
            all_detections.append((current_time, tone))
            print(f"  {current_time:7.2f}s: {tone}")
            last_time = current_time
        last_tone = tone
    elif not tone:
        last_tone = None

# Extract just the sequence
sequence = ''.join([t[1] for t in all_detections])

print(f"\n{'='*70}")
print(f"COMPLETE SEQUENCE ({len(sequence)} tones):")
print(f"{sequence}")
print(f"{'='*70}")

# Try ASCII decoding (2-digit groups)
print("\n[1] ASCII Decode (2-digit groups):")
if len(sequence) >= 2:
    ascii_result = []
    i = 0
    while i < len(sequence) - 1:
        try:
            code = int(sequence[i:i+2])
            if 32 <= code <= 126:
                ascii_result.append(chr(code))
                i += 2
            else:
                i += 1
        except:
            i += 1
    
    if ascii_result:
        text = ''.join(ascii_result)
        print(f"  {text}")
        if 'CIT{' in text:
            print(f"\n  ✓✓ FOUND FLAG: {text}")

# Try ASCII decoding (3-digit groups)
print("\n[2] ASCII Decode (3-digit groups):")
if len(sequence) >= 3:
    ascii_result = []
    i = 0
    while i < len(sequence) - 2:
        try:
            code = int(sequence[i:i+3])
            if 32 <= code <= 126:
                ascii_result.append(chr(code))
                i += 3
            else:
                i += 1
        except:
            i += 1
    
    if ascii_result:
        text = ''.join(ascii_result)
        print(f"  {text}")
        if 'CIT{' in text:
            print(f"\n  ✓✓ FOUND FLAG: {text}")

# Look for patterns
print("\n[3] Pattern Analysis:")
print(f"  Total tones: {len(sequence)}")
print(f"  Unique tones: {set(sequence)}")
print(f"  First 20: {sequence[:20]}")
print(f"  Last 20: {sequence[-20:]}")

print(f"\n{'='*70}")
