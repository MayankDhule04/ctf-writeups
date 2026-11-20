#!/usr/bin/env python3
"""
Wiretap - Improved DTMF Decoder
Using Goertzel algorithm for better tone detection
"""

import wave
import numpy as np
import struct

def goertzel(samples, sample_rate, target_freq):
    """
    Goertzel algorithm for detecting a specific frequency
    More efficient than FFT for single frequency detection
    """
    n = len(samples)
    k = int(0.5 + (n * target_freq) / sample_rate)
    omega = (2.0 * np.pi * k) / n
    sine = np.sin(omega)
    cosine = np.cos(omega)
    coeff = 2.0 * cosine
    
    q0 = 0.0
    q1 = 0.0
    q2 = 0.0
    
    for sample in samples:
        q0 = coeff * q1 - q2 + sample
        q2 = q1
        q1 = q0
    
    magnitude = np.sqrt(q1**2 + q2**2 - q1*q2*coeff)
    return magnitude

def detect_dtmf_tone(samples, sample_rate):
    """
    Detect DTMF tone in audio samples
    """
    # DTMF frequencies
    low_freqs = [697, 770, 852, 941]
    high_freqs = [1209, 1336, 1477, 1633]
    
    # DTMF keypad
    dtmf_table = [
        ['1', '2', '3', 'A'],
        ['4', '5', '6', 'B'],
        ['7', '8', '9', 'C'],
        ['*', '0', '#', 'D']
    ]
    
    # Calculate magnitudes for all frequencies
    low_mags = [goertzel(samples, sample_rate, f) for f in low_freqs]
    high_mags = [goertzel(samples, sample_rate, f) for f in high_freqs]
    
    # Find strongest frequencies
    low_idx = np.argmax(low_mags)
    high_idx = np.argmax(high_mags)
    
    # Check if magnitudes are strong enough
    threshold = 1000000  # Adjust based on audio
    if low_mags[low_idx] > threshold and high_mags[high_idx] > threshold:
        return dtmf_table[low_idx][high_idx]
    
    return None

print("="*70)
print("WIRETAP - IMPROVED DTMF DECODER")
print("="*70)

# Read WAV file
wav_file = "beep_beep_boop.wav"
with wave.open(wav_file, 'rb') as wav:
    sample_rate = wav.getframerate()
    n_frames = wav.getnframes()
    frames = wav.readframes(n_frames)
    
    print(f"\nAudio: {n_frames/sample_rate:.1f}s @ {sample_rate}Hz")

# Convert to numpy array
audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float64)

# Process in chunks
chunk_duration = 0.05  # 50ms chunks
chunk_size = int(sample_rate * chunk_duration)
hop_size = int(sample_rate * 0.02)  # 20ms hop

detected_sequence = []
last_tone = None
last_time = -1

print("\nDetecting DTMF tones...")

for i in range(0, len(audio_data) - chunk_size, hop_size):
    chunk = audio_data[i:i+chunk_size]
    tone = detect_dtmf_tone(chunk, sample_rate)
    
    current_time = i / sample_rate
    
    if tone and tone != last_tone:
        # Avoid duplicates (require 100ms gap)
        if current_time - last_time > 0.1:
            detected_sequence.append(tone)
            print(f"  {current_time:.2f}s: {tone}")
            last_time = current_time
        last_tone = tone
    elif not tone:
        last_tone = None

print(f"\n{'='*70}")
print(f"DETECTED SEQUENCE: {''.join(detected_sequence)}")
print(f"{'='*70}")

# Try to decode
sequence = ''.join(detected_sequence)

# Check if it's ASCII
print(f"\n[1] Trying ASCII interpretation:")
try:
    # Try as decimal ASCII codes (groups of 2 or 3)
    for group_size in [2, 3]:
        if len(sequence) % group_size == 0:
            ascii_chars = []
            for i in range(0, len(sequence), group_size):
                code = int(sequence[i:i+group_size])
                if 32 <= code <= 126:
                    ascii_chars.append(chr(code))
                else:
                    break
            if len(ascii_chars) * group_size == len(sequence):
                result = ''.join(ascii_chars)
                print(f"  Group size {group_size}: {result}")
                if 'CIT{' in result or 'cit{' in result.lower():
                    print(f"  ✓✓ FOUND FLAG: {result}")
except:
    pass

# Try hex
print(f"\n[2] Trying hex interpretation:")
try:
    if len(sequence) % 2 == 0:
        hex_bytes = bytes.fromhex(sequence)
        text = hex_bytes.decode('ascii', errors='ignore')
        print(f"  As hex: {text}")
        if 'CIT{' in text:
            print(f"  ✓✓ FOUND FLAG: {text}")
except:
    pass

# Phone keypad T9
print(f"\n[3] Phone keypad mapping (T9):")
phone_map = {
    '2': 'ABC', '3': 'DEF', '4': 'GHI', '5': 'JKL',
    '6': 'MNO', '7': 'PQRS', '8': 'TUV', '9': 'WXYZ',
    '0': ' ', '1': '', '*': '', '#': ''
}
for char in sequence:
    if char in phone_map and phone_map[char]:
        print(f"  {char} -> {phone_map[char]}")

print(f"\n{'='*70}")
